from pathlib import Path

from django.core.exceptions import ImproperlyConfigured


def load_secret_key(environ):
    key = environ.get("DJANGO_SECRET_KEY", "")
    if not key and environ.get("DJANGO_SECRET_KEY_FILE"):
        try:
            key = (
                Path(environ["DJANGO_SECRET_KEY_FILE"])
                .read_text(encoding="utf-8")
                .strip()
            )
        except OSError:
            raise ImproperlyConfigured(
                "Cannot read configured Django signing-key file"
            ) from None
    if (
        len(key) < 50
        or len(set(key)) < 5
        or key.startswith("django-insecure-")
        or any(character.isspace() for character in key)
    ):
        raise ImproperlyConfigured(
            "Configure a private random DJANGO_SECRET_KEY of at least 50 characters"
        )
    return key
