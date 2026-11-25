"""Request id, request log line and ``X-Robots-Tag`` (docs/05-backend/BACKEND.md §1, §6)."""

import re
import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.http import HttpRequest, HttpResponse

REQUEST_ID_HEADER = "X-Request-ID"
# Only accept a client-supplied id that is short and boring; anything else is replaced.
_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")

_log = structlog.get_logger("galeway.request")


class RequestIdMiddleware:
    """Async-only middleware: tags the request, logs one line, adds response headers."""

    sync_capable = False
    async_capable = True

    def __init__(self, get_response: Callable[[HttpRequest], Awaitable[HttpResponse]]) -> None:
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request: HttpRequest) -> HttpResponse:
        supplied = request.headers.get(REQUEST_ID_HEADER, "")
        request_id = supplied if _VALID_REQUEST_ID.fullmatch(supplied) else uuid.uuid4().hex
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        started = time.perf_counter()
        response = await self.get_response(request)
        duration_ms = round((time.perf_counter() - started) * 1000, 1)

        response[REQUEST_ID_HEADER] = request_id
        # The API is not a web page; keep it out of search indexes (docs/04-frontend/SEO.md §1).
        response["X-Robots-Tag"] = "noindex"
        # Path only: query strings can carry user input and must not be logged verbatim.
        _log.info(
            "request",
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response
