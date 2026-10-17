import secrets
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from django.core.exceptions import ImproperlyConfigured
from portfolio.signing_config import load_secret_key


class SigningConfigurationTests(TestCase):
    def test_missing_or_weak_key_is_rejected_without_echoing_it(self):
        for value in (
            "",
            "short",
            "a" * 64,
            "django-insecure-" + secrets.token_urlsafe(64),
        ):
            with self.subTest(configured=bool(value)):
                with self.assertRaises(ImproperlyConfigured) as error:
                    load_secret_key({"DJANGO_SECRET_KEY": value})
                if value:
                    self.assertNotIn(value, str(error.exception))

    def test_explicit_environment_and_private_file_are_supported(self):
        value = secrets.token_urlsafe(64)
        self.assertEqual(load_secret_key({"DJANGO_SECRET_KEY": value}), value)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "signing.key"
            path.write_text(value + "\n", encoding="utf-8")
            self.assertEqual(
                load_secret_key({"DJANGO_SECRET_KEY_FILE": str(path)}), value
            )
            self.assertEqual(
                load_secret_key(
                    {"DJANGO_SECRET_KEY": value, "DJANGO_SECRET_KEY_FILE": "missing"}
                ),
                value,
            )

    def test_unreadable_file_is_reported_without_fallback(self):
        with self.assertRaises(ImproperlyConfigured):
            load_secret_key({"DJANGO_SECRET_KEY_FILE": "missing-private-signing-file"})
