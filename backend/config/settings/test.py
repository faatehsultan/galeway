"""Test settings: hermetic (never reads .env or real keys)."""

from .base import *

SECRET_KEY = "test-only-not-secret"
ALLOWED_HOSTS = ["testserver"]
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
LOGGING_CONFIG = None  # keep pytest's own log capture; tests configure structlog explicitly
