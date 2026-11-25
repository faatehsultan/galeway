"""Structured JSON logging with secret redaction (docs/05-backend/BACKEND.md §6).

Golden rule 5: provider keys never reach logs. Every log line, ours and the standard
library's (httpx, uvicorn, Django), passes through ``redact_event`` before it is written.
"""

import logging
import re
from collections.abc import MutableMapping
from typing import Any

import structlog

REDACTED = "[REDACTED]"

# Query-string style secrets inside any message, e.g. ".../route?key=abc123&x=1".
_SECRET_PARAM = re.compile(r"(?i)\b(key|api_key|apikey|token|access_token)=[^&\s\"']+")
_SENSITIVE_FIELDS = frozenset({"authorization", "cookie", "set-cookie", "key", "api_key", "token"})

EventDict = MutableMapping[str, Any]


def redact_text(text: str) -> str:
    return _SECRET_PARAM.sub(lambda m: f"{m.group(1)}={REDACTED}", text)


def redact_event(_logger: object, _method: str, event_dict: EventDict) -> EventDict:
    """structlog processor.

    shortcut: top-level string fields only; extend if nested logging appears.
    """
    for name, value in event_dict.items():
        if name.lower() in _SENSITIVE_FIELDS:
            event_dict[name] = REDACTED
        elif isinstance(value, str):
            event_dict[name] = redact_text(value)
    return event_dict


def _shared_processors() -> list[structlog.typing.Processor]:
    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.format_exc_info,  # before redaction so tracebacks are scrubbed too
        redact_event,
    ]


def configure_structlog() -> None:
    structlog.configure(
        processors=[
            *_shared_processors(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def build_logging_config(level: str) -> dict[str, Any]:
    """Django ``LOGGING``: all stdlib loggers render as JSON through the same redaction."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "foreign_pre_chain": _shared_processors(),
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.JSONRenderer(),
                ],
            }
        },
        "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
        "root": {"handlers": ["console"], "level": level},
        "loggers": {
            # Uvicorn's access log would print every URL; our request log replaces it.
            "uvicorn.access": {"level": logging.WARNING},
        },
    }
