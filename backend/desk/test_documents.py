import io
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import CommandError
from django.db import connection
from django.test import TransactionTestCase, override_settings
from PIL import Image

from .backups import backup_bundle, verify_bundle
from .documents import (
    blob_path,
    decrypt_document,
    edit_document,
    upload_document,
    validate_file,
)
from .models import Document, Transaction


def png():
    stream = io.BytesIO()
    Image.new("RGB", (20, 20), (24, 50, 36)).save(stream, "PNG")
    return stream.getvalue()


class DocumentTests(TransactionTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="synthetic-desk-")
        self.addCleanup(self.directory.cleanup)
        self.override = override_settings(
            DOCUMENT_ROOT=Path(self.directory.name) / "original",
            DOCUMENT_KEY=Fernet.generate_key().decode(),
        )
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.user = get_user_model().objects.create_user(
            settings.OWNER_USERNAME,
            password="Synthetic-document-owner-123",
            is_superuser=True,
        )
        self.raw = png()

    def create(self):
        return upload_document(
            {"title": "Synthetic proof only", "kind": "receipt"},
            SimpleUploadedFile("synthetic.png", self.raw, content_type="image/png"),
            actor="test",
        )

    def test_ciphertext_duplicate_and_receipt_do_not_create_money(self):
        record = self.create()
        encrypted = blob_path(record.storage_key).read_bytes()
        self.assertNotEqual(encrypted, self.raw)
        self.assertFalse(encrypted.startswith(b"\x89PNG"))
        self.assertEqual(decrypt_document(record), self.raw)
        with self.assertRaises(ValidationError):
            self.create()
        self.assertEqual(Document.objects.count(), 1)
        self.assertFalse(Transaction.objects.exists())
        edit_document(record, {"archived": True}, actor="test")
        self.assertTrue(blob_path(record.storage_key).exists())

    def test_type_name_size_and_image_spoofing_are_rejected(self):
        for name, mime, data in [
            ("../synthetic.png", "image/png", self.raw),
            ("folder\\synthetic.png", "image/png", self.raw),
            ("synthetic.svg", "image/svg+xml", b"<svg/>"),
            ("synthetic.pdf", "application/pdf", b"<html>unsafe</html>"),
            ("synthetic.png", "image/jpeg", self.raw),
            ("synthetic.jpg", "image/jpeg", self.raw),
            ("synthetic.png", "image/png", b"0" * (10 * 1024 * 1024 + 1)),
        ]:
            with self.subTest(name=name), self.assertRaises(ValidationError):
                validate_file(name, mime, data)

    def test_every_preview_download_is_owner_only_host_checked_no_store(self):
        record = self.create()
        for mode in ("preview", "download"):
            url = f"/documents/{record.pk}/{mode}/"
            self.assertEqual(
                self.client.get(
                    url, secure=True, HTTP_HOST="desk.rexileer.ru"
                ).status_code,
                302,
            )
            self.client.force_login(self.user)
            response = self.client.get(url, secure=True, HTTP_HOST="desk.rexileer.ru")
            self.assertEqual(response.content, self.raw)
            self.assertIn("no-store", response["Cache-Control"])
            self.assertEqual(response["X-Content-Type-Options"], "nosniff")
            self.assertIn("sandbox", response["Content-Security-Policy"])
            self.assertNotIn("synthetic.png", response["Content-Disposition"])
            self.assertEqual(
                self.client.get(url, secure=True, HTTP_HOST="rexileer.ru").status_code,
                400,
            )
            self.client.logout()

    def test_wrong_key_does_not_return_plaintext(self):
        record = self.create()
        self.client.force_login(self.user)
        with override_settings(DOCUMENT_KEY=Fernet.generate_key().decode()):
            response = self.client.get(
                f"/documents/{record.pk}/preview/",
                secure=True,
                HTTP_HOST="desk.rexileer.ru",
            )
            self.assertEqual(response.status_code, 503)
            self.assertNotIn(self.raw, response.content)
            self.assertNotIn(settings.DOCUMENT_KEY.encode(), response.content)

    def test_complete_backup_restores_db_and_encrypted_blob_with_separate_key(self):
        record = self.create()
        database = Path(self.directory.name) / "source.sqlite3"
        with closing(sqlite3.connect(database)) as copy:
            connection.connection.backup(copy)
        bundle = Path(self.directory.name) / "complete.desk"
        backup_bundle(database, bundle)
        self.assertEqual(verify_bundle(bundle), 1)
        with (
            override_settings(DOCUMENT_KEY=Fernet.generate_key().decode()),
            self.assertRaises(CommandError),
        ):
            verify_bundle(bundle)
        restored = Path(self.directory.name) / "restored.sqlite3"
        with override_settings(
            DOCUMENT_ROOT=Path(self.directory.name) / "restored-blobs"
        ):
            self.assertEqual(verify_bundle(bundle, restore_to=restored), 1)
            self.assertEqual(decrypt_document(record), self.raw)
        with closing(sqlite3.connect(restored)) as db:
            self.assertEqual(
                db.execute("SELECT count(*) FROM desk_document").fetchone()[0], 1
            )
        self.assertNotIn(settings.DOCUMENT_KEY.encode(), bundle.read_bytes())
