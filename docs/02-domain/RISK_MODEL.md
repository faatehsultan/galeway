# Risk model

> Source of truth for all scoring and ranking logic. [REQUIREMENTS](../01-product/REQUIREMENTS.md) gives the tables. This doc adds the decisions needed to turn them into exact, testable code. Code lives in `backend/galeway/planning/domain/` and is **pure** (no I/O).

## 1. Levels

| Level | Ordinal | Bar color | Meaning |
|---|---|---|---|
| `LOW` | 0 | `#10B981` | Normal driving |
| `MODERATE` | 1 | `#EAB308` | Take care |
| `HIGH` | 2 | `#F97316` | Dangerous for trucks |
| `SEVERE` | 3 | `#DC2626` | Should avoid |
| `NO_TRAVEL` | 4 | `#A21CAF` | Do not drive |
| `NO_DATA` | n/a | gray | Forecast unavailable. **Never treated as safe.** |

Ordinals are used for averaging and ordering. `NO_DATA` is excluded from averages and counted separately (§6).

## 2. Inputs per checkpoint

| Input | Unit | Source field (Open-Meteo, hourly) |
|---|---|---|
| `wind_mph` | mph, **sustained** at 10 m | `wind_speed_10m` with `wind_speed_unit=mph` |
| `gust_mph` | mph (display only) | `wind_gusts_10m` |
| `rain_in_hr` | in/hr | `rain` + `showers` with `precipitation_unit=inch` |
| `snow_in_hr` | in/hr (snow depth, not water) | `snowfall` with `precipitation_unit=inch` |
| `load_lb` | lb | user input |

Why sustained wind and not gusts: [ADR-0006](../09-decisions/0006-sustained-wind-for-scoring.md). Why not `precipitation`: it includes melted snow, so snow would be counted twice.

## 3. Thresholds (exact boundaries)

Values are compared **as raw floats after unit conversion**. Nothing is rounded before classifying. Display rounding happens only in the UI.

**Boundary rule:** the requirement ranges overlap at their edges (rain "0.10–0.25" and "0.25–0.50" both include 0.25). We resolve every shared edge **upward**: a value exactly on a boundary takes the higher level. This is the conservative choice for a safety product. The two places where the requirements use "≤" (Severe upper edge for rain 1.00 and snow 3.0) stay inclusive, because No travel starts strictly above them (`> 1.00`, `> 3.0`).

### Wind (sustained, mph)

| Level | Condition |
|---|---|
| LOW | `w < 25` |
| MODERATE | `25 ≤ w < 35` |
| HIGH | `35 ≤ w < 45` |
| SEVERE | `45 ≤ w < 55` |
| NO_TRAVEL | `w ≥ 55` |

(The requirements write 25–34, 35–44, 45–54 with whole numbers. With continuous values, 34.6 is Moderate because it is below 35.)

### Rain (in/hr)

| Level | Condition |
|---|---|
| LOW | `r < 0.10` |
| MODERATE | `0.10 ≤ r < 0.25` |
| HIGH | `0.25 ≤ r < 0.50` |
| SEVERE | `0.50 ≤ r ≤ 1.00` |
| NO_TRAVEL | `r > 1.00` |

### Snow (in/hr)

| Level | Condition |
|---|---|
| LOW | `s < 0.5` |
| MODERATE | `0.5 ≤ s < 1.0` |
| HIGH | `1.0 ≤ s < 2.0` |
| SEVERE | `2.0 ≤ s ≤ 3.0` |
| NO_TRAVEL | `s > 3.0` |

## 4. Load rules (apply to wind only)

```text
wind_level = classify_wind(w)
if w >= 55:                         wind_level = NO_TRAVEL          # any load
elif 45 <= w < 55 and load > 30000: wind_level = NO_TRAVEL
elif 35 <= w < 45 and load > 40000: wind_level = max(wind_level, SEVERE)
```

- "More than" is strict: exactly 30,000 lb or 40,000 lb does **not** trigger the rule.
- Load rules can only raise a level, never lower it.

## 5. Checkpoint level

```text
level   = max(wind_level_after_load, rain_level, snow_level)
drivers = every condition whose level == level   # e.g. ["rain"] or ["wind", "snow"]
```

If any of the three inputs is missing, `level = NO_DATA` and `drivers = []`. We don't classify on partial inputs, because a missing wind value can't be assumed calm.

Each checkpoint also gets a short reason string for the UI, built from the drivers, e.g. *"Rain 0.30 in/hr (0.25–0.50) → High"* or *"Wind 38 mph with 42,000 lb (over 40,000 lb) → Severe"*.

## 6. Miles per checkpoint (how "Severe miles" are counted)

Checkpoints sit at mile 0 (origin), every `interval` miles, and at the destination. Each checkpoint **stands for the stretch of road closest to it**: from halfway back to the previous checkpoint to halfway forward to the next one.

```text
cover_i = (m_{i+1} − m_{i−1}) / 2      # with m_{−1} = m_0 and m_{n+1} = m_n
```

- The covers add up exactly to the route length (property-tested).
- `severe_mi` = sum of `cover_i` where level is SEVERE. Same for every level, including `no_data_mi`.
- `avg_risk` = **distance-weighted** mean of ordinals over checkpoints with data:
  `Σ(ordinal_i × cover_i) / Σ(cover_i)` for `level ≠ NO_DATA`. Reported to 2 decimals.

## 7. Ranking and recommendation

Each route gets a sort key; the smallest key wins:

```text
key = (
  has_no_travel,            # False before True: any No-travel mile disqualifies
  round(severe_mi, 1),      # 1. fewest Severe miles
  round(high_mi, 1),        # 2. fewest High miles
  round(no_data_mi, 1),     # unknown miles are never free
  round(avg_risk, 2),       # 3. lowest average risk
  duration_s,               # 4. shortest travel time
  provider_index            # stable final tie-break (A before B before C)
)
```

- Rounding inside the key prevents floating-point noise from deciding a tie.
- **Recommendation status:**
  - `ok`: the best route has no No-travel miles. It is recommended.
  - `all_no_travel`: every route has No-travel miles. **No route is recommended.** The UI says so and offers "Depart 6 hours later." Routes are still ranked for comparison.
  - `partial`: the recommended route has `no_data_mi > 0`. It is still recommended, with a warning.
- **`decided_by`** records the first key element that separated #1 from #2: `no_travel`, `severe_miles`, `high_miles`, `unknown_miles`, `average_risk`, `travel_time` or `tie`.

## 8. Explanation ("Why this route")

Generated from the ranking, never written by hand. 2–4 short lines:

1. Exclusions: *"Route C is excluded: No travel at mile 610 (wind 56 mph, 55 or more for any load)."*
2. The deciding comparison: *"Fewest severe miles: A has 0, B has 50."*
3. What was not needed: *"Settled at rule 1. High miles, average risk and travel time were not needed."*
4. When time decided, show the trade-off: *"Same risk profile; A is 1h 30m faster."*

## 9. Required tests (minimum)

| Area | Cases |
|---|---|
| Wind | 24.99→LOW, 25→MOD, 34.99→MOD, 35→HIGH, 44.99→HIGH, 45→SEV, 54.99→SEV, 55→NT |
| Rain | 0.0999→LOW, 0.10→MOD, 0.25→HIGH, 0.4999→HIGH, 0.50→SEV, 1.00→SEV, 1.0001→NT |
| Snow | 0.4999→LOW, 0.5→MOD, 1.0→HIGH, 2.0→SEV, 3.0→SEV, 3.0001→NT |
| Load | 40 mph @ 40,000→HIGH; 40 mph @ 40,001→SEV; 50 mph @ 30,000→SEV; 50 mph @ 30,001→NT; 60 mph @ 1,000→NT; load never lowers a level |
| Combine | max of three; multiple drivers; any missing input → NO_DATA |
| Miles | covers sum to route length; single-checkpoint route; last segment shorter than interval |
| Ranking | each of the 4 rules decides once; tie → provider order; all-no-travel; partial data; `decided_by` correct |
| Properties (Hypothesis) | more wind/rain/snow never lowers a level; more load never lowers a level; ranking is deterministic and order-independent of input list |
