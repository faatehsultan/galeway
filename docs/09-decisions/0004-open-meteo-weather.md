# 0004. Open-Meteo for hourly forecasts

- Status: Accepted
- Date: 2026-11-25

## Context

We need hourly wind, rain and snow forecasts for many points along a corridor, for at least the next 48 hours past departure, in mph and inches, at $0.

## Decision

Use the **Open-Meteo Forecast API**: `hourly=wind_speed_10m,wind_gusts_10m,rain,showers,snowfall`, `wind_speed_unit=mph`, `precipitation_unit=inch`, many coordinates per request.

## Consequences

- No key, no card; multi-location requests keep the call count low.
- Native units match the rules, so there's less conversion code.
- `precipitation` includes melted snow, so rain must be `rain + showers` ([RISK_MODEL §2](../02-domain/RISK_MODEL.md#2-inputs-per-checkpoint)).
- The free API is intended for non-commercial use. That fits this project today; a commercial launch would need the paid API (same interface).
