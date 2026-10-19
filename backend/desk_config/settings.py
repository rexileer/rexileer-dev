"""Isolated owner workspace. Never import the portfolio settings or models."""

import os
from pathlib import Path

from cryptography.fernet import Fernet
from portfolio.signing_config import load_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = load_secret_key(
    {
        "DJANGO_SECRET_KEY": os.environ.get("DESK_SECRET_KEY", ""),
        "DJANGO_SECRET_KEY_FILE": os.environ.get("DESK_SECRET_KEY_FILE", ""),
    }
)
SECRET_KEY_FALLBACKS = []
DOCUMENT_KEY = os.environ.get("DESK_DOCUMENT_KEY", "")
if not DOCUMENT_KEY and os.environ.get("DESK_DOCUMENT_KEY_FILE"):
    DOCUMENT_KEY = (
        Path(os.environ["DESK_DOCUMENT_KEY_FILE"]).read_text(encoding="utf-8").strip()
    )
Fernet(DOCUMENT_KEY.encode("ascii"))
DOCUMENT_ROOT = Path(
    os.environ.get("DESK_DOCUMENT_ROOT", str(BASE_DIR / "desk-documents"))
)
DOCUMENT_MAX_BYTES = 10 * 1024 * 1024
DOCUMENT_QUOTA_BYTES = 512 * 1024 * 1024
DEBUG = False
ALLOWED_HOSTS = ["desk.rexileer.ru"]
OWNER_USERNAME = os.environ.get("DESK_OWNER_USERNAME", "owner")
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "desk",
]
MIDDLEWARE = [
    "desk.security.PrivateHeadersMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "desk.security.OwnerMiddleware",
]
ROOT_URLCONF = "desk_config.urls"
WSGI_APPLICATION = "desk_config.wsgi.application"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DESK_DB_PATH", str(BASE_DIR / "desk.sqlite3")),
        "OPTIONS": {"timeout": 15},
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Moscow"
USE_TZ = True
USE_I18N = True
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"
SESSION_COOKIE_NAME = "__Host-rexileer_desk"
CSRF_COOKIE_NAME = "__Host-rexileer_desk_csrf"
SESSION_COOKIE_DOMAIN = None
CSRF_COOKIE_DOMAIN = None
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_AGE = 43200
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_TRUSTED_ORIGINS = ["https://desk.rexileer.ru"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
DATA_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 14},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
]
