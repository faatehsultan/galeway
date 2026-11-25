# Frontend

React 19 + TypeScript (strict) + Vite, Tailwind CSS v4 with shadcn/ui (Radix primitives), TanStack Router + Query, MapLibre GL JS, zod, react-hook-form, Sonner (toasts), lucide-react (icons), Fontsource (self-hosted Inter, Space Grotesk, JetBrains Mono). Pin exact latest stable versions at scaffold time ([AGENTS §6](../../AGENTS.md#6-versions-policy)).

## 1. Structure

```text
frontend/src/
├── main.tsx                     # mount, providers
│   (build/pagesHeaders.ts, outside src/, writes dist/_headers with the CSP hash)
├── app/
│   ├── router.tsx               # TanStack Router instance, custom search (de)serializer
│   ├── providers.tsx            # QueryClient, ThemeProvider, Toaster, TooltipProvider
│   ├── theme.ts                 # light/dark/system, persisted, no flash (inline script in index.html)
│   ├── seo.ts                   # per-route head (title, description, canonical, robots)
│   └── ErrorBoundary.tsx
├── routes/                      # file-based routes: __root, index, trip, trip.routes.$routeId, methodology, $404
├── features/
│   ├── plan-form/               # PlanForm, PlaceCombobox, DepartureField, LoadField, IntervalToggle, schema.ts
│   ├── results/                 # RouteList, RouteCard, RecommendationBadge, Warnings
│   ├── map/                     # MapView, useMap, layers/{routes,checkpoints,heatmap,truck}.ts, ForecastBar, LayerPanel, CheckpointPopup
│   ├── route-detail/            # StatsGrid, WhyThisRoute, RiskStrip, CheckpointTable, Pagination
│   ├── saved-trips/             # SavedTripsDrawer, SavedTripItem, store.ts, schema.ts
│   ├── methodology/             # RiskRules (used by modal and page)
│   ├── share/                   # ShareButton
│   └── system/                  # ColdStartBanner, OfflineBanner, LoadingStages, NotFound
├── components/ui/               # shadcn primitives (button, input, dialog, sheet, tooltip, …)
├── lib/
│   ├── api/                     # schema.d.ts (GENERATED), client.ts, queries.ts, sse.ts, problem.ts
│   ├── url-state/               # schemas.ts, serialize.ts, normalize.ts
│   ├── storage.ts               # safe localStorage wrapper (feature detect, quota, JSON+zod)
│   ├── format.ts                # durations, miles, local times with tz, numbers
│   └── risk.ts                  # level → color/label tokens (display only; no scoring in the browser)
└── styles/                      # tokens.css (CSS variables, light + dark), globals.css
```

Rules: feature folders own their components, hooks and tests. `lib/` has no React. Components stay under ~150 lines; split them when they grow. **No risk scoring in the browser.** The backend is the single source of truth; the frontend only displays it.

## 2. State

| Kind | Where |
|---|---|
| Trip and view state | URL search params ([URL_STATE](../03-architecture/URL_STATE.md)) |
| Server data | TanStack Query ([CACHING §1](../03-architecture/CACHING.md#1-browser-tanstack-query)) |
| Form draft | react-hook-form + zod resolver (`features/plan-form/schema.ts`, same limits as the API) |
| Saved trips, theme | `localStorage` via `lib/storage.ts` |
| High-frequency map/slider values | refs inside `features/map`, synced to the URL with debounce |

No global state library is needed.

## 3. Data access

- `lib/api/client.ts` is a typed fetch wrapper built on the generated OpenAPI types (`openapi-fetch` style): base URL from `VITE_API_BASE_URL`, `AbortSignal` support, request id header, timeout, and parsing of problem+json into a typed `ApiProblem`.
- `lib/api/sse.ts` opens the plan stream with `fetch` + `ReadableStream`, so normal headers and abort work. Stages feed `LoadingStages`, and the final `result` is written into the Query cache under the plan key. If streaming fails, it falls back to the JSON request.
- Map `ApiProblem.errors[]` back to form fields with `setError`.

## 4. Plan form

- `PlaceCombobox`: Radix Popover + listbox with the ARIA combobox pattern. Debounce 200 ms, min 2 chars, abort stale requests, keyboard arrows/enter/escape. Shows "No places found" and an error row.
- Departure: native `datetime-local` styled to match, shown in the **origin's** time zone and converted to UTC for the URL.
- Load: numeric input with thousands separators on blur and `inputMode="numeric"`.
- Validation: on blur and on submit; messages from [PRODUCT_SPEC §5](../01-product/PRODUCT_SPEC.md#5-input-rules-shared-by-client-and-server). The submit button shows "Planning your trip…" and stays disabled while a request is in flight.

## 5. Map, heatmap and the forecast slider

- **Own thin wrapper** (`useMap`) around `maplibre-gl`, not a React map library. It gives full control and no per-frame React work ([ADR-0008](../09-decisions/0008-tanstack-router-and-maplibre-wrapper.md)).
- **Base style**: OpenFreeMap. Light uses its light style. Dark uses the same style with a recolor pass applied at load (background, water, land, roads, labels to the dark tokens). Switching themes calls `setStyle` with `diff: true` and re-adds our layers.
- **Layers**, bottom to top: heatmap → alternate routes (dashed, `alt` token) → selected route casing + line (accent) → checkpoints (circle, risk color, 2 px panel-color stroke; larger when hovered or selected) → truck marker → popup.
- **Heatmap**:
  - One GeoJSON point source built once from the columnar heatmap response.
  - Each feature carries 49 numeric props per layer (`r0…r48`, `w0…w48`, …), normalized to 0–1. Risk: ordinal / 4. Wind/rain/snow: value / that condition's No-travel threshold, clamped.
  - Color ramp uses the five risk colors, so every layer reads the same way.
  - **Slider tick** = `map.setPaintProperty('heatmap', 'heatmap-weight', ['get', 'r8'])`, inside `requestAnimationFrame` and coalesced. No `setData`, no React render, no network.
  - Layer switch = same call with a different prefix.
- **Play**: advances 1 hour every 400 ms (800 ms with reduced motion) and loops at the end. Pause on user drag, on tab hidden, or when reaching unavailable hours.
- **Truck marker** at the slider hour along the selected route (position from the checkpoints' ETAs, interpolated client-side on the route geometry).
- **Hours beyond the forecast** (`available_hours`) are greyed on the track and can't be selected.
- **Interaction**: click a route → `route` param; click a checkpoint → `cp` param + popup; Escape closes the popup. Keyboard users get the same via the route list and the route detail table.
- **Accessibility**: the map canvas has an `aria-label` summary; everything on the map is also available as text in the side panel and the detail table.

## 6. Loading, empty, error

| Situation | UI |
|---|---|
| First visit | `01-first-visit.png`: form, examples, saved trips, explainer card |
| Planning | `02-planning-loading.png`: skeleton cards matching final size, progress card with **real** stages from SSE, Cancel (aborts the request) |
| Field errors | Inline under fields, `aria-invalid`, focus the first invalid field |
| Blocking error | Inline card in the results area: what happened, what still works, Retry, reference id |
| Partial forecast / no safe route | Banners as in `06-states-errors-toasts.png` |
| Departure passed | Trip summary from the URL + "Replan for now" ([URL_STATE §5](../03-architecture/URL_STATE.md#5-data-fetching-from-the-url)) |
| Offline | Toast once + small persistent pill; retry automatically on `online` |
| Cold start | After 3 s without the first byte, the "Starting up the server…" banner. The first request after app load allows up to 90 s (a free instance can take about a minute to wake); later requests time out at 30 s. |
| Render crash | `ErrorBoundary` with a calm message, a "Reload" button and the reference id |

## 7. Saved trips

Decision: [ADR-0007](../09-decisions/0007-saved-trips-in-localstorage.md). Mockup: `05-saved-trips.png`.

**Storage key** `galeway.savedTrips.v1`, value:

```ts
type SavedTripsV1 = {
  version: 1;
  trips: Array<{
    id: string;            // crypto.randomUUID()
    name: string;          // default "Dallas → Denver", max 80 chars
    search: string;        // canonical trip params only (from,to,depart,load,every)
    savedAt: string;       // ISO
    snapshot: {            // shown in the list without refetching
      fromLabel: string; toLabel: string; departUtc: string; loadLb: number;
      recommendedRouteId: 'a' | 'b' | 'c' | null; recommendedName: string | null;
      worstLevel: 'LOW' | 'MODERATE' | 'HIGH' | 'SEVERE' | 'NO_TRAVEL' | null;
      severeMi: number; highMi: number;
    };
  }>;
};
```

**Behavior**

- Save from the header ("Save trip" → "Trip saved"). Saving the same trip params again updates the existing item, so there are no duplicates.
- Max 50 trips, newest first. At the limit, the toast offers to remove the oldest.
- Rename inline (Enter saves, Escape cancels). Delete shows an **Undo** toast (5 s).
- Search filters by name and place labels.
- Opening a trip navigates to `/trip?{search}` and always loads a fresh forecast. A departure in the past gets the chip "Replan", and opening it offers "Replan for now."
- **Cross-tab sync** through the `storage` event.
- **Robustness**: every read goes through zod. Invalid items are dropped and reported once ("1 saved trip couldn't be read and was removed"). A future `version` is migrated or ignored safely. If `localStorage` is unavailable (private mode, quota), saving shows a toast and the session keeps an in-memory list.

## 8. Toasts (Sonner)

Bottom-right on desktop, bottom-center on mobile, max 3 visible, auto-hide after 5 s, pause on hover/focus, announced with `role="status"` (errors `role="alert"`).

| Use toasts for | Don't use toasts for |
|---|---|
| Link copied, trip saved/deleted (with Undo), rate limited (with Retry), offline/online, route fell back | Field validation (inline), blocking errors (inline card), anything the user must read to continue |

## 9. Theme

Light by default. Choices: Light / Dark / System. An inline script in `index.html` sets `data-theme` before first paint (no flash). `meta[name=theme-color]` is updated per theme. The map style switches with the theme.

## 10. Accessibility checklist

Keyboard path through the whole app; visible focus rings (accent, 2 px offset); skip link to results; `aria-live="polite"` for loading stages and result counts; color is never the only signal (risk chips have text; checkpoint popups name the level); 4.5:1 text contrast in both themes; 44 px touch targets; `prefers-reduced-motion` respected. axe runs in Playwright with zero serious/critical violations.
