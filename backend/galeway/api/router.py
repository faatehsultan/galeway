from django.conf import settings
from ninja import NinjaAPI

from galeway.api.endpoints import health

# Interactive docs and the schema URL exist in dev only (docs/05-backend/BACKEND.md §1).
api = NinjaAPI(
    title="Galeway API",
    version="1",
    urls_namespace="v1",
    docs_url="/docs" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)
api.add_router("", health.router)
