# AGENTS.md: operating manual for coding agents

This file is for any coding agent (Claude Code, Codex, Cursor, …) and for humans. Read it fully before writing code. `CLAUDE.md` imports this file.

## 1. What we are building

**Galeway** is a weather-aware truck routing web app. Priorities, in order:

1. **Correct logic** (routes, weather at ETA, risk, recommendation) and a **smooth, fast UI** (map, heatmap, slider). These two are equal top priority.
2. **Code quality**.
3. **Documentation**.

**Correctness and clarity come before extra features.** Every decision follows from that. The core requirements are in [docs/01-product/REQUIREMENTS.md](docs/01-product/REQUIREMENTS.md).

## 2. Read in this order

1. [docs/01-product/REQUIREMENTS.md](docs/01-product/REQUIREMENTS.md): the core requirements. They override everything else.
2. [docs/02-domain/RISK_MODEL.md](docs/02-domain/RISK_MODEL.md): the exact rules and edge cases. This is the source of truth for logic.
3. [docs/01-product/PRODUCT_SPEC.md](docs/01-product/PRODUCT_SPEC.md): features, scope and acceptance criteria.
4. [docs/10-planning/ROADMAP.md](docs/10-planning/ROADMAP.md): phases, time budget and what to build next.
5. The doc for the area you are touching: [architecture](docs/03-architecture/ARCHITECTURE.md), [API](docs/03-architecture/API.md), [URL state](docs/03-architecture/URL_STATE.md), [frontend](docs/04-frontend/FRONTEND.md), [backend](docs/05-backend/BACKEND.md), [design](docs/06-design/DESIGN.md).

If two docs disagree, the order above wins. Fix the losing doc in the same change.

## 3. Golden rules

1. **The spec first, then polish.** Build only what [PRODUCT_SPEC.md](docs/01-product/PRODUCT_SPEC.md) lists. Ideas go to the *Parking lot* in [ROADMAP.md](docs/10-planning/ROADMAP.md), not into code.
2. **The domain core stays pure.** Risk classification, sampling, ETA interpolation, ranking and explanation are pure functions with no I/O, no Django and no HTTP. They live in `backend/galeway/planning/domain/` and have the highest test coverage in the repo.
3. **Write tests before or with the code.** Every rule in RISK_MODEL.md has a test. No feature is done without tests.
4. **Never call real third-party APIs in tests.** Use recorded fixtures (`respx` on the backend, MSW on the frontend).
5. **Keep secrets on the server.** The TomTom key never reaches the browser, logs, fixtures or git. Redact `key=` from every logged URL.
6. **The URL is the app state.** Anything the user can see (trip, selected route, forecast hour, layer, map view, panel, page) must round-trip through the URL as described in [URL_STATE.md](docs/03-architecture/URL_STATE.md).
7. **Match the mockups.** Build screens against [docs/06-design/mockups](docs/06-design/mockups) (light and dark) and the tokens in [DESIGN.md](docs/06-design/DESIGN.md). Do not invent new colors, fonts or spacing.
8. **Every state is designed.** Loading, empty, error, partial data, no safe route, offline and cold start all have a UI (see `06-states-errors-toasts.png`). Never show a blank screen or a raw error.
9. **Keep the repo root clean.** The only markdown files at the root are `AGENTS.md`, `CLAUDE.md` and `README.md`. All other docs go under `docs/` in the matching numbered folder. Tooling config (`.github/`, `.gitignore`, `.editorconfig`, `docker-compose.yml`, `Makefile`) may live at the root; nothing else.
10. **Docs move with code. Always.** Every change that alters behavior, an API, a URL param, a rule, a command, a dependency, a screen or a decision updates the matching docs **and the root README** in the same commit. This is mandatory; see §9. A change isn't finished until the docs say what the code does.
11. **No new dependency without a reason.** Prefer the platform and the existing stack. If you add one, say why in the PR or commit body, and write an ADR if it is structural.
12. **Flag ambiguity, don't guess silently.** If something isn't covered, pick the safest reasonable option, write it down in the relevant doc, and mention it in your summary.

## 4. Repository layout

```text
galeway/
├── AGENTS.md · CLAUDE.md · README.md
├── Makefile                      # one entry point for common tasks
├── docker-compose.yml            # redis (+ api) for local dev
├── .github/workflows/            # ci.yml, keep-warm.yml
├── backend/
│   ├── pyproject.toml · uv.lock · manage.py · Dockerfile · .env.example
│   ├── config/                   # settings/{base,dev,prod,test}.py, urls.py, asgi.py
│   ├── galeway/
│   │   ├── api/                  # Ninja routers, schemas, errors, throttles
│   │   ├── planning/
│   │   │   ├── domain/           # PURE: risk.py, sampling.py, eta.py, ranking.py, explain.py, heatmap_grid.py, units.py, types.py
│   │   │   └── service.py        # orchestrates providers + domain (the only place both meet)
│   │   ├── providers/            # tomtom.py, openmeteo.py, http.py (retries/timeouts), cache.py
│   │   └── core/                 # logging, request-id middleware, health
│   └── tests/                    # unit/, api/, providers/, fixtures/
└── frontend/
    ├── package.json · pnpm-lock.yaml · vite.config.ts · index.html
    ├── build/                    # Vite plugin that fills the CSP in _headers
    ├── public/                   # favicon.svg, _headers, _redirects
    └── src/
        ├── app/                  # router, providers, theme, error boundary
        ├── routes/               # TanStack Router route files
        ├── features/             # plan-form, results, map, route-detail, saved-trips, methodology, share
        ├── components/ui/        # shadcn/ui primitives
        ├── lib/                  # api (generated types + client), url-state, storage, format, units
        └── styles/
```

Details: [ARCHITECTURE.md](docs/03-architecture/ARCHITECTURE.md), [FRONTEND.md](docs/04-frontend/FRONTEND.md), [BACKEND.md](docs/05-backend/BACKEND.md).

## 5. Commands

All through the `Makefile` (full list in [LOCAL_DEVELOPMENT.md](docs/08-operations/LOCAL_DEVELOPMENT.md)):

| Command | Does |
|---|---|
| `make setup` | Install backend (uv) and frontend (pnpm) deps, install pre-commit hooks |
| `make dev` | Run API (uvicorn, reload) and web (Vite) together |
| `make test` | Backend + frontend unit/integration tests with coverage |
| `make e2e` | Playwright end-to-end + axe accessibility checks |
| `make lint` / `make format` | ruff + ESLint + Prettier |
| `make typecheck` | mypy (strict) + `tsc --noEmit` |
| `make api-types` | Export OpenAPI from the backend and regenerate `frontend/src/lib/api/schema.d.ts` |
| `make check` | Everything CI runs. **Run before every commit.** |

## 6. Versions policy

- At scaffold time, look up the **latest stable** version of every dependency (`npm view <pkg> version`, `uv pip index versions <pkg>` or PyPI) and **pin exact versions**. Lockfiles are committed.
- Baselines (minimums): Python 3.13, Django 6.1, Django Ninja (latest), Node Active LTS, React 19, Vite 8, Tailwind CSS 4, TanStack Router and Query (latest), MapLibre GL JS 6, TypeScript (latest stable).
- Read each library's current docs or migration guide before using APIs you remember. Several of these had breaking majors recently (MapLibre 6, Vite 8, Tailwind 4).
- **Check compatibility before you pin.** Django Ninja must officially support the chosen Django version, and the OpenFreeMap styles must load in the chosen MapLibre major. If one doesn't, fall back one step (Django 5.2 LTS, or the previous MapLibre major), write an ADR, and update the README stack table.

## 7. Workflow for each roadmap phase

1. Re-read the phase in [ROADMAP.md](docs/10-planning/ROADMAP.md) and its acceptance criteria.
2. Plan briefly: list the files you will touch and the tests you will add.
3. Write tests first for domain logic, then implement.
4. Run `make check`. Fix everything; don't skip or weaken a gate.
5. For UI work, compare against the mockup PNGs in both themes and at mobile width.
6. Update docs if behavior changed. Tick the phase checkboxes in ROADMAP.md.
7. Commit with **Conventional Commits** (`feat(planning): rank routes by severe miles`). Commits are small and focused.

## 8. Definition of done (every change)

- [ ] Meets the acceptance criteria in PRODUCT_SPEC.md / ROADMAP.md
- [ ] Tests added; `make check` is green; coverage thresholds hold ([TESTING.md](docs/07-engineering/TESTING.md))
- [ ] No type errors, no lint warnings, no `any`, no `# type: ignore` without a comment explaining why
- [ ] Loading, empty and error states handled; keyboard and screen-reader usable
- [ ] Looks right in light and dark mode, at 1440 px and 390 px wide
- [ ] No secrets, no `console.log`/`print` left behind, no TODO without an issue reference
- [ ] **Docs sync done** (§9): matching docs and `README.md` updated, `CHANGELOG.md` entry added, ROADMAP boxes ticked, `make docs-check` green

## 9. Keeping docs in sync (mandatory, after every change)

At the end of **every** task, however small, run this checklist before you report done or commit.

**1. Update the docs your change touched:**

| If you changed… | Update |
|---|---|
| Risk rules, thresholds, ranking, explanation text | [RISK_MODEL.md](docs/02-domain/RISK_MODEL.md) (+ its test table) |
| Providers, sampling, ETA, forecast lookup, heatmap grid | [ROUTING_AND_WEATHER.md](docs/02-domain/ROUTING_AND_WEATHER.md) |
| An endpoint, a param, a response field, an error code, a rate limit | [API.md](docs/03-architecture/API.md), then run `make api-types` |
| A URL param, a route path, history behavior | [URL_STATE.md](docs/03-architecture/URL_STATE.md) |
| Cache keys, TTLs, headers | [CACHING.md](docs/03-architecture/CACHING.md) |
| Headers, CSP, validation limits, secrets handling | [SECURITY.md](docs/03-architecture/SECURITY.md) (+ [PRODUCT_SPEC §5](docs/01-product/PRODUCT_SPEC.md#5-input-rules-shared-by-client-and-server) for input limits) |
| Budgets or a performance technique | [PERFORMANCE.md](docs/03-architecture/PERFORMANCE.md) |
| Frontend structure, state, map, saved trips, toasts, theme | [FRONTEND.md](docs/04-frontend/FRONTEND.md) |
| Titles, meta, indexing, public files | [SEO.md](docs/04-frontend/SEO.md) |
| Backend layout, settings, env vars, logging | [BACKEND.md](docs/05-backend/BACKEND.md) and [LOCAL_DEVELOPMENT.md](docs/08-operations/LOCAL_DEVELOPMENT.md) |
| A token, component, screen or copy pattern | [DESIGN.md](docs/06-design/DESIGN.md); if a screen changed visibly, refresh its PNG in `mockups/light` and `mockups/dark` from the running app |
| Lint/type/test config, coverage thresholds, CI | [CODING_STANDARDS.md](docs/07-engineering/CODING_STANDARDS.md), [TESTING.md](docs/07-engineering/TESTING.md), [QUALITY_GATES.md](docs/07-engineering/QUALITY_GATES.md) |
| Hosting, env vars, release steps | [DEPLOYMENT.md](docs/08-operations/DEPLOYMENT.md) |
| A Makefile target or setup step | [LOCAL_DEVELOPMENT.md](docs/08-operations/LOCAL_DEVELOPMENT.md) and §5 of this file |
| A structural choice (library, pattern, provider, trade-off) | A new ADR in [docs/09-decisions](docs/09-decisions/README.md) + the ADR index |
| Scope (added, cut, deferred) | [PRODUCT_SPEC.md](docs/01-product/PRODUCT_SPEC.md) and [ROADMAP.md](docs/10-planning/ROADMAP.md) |
| Folder layout | §4 of this file, [ARCHITECTURE.md](docs/03-architecture/ARCHITECTURE.md), the tree in [docs/README.md](docs/README.md) |

**2. Keep the root `README.md` true.** It's the front page. Check that these still match reality: the feature list, tech stack table (names and versions), repository layout, run commands, quality section (coverage numbers once measured), assumptions and limits, and the live app and video links once they exist. Never describe a feature that doesn't work yet; mark it "planned" or leave it out.

**3. Log it.** Add an entry under `Unreleased` in [docs/10-planning/CHANGELOG.md](docs/10-planning/CHANGELOG.md) (Added / Changed / Fixed / Removed), and tick finished items in [ROADMAP.md](docs/10-planning/ROADMAP.md).

**4. Verify.** Run `make docs-check` (broken links and anchors, markdown lint, API types up to date). It must pass.

**5. Say it.** Your end-of-task summary lists which docs you updated, or states "no doc changes needed" with the reason.

If you find a doc that is already wrong, fix it in the same change, even if your task didn't cause it.

## 10. Things that are easy to get wrong (read twice)

- TomTom `vehicleWeight` is in **kilograms**. The UI takes pounds. Convert once in the provider adapter.
- Open-Meteo `precipitation` includes melted snow. **Rain = `rain` + `showers`**, snow = `snowfall`. Request `wind_speed_unit=mph` and `precipitation_unit=inch`.
- All internal times are **UTC**. Convert to local time only in the UI, per checkpoint (routes cross time zones).
- Boundary values go to the **higher** level (rain 0.25 → High). See RISK_MODEL.md §3.
- Missing forecast is **No data**, never Low.
- The heatmap slider must **not** re-render React or refetch on each tick. It swaps a MapLibre paint expression. See [FRONTEND.md §5](docs/04-frontend/FRONTEND.md#5-map-heatmap-and-the-forecast-slider).
- Never fake progress. Loading steps reflect real backend stages, or show an honest indeterminate state.
