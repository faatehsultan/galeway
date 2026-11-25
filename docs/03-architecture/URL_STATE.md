# URL state and share links

> **Rule:** if the user can see it, the URL can recreate it. "Share trip" copies `location.href`, nothing else. The decision is recorded in [ADR-0005](../09-decisions/0005-url-as-source-of-truth.md).

## 1. Paths

| Path | Screen |
|---|---|
| `/` | First visit (form; params may pre-fill it) |
| `/trip` | Results + map (needs trip params) |
| `/trip/routes/:routeId` | Route detail (`a`, `b` or `c`) |
| `/methodology` | "How we score risk" as a standalone, indexable page (also opened as a modal with `panel=methodology`) |
| `*` | 404 |

## 2. Query params

Params with default values are **left out** to keep links short. They are always written in the order shown below, so the same state always gives the same URL (good for caching and comparing).

| Param | Example | Default | Notes |
|---|---|---|---|
| `from` | `Dallas,+TX@32.7767,-96.797` | (required) | label `@` lat,lon (4–5 dp). Coordinates mean opening a link never re-geocodes. |
| `to` | `Denver,+CO@39.7392,-104.9903` | (required) | |
| `depart` | `2026-11-26T12:00Z` | (required) | UTC, minute precision |
| `load` | `42000` | (required) | lb |
| `every` | `10` | `25` | |
| `route` | `b` | recommended | selected route on the map |
| `hour` | `8` | `0` | forecast slider, hours after departure |
| `layer` | `wind` | `risk` | `risk` \| `wind` \| `rain` \| `snow` |
| `cp` | `18` | none | selected checkpoint index (opens its popup) |
| `map` | `6.2/35.21/-101.83` | fit to routes | `zoom/lat/lon` |
| `panel` | `saved` | none | `saved` \| `methodology` |
| `level` | `moderate` | `all` | route detail table filter |
| `page` | `2` | `1` | route detail table page |

Example:

```text
https://galeway.pages.dev/trip?from=Dallas,+TX@32.7767,-96.797&to=Denver,+CO@39.7392,-104.9903&depart=2026-11-26T12:00Z&load=42000&route=a&hour=8&cp=18
```

## 3. Encoding

- A custom `stringifySearch`/`parseSearch` for TanStack Router keeps `, @ / :` **unescaped**. They are legal in a query string (RFC 3986), and the link stays readable. Spaces become `+`. Everything else is percent-encoded.
- Parsing is a **zod schema** per route (`validateSearch`). Invalid required params show the 404 page ("the trip link is incomplete"). Invalid optional params are dropped silently and fall back to defaults.
- Round-trip property test (fast-check): `parse(stringify(state)) == state` for all valid states.

## 4. History behavior

| Action | History |
|---|---|
| Submit form, pick a saved trip, open route detail | `push` (Back returns to the previous trip/screen) |
| Select route, change layer, select checkpoint, open/close panel | `push` |
| Drag slider, play animation, pan/zoom map | `replace`, debounced 250 ms (no history spam) |
| Fix an invalid optional param | `replace` |

## 5. Data fetching from the URL

- TanStack Query keys are built from the **normalized trip params only** (`from`, `to`, `depart`, `load`, `every`). View params (`route`, `hour`, `layer`, `cp`, `map`, `panel`) never trigger a refetch.
- Opening a link always gets the **latest forecast** for that trip. The UI shows "Forecast issued 15:00 UTC" so nobody mistakes it for a snapshot.
- If `route` names a route that no longer exists (the provider returned different alternatives), fall back to the recommended route, `replace` the URL and show an info toast.
- If `depart` is in the past (an old link or saved trip), the client **doesn't call the API** (the API would reject it with `DEPARTURE_PASSED`). It shows a calm "Departure has passed" state with the trip read from the URL (places, load, interval) and one button, **Replan for now**, which sets `depart` to the next quarter hour (`push`). The same state handles a `DEPARTURE_PASSED` response if the clock crossed the line while loading.

## 6. Share button

1. `navigator.share` on mobile when available, otherwise `navigator.clipboard.writeText(location.href)`.
2. Success toast: "Link copied. Anyone with it sees this exact trip, route and forecast hour."
3. If the clipboard is blocked: a small dialog with the URL selected for manual copy.
