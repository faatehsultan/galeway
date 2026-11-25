# Requirements

> The core requirements for Galeway. **This document overrides every other doc.** If a feature or rule elsewhere conflicts with it, this one wins.

## Goal

A **React + Django** web app that helps a truck driver choose the **safest route** based on **weather, load weight and travel time**.

## Inputs

- Origin and destination
- Departure date and time
- Load weight

## The app must

1. Generate **3 route options** using a routing API.
2. Sample weather **every 10 / 25 / 50 miles**, using the truck's **estimated arrival time at each checkpoint**.
3. Calculate weather risk using the risk and load rules below.
4. **Recommend the best route**, balancing weather risk and travel time.
5. Show **all routes, checkpoints, risk levels, ETAs and route summaries on a map**.
6. Show a **weather heatmap along the trip corridor** with a **0–48 hour forecast slider**.

Third-party APIs are used for routing, geocoding and weather. We don't build a routing engine.

## Risk rules (per checkpoint)

| Condition | Low | Moderate | High | Severe | No travel |
|---|---|---|---|---|---|
| Wind | < 25 mph | 25–34 | 35–44 | 45–54 | ≥ 55 mph |
| Rain | < 0.10 in/hr | 0.10–0.25 | 0.25–0.50 | 0.50–1.00 | > 1.00 |
| Snow | < 0.5 in/hr | 0.5–1.0 | 1.0–2.0 | 2.0–3.0 | > 3.0 |

## Load rules

- ≥ 55 mph: **No travel** for any load
- 45–54 mph and > 30,000 lb: **No travel**
- 35–44 mph and > 40,000 lb: **Severe**

## Route recommendation: prefer, in order

1. Fewest Severe miles
2. Fewest High miles
3. Lowest average risk
4. Shortest travel time

## Release outputs

- Public GitHub repository
- Hosted application
- A 5–10 minute product walkthrough video

## Priorities

1. **Correctness** of routes, weather, risk and recommendation logic, and **smoothness and performance** of the UI, map and heatmap. These two are equal top priority.
2. Code quality.
3. Documentation and the walkthrough.

**Correctness and clarity come before extra features.**

The tables above leave some gaps (overlapping boundaries, which wind measure, how miles are counted). The decisions that fill them are in [RISK_MODEL.md](../02-domain/RISK_MODEL.md).
