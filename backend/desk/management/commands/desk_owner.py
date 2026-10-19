import os
import secrets
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Create the isolated owner from a private password file; never print secrets."
    )

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--password-file")
        group.add_argument("--generate-file")
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **options):
        model = get_user_model()
        user = model.objects.filter(username=settings.OWNER_USERNAME).first()
        if user and not options["reset"]:
            self.stdout.write("Owner already exists; password unchanged.")
            return
        path = Path(options["password_file"] or options["generate_file"])
        if options["generate_file"] and not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with os.fdopen(
                os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w"
            ) as stream:
                stream.write(secrets.token_urlsafe(32) + "\n")
        if not path.is_file() or (os.name != "nt" and path.stat().st_mode & 0o077):
            raise CommandError("Password file must exist and be private (0600).")
        password = path.read_text(encoding="utf-8").strip()
        user = user or model(username=settings.OWNER_USERNAME)
        try:
            validate_password(password, user)
        except ValidationError as error:
            raise CommandError("; ".join(error.messages)) from None
        user.set_password(password)
        user.is_active = user.is_staff = user.is_superuser = True
        user.save()
        self.stdout.write(
            "Isolated owner account ready. Secret remains in the private file."
        )
