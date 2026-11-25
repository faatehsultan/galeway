"""Local development. Reads backend/.env (git-ignored) if present."""

from pathlib import Path

import environ

_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"
if _ENV_FILE.exists():
    environ.Env.read_env(_ENV_FILE)

from .base import *

DEBUG = True
SECRET_KEY = env.str("SECRET_KEY", default="dev-only-not-secret")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:5173"])
