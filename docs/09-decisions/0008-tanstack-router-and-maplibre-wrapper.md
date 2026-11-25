# 0008. TanStack Router and a thin MapLibre wrapper

- Status: Accepted
- Date: 2026-11-25

## Context

The URL holds a lot of typed state (trip, route, hour, layer, map view, panel, page). The map must stay at 60 fps while the slider moves, and MapLibre GL JS 6 is a recent major.

## Decision

- **TanStack Router** with `validateSearch` (zod) and a custom search serializer: typed, validated search params as first-class state.
- **Own `useMap` wrapper** around `maplibre-gl` (create once, imperative layer/paint updates through refs) instead of a React map binding.

## Consequences

- Search params are typed end to end; invalid links are caught in one place.
- Slider and hover updates bypass React entirely.
- No dependency on a binding library catching up with MapLibre 6.
- A little more code (~200 lines) for map lifecycle, which we own and test.

## Alternatives considered

- React Router v7 with manual search parsing: works, but more hand-written plumbing for typed params.
- `react-map-gl`: convenient, but adds a re-render path we'd have to work around for the slider, and its MapLibre 6 support has to be checked.
