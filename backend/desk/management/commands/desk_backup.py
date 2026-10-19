import os
import sqlite3
import tempfile
import time
from contextlib import closing
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from desk.backups import backup_bundle, verify_bundle
from desk.models import Document


def clone(source, destination):
    with (
        closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as incoming,
        closing(sqlite3.connect(destination)) as outgoing,
    ):
        incoming.execute("PRAGMA trusted_schema=OFF")
        incoming.backup(outgoing)
    destination.chmod(0o600)


def verify(source):
    with tempfile.TemporaryDirectory(prefix="desk-restore-check-") as directory:
        copy = Path(directory) / "restore.sqlite3"
        clone(source, copy)
        with closing(sqlite3.connect(copy)) as db:
            db.execute("PRAGMA trusted_schema=OFF")
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise CommandError("Backup integrity check failed.")
            tables = {
                row[0]
                for row in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            required = {
                "desk_obligation",
                "desk_transaction",
                "desk_change",
                "auth_user",
                "django_migrations",
            }
            if not required <= tables:
                raise CommandError("This is not a complete Desk database backup.")
            return {
                name: db.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
                for name in sorted(required)
            }


class Command(BaseCommand):
    help = "Private SQLite backup, isolated restore verification, and maintenance-only restore."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["backup", "verify", "restore"])
        parser.add_argument("file")
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **options):
        path = Path(options["file"]).resolve()
        current = Path(settings.DATABASES["default"]["NAME"]).resolve()
        if path == current:
            raise CommandError("Backup and working database must be different files.")
        if path.suffix == ".desk":
            if options["action"] == "backup":
                backup_bundle(current, path)
                verify_bundle(path)
                self.stdout.write(
                    "Complete private DB + encrypted documents backup verified; keys excluded."
                )
                return
            if not path.is_file() or (os.name != "nt" and path.stat().st_mode & 0o077):
                raise CommandError("Backup must be private (0600).")
            count = verify_bundle(path)
            if options["action"] == "restore" and options["apply"]:
                if os.environ.get("DESK_RESTORE_MAINTENANCE") != "1":
                    raise CommandError(
                        "Stop Desk and use a one-off maintenance container."
                    )
                connections.close_all()
                if current.exists():
                    backup_bundle(
                        current, current.parent / f"pre-restore-{time.time_ns()}.desk"
                    )
                verify_bundle(path, restore_to=current)
                self.stdout.write(
                    "Complete private restore applied; previous state backed up."
                )
            else:
                self.stdout.write(
                    f"Isolated DB + {count} encrypted files verified with separate key; working DB unchanged."
                )
            return
        if Document.objects.exists() and options["action"] == "backup":
            raise CommandError(
                "Use a complete .desk backup when documents exist; SQLite alone omits files."
            )
        try:
            if options["action"] == "backup":
                if path.exists():
                    raise CommandError("Keep backup history: choose a new filename.")
                path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                clone(current, path)
                verify(path)
                self.stdout.write("Private consistent SQLite backup verified.")
                return
            if not path.is_file() or (os.name != "nt" and path.stat().st_mode & 0o077):
                raise CommandError("Backup must be a private regular file (0600).")
            counts = verify(path)
            if options["action"] == "restore" and options["apply"]:
                if os.environ.get("DESK_RESTORE_MAINTENANCE") != "1":
                    raise CommandError(
                        "Stop Desk and use a one-off maintenance container with DESK_RESTORE_MAINTENANCE=1."
                    )
                connections.close_all()
                if current.exists():
                    clone(
                        current,
                        current.parent / f"pre-restore-{time.time_ns()}.sqlite3",
                    )
                clone(path, current)
                self.stdout.write(
                    "Private restore applied; previous database backed up."
                )
            else:
                self.stdout.write(
                    f"Isolated restore verification passed ({sum(counts.values())} rows in checked tables); working DB unchanged."
                )
        except (OSError, sqlite3.Error):
            raise CommandError(
                "Cannot read, verify or copy the private SQLite file."
            ) from None
