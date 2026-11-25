# Galeway documentation

Everything except the three root files lives here. Folders are numbered in reading order.

```text
docs/
├── README.md                         ← you are here
├── 01-product/
│   ├── REQUIREMENTS.md               core requirements and priorities
│   └── PRODUCT_SPEC.md               features, scope, acceptance criteria, non-goals
├── 02-domain/
│   ├── RISK_MODEL.md                 risk rules, load rules, ranking, every edge case
│   └── ROUTING_AND_WEATHER.md        providers, sampling, ETAs, forecast lookup, heatmap grid
├── 03-architecture/
│   ├── ARCHITECTURE.md               system overview, data flow, failure modes
│   ├── API.md                        HTTP contract, errors, pagination, rate limits
│   ├── URL_STATE.md                  share links: every URL param and how history works
│   ├── CACHING.md                    browser, HTTP, Redis and request-merging layers
│   ├── SECURITY.md                   threat model and controls
│   └── PERFORMANCE.md                budgets and how we hit them
├── 04-frontend/
│   ├── FRONTEND.md                   app structure, state, map, slider, saved trips, toasts
│   └── SEO.md                        meta, social previews, structured data, indexing rules
├── 05-backend/
│   └── BACKEND.md                    Django/Ninja layout, services, providers, settings
├── 06-design/
│   ├── DESIGN.md                     design system: tokens, type, components, motion, screens
│   ├── brand/                        logo, mark, favicon, app icons, social image
│   └── mockups/
│       ├── light/                    9 screens, light theme (default)
│       └── dark/                     9 screens, dark theme
├── 07-engineering/
│   ├── CODING_STANDARDS.md           Python and TypeScript conventions
│   ├── TESTING.md                    test strategy, required cases, coverage
│   └── QUALITY_GATES.md              CI pipeline and definition of done
├── 08-operations/
│   ├── LOCAL_DEVELOPMENT.md          setup, env vars, Makefile
│   └── DEPLOYMENT.md                 free-tier hosting, step by step
├── 09-decisions/
│   ├── README.md                     ADR index
│   └── 0001 … 0010                  one file per decision
└── 10-planning/
    ├── ROADMAP.md                    phases, time budget, acceptance checklists, parking lot
    ├── CHANGELOG.md                  every notable change (Keep a Changelog)
    └── WALKTHROUGH_SCRIPT.md         outline for the 5–10 min product walkthrough video
```

## Where to start

| You want to… | Read |
|---|---|
| Understand the product | [REQUIREMENTS](01-product/REQUIREMENTS.md) → [PRODUCT_SPEC](01-product/PRODUCT_SPEC.md) |
| Implement the logic | [RISK_MODEL](02-domain/RISK_MODEL.md) → [ROUTING_AND_WEATHER](02-domain/ROUTING_AND_WEATHER.md) → [BACKEND](05-backend/BACKEND.md) |
| Build the UI | [DESIGN](06-design/DESIGN.md) → [FRONTEND](04-frontend/FRONTEND.md) → [URL_STATE](03-architecture/URL_STATE.md) → [SEO](04-frontend/SEO.md) |
| Call the API | [API](03-architecture/API.md) |
| Ship it | [QUALITY_GATES](07-engineering/QUALITY_GATES.md) → [DEPLOYMENT](08-operations/DEPLOYMENT.md) |
| Know why something is the way it is | [Decisions](09-decisions/README.md) |
| Know what to do next | [ROADMAP](10-planning/ROADMAP.md) |
| See what changed | [CHANGELOG](10-planning/CHANGELOG.md) |

## Conventions for these docs

- File names are `UPPER_SNAKE_CASE.md`; ADRs are `NNNN-kebab-title.md`.
- Links are relative, so they work on GitHub and in editors.
- Units are imperial in the product (mph, in/hr, mi, lb) and SI inside provider adapters only.
- If a doc and the code disagree, the doc is wrong *or* the code is wrong. Fix one of them in the same change.
- **Docs are updated with every change**, not at the end. The rules, the change-to-doc map and the checks are in [AGENTS.md §9](../AGENTS.md#9-keeping-docs-in-sync-mandatory-after-every-change).
