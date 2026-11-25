# Performance

UI smoothness is a top priority. These budgets are checked in CI where possible.

## 1. Budgets

| Metric | Budget | How it's checked |
|---|---|---|
| LCP (desktop, first visit) | < 2.0 s | Lighthouse CI on the preview build |
| CLS | < 0.05 | Lighthouse CI |
| INP | < 200 ms | Lighthouse CI + manual check of slider and form |
| Initial JS (gzip), excluding map chunk | ≤ 180 KB | `size-limit` in CI |
| Map chunk (MapLibre + map feature) | lazy loaded, ≤ 300 KB gzip | `size-limit` |
| Slider / play | 60 fps, no React render per tick | Playwright trace + manual Performance panel check |
| `/plans` warm (cached) | p50 < 150 ms server time | `Server-Timing` header |
| `/plans` cold (uncached) | p50 < 2.5 s | `Server-Timing` header, logs |
| Heatmap payload | < 150 KB compressed | API test asserts size on fixture |

## 2. Backend

- **Concurrency**: TomTom calls and Open-Meteo batches run with `asyncio.gather` (bounded with a semaphore). There are no sequential provider loops.
- **Fewer calls**: 0.05° grid snapping dedupes checkpoints across the 3 routes and the heatmap ([ROUTING_AND_WEATHER §4.2](../02-domain/ROUTING_AND_WEATHER.md#42-snap-to-a-grid-sharing-and-caching)).
- **Cache first**: see [CACHING](CACHING.md).
- **Payloads**: polyline-encoded geometry; route geometry simplified to about 15 m tolerance for display; heatmap columnar and quantized; gzip/brotli.
- **Timing visibility**: a `Server-Timing` header reports `routing`, `weather`, `domain` and `cache` timings on every plan response.
- **Process**: uvicorn, one worker on the free instance. Async views mean the single worker isn't blocked by provider I/O.

## 3. Frontend

- **Code splitting**: map feature, route detail, methodology and saved-trips drawer are lazy routes or components. The form and shell paint first.
- **Pre-warm**: on app load, fire `GET /api/v1/health` (wakes a sleeping free-tier server) and preconnect to the API and tile hosts.
- **Prefetch**: hovering a saved trip or example prefetches its plan.
- **Progressive render**: routes and checkpoints render as soon as the plan arrives; the heatmap loads after it in the background.
- **Map**:
  - one GeoJSON source per concern (routes, checkpoints, heatmap, truck marker); update with `setData` only when data changes
  - slider changes only `setPaintProperty` / `setFilter` ([FRONTEND §5](../04-frontend/FRONTEND.md#5-map-heatmap-and-the-forecast-slider))
  - hover state via `feature-state`, not React state
  - `fitBounds` once per new plan
- **React**: map callbacks and slider values live in refs. Components that re-render often are memoized. Route lists are small, so there's no virtualization needed, except the checkpoint table, which is paginated.
- **No layout shift**: skeletons match final sizes; fonts preloaded with `font-display: swap` and matched fallback metrics; images have fixed dimensions.
- **Motion**: transforms and opacity only; `prefers-reduced-motion` turns off non-essential motion and slows the play speed.
