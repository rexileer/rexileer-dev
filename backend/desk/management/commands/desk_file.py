import json
import os
from pathlib import Path

from django.core.exceptions import (
    FieldDoesNotExist,
    ObjectDoesNotExist,
    ValidationError,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from desk.documents import MIMES, edit_document, upload_document
from desk.models import Document
from desk.services import resolve


class Command(BaseCommand):
    help = "Private file upload or metadata update, preview by default; same validation as UI."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["upload", "update"])
        parser.add_argument("--metadata", required=True)
        parser.add_argument("--file")
        parser.add_argument("--source", default="desk")
        parser.add_argument("--external-id", required=True)
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        meta = Path(options["metadata"])
        if (
            not meta.is_file()
            or meta.stat().st_size > 64000
            or (os.name != "nt" and meta.stat().st_mode & 0o077)
        ):
            raise CommandError("Metadata must be a private JSON file, at most 64 KB.")
        try:
            fields = json.loads(meta.read_text(encoding="utf-8"))
            if not isinstance(fields, dict):
                raise ValidationError("Expected a metadata object.")
            for name, value in list(fields.items()):
                field = Document._meta.get_field(name)
                value = resolve(field, value)
                fields[name] = (
                    field.related_model.objects.get(pk=value)
                    if field.is_relation and value
                    else value
                )
            if options["action"] == "upload":
                if not options["file"]:
                    raise CommandError("Upload requires --file.")
                path = Path(options["file"])
                if not path.is_file() or (
                    os.name != "nt" and path.stat().st_mode & 0o077
                ):
                    raise CommandError("Input file must be private (0600).")
                with path.open("rb") as stream:
                    raw = stream.read(10 * 1024 * 1024 + 1)
                file = SimpleUploadedFile(
                    path.name,
                    raw,
                    content_type=MIMES.get(
                        path.suffix.lower(), "application/octet-stream"
                    ),
                )
                result = upload_document(
                    fields,
                    file,
                    actor="ssh-owner",
                    source=options["source"],
                    external_id=options["external_id"],
                    dry_run=not options["apply"],
                )
            else:
                document = Document.objects.get(
                    source=options["source"], external_id=options["external_id"]
                )
                with transaction.atomic():
                    result = edit_document(document, fields, actor="ssh-owner")
                    if not options["apply"]:
                        transaction.set_rollback(True)
            self.stdout.write(
                json.dumps({"dry_run": not options["apply"], "id": result.pk})
            )
        except (
            ValidationError,
            ValueError,
            OSError,
            ObjectDoesNotExist,
            FieldDoesNotExist,
        ):
            raise CommandError(
                "File operation rejected; check private input, metadata fields, duplicates and types. No file contents or secrets are printed."
            ) from None
