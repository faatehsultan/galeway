from django.conf import settings
from django.http import HttpRequest
from django.views.decorators.cache import never_cache
from ninja import Router
from ninja.decorators import decorate_view

from galeway.api.schemas import HealthOut

router = Router(tags=["system"])


@router.get("/health", response=HealthOut, summary="Liveness check", operation_id="health")
@decorate_view(never_cache)
async def health(request: HttpRequest) -> HealthOut:  # noqa: ARG001  # Ninja requires the name `request`
    """Does not touch providers. Used for keep-warm pings and the frontend pre-warm."""
    return HealthOut(status="ok", version=settings.GIT_SHA)
