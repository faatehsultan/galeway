# One entry point for common tasks. Docs: docs/08-operations/LOCAL_DEVELOPMENT.md §4
SHELL := /bin/bash
.DEFAULT_GOAL := help

OPENAPI := backend/openapi.json
SCHEMA  := frontend/src/lib/api/schema.d.ts
PY      := uv run --project backend python

.PHONY: help setup dev api web test e2e lint format typecheck api-types api-types-check \
        audit docs-check check docker-build

help: ## List targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-16s %s\n", $$1, $$2}'

setup: ## Install backend + frontend deps and git hooks
	cd backend && uv sync
	cd frontend && pnpm install --frozen-lockfile
	uv run --project backend pre-commit install --install-hooks -t pre-commit -t commit-msg

dev: ## API (:8000, reload) and web (:5173) together
	@trap 'kill 0' INT TERM EXIT; $(MAKE) --no-print-directory api & $(MAKE) --no-print-directory web & wait

api: ## API only
	cd backend && DJANGO_SETTINGS_MODULE=config.settings.dev uv run uvicorn config.asgi:application --reload --port 8000

web: ## Web only
	cd frontend && pnpm dev

test: ## Backend + frontend tests with coverage
	cd backend && uv run pytest --cov
	cd frontend && pnpm exec vitest run --coverage

e2e: ## Playwright + axe (arrives in Phase 6)
	@echo "The Playwright suite is added in Phase 6 (docs/10-planning/ROADMAP.md)."

lint: ## ruff + import-linter + ESLint + Prettier (check only)
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run lint-imports
	cd frontend && pnpm lint

format: ## ruff format + Prettier + autofix
	cd backend && uv run ruff check --fix . && uv run ruff format .
	cd frontend && pnpm format

typecheck: ## mypy (strict) + tsc
	cd backend && uv run mypy
	cd frontend && pnpm typecheck

api-types: ## Export OpenAPI and regenerate frontend/src/lib/api/schema.d.ts
	cd backend && uv run python manage.py export_openapi_schema --api galeway.api.router.api --output openapi.json
	cd frontend && pnpm api-types

api-types-check: ## Fail if schema.d.ts is out of date with the API
	cd backend && uv run python manage.py export_openapi_schema --api galeway.api.router.api --output openapi.json
	cd frontend && pnpm exec openapi-typescript ../$(OPENAPI) -o /tmp/galeway-schema.d.ts >/dev/null
	@diff -q /tmp/galeway-schema.d.ts $(SCHEMA) >/dev/null || { echo "$(SCHEMA) is out of date: run 'make api-types'"; exit 1; }

audit: ## Dependency audits + secret scan
	cd backend && uv run pip-audit
	cd frontend && pnpm audit --prod --audit-level high
	@if command -v gitleaks >/dev/null; then gitleaks detect --redact --no-banner; \
	else echo "gitleaks not installed: skipped here. The pre-commit hook and CI still scan (brew install gitleaks)."; fi

docs-check: ## Links, anchors, markdownlint, docs-sync, api-types drift
	$(PY) .github/scripts/check_docs_links.py
	$(PY) .github/scripts/check_docs_sync.py
	frontend/node_modules/.bin/markdownlint-cli2
	$(MAKE) --no-print-directory api-types-check

check: lint typecheck test docs-check audit ## Everything CI runs (minus e2e/lighthouse)

docker-build: ## Build the backend image
	docker build -t galeway-api backend
