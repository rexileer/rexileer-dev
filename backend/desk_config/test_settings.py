"""Explicitly opt-in local browser verification, never used in Compose."""

from .settings import *  # noqa: F403

ALLOWED_HOSTS = ["desk.rexileer.ru", "testserver", "127.0.0.1", "localhost"]
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_NAME = "desk_local_session"
CSRF_COOKIE_NAME = "desk_local_csrf"
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8092", "https://desk.rexileer.ru"]
