# Roadmap

Time budget: **16 working hours over 4 days**. Phases are ordered so that there's **a deployed, working app from Phase 2 onward**, and every later phase only adds to it. If time runs short, use the cut list (§3), never cut tests for the domain.

## 1. Overview

| Phase | Focus | Hours | Priority |
|---|---|---|---|
| 0 | Skeleton, tooling, CI, first deploy | 1.5 | Code quality |
| 1 | Domain core (pure logic) | 2.5 | Correctness |
| 2 | Providers + plan API | 2.5 | Correctness |
| 3 | Plan flow UI + map | 3.0 | UI smoothness |
| 4 | Heatmap + forecast slider | 2.0 | UI smoothness |
| 5 | Detail, saved trips, states, theme, SEO | 2.5 | UI + quality |
| 6 | Hardening and polish | 1.5 | All |
| 7 | Release + walkthrough | 0.5 | Docs |
| | **Total** | **16.0** | |

## 2. Phases and acceptance criteria

### Phase 0: Skeleton, tooling, CI, first deploy

- [x] Monorepo layout as in [AGENTS §4](../../AGENTS.md#4-repository-layout); root has only the 3 markdown files plus tooling config
- [x] Backend: uv project, Django 6.1 + Ninja, settings split, `/api/v1/health`, Dockerfile (non-root; image build is verified on the first `make docker-build`), ruff/mypy/pytest configured
- [x] Frontend: Vite + React + TS strict, Tailwind v4 with tokens from [DESIGN §3](../06-design/DESIGN.md#3-color-tokens), shadcn init, TanStack Router + Query, fonts self-hosted, theme without flash, favicon/manifest/icons from [brand/](../06-design/brand/)
- [x] Makefile, pre-commit, `docker-compose.yml` (redis)
- [x] Docs tooling: `make docs-check` (link/anchor checker, markdownlint, docs-sync script in `.github/scripts/`), PR template with a "Docs updated" checklist
- [x] Claude Code Stop hook in `.claude/settings.json` that runs `make docs-check` and blocks finishing on failure (check the current hooks schema in the Claude Code docs; shape: `{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"make docs-check"}]}]}}`)
- [x] CI workflow with every gate that has code to test wired: lint, types, import-linter, tests + coverage, size budget, audits, gitleaks, CodeQL, docs checks, API-types drift (thresholds can start at current numbers and rise to target by Phase 6). Schemathesis is added in Phase 2 and Playwright/axe/CSP and Lighthouse in Phase 6, with the code they test
- [ ] **Deployed**: Pages shows the shell; Render returns `/health`; CORS works between them

### Phase 1: Domain core

- [ ] `units`, `risk`, `sampling`, `eta`, `forecast`, `ranking`, `explain`, `heatmap_grid` implemented as pure functions per [RISK_MODEL](../02-domain/RISK_MODEL.md) and [ROUTING_AND_WEATHER](../02-domain/ROUTING_AND_WEATHER.md)
- [ ] Every case in [RISK_MODEL §9](../02-domain/RISK_MODEL.md#9-required-tests-minimum) tested, plus Hypothesis properties
- [ ] Domain coverage ≥ 95% lines and branches; import-linter contract passes

### Phase 2: Providers + plan API

- [ ] HTTP client with timeouts, retries, circuit breaker, log redaction
- [ ] TomTom adapter (search, routes: truck, **kg**, alternatives, fill to 3, dedupe) with fixtures
- [ ] Open-Meteo adapter (batched, grid-snapped, rain = rain + showers) with fixtures
- [ ] Redis cache + in-memory fallback + single-flight; rate limits
- [ ] Endpoints per [API](../03-architecture/API.md): `/places`, `/plans` (JSON + SSE), `/plans/heatmap`, `/plans/routes/{id}/checkpoints`; problem+json errors; ETag/Cache-Control; `Server-Timing`
- [ ] `make api-types` produces `schema.d.ts`; `PROVIDERS_MODE=fixtures` works
- [ ] Deployed and callable from the hosted frontend origin

### Phase 3: Plan flow UI + map

- [ ] Form with combobox, departure, load, interval; zod schema equals API limits; server errors map to fields
- [ ] URL state per [URL_STATE](../03-architecture/URL_STATE.md) with round-trip property tests
- [ ] Loading screen with real SSE stages and Cancel (`02-planning-loading.png`)
- [ ] Results list: 3 cards, recommended badge, deltas, risk bars, worst stretch (`03-results-map.png`)
- [ ] Map: base style per theme, routes (selected vs alternate), checkpoints with popup, fit bounds, click to select (URL updates)
- [ ] Share button with clipboard/toast

### Phase 4: Heatmap + forecast slider

- [ ] Heatmap source built once from the columnar response; layers Risk/Wind/Rain/Snow
- [ ] Slider + play: `setPaintProperty` only, rAF-coalesced, 60 fps; URL `replace` debounced; unavailable hours greyed
- [ ] Truck marker at the slider hour on the selected route
- [ ] Test asserting no React re-render of the panel per tick

### Phase 5: Detail, saved trips, states, theme, SEO

- [ ] Route detail (`04-route-detail.png`): stats, why, risk strip, paginated + filtered table using the API pagination
- [ ] Saved trips drawer (`05-saved-trips.png`) with all behaviors in [FRONTEND §7](../04-frontend/FRONTEND.md#7-saved-trips)
- [ ] Methodology modal + `/methodology` page (`07-risk-methodology.png`)
- [ ] All states in `06-states-errors-toasts.png`, 404 (`08-not-found.png`), offline, cold start, error boundary
- [ ] Dark theme on every screen; mobile layout (`09-mobile-results.png`)
- [ ] SEO per [SEO](../04-frontend/SEO.md): static meta/OG/JSON-LD, per-route head, robots, sitemap, prerender of `/` and `/methodology`

### Phase 6: Hardening and polish

- [ ] Playwright suite ([TESTING §4](../07-engineering/TESTING.md#4-end-to-end-playwright)) green in Chromium, WebKit and mobile; axe clean; no CSP violations
- [ ] Coverage at target; bundle budgets met; Lighthouse targets met
- [ ] Security headers verified in production; `gitleaks`/audits clean
- [ ] Visual pass against every mockup in both themes; motion and reduced-motion checked

### Phase 7: Release + walkthrough

- [ ] Release checklist in [DEPLOYMENT §4](../08-operations/DEPLOYMENT.md#4-release-checklist)
- [ ] Walkthrough video recorded from [WALKTHROUGH_SCRIPT](WALKTHROUGH_SCRIPT.md) (5–10 min)
- [ ] README links and coverage numbers filled in; GitHub repo description, topics and social preview image set (`og-image.png`)
- [ ] Final docs pass: every doc re-read against the shipped code; `CHANGELOG.md` `Unreleased` renamed to `1.0.0` with the date

## 3. Cut list (if behind schedule, cut in this order)

1. Cloudflare Pages Function for per-trip OG titles ([SEO §5](../04-frontend/SEO.md#5-shared-trip-previews-optional-phase-6-stretch))
2. Saved-trips search box (keep save/open/rename/delete)
3. SSE progress (fall back to an honest indeterminate loader with static step labels)
4. WebKit in the e2e matrix (keep Chromium + mobile Chromium)
5. Prerendering (keep static meta in `index.html`)

**Never cut:** domain tests, any item in REQUIREMENTS.md, error states, share links, the slider's performance approach.

## 4. Parking lot (ideas, not in scope)

- Frozen "snapshot" share links (store a plan for 7 days)
- "Best departure time" search across the next 24 h
- Hours-of-service breaks and rest-stop suggestions
- Gust-based scoring toggle ([ADR-0006](../09-decisions/0006-sustained-wind-for-scoring.md))
- Vehicle dimensions (height, axles, hazmat)
- Accounts with synced trips ([ADR-0002](../09-decisions/0002-no-authentication.md))
- Weather alerts from NWS overlaid on the map
