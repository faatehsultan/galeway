# Architecture

## 1. System overview

```mermaid
flowchart LR
  subgraph Browser
    UI[React SPA<br/>TanStack Router + Query]
    MAP[MapLibre GL<br/>routes · checkpoints · heatmap]
    LS[(localStorage<br/>saved trips · theme)]
    UI --- MAP
    UI --- LS
  end
  subgraph Cloudflare Pages
    STATIC[Static assets<br/>CSP + cache headers]
  end
  subgraph Render
    API[Django 6 + Ninja<br/>ASGI / uvicorn]
    DOM[planning.domain<br/>pure functions]
    API --> DOM
  end
  REDIS[(Upstash Redis<br/>cache · rate limits)]
  TT[TomTom<br/>Search + Routing]
  OM[Open-Meteo<br/>hourly forecast]
  TILES[OpenFreeMap<br/>vector tiles]

  STATIC --> UI
  UI -- "GET /api/v1/*" --> API
  MAP --> TILES
  API <--> REDIS
  API --> TT
  API --> OM
```

**Key properties**

- **Stateless backend, no database.** Every request carries the full trip in its query string. Results are recomputable and cacheable by key ([ADR-0005](../09-decisions/0005-url-as-source-of-truth.md)).
- **Functional core, imperative shell.** `planning/domain` is pure and does the logic. `planning/service.py` does the I/O and calls the domain. Ninja routers do HTTP only.
- **One typed contract.** Ninja generates OpenAPI. `make api-types` generates `frontend/src/lib/api/schema.d.ts`, so the build fails if frontend and backend drift.
- **Keys stay server-side.** The browser talks only to our API and to the tile CDN.

## 2. Request flow: planning a trip

```mermaid
sequenceDiagram
  autonumber
  participant B as Browser
  participant A as API (Ninja)
  participant C as Redis
  participant T as TomTom
  participant W as Open-Meteo
  B->>A: GET /api/v1/plans?from&to&depart&load&every (Accept: text/event-stream)
  A->>C: GET plan:{key}
  alt cache hit
    C-->>A: plan JSON
  else miss
    A->>T: calculateRoute (truck, kg, alternatives, per-point time)
    T-->>A: routes
    A-->>B: event: stage routes_ready
    A->>A: sample checkpoints + ETAs (domain)
    A->>C: MGET wx cells
    A->>W: batched forecasts for missing cells (concurrent)
    W-->>A: hourly series
    A-->>B: event: stage weather_ready
    A->>A: classify · summarize · rank · explain (domain)
    A->>C: SET plan:{key} (TTL)
  end
  A-->>B: event: result {plan}
  B->>A: GET /api/v1/plans/heatmap?… (in parallel, after routes render)
```

The same `GET /api/v1/plans` returns plain JSON when `Accept: application/json`. That form is cacheable by CDN and browser and is used for direct links and refetches. SSE progress is a progressive enhancement; if it fails, the client falls back to JSON with an indeterminate loader.

## 3. Modules

| Module | Responsibility | Must not |
|---|---|---|
| `galeway.api` | Routers, request/response schemas, validation, problem+json errors, throttles, cache headers | contain business logic |
| `galeway.planning.domain` | Units, risk, sampling, ETA, ranking, explanation, heatmap grid math | import Django, httpx, Redis, or read the clock |
| `galeway.planning.service` | Orchestrate: geocode → route → sample → weather → classify → rank; cache; progress events | know about HTTP request objects |
| `galeway.providers` | TomTom and Open-Meteo adapters, shared HTTP client (timeouts, retries, circuit breaker), cache helpers | leak provider JSON shapes outside |
| `galeway.core` | Settings helpers, structured logging, request id, health check | |

The clock is injected (`now: datetime` parameter) so domain tests are deterministic.

## 4. Failure modes

| Failure | Behavior | User sees |
|---|---|---|
| TomTom down / 5xx | 2 retries with jittered backoff, then 502 `PROVIDER_UNAVAILABLE` | Blocking error card with Retry and a reference id |
| TomTom quota exhausted (403/429) | No retry; 503 `ROUTING_QUOTA` | "Routing is busy right now, try again shortly." |
| Open-Meteo partial failure | Affected checkpoints `NO_DATA`; plan still returned with `PARTIAL_FORECAST` warning | Amber banner; unknown miles counted, never safe |
| Open-Meteo fully down | 502 `WEATHER_UNAVAILABLE`, routes still returned in the error payload | "Your routes are ready, but we couldn't load the forecast." |
| Redis down | Fail open: in-process TTL cache + in-process rate limiter; log error | Nothing (slightly slower) |
| Rate limit hit | 429 with `Retry-After` | Toast with countdown and Retry |
| Cold start (free tier) | Client pre-warms `/api/v1/health` on load | After 3 s: "Starting up the server…" banner |
| Invalid share link | Client-side zod parse fails | 404 page: "This road doesn't go anywhere" |
| Unexpected exception | 500 problem+json with request id; full trace in logs only | Error card with reference id; error boundary for render errors |

## 5. Cross-cutting docs

[API](API.md) · [URL state](URL_STATE.md) · [Caching](CACHING.md) · [Security](SECURITY.md) · [Performance](PERFORMANCE.md) · [Frontend](../04-frontend/FRONTEND.md) · [Backend](../05-backend/BACKEND.md)
