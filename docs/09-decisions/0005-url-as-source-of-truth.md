# 0005. The URL is the app state; no database

- Status: Accepted
- Date: 2026-11-25

## Context

Users must be able to share exactly what they see. Forecast data changes hourly, so stored results would go stale anyway. A database adds hosting cost (free Postgres tiers expire or sleep) and operations.

## Decision

Everything visible is encoded in the URL ([URL_STATE](../03-architecture/URL_STATE.md)). The backend is stateless: each request carries the full trip, and results are cached by a hash of the normalized inputs. There is no database.

## Consequences

- Share = copy the URL. Back/forward and reload just work.
- Shared links always show the latest forecast (with "forecast issued at"). Frozen snapshots aren't supported; they're in the Parking lot.
- URLs are longer, but stay readable thanks to custom encoding.
- Hosting is simpler and free, with one less thing that can fail.
