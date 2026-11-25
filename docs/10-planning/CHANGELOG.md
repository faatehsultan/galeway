# Changelog

All notable changes to Galeway. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/).

Every change adds a line under **Unreleased** in the right group ([AGENTS.md §9](../../AGENTS.md#9-keeping-docs-in-sync-mandatory-after-every-change)). On release, rename **Unreleased** to the version and date.

## [Unreleased]

### Added

- Phase 0 skeleton: monorepo layout, `.gitignore`/`.editorconfig`, `Makefile`, `docker-compose.yml` (Redis), pre-commit config.
- Backend: uv project with pinned dependencies, Django 6.1 + Ninja, settings split (base/dev/prod/test), `GET /api/v1/health`, request-id middleware, JSON logging with secret redaction, non-root Dockerfile, ruff/mypy/pytest/import-linter configured, tests at 96% coverage.
- Frontend: Vite 8 + React 19 + strict TypeScript, Tailwind v4 with the design tokens, shadcn-style `Button`, TanStack Router + Query, self-hosted fonts, no-flash theme (System/Light/Dark), brand icons and manifest, `_headers` with a build-time CSP hash, Vitest + MSW tests, generated API types, 180 KB size budget.
- Docs tooling: `make docs-check` (link/anchor checker, markdownlint, docs-sync check, API-types drift), PR template, CI, CodeQL, keep-warm and Dependabot configs.
- ADR-0010: TypeScript 6 and ESLint 9.

- Project documentation: requirements, product spec, risk model, routing and weather, architecture, API, URL state, caching, security, performance, frontend, SEO, backend, design system with light and dark mockups, engineering standards, operations, decision records, roadmap and walkthrough script.
- Brand assets: logo, mark, favicon, app icons, social share image.

### Changed

- Docs review: past-departure links now get a dedicated "Replan for now" state (`DEPARTURE_PASSED`); `Vary: Accept, Origin` on cacheable responses; safe client-IP parsing for rate limits; SSE heartbeat, no buffering and a 25 s plan deadline; longer first-request timeout for cold starts; version-compatibility fallback rule; CodeQL and Schemathesis added to quality gates.

### Fixed

- Docs: unlabelled code fences, missing blank lines around headings and lists (markdownlint clean).

### Removed
