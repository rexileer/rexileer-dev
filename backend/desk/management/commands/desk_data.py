import json
import os
import sys
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from desk.services import export_records, import_records, read_records


class Command(BaseCommand):
    help = "Private CRUD/import by external ID, transactional preview, and JSON export."

    def add_arguments(self, parser):
        sub = parser.add_subparsers(dest="action", required=True)
        incoming = sub.add_parser("import")
        incoming.add_argument("input", help="Private UTF-8 file, or - for stdin")
        incoming.add_argument("--format", choices=["json", "csv"], default="json")
        incoming.add_argument("--source", default="import")
        incoming.add_argument("--batch", default="")
        incoming.add_argument("--entity", default="")
        incoming.add_argument(
            "--apply", action="store_true", help="Otherwise preview with rollback"
        )
        incoming.add_argument("--actor", default="ssh-owner")
        outgoing = sub.add_parser("export")
        outgoing.add_argument("--output", required=True)

    def handle(self, *args, **options):
        if options["action"] == "export":
            path = Path(options["output"])
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            try:
                with os.fdopen(
                    os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600),
                    "w",
                    encoding="utf-8",
                ) as stream:
                    json.dump(export_records(), stream, ensure_ascii=False, indent=2)
            except OSError:
                raise CommandError(
                    "Cannot create private export; use a new output filename."
                ) from None
            self.stdout.write("Private JSON export saved.")
            return
        path = None if options["input"] == "-" else Path(options["input"])
        if path and (
            not path.is_file() or (os.name != "nt" and path.stat().st_mode & 0o077)
        ):
            raise CommandError("Input must be a private regular file (0600), or stdin.")
        if path:
            with path.open("rb") as stream:
                raw = stream.read(2 * 1024 * 1024 + 1)
        else:
            raw = sys.stdin.buffer.read(2 * 1024 * 1024 + 1)
        try:
            records = read_records(
                raw,
                options["format"],
                source=options["source"],
                batch=options["batch"],
                entity=options["entity"],
            )
            result = import_records(
                records, actor=options["actor"], dry_run=not options["apply"]
            )
        except (ValidationError, ValueError) as error:
            # Do not echo source values, client names or financial payloads in logs.
            message = (
                "; ".join(error.messages)
                if isinstance(error, ValidationError)
                else "Invalid input."
            )
            raise CommandError(message) from None
        self.stdout.write(
            json.dumps(
                {
                    "dry_run": not options["apply"],
                    "records": len(result),
                    "changed": sum(row["changed"] for row in result),
                }
            )
        )
