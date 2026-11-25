import re

from django.test import AsyncClient

HEALTH = "/api/v1/health"


async def test_health_returns_ok_and_version(async_client: AsyncClient) -> None:
    response = await async_client.get(HEALTH)

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "dev"}


async def test_health_is_never_cached(async_client: AsyncClient) -> None:
    response = await async_client.get(HEALTH)

    assert "no-store" in response["Cache-Control"]


async def test_api_responses_are_noindex(async_client: AsyncClient) -> None:
    response = await async_client.get(HEALTH)

    assert response["X-Robots-Tag"] == "noindex"


async def test_docs_are_not_exposed_outside_dev(async_client: AsyncClient) -> None:
    assert (await async_client.get("/api/v1/docs")).status_code == 404
    assert (await async_client.get("/api/v1/openapi.json")).status_code == 404


async def test_unknown_path_is_404(async_client: AsyncClient) -> None:
    assert (await async_client.get("/api/v1/nope")).status_code == 404


async def test_cors_allows_only_the_configured_origin(async_client: AsyncClient) -> None:
    allowed = await async_client.get(HEALTH, headers={"Origin": "http://localhost:5173"})
    denied = await async_client.get(HEALTH, headers={"Origin": "https://evil.example"})

    assert allowed["Access-Control-Allow-Origin"] == "http://localhost:5173"
    assert "Access-Control-Allow-Origin" not in denied
    assert "Access-Control-Allow-Credentials" not in allowed


async def test_cors_exposes_request_id(async_client: AsyncClient) -> None:
    response = await async_client.get(HEALTH, headers={"Origin": "http://localhost:5173"})

    assert "x-request-id" in response["Access-Control-Expose-Headers"]


class TestRequestId:
    async def test_generates_an_id_when_none_is_sent(self, async_client: AsyncClient) -> None:
        response = await async_client.get(HEALTH)

        assert re.fullmatch(r"[0-9a-f]{32}", response["X-Request-ID"])

    async def test_echoes_a_well_formed_client_id(self, async_client: AsyncClient) -> None:
        response = await async_client.get(HEALTH, headers={"X-Request-ID": "web-1234.abcd_EF"})

        assert response["X-Request-ID"] == "web-1234.abcd_EF"

    async def test_replaces_a_malformed_client_id(self, async_client: AsyncClient) -> None:
        # Header/log injection attempt and an over-long value are both rejected.
        for bad in ("short", "x" * 65, "has spaces in it!", "a/b/c/d/e/f/g/h"):
            response = await async_client.get(HEALTH, headers={"X-Request-ID": bad})

            assert response["X-Request-ID"] != bad
            assert re.fullmatch(r"[0-9a-f]{32}", response["X-Request-ID"])
