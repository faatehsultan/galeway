# Product spec

## 1. The idea in one paragraph

A truck driver or dispatcher enters where, when and how heavy. Galeway fetches three truck-legal routes, checks the forecast at evenly spaced checkpoints **for the hour the truck will actually be there**, scores each checkpoint against the risk and load rules, and recommends the route with the fewest dangerous miles, using time only to break ties. Everything is shown on a calm map with a 48-hour weather slider and a plain-English "why this route." It is a safety co-pilot that **explains** its decision rather than a black box.

## 2. Users and jobs

| User | Job to be done |
|---|---|
| Driver | "Before I leave, tell me which way is safe for this load, and where the bad stretch is." |
| Dispatcher | "Compare routes for a planned departure and send the driver a link that shows exactly what I see." |
| First-time visitor | "Show me in a minute what this does, without signing up." |

## 3. Scope

### 3.1 Required features (from [REQUIREMENTS](REQUIREMENTS.md))

| # | Feature | Acceptance criteria |
|---|---|---|
| F1 | **Trip form**: origin, destination (autocomplete), departure date/time, load weight (lb), sampling interval 10/25/50 mi | Validated on client and server with the same limits (§5). Keyboard-only usable. Submitting updates the URL. |
| F2 | **3 route options** from a routing API, truck mode, with load weight | Always shows exactly 3 when the provider can produce them; fills gaps with route-type variants and removes near-duplicates (≥ 90% shared length). If fewer than 3 truly distinct routes exist, shows what exists and says why. |
| F3 | **Checkpoints with ETAs** at the chosen interval, plus origin and destination | ETA comes from per-point travel time along the route, not a straight-line guess. Shown in each checkpoint's local time zone. |
| F4 | **Weather at ETA** for each checkpoint | Forecast hour matches the ETA (rules in [ROUTING_AND_WEATHER §4](../02-domain/ROUTING_AND_WEATHER.md#4-weather-lookup)). |
| F5 | **Risk per checkpoint** using risk and load rules | Exactly as [RISK_MODEL](../02-domain/RISK_MODEL.md). Each checkpoint names the condition that drove its level. |
| F6 | **Recommendation** using the 4-step preference | Deterministic. Shows which rule decided and why (plain English). Handles "all routes No travel." |
| F7 | **Map**: all routes, checkpoints colored by risk, ETAs, route summaries | Recommended route emphasized. Click or hover a checkpoint for details. Click a route to select it. |
| F8 | **Corridor heatmap with 0–48 h slider** | Slider and play button move smoothly (60 fps target). Layers: Risk, Wind, Rain, Snow. Shows where the truck is at that hour. |

### 3.2 Extras (small, useful, approved)

| # | Feature | Acceptance criteria |
|---|---|---|
| X1 | **Share trip** (URL holds the full state) | Copy-link button with a toast. Opening the link restores trip, selected route, forecast hour, layer, map view and open panel. Spec: [URL_STATE](../03-architecture/URL_STATE.md). |
| X2 | **Saved trips** in `localStorage` | Save, rename, delete with undo, search, open. Up to 50. Syncs across tabs. Survives bad or old data. A trip whose departure has passed is marked and offers "Replan for now." Spec: [FRONTEND §7](../04-frontend/FRONTEND.md#7-saved-trips). |
| X3 | **Route detail** | Stats, "why this route," risk strip along the route, paginated checkpoint table with a "Moderate and above" filter. |
| X4 | **"How we score risk"** panel | Shows the rule tables, load rules, ranking order and our assumptions. |
| X5 | **Light and dark theme** | Light by default; follows the system setting until the user picks one; remembered. |
| X6 | **Designed states** | Loading with real stages, empty, field errors, blocking errors with retry, partial forecast, no safe route, offline, cold start, 404. |

### 3.3 Non-goals (deliberately not built)

- User accounts and authentication ([ADR-0002](../09-decisions/0002-no-authentication.md)).
- Turn-by-turn navigation, live GPS tracking.
- Driver hours-of-service breaks, fuel stops, tolls, bridge heights.
- Non-US trips, metric units.
- A database. State lives in the URL and in the browser ([ADR-0005](../09-decisions/0005-url-as-source-of-truth.md)).

## 4. Screens

All screens are mocked in [DESIGN.md §9](../06-design/DESIGN.md#9-screen-inventory) (light and dark).

| Screen | URL | Mockup |
|---|---|---|
| First visit | `/` | `01-first-visit.png` |
| Planning (loading) | `/trip?…` while loading | `02-planning-loading.png` |
| Results + map | `/trip?…` | `03-results-map.png` |
| Route detail | `/trip/routes/:routeId?…` | `04-route-detail.png` |
| Saved trips (drawer) | `…&panel=saved` | `05-saved-trips.png` |
| States and toasts | (various) | `06-states-errors-toasts.png` |
| How we score risk (modal) | `…&panel=methodology` | `07-risk-methodology.png` |
| Not found / broken link | any unknown path or invalid params | `08-not-found.png` |
| Mobile results | `/trip?…` at < 768 px | `09-mobile-results.png` |

## 5. Input rules (shared by client and server)

| Field | Rule | Error message |
|---|---|---|
| Origin / destination | Chosen from suggestions (has coordinates); inside the continental US | "Pick a place from the list" / "Galeway covers the continental US only" |
| Same place | Origin and destination more than 1 mile apart | "Origin and destination are the same place" |
| Departure | From now − 5 min to now + 7 days | "Departure must be within the next 7 days" |
| Load weight | Integer, 1,000–80,000 lb (US federal gross limit) | "Enter a weight between 1,000 and 80,000 lb" |
| Interval | One of 10, 25, 50 | (control prevents others) |
| Route length | ≤ 3,000 miles | "That trip is too long to plan reliably" |

## 6. Copy and tone

Calm, plain, specific. Say what happened and what to do next. No exclamation marks, no blame, no jargon ("No travel" rather than "NT"). Numbers always have units. Times always show their time zone.
