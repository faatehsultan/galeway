# Caching

Four layers, each with one job. They keep the app fast, protect the free-tier quotas (TomTom requests, Upstash commands) and make shared links instant.

```text
Browser memory (TanStack Query) → HTTP cache / CDN (Cache-Control + ETag) → Redis (Upstash) → request merging → providers
```

## 1. Browser: TanStack Query

| Query | Key | `staleTime` | `gcTime` |
|---|---|---|---|
| places | `["places", q]` | 24 h | 1 h |
| plan | `["plan", normalizedTrip]` | 5 min | 30 min |
| heatmap | `["heatmap", normalizedTrip]` | 5 min | 30 min |
| checkpoints | `["checkpoints", normalizedTrip, routeId, page, level]` | 5 min | 30 min |

- `placeholderData: keepPreviousData` on checkpoints, so changing page doesn't flash empty.
- On hover/focus of a saved trip or example, **prefetch** its plan.
- Retries: 2 for network errors and 5xx, **0 for 4xx**. Retry is honest: the user sees a retry state, not a silent spinner.
- View params (`route`, `hour`, `layer`, `map`, …) are **not** in any key ([URL_STATE §5](URL_STATE.md#5-data-fetching-from-the-url)).

## 2. HTTP: Cache-Control and ETag

Set by the API on success responses only (errors are `no-store`). See [API §7](API.md#7-caching-headers). `stale-while-revalidate` lets repeat visits paint instantly while a fresh copy loads. ETag is a hash of the response body, and `If-None-Match` returns `304` with no body.

Static frontend (Cloudflare Pages `_headers`):

| Path | Header |
|---|---|
| `/assets/*` (hashed) | `Cache-Control: public, max-age=31536000, immutable` |
| `/index.html`, `/` | `Cache-Control: no-cache` (always revalidate) |
| `/og-image.png`, icons | `public, max-age=86400` |

## 3. Server: Redis

All keys are prefixed with a schema version (`v1:`), so a deploy that changes shapes can bump the version instead of flushing.

| Data | Key | TTL | Why |
|---|---|---|---|
| Place search | `v1:places:{q_normalized}` | 30 days | Places don't move |
| Empty place search | same | 1 h | Negative cache, limits abuse |
| Routes | `v1:routes:{from}:{to}:{depart_15min}:{load_kg}` | 15 min | Traffic-aware; depart bucketed to 15 min |
| Weather cell | `v1:wx:{lat_0.05}:{lon_0.05}:{start_hour}` | 30 min | Forecast models update about hourly; shared across trips and users |
| Plan result | `v1:plan:{plan_key}` | 10 min | Instant shared links, cheap checkpoints pagination |
| Heatmap | `v1:heat:{plan_key}` | 10 min | |
| Timezone of cell | `v1:tz:{lat_0.1}:{lon_0.1}` | 30 days | Static |

**Budget note (Upstash free tier: 500K commands/month):** weather cells are read with one `MGET` per batch and written with one pipelined `SET … EX` per batch, never key by key. A typical uncached plan costs about 10–15 commands.

**Redis unavailable:** fall back to an in-process TTL cache (bounded LRU, 2,000 entries) and log once per minute. The app keeps working.

## 4. Request merging (single-flight)

If 5 identical requests arrive together (a link shared in a group chat), only the first does the work:

- In-process: a dict of `asyncio.Future` by cache key. Later callers await the same future.
- Across instances: `SET v1:lock:{key} NX EX 20`. Callers that lose the race poll the result key for up to 15 s, then compute themselves.

## 5. What is never cached

- Error responses (any status ≥ 400).
- Anything with the provider key in it (the key never enters cache keys; we hash inputs only).
- Rate-limit counters are kept in Redis but are not a cache.
