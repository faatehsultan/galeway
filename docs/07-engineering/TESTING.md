# Testing

## 1. Strategy

```text
               ▲  few   Playwright e2e + axe (real browser, mocked API)
              ▲▲▲       API tests (Ninja TestClient + respx fixtures)
             ▲▲▲▲▲      Component tests (Testing Library + MSW)
           ▲▲▲▲▲▲▲▲▲ many  Domain unit + property tests (pure functions)
```

Most confidence comes from the **pure domain tests**, which are fast, exhaustive and deterministic. Nothing in CI calls a real provider.

## 2. Backend (pytest)

Tools: `pytest`, `pytest-asyncio`, `pytest-django`, `respx` (httpx mocking), `hypothesis` (property tests), `time-machine` (clock), `coverage` with branch coverage.

| Suite | Must cover |
|---|---|
| `unit/test_risk.py` | Every boundary in [RISK_MODEL §9](../02-domain/RISK_MODEL.md#9-required-tests-minimum) as a parametrized table; load rules; combining; NO_DATA |
| `unit/test_sampling.py` | Checkpoint placement for 10/25/50; last short segment; covers sum to length (property) |
| `unit/test_eta.py` | Interpolation exactness on synthetic polylines; time ↔ distance inverse (property); fallback path |
| `unit/test_forecast.py` | Ceil-hour for sums, nearest for instants; out-of-range → NO_DATA |
| `unit/test_ranking.py` | Each rule decides once; ties; all-no-travel; partial; `decided_by`; input order doesn't matter (property) |
| `unit/test_explain.py` | Exact sentences for each `decided_by` |
| `unit/test_units.py` | lb↔kg, m↔mi round trips |
| `providers/test_tomtom.py` | Request params (truck, **kg**, alternatives, departAt, extended representation); parsing; fill-to-3; dedupe; 429/5xx/timeout; key never appears in logs |
| `providers/test_openmeteo.py` | Batching ≤ 100; units params; rain = rain + showers; partial failure → NO_DATA |
| `api/test_plans.py` | Happy path on fixtures; validation messages match the UI; problem+json shape; ETag/304; Cache-Control; SSE event order; heatmap size < 150 KB; pagination (`total`, `Link`) |
| `api/test_throttle.py` | 429 + `Retry-After`; fail-open when Redis is down |
| `api/test_security.py` | Security headers in prod settings; CORS allowlist; no stack traces; `X-Robots-Tag` |

**Coverage gates** (CI fails below): `planning/domain` **≥ 95% lines and branches**, backend overall **≥ 85%**.

## 3. Frontend (Vitest)

Tools: `vitest` (jsdom), `@testing-library/react` + `user-event`, `msw`, `fast-check`, `@vitest/coverage-v8`.

| Area | Must cover |
|---|---|
| `lib/url-state` | parse/stringify round-trip (property); defaults omitted; invalid required → not-found; invalid optional → dropped; readable encoding |
| `lib/storage` + saved trips store | save/update/dedupe/rename/delete/undo; cap 50; corrupt JSON; future version; unavailable storage; cross-tab event |
| `features/plan-form` | Validation messages; combobox keyboard path; server field errors mapped onto fields; submit pushes URL |
| `features/results` | Recommended badge; deltas; warnings; all-no-travel state |
| `features/map` | `useMap` layer setup (MapLibre mocked); slider calls `setPaintProperty` and **does not** re-render the panel (render-count assertion) |
| `features/share` | Clipboard success/fallback; toast text |
| `lib/format` | Durations, local times across zones, numbers |

**Coverage gate:** frontend overall **≥ 80%** lines; `lib/` **≥ 90%**.

## 4. End-to-end (Playwright)

Runs against the production build (`vite preview`) with the API mocked by recorded fixtures (MSW in the browser, or Playwright `route()`), in Chromium, WebKit and a mobile viewport.

1. Plan Dallas → Denver: loading stages show → 3 routes → A recommended → map has checkpoints.
2. Move the slider and switch layers: URL updates (`replace`), no network calls.
3. Share: copy link → open it in a new context → same route, hour, layer, checkpoint.
4. Route detail: pagination and filter; Back returns to the map in the same state.
5. Saved trips: save → reload → open → rename → delete → undo.
6. Errors: 422 shows field errors; 502 shows the error card and Retry works; 429 shows a toast.
7. Theme: toggle, reload, no flash; both themes pass axe.
8. 404 and broken share link.
9. **Accessibility**: `@axe-core/playwright` on every screen, both themes: zero serious/critical issues.
10. **CSP**: the test fails on any CSP violation in the console.

## 5. API fuzzing (Schemathesis)

`schemathesis` generates hundreds of requests from our OpenAPI spec (odd values, edges, wrong types) and checks that the API never returns a 500, always returns problem+json for errors, and matches its own schema. Runs in CI against the app in `PROVIDERS_MODE=fixtures`.

## 6. Reports

- Backend: `coverage.xml` + HTML (`htmlcov/`); JUnit XML.
- Frontend: `lcov` + HTML (`coverage/`); JUnit XML.
- Playwright: HTML report + traces on failure.
- All uploaded as CI artifacts. The README shows the coverage numbers of the release build.

## 7. Fixtures

Recorded once with `backend/scripts/record_fixtures.py` (manual, needs a key), then scrubbed by a script that removes keys and checks no secret patterns remain (also enforced by `gitleaks`). Fixture scenarios: normal (Dallas → Denver), windy (forces load rule), snow (I-70 in winter), all-no-travel (synthetic), partial weather failure (synthetic), fewer than 3 routes (synthetic).
