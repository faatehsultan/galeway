# Local development

## 1. Prerequisites

| Tool | Version | Install |
|---|---|---|
| Docker + Compose | recent | Docker Desktop / Engine |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Python | 3.13 (uv installs it) | `uv python install 3.13` |
| Node.js | Active LTS | nvm / fnm; version pinned in `frontend/.nvmrc` |
| pnpm | latest | `npm install -g pnpm` (Node 25+ no longer bundles corepack); the version is pinned in `frontend/package.json` |
| gitleaks | latest (optional locally) | `brew install gitleaks`. Without it `make audit` skips the local secret scan; the pre-commit hook and CI still scan |
| TomTom API key | free, no card; needed from Phase 2 | developer.tomtom.com → create app → copy key |

Open-Meteo and OpenFreeMap need no keys.

## 2. First run

```bash
git clone <repo> galeway && cd galeway
cp backend/.env.example backend/.env      # set TOMTOM_API_KEY (and SECRET_KEY for prod-like runs)
cp frontend/.env.example frontend/.env    # VITE_API_BASE_URL=http://localhost:8000
make setup                                # uv sync, pnpm install, pre-commit install
docker compose up -d redis                # optional: without it the API uses an in-memory cache
make dev                                  # API :8000 (reload) + web :5173
```

Open <http://localhost:5173>.

## 3. Environment variables

**backend/.env** (see [BACKEND §3](../05-backend/BACKEND.md#3-settings-environment) for all of them)

```text
DJANGO_SETTINGS_MODULE=config.settings.dev
SECRET_KEY=dev-only-not-secret
TOMTOM_API_KEY=
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:5173
LOG_LEVEL=DEBUG
```

**frontend/.env**

```text
VITE_API_BASE_URL=http://localhost:8000
VITE_SITE_URL=http://localhost:5173
```

`.env` files are git-ignored. The `.env.example` files list every variable without values.

## 4. Makefile targets

| Target | What it runs |
|---|---|
| `setup` | `uv sync` (backend), `pnpm install --frozen-lockfile` (frontend), `pre-commit install` (pre-commit and commit-msg hooks; the first run builds the gitleaks hook and needs network) |
| `dev` | `uv run uvicorn config.asgi:application --reload --port 8000` and `pnpm dev` in parallel |
| `api` / `web` | one side only |
| `test` | `uv run pytest --cov` and `pnpm test --coverage` |
| `e2e` | `pnpm build && pnpm exec playwright test` (placeholder until Phase 6) |
| `lint` / `format` | ruff + ESLint / ruff format + Prettier |
| `typecheck` | `uv run mypy .` and `pnpm tsc --noEmit` |
| `api-types` | export `backend/openapi.json` (git-ignored) with `manage.py export_openapi_schema` → `openapi-typescript` → `frontend/src/lib/api/schema.d.ts` |
| `api-types-check` | same export, then fails if the committed `schema.d.ts` differs |
| `audit` | `pip-audit`, `pnpm audit --prod`, `gitleaks detect` |
| `docs-check` | link + anchor check over every `.md`, markdownlint, api-types drift, docs-sync check against `main` |
| `check` | lint + typecheck + test + docs-check + audit (same as CI minus e2e/lighthouse) |
| `docker-build` | build the backend image locally |

## 5. Dev tips

- **Without a TomTom key:** set `PROVIDERS_MODE=fixtures` in `backend/.env` to serve recorded fixtures (Dallas → Denver and the other scenarios). Useful for UI work and offline.
- **Trigger states:** in dev only, `?debug_state=partial|no_travel|weather_down|rate_limited|cold_start` makes the API (fixtures mode) return that scenario, so every designed state can be seen.
- **API docs:** <http://localhost:8000/api/v1/docs> (dev only).
