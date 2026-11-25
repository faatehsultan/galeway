# 0003. TomTom for truck routing and place search

- Status: Accepted
- Date: 2026-11-25

## Context

We need 3 route options for long US trips, ideally truck-aware with the load weight, a departure time and per-point timing for ETAs. It must be free without a card.

## Decision

Use **TomTom Routing API v1** (`travelMode=truck`, `vehicleWeight` in kg, `vehicleCommercial=true`, `maxAlternatives`, `departAt`, `extendedRouteRepresentation=distance,travelTime`) and **TomTom Search** for autocomplete, with one server-side key.

## Consequences

- Truck-legal routes that consider weight and depart-time traffic.
- Per-point travel time gives accurate checkpoint ETAs.
- The free quota is limited, so caching and rate limits are required ([CACHING](../03-architecture/CACHING.md)).
- Alternatives aren't guaranteed, so we fill to 3 with `shortest`/`eco` variants and dedupe ([ROUTING_AND_WEATHER §2.2](../02-domain/ROUTING_AND_WEATHER.md#22-making-sure-there-are-3-routes)).

## Alternatives considered

- **OpenRouteService** (`driving-hgv`): its public API only returns alternative routes for trips under 100 km, which rules out real truck trips.
- **Mapbox Directions**: generous free tier, but no truck profile.
- **HERE**: strong truck routing, but a more complex signup and smaller free quota for this use.
- **Google Routes**: no truck mode; billing account required.
