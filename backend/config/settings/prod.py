"""Production. Fails fast at startup when a required variable is missing."""

from .base import *

DEBUG = False

# Each call below raises ImproperlyConfigured when the variable is unset.
SECRET_KEY = env.str("SECRET_KEY")
# 127.0.0.1/localhost are only for the container HEALTHCHECK, which calls the app directly.
ALLOWED_HOSTS = [*env.list("ALLOWED_HOSTS"), "127.0.0.1", "localhost"]
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
# Health checks reach the container over plain HTTP without the proxy header.
SECURE_REDIRECT_EXEMPT = [r"^api/v1/health$"]
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
