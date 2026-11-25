"""Settings shared by every environment. See docs/05-backend/BACKEND.md §3-4."""

from pathlib import Path

import environ

from galeway.core.logging import build_logging_config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

# Trimmed Django: no admin, auth, sessions, messages or contenttypes, and no database.
INSTALLED_APPS = [
    "corsheaders",
    "ninja",
    "galeway.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "galeway.core.middleware.RequestIdMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"
DATABASES: dict[str, dict[str, str]] = {}

# Needed only by the dev-only API docs page.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {},
    }
]

USE_TZ = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
USE_I18N = False

# CORS: GET only, no credentials, no cookies anywhere (docs/03-architecture/SECURITY.md §2).
CORS_ALLOW_METHODS = ("GET", "HEAD", "OPTIONS")
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_HEADERS = ("accept", "content-type", "if-none-match", "x-request-id")
CORS_EXPOSE_HEADERS = ("etag", "link", "retry-after", "server-timing", "x-request-id")
CORS_PREFLIGHT_MAX_AGE = 86400

LOG_LEVEL = env.str("LOG_LEVEL", default="INFO").upper()
LOGGING = build_logging_config(LOG_LEVEL)

# Shown by /api/v1/health so a deploy can be matched to a commit.
GIT_SHA = env.str("GIT_SHA", default="dev")

# DEBUG is False unless an environment turns it on (dev only).
DEBUG = False
