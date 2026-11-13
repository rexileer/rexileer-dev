import json
from decimal import Decimal
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from desk.bureau_import import import_bureau


class Command(BaseCommand):
    help = "Privately append dated bureau evidence; defaults to rollback preview."

    def add_arguments(self, parser):
        parser.add_argument("file")
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        try:
            raw = Path(options["file"]).read_bytes()
            if len(raw) > 8 * 1024 * 1024:
                raise CommandError("Private package exceeds 8 MiB.")
            payload = json.loads(raw, parse_float=Decimal)
            result = import_bureau(
                payload, actor="bki-cli", dry_run=not options["apply"]
            )
        except (OSError, ValueError, ValidationError):
            raise CommandError(
                "Bureau package rejected; transaction rolled back. No private rows printed."
            ) from None
        self.stdout.write(json.dumps({"applied": options["apply"], **result}))
