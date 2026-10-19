"""A DB snapshot plus exactly its immutable encrypted blobs; keys excluded."""

import hashlib
import io
import json
import os
import shutil
import sqlite3
import tarfile
import tempfile
from contextlib import closing
from pathlib import Path

from cryptography.fernet import InvalidToken
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import CommandError

from .documents import blob_path, cipher


def sqlite_copy(source, target):
    with (
        closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as src,
        closing(sqlite3.connect(target)) as dst,
    ):
        src.backup(dst)
    target.chmod(0o600)


def document_rows(database):
    with closing(sqlite3.connect(database)) as db:
        db.execute("PRAGMA trusted_schema=OFF")
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise CommandError("Database integrity check failed.")
        required = {
            "desk_document",
            "desk_obligation",
            "desk_change",
            "auth_user",
            "django_migrations",
        }
        actual = {
            r[0]
            for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        if not required <= actual:
            raise CommandError("Not a complete Desk backup.")
        return list(db.execute("SELECT storage_key, sha256 FROM desk_document"))


def backup_bundle(database, target):
    if target.exists():
        raise CommandError(
            "Choose a new backup filename; existing history is retained."
        )
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix="desk-backup-") as directory:
        snapshot = Path(directory) / "database.sqlite3"
        sqlite_copy(database, snapshot)
        rows = document_rows(snapshot)
        paths = [(key, blob_path(key)) for key, _ in rows]
        required = snapshot.stat().st_size + sum(p.stat().st_size for _, p in paths)
        if shutil.disk_usage(target.parent).free < required + 512 * 1024 * 1024:
            raise CommandError("Not enough free space for a complete private backup.")
        manifest = {
            "format": "rexileer-desk-1",
            "database_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
            "blobs": {
                key: hashlib.sha256(p.read_bytes()).hexdigest() for key, p in paths
            },
        }
        partial = target.with_name(target.name + ".partial")
        try:
            with (
                os.fdopen(
                    os.open(partial, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb"
                ) as output,
                tarfile.open(fileobj=output, mode="w") as archive,
            ):
                archive.add(snapshot, arcname="database.sqlite3", recursive=False)
                data = json.dumps(manifest).encode()
                info = tarfile.TarInfo("manifest.json")
                info.size, info.mode = len(data), 0o600
                archive.addfile(info, io.BytesIO(data))
                for key, path in paths:
                    archive.add(path, arcname=f"blobs/{key}.fernet", recursive=False)
            os.replace(partial, target)
        finally:
            if partial.exists():
                partial.unlink()


def verify_bundle(source, *, restore_to=None):
    try:
        with (
            tempfile.TemporaryDirectory(prefix="desk-restore-") as directory,
            tarfile.open(source, "r:") as archive,
        ):
            members = archive.getmembers()
            names = [m.name for m in members]
            if (
                len(names) != len(set(names))
                or len(names) > 10002
                or sum(m.size for m in members) > 1024 * 1024 * 1024
            ):
                raise ValueError
            if any(not m.isfile() or m.size < 0 for m in members):
                raise ValueError
            manifest_file = archive.getmember("manifest.json")
            database_file = archive.getmember("database.sqlite3")
            if (
                manifest_file.size > 2 * 1024 * 1024
                or database_file.size > 128 * 1024 * 1024
            ):
                raise ValueError
            manifest = json.loads(archive.extractfile(manifest_file).read())
            if manifest.get("format") != "rexileer-desk-1":
                raise ValueError
            expected_names = {"manifest.json", "database.sqlite3"} | {
                f"blobs/{key}.fernet" for key in manifest["blobs"]
            }
            if set(names) != expected_names:
                raise ValueError
            database = Path(directory) / "database.sqlite3"
            raw_db = archive.extractfile(database_file).read()
            if hashlib.sha256(raw_db).hexdigest() != manifest["database_sha256"]:
                raise ValueError
            database.write_bytes(raw_db)
            database.chmod(0o600)
            rows = document_rows(database)
            if {key for key, _ in rows} != set(manifest["blobs"]):
                raise ValueError
            for key, plain_digest in rows:
                target = blob_path(key)  # Also validates the UUID; never extract paths.
                member = archive.getmember(f"blobs/{key}.fernet")
                if member.size > settings.DOCUMENT_MAX_BYTES * 2:
                    raise ValueError
                token = archive.extractfile(member).read()
                if hashlib.sha256(token).hexdigest() != manifest["blobs"][key]:
                    raise ValueError
                plain = cipher().decrypt(token)
                if hashlib.sha256(plain).hexdigest() != plain_digest:
                    raise ValueError
                if restore_to:
                    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                    if target.exists():
                        if target.read_bytes() != token:
                            raise ValueError
                    else:
                        with os.fdopen(
                            os.open(
                                target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
                            ),
                            "wb",
                        ) as output:
                            output.write(token)
            if restore_to:
                sqlite_copy(database, restore_to)
            return len(rows)
    except (
        KeyError,
        ValueError,
        OSError,
        tarfile.TarError,
        sqlite3.Error,
        InvalidToken,
        ValidationError,
        TypeError,
        AttributeError,
        RecursionError,
    ) as error:
        # Crypto failures and malformed backup contents must not echo payloads.
        if isinstance(error, CommandError):
            raise
        raise CommandError(
            "Private backup verification failed: archive, integrity or separate document key is invalid."
        ) from None
