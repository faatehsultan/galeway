# API

Base path: `/api/v1`. JSON over HTTPS. All endpoints are **`GET`, idempotent and cacheable**, with no cookies and no sessions. The OpenAPI spec is served at `/api/v1/openapi.json`, and interactive docs at `/api/v1/docs` (dev only).

## 1. Conventions

| Topic | Rule |
|---|---|
| Naming | `snake_case` fields; units in names (`distance_mi`, `duration_s`, `wind_mph`, `rain_in_hr`) |
| Times | ISO 8601 UTC with `Z` (`2026-11-26T12:00:00Z`) |
| Coordinates | `lat,lon` decimal degrees, max 5 decimals |
| IDs | Routes: `a`, `b`, `c`. Plan key: `pln_` + 16 hex chars, a hash of the normalized inputs |
| Versioning | URL prefix `/v1`; additive changes only within v1 |
| Request id | Every response has `X-Request-ID` (echoed if the client sent a valid one) |
| Compression | gzip/brotli for responses over 1 KB |
| Robots | `X-Robots-Tag: noindex` on every API response |

## 2. Trip inputs (shared query params)

Used by every `/plans*` endpoint. Names match the app URL ([URL_STATE](URL_STATE.md)).

| Param | Type | Example | Rule |
|---|---|---|---|
| `from` | `label@lat,lon` | `Dallas, TX@32.7767,-96.797` | continental US bbox |
| `to` | `label@lat,lon` | `Denver, CO@39.7392,-104.9903` | > 1 mi from `from` |
| `depart` | ISO UTC | `2026-11-26T12:00Z` | now − 5 min … now + 7 days |
| `load` | int lb | `42000` | 1,000 – 80,000 |
| `every` | int mi | `25` | 10, 25 or 50 |

Normalization (for cache keys and `plan_key`): coordinates rounded to 4 dp, `depart` floored to the minute, labels excluded.

## 3. Errors: RFC 9457 `application/problem+json`

```json
{
  "type": "https://galeway.app/problems/validation-error",
  "title": "Some trip details need fixing",
  "status": 422,
  "code": "VALIDATION_ERROR",
  "detail": "2 fields are invalid.",
  "errors": [
    { "field": "load", "code": "out_of_range", "message": "Enter a weight between 1,000 and 80,000 lb" }
  ],
  "request_id": "req_7f3a91c2"
}
```

| Status | `code` | When |
|---|---|---|
| 400 | `BAD_REQUEST` | Malformed params |
| 404 | `NOT_FOUND` | Unknown route id or path |
| 422 | `VALIDATION_ERROR` | Params fail rules (per-field `errors[]`, same messages as the UI) |
| 422 | `NO_ROUTE` | Provider found no truck route between the points |
| 422 | `DEPARTURE_PASSED` | `depart` is more than 5 minutes in the past (old link or saved trip). The UI offers "Replan for now" |
| 429 | `RATE_LIMITED` | Includes `Retry-After` |
| 502 | `PROVIDER_UNAVAILABLE` / `WEATHER_UNAVAILABLE` | Upstream failure after retries |
| 503 | `ROUTING_QUOTA` | Provider quota exhausted |
| 500 | `INTERNAL_ERROR` | Bug. No stack traces in the body. |

## 4. Endpoints

### 4.1 `GET /api/v1/health`

`200 {"status":"ok","version":"<git sha>"}`. Doesn't touch providers. Used for keep-warm and pre-warm. Not rate limited.

### 4.2 `GET /api/v1/places?q=dall&limit=5`

Autocomplete. `q` is 2–100 chars, `limit` 1–8 (default 5). US only.

```json
{ "items": [ { "id": "tt:…", "label": "Dallas, TX", "detail": "Dallas County, Texas", "lat": 32.7767, "lon": -96.797 } ] }
```

The client debounces at 200 ms and cancels stale requests.

### 4.3 `GET /api/v1/plans?{trip inputs}`

The core endpoint. With `Accept: text/event-stream` it streams progress (§5). Otherwise it returns JSON:

```json
{
  "plan_key": "pln_3f9a1c0be47d2a11",
  "inputs": { "from": {"label":"Dallas, TX","lat":32.7767,"lon":-96.797}, "to": {…}, "depart": "2026-11-26T12:00:00Z", "load_lb": 42000, "every_mi": 25 },
  "generated_at": "2026-11-25T15:40:02Z",
  "forecast_issued_at": "2026-11-25T15:00:00Z",
  "recommendation": {
    "status": "ok",
    "route_id": "a",
    "decided_by": "severe_miles",
    "explanation": ["Route C is excluded: …", "Fewest severe miles: A has 0, B has 50.", "Settled at rule 1. …"]
  },
  "routes": [
    {
      "id": "a", "name": "US-287 via Amarillo", "rank": 1, "recommended": true,
      "distance_mi": 794.2, "duration_s": 45600,
      "depart_at": "2026-11-26T12:00:00Z", "arrive_at": "2026-11-27T00:40:00Z",
      "geometry": "<encoded polyline, precision 5>",
      "summary": { "low_mi": 556.1, "moderate_mi": 175.3, "high_mi": 25.0, "severe_mi": 0, "no_travel_mi": 0, "no_data_mi": 0,
                   "avg_risk": 0.38, "max_level": "HIGH",
                   "worst_stretch": { "from_mi": 437.5, "to_mi": 462.5, "level": "HIGH", "near": "Dalhart, TX", "eta": "2026-11-26T20:10:00Z", "driver": "rain" } },
      "checkpoints": [
        { "i": 18, "mile": 450.0, "lat": 36.06, "lon": -102.52, "eta": "2026-11-26T20:10:00Z", "tz": "America/Chicago",
          "level": "HIGH", "drivers": ["rain"], "wind_mph": 22.1, "gust_mph": 31.0, "rain_in_hr": 0.30, "snow_in_hr": 0.0,
          "place": "Dalhart, TX", "reason": "Rain 0.30 in/hr (0.25–0.50) → High" }
      ]
    }
  ],
  "warnings": [ { "code": "PARTIAL_FORECAST", "route_id": "b", "message": "2 checkpoints have no forecast." } ]
}
```

All checkpoints are included because the map needs them. For a 1,000 mi trip at 10 mi that is about 300 points (~40 KB gzipped).

### 4.4 Heatmap: `GET /api/v1/plans/heatmap`

`GET /api/v1/plans/heatmap?{trip inputs}&hours=48`. Corridor grid for the slider, fetched after the plan renders. Columnar and quantized to stay small:

```json
{
  "plan_key": "pln_…",
  "start": "2026-11-26T12:00:00Z",
  "hours": 49,
  "available_hours": 49,
  "points": { "lat": [35.25, 35.5, …], "lon": [-101.75, …] },
  "scale": { "wind": 1, "rain": 0.01, "snow": 0.1 },
  "wind": [22, 23, …],
  "rain": [0, 12, …],
  "snow": [0, 0, …],
  "risk": [0, 1, …]
}
```

Arrays are `points × hours`, point-major (`index = p * hours + h`). Integers × `scale` give real units. `risk` is the 0–4 ordinal, with `255` for no data.

### 4.5 `GET /api/v1/plans/routes/{route_id}/checkpoints?{trip inputs}&page=1&page_size=10&min_level=MODERATE`

Paginated table for the route detail screen. Uses the cached plan, or recomputes it.

| Param | Rule |
|---|---|
| `page` | ≥ 1 (default 1) |
| `page_size` | 1–100 (default 10) |
| `min_level` | optional: `MODERATE`, `HIGH`, `SEVERE`, `NO_TRAVEL` |

```json
{ "items": [ { …checkpoint… } ], "page": 1, "page_size": 10, "total": 32, "total_pages": 4 }
```

Links to other pages are also sent in a `Link` header (`rel="next"`, `rel="prev"`).

## 5. Progress stream (SSE)

`GET /api/v1/plans?…` with `Accept: text/event-stream`:

```text
event: stage
data: {"stage":"routes_ready","routes":3,"distance_mi":[794,935,812]}

event: stage
data: {"stage":"weather_progress","done":62,"total":96}

event: stage
data: {"stage":"weather_ready"}

event: result
data: { …same JSON as §4.3… }
```

Errors arrive as `event: error` with a problem+json body. The server sends a comment line (`: ping`) every 10 s so proxies don't close an idle stream, and sets `Cache-Control: no-store` and `X-Accel-Buffering: no` so events aren't buffered. The whole plan has a **25 s deadline**: if weather is still missing then, the plan is returned with those checkpoints as `NO_DATA` and a `PARTIAL_FORECAST` warning, rather than failing. On a cache hit the server sends `result` straight away. The client never invents percentages: it shows only the stages it has received.

## 6. Rate limits

Per client IP, sliding window, in Redis. The client IP is the **right-most untrusted** entry of `X-Forwarded-For`, counting back from the host's known number of proxy hops (`TRUSTED_PROXY_HOPS`, 1 on Render). Never the left-most entry, which the client can forge. Requests without the header in production are treated as one shared bucket.

| Endpoint | Limit |
|---|---|
| `/places` | 60 / min |
| `/plans` (+ stream) | 20 / min and 300 / day |
| `/plans/heatmap` | 20 / min |
| `/plans/routes/*/checkpoints` | 120 / min |

Responses carry `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`. A 429 adds `Retry-After`.

## 7. Caching headers

| Endpoint | `Cache-Control` | Validator |
|---|---|---|
| `/places` | `public, max-age=86400` | ETag |
| `/plans`, `/plans/heatmap`, `/checkpoints` | `public, max-age=300, stale-while-revalidate=600` | ETag (hash of body); `If-None-Match` → 304 |
| `/health` | `no-store` | |

**`Vary: Accept, Origin`** on every cacheable response. `/plans` returns JSON or an event stream from the same URL, and CORS headers depend on `Origin`, so caches must key on both. Event-stream responses are always `Cache-Control: no-store`.
| Errors | `no-store` | |

Full strategy: [CACHING](CACHING.md).
