# Backend

Python 3.13 · Django 6.1 · Django Ninja (async) · httpx · redis-py (asyncio) · Pydantic v2 · uvicorn · uv for packaging. No database. See [ADR-0001](../09-decisions/0001-django-ninja-over-drf.md) for the choice of Ninja.

## 1. Layout

```text
backend/
├── manage.py                 # only for `export_openapi_schema` and Django checks
├── pyproject.toml            # deps, ruff, mypy, pytest, coverage, import-linter config
├── uv.lock
├── Dockerfile                # multi-stage, non-root
├── .env.example
├── config/
│   ├── settings/{base,dev,prod,test}.py
│   ├── urls.py               # mounts api at /api/v1
│   └── asgi.py
├── galeway/
│   ├── api/
│   │   ├── router.py         # NinjaAPI(version="1", urls_namespace="v1", docs only in dev)
│   │   ├── endpoints/{health,places,plans}.py
│   │   ├── schemas.py        # request/response Pydantic models (the public contract)
│   │   ├── params.py         # trip input parsing + normalization (shared by all /plans*)
│   │   ├── errors.py         # ApiError hierarchy → RFC 9457 problem+json
│   │   ├── throttles.py      # Redis sliding window, fail-open
│   │   └── caching.py        # Cache-Control, ETag, 304 helpers
│   ├── planning/
│   │   ├── domain/           # PURE. No Django, no I/O, no clock.
│   │   │   ├── types.py      # Level (IntEnum), Conditions, Checkpoint, RouteSummary, Ranking …
│   │   │   ├── units.py      # lb↔kg, m↔mi, s↔h
│   │   │   ├── risk.py       # classify_wind/rain/snow, apply_load_rules, checkpoint_level, reason()
│   │   │   ├── sampling.py   # checkpoint placement, mile covers
│   │   │   ├── eta.py        # distance↔time interpolation along a polyline
│   │   │   ├── ranking.py    # sort key, decided_by, status
│   │   │   ├── explain.py    # "why this route" sentences
│   │   │   ├── forecast.py   # pick hour for ETA (ceil for sums, nearest for instants)
│   │   │   └── heatmap_grid.py
│   │   ├── service.py        # PlanService: orchestration, progress callback, caching
│   │   └── progress.py       # stage events for SSE
│   ├── providers/
│   │   ├── http.py           # shared AsyncClient, timeouts, retries, circuit breaker, log redaction
│   │   ├── tomtom.py         # search(), calculate_routes() → domain types
│   │   ├── openmeteo.py      # hourly(points, start, end) → domain Forecast
│   │   ├── timezones.py      # timezonefinder, cached
│   │   └── cache.py          # Redis wrapper + in-process fallback + single-flight
│   └── core/
│       ├── logging.py        # structlog JSON, redaction processor
│       ├── middleware.py     # request id, Server-Timing, X-Robots-Tag
│       └── clock.py          # now() injectable
└── tests/
    ├── unit/                 # domain (the bulk of tests)
    ├── providers/            # respx against recorded fixtures
    ├── api/                  # Ninja TestClient: validation, errors, headers, throttles, SSE
    └── fixtures/             # scrubbed provider responses (dallas_denver_routes.json, …)
```

## 2. Request lifecycle (plan)

1. `params.py` parses and normalizes inputs (raises `ValidationError` with per-field messages matching the UI).
2. `PlanService.plan(inputs, progress)`:
   1. Cache `v1:plan:{key}` → return on hit.
   2. Single-flight guard.
   3. `tomtom.calculate_routes()` (fill to 3 + dedupe) → `progress("routes_ready")`.
   4. `domain.sampling` + `domain.eta` → checkpoints with ETAs.
   5. Snap to weather cells, `MGET`, fetch the missing ones concurrently from Open-Meteo, `progress("weather_progress")`, then `SET`.
   6. `domain.forecast` picks the hour; `domain.risk` classifies; `domain.sampling` covers → summaries.
   7. `domain.ranking` + `domain.explain` → recommendation.
   8. Store the plan and return it.
3. The endpoint renders JSON (with ETag/Cache-Control) or SSE.

The heatmap and checkpoints endpoints reuse steps 1–2 (cached), then do their own shaping.

> **Built so far (Phase 0):** `api/router.py`, `api/schemas.py`, `api/endpoints/health.py`, `core/{apps,logging,middleware}.py`, the settings split and an empty `planning/domain/`. `httpx`, `redis`, `respx`, `hypothesis` and `time-machine` are added in the phase that first uses them, and `core/clock.py` and `Server-Timing` arrive with the plan endpoints (Phase 2).

## 3. Settings (environment)

| Var | Example | Notes |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.prod` | |
| `SECRET_KEY` | random 50 chars | required in prod |
| `ALLOWED_HOSTS` | `galeway-api.onrender.com` | comma list |
| `CORS_ALLOWED_ORIGINS` | `https://galeway.pages.dev` | comma list |
| `TOMTOM_API_KEY` | (secret) | never logged |
| `REDIS_URL` | `rediss://default:…@….upstash.io:6379` | optional in dev (falls back to memory) |
| `TRUSTED_PROXY_HOPS` | `1` | number of trusted proxies in front of the app; the client IP is read from `X-Forwarded-For` counting from the right ([API §6](../03-architecture/API.md#6-rate-limits)) |
| `LOG_LEVEL` | `INFO` | |
| `GIT_SHA` | set by CI/host | shown in `/health` |

Settings use `django-environ`. `prod.py` fails fast at startup if a required var is missing (today `SECRET_KEY`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`; `TOMTOM_API_KEY` and `REDIS_URL` join in Phase 2). Only `dev.py` reads `backend/.env`; `test.py` is hermetic. Prod adds `127.0.0.1` and `localhost` to `ALLOWED_HOSTS` for the container `HEALTHCHECK`, and exempts `/api/v1/health` from the HTTPS redirect because health checks arrive over plain HTTP. Verify both against Render's health check on first deploy.

## 4. Django trimmed to what we use

`INSTALLED_APPS`: `corsheaders`, `ninja`, `galeway.*` only. No admin, auth, sessions, messages or contenttypes. `DATABASES = {}`. Middleware: security, CORS, request id, server timing, common. The ASGI app runs under `uvicorn` (`--proxy-headers`, `--forwarded-allow-ips` set for the host).

## 5. Provider adapter rules

- Adapters return **domain types**, never raw JSON.
- Units are converted at the edge: TomTom meters/seconds → miles/seconds; load lb → **kg** for the request.
- Every adapter function has a recorded-fixture test, plus failure tests (timeout, 5xx, 429, malformed JSON).
- Fixtures are recorded once with a script (`scripts/record_fixtures.py`, manual, needs a key), then **scrubbed** of keys. CI never touches real providers.

## 6. Logging and observability

- A request-id middleware accepts a client `X-Request-ID` only if it matches `[A-Za-z0-9._-]{8,64}`, otherwise it generates one, and sets `X-Robots-Tag: noindex` on every response. The redaction processor scrubs `key=`/`token=` query values and `Authorization` for our logs and for stdlib loggers (httpx, Django), so URLs logged by libraries are safe.
- `structlog` JSON lines: `request_id`, `path`, `status`, `duration_ms`, `cache` (hit/miss), `provider_calls`, `plan_key`. No PII exists to log; place labels are fine.
- `Server-Timing` header on plan endpoints (`routing;dur=…, weather;dur=…, domain;dur=…, cache;desc=hit`).
- Errors log the full trace with the request id; the response shows only the id.
