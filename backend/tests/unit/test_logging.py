import json
import logging.config

import pytest
import structlog

from galeway.core.logging import REDACTED, build_logging_config, redact_event, redact_text


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "GET https://api.tomtom.com/r?key=SECRET123&x=1",
            f"GET https://api.tomtom.com/r?key={REDACTED}&x=1",
        ),
        ("https://x.test/?a=1&API_KEY=abc", f"https://x.test/?a=1&API_KEY={REDACTED}"),
        ("token=abc.def", f"token={REDACTED}"),
        ("nothing sensitive: monkey=banana", "nothing sensitive: monkey=banana"),
        ("no query string at all", "no query string at all"),
    ],
)
def test_redact_text(raw: str, expected: str) -> None:
    assert redact_text(raw) == expected


def test_redact_event_scrubs_sensitive_fields_and_urls() -> None:
    event = {"event": "calling https://h/?key=abc", "Authorization": "Bearer xyz", "status": 200}

    result = redact_event(None, "info", event)

    assert result["event"] == f"calling https://h/?key={REDACTED}"
    assert result["Authorization"] == REDACTED
    assert result["status"] == 200


def test_stdlib_logs_are_json_and_redacted(capsys: pytest.CaptureFixture[str]) -> None:
    """httpx logs full URLs through the stdlib logger: the key must never come out."""
    structlog.contextvars.clear_contextvars()
    logging.config.dictConfig(build_logging_config("INFO"))

    logging.getLogger("httpx").info(
        "HTTP Request: GET %s", "https://api.tomtom.com/r?key=SECRET123"
    )

    line = json.loads(capsys.readouterr().err.strip().splitlines()[-1])
    assert "SECRET123" not in json.dumps(line)
    assert line["event"] == f"HTTP Request: GET https://api.tomtom.com/r?key={REDACTED}"
    assert line["level"] == "info"
