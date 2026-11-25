# Routing and weather

How a trip request becomes routes, checkpoints, ETAs and forecasts. Provider details are kept inside `backend/galeway/providers/`. The domain only sees our own types (`Route`, `Checkpoint`, `Forecast`).

## 1. Providers

| Need | Provider | Endpoint | Key |
|---|---|---|---|
| Place search (autocomplete) | TomTom Search API | fuzzy/typeahead search, `countrySet=US`, `typeahead=true`, `limit=5` | server-side `TOMTOM_API_KEY` |
| Truck routes | TomTom Routing API v1 | `GET /routing/1/calculateRoute/{lat,lon:lat,lon}/json` | same |
| Hourly forecast | Open-Meteo Forecast API | `GET /v1/forecast` | none |
| Base map tiles | OpenFreeMap | vector styles (positron-style light; dark derived, see [FRONTEND §5](../04-frontend/FRONTEND.md#5-map-heatmap-and-the-forecast-slider)) | none |

Why these: [ADR-0003](../09-decisions/0003-tomtom-truck-routing.md), [ADR-0004](../09-decisions/0004-open-meteo-weather.md). Always confirm parameter names against the providers' current docs before coding.

## 2. Routes

### 2.1 Request

```text
travelMode=truck
vehicleWeight=<load_lb × 0.45359237, rounded to int>   # KILOGRAMS
vehicleCommercial=true
maxAlternatives=2                                      # 1 main + up to 2 alternatives
departAt=<RFC 3339 with offset, e.g. 2026-11-26T12:00:00Z>
routeType=fastest
traffic=true
routeRepresentation=polyline
extendedRouteRepresentation=distance,travelTime        # per-point progress → ETAs
computeTravelTimeFor=all
```

### 2.2 Making sure there are 3 routes

TomTom may return fewer than 3. Fill up in this order, stopping at 3:

1. Main + alternatives from the request above.
2. Same request with `routeType=shortest`.
3. Same request with `routeType=eco`.

**Deduplicate** after each step: two routes are the same if ≥ 90% of one's length lies within 200 m of the other (compare simplified polylines). Keep the faster one. If still under 3, return what we have plus a `FEWER_ROUTES` warning.

Route ids are `a`, `b`, `c` in final provider order (stable labels). "Recommended" is a separate flag, so labels don't shuffle when the forecast changes.

### 2.3 Route naming

Name each route by its 1–2 most-used major roads and a waypoint town from the guidance/sections (e.g. "US-287 via Amarillo"). If that data is missing, fall back to "Route A".

## 3. Checkpoints and ETAs

1. Walk the polyline with cumulative distance (from `extendedRouteRepresentation=distance`; Haversine fallback).
2. Place checkpoints at mile 0, every `interval` miles (10, 25 or 50) and at the destination. Skip an interval point that would sit less than 20% of an interval before the destination.
3. **ETA**: linearly interpolate cumulative `travelTime` between the two polyline points around each checkpoint's distance. `eta = departAt + t`. If per-point time is missing, scale by the summary's total time (and log a warning metric).
4. Store `eta_utc`. The UI shows local time from the checkpoint's IANA time zone (resolved offline with `timezonefinder`, cached by rounded coordinate).
5. **Truck position at slider hour `h`**: invert the same interpolation (time → distance → lat/lon). Used for the truck marker on the map.

Assumption: continuous driving at provider speeds; hours-of-service breaks are not modeled (see [PRODUCT_SPEC §3.3](../01-product/PRODUCT_SPEC.md#33-non-goals-deliberately-not-built)).

## 4. Weather lookup

### 4.1 Request

```text
GET https://api.open-meteo.com/v1/forecast
  ?latitude=<lat1,lat2,…>&longitude=<lon1,lon2,…>       # batched, ≤ 100 points per call
  &hourly=wind_speed_10m,wind_gusts_10m,rain,showers,snowfall
  &wind_speed_unit=mph&precipitation_unit=inch
  &timezone=GMT&timeformat=unixtime
  &start_hour=<departure hour UTC>&end_hour=<departure + 48h, or arrival if later>
```

Several coordinates in one request return a list (one entry per location). Calls for different batches run **concurrently** (`asyncio.gather`, max 4 in flight).

### 4.2 Snap to a grid (sharing and caching)

Round each coordinate to a **0.05° grid** (~5 km) before fetching. Checkpoints from all 3 routes and the heatmap share cells, so most trips need far fewer calls than they have checkpoints, and other users' trips warm the same cache ([CACHING](../03-architecture/CACHING.md)).

### 4.3 Picking the hour for an ETA

Open-Meteo hourly values have different meanings:

- `rain`, `showers`, `snowfall` are **sums over the preceding hour**, stamped at the end of the hour. The value stamped `14:00` is what fell from 13:00 to 14:00. For an ETA of 13:20 we use the bucket **ending at `ceil_hour(eta)`** (14:00). A one-hour sum equals the in/hr rate for that hour.
- `wind_speed_10m` and `wind_gusts_10m` are **instant values** on the hour, so we use the **nearest hour** to the ETA.

If the needed hour is outside the returned range, that checkpoint is `NO_DATA`.

## 5. Heatmap grid (trip corridor)

Goal: a smooth heatmap along all routes for hours 0–48 after departure, fetched **once** per trip.

1. Bounding box of all routes, padded by 0.5°.
2. Grid spacing `max(0.25°, sqrt(bbox_area / 400))`, so there are at most about 400 points.
3. Keep only grid points within 60 km of any route (distance to simplified polylines).
4. Fetch hourly values for hours 0–48 relative to departure (same request shape as §4.1, same 0.05° cache cells).
5. For each point and hour compute `wind`, `rain`, `snow` and `risk` (the full classifier, including the trip's load rules).
6. Return **columnar, quantized** arrays (see [API §4.4](../03-architecture/API.md#44-heatmap-get-apiv1plansheatmap)). Target: under 150 KB compressed.

Slider hour `0` = departure hour. The slider ends at 48 h, or earlier if the forecast horizon ends sooner (the UI greys out the missing part).
