# 0007. Saved trips in localStorage

- Status: Accepted
- Date: 2026-11-25

## Context

Saving trips is a useful extra. Without accounts ([ADR-0002](0002-no-authentication.md)) there's nowhere server-side to keep them, and trip params aren't sensitive.

## Decision

Store saved trips in `localStorage` under `galeway.savedTrips.v1`, validated with zod on every read, capped at 50, synced across tabs with the `storage` event. Details: [FRONTEND §7](../04-frontend/FRONTEND.md#7-saved-trips).

## Consequences

- Works instantly, offline, with no backend work.
- Per browser and device only, and cleared if the user clears site data. The UI says "Kept on this device only."
- Versioned schema allows safe migration later (to IndexedDB or a server).
