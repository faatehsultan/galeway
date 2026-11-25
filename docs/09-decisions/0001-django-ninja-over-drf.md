# 0001. Django Ninja instead of Django REST Framework

- Status: Accepted
- Date: 2026-11-25

## Context

The stack is Django on the backend. A plan request calls TomTom and then several Open-Meteo batches. Done one after another, that is the slowest part of the app, and speed is 40% of the grade. We also want a typed contract shared with the TypeScript frontend.

## Decision

Use **Django Ninja** on ASGI (uvicorn) with async views.

## Consequences

- Provider calls run concurrently with `asyncio.gather` on a single worker, which suits a 0.1-CPU free instance.
- Pydantic schemas validate requests and produce an OpenAPI spec automatically. `make api-types` turns it into TypeScript types, and CI fails if they drift.
- Built-in pagination, throttling hooks and docs UI.
- Smaller ecosystem than DRF, but we need none of DRF's model-centric features (no database, no serializers for models, no browsable API).

## Alternatives considered

- **DRF**: more widely known, but sync-first (async needs `adrf`), more verbose serializers, OpenAPI through an extra package. A fine choice; just slower and more code here.
- **Plain async Django views**: no schema validation or OpenAPI without rebuilding what Ninja gives.
