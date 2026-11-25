# Architecture decision records

Short records of decisions that shape the codebase. Format: context → decision → consequences. When a decision changes, write a new ADR that **supersedes** the old one; don't edit history.

| # | Decision | Status |
|---|---|---|
| [0001](0001-django-ninja-over-drf.md) | Django Ninja instead of Django REST Framework | Accepted |
| [0002](0002-no-authentication.md) | No user accounts or authentication | Accepted |
| [0003](0003-tomtom-truck-routing.md) | TomTom for truck routing and place search | Accepted |
| [0004](0004-open-meteo-weather.md) | Open-Meteo for hourly forecasts | Accepted |
| [0005](0005-url-as-source-of-truth.md) | The URL is the app state; no database | Accepted |
| [0006](0006-sustained-wind-for-scoring.md) | Score wind on sustained speed, show gusts | Accepted |
| [0007](0007-saved-trips-in-localstorage.md) | Saved trips in `localStorage` | Accepted |
| [0008](0008-tanstack-router-and-maplibre-wrapper.md) | TanStack Router and a thin MapLibre wrapper | Accepted |
| [0009](0009-free-tier-hosting.md) | Free-tier hosting: Render + Cloudflare Pages + Upstash | Accepted |
| [0010](0010-typescript-6-and-eslint-9.md) | TypeScript 6 and ESLint 9 instead of the newest majors | Accepted |

Template for new ADRs:

```text
# NNNN. Title
- Status: Proposed | Accepted | Superseded by NNNN
- Date: YYYY-MM-DD
## Context
## Decision
## Consequences
## Alternatives considered
```
