# 0006. Score wind on sustained speed, show gusts

- Status: Accepted
- Date: 2026-11-25

## Context

The rules say "Wind" without saying whether that means sustained speed or gusts. Sustained wind is the steady average; gusts are bursts of a few seconds and are usually much higher. Scoring on gusts would mark large areas Severe in normal weather.

## Decision

Classify on **sustained wind at 10 m** (`wind_speed_10m`). Show gusts next to it in popups and tables. State the assumption in the methodology panel.

## Consequences

- Matches the usual reading of such tables and the numbers in the requirements.
- Gust-driven rollover risk is visible to the driver, but not scored.
- If the team prefers gusts, it's a one-line change in `domain/risk.py` (the input selector) plus test updates. Worth asking about in the review.
