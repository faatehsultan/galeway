# Deployment (all free tiers, no card)

| Part | Host | Plan | Why |
|---|---|---|---|
| Frontend (static) | Cloudflare Pages | Free | Global CDN, `_headers`/`_redirects`, preview deploys per branch |
| API (Docker) | Render web service | Free | Builds from `backend/Dockerfile`, HTTPS, health checks |
| Cache + rate limits | Upstash Redis | Free (256 MB, 500K commands/month) | Serverless Redis over TLS |
| Routing + places | TomTom | Freemium | Truck routing; quota is blocked, never billed |
| Weather | Open-Meteo | Free (non-commercial use) | No key |
| Tiles | OpenFreeMap | Free | No key |

Decision and trade-offs: [ADR-0009](../09-decisions/0009-free-tier-hosting.md).

## 1. Known free-tier limits and how we handle them

| Limit | Mitigation |
|---|---|
| Render free services **spin down after 15 min idle** and take about a minute to wake | (1) `keep-warm.yml` GitHub Action pings `/api/v1/health` every 10 min while the demo is being shared (one always-on service fits in the 750 free instance hours/month). (2) The frontend pre-warms on load. (3) The "Starting up the server…" banner after 3 s. |
| Render free filesystem is ephemeral | Nothing is stored on disk (no DB, no uploads) |
| Upstash 500K commands/month | Batched `MGET`/pipelines, plan-level caching ([CACHING §3](../03-architecture/CACHING.md#3-server-redis)) |
| TomTom daily/monthly free quota | Caching (routes 15 min, places 30 days), rate limits, 3 routes max per plan |
| Open-Meteo free API has fair-use limits, and a request with many locations may count as several calls | Check the current limits on their site before Phase 2; grid snapping and the 30-min weather cache keep usage low; set an alert in logs when Open-Meteo returns 429 |
| GitHub scheduled workflows can be delayed, and are disabled after 60 days of no repo activity | Fine for a demo period; the pre-warm + banner covers gaps |

## 2. One-time setup

### Upstash Redis

1. Create a free Redis database (region near the Render region).
2. Copy the **TLS** URL (`rediss://…`) → `REDIS_URL` on Render.

### TomTom

1. Create a free account and app, enable Search + Routing, copy the key → `TOMTOM_API_KEY` on Render.

### Render (API)

1. New → Web Service → connect the repo. Root directory `backend`, runtime **Docker**, instance type **Free**.
2. Health check path `/api/v1/health`.
3. Environment: `DJANGO_SETTINGS_MODULE=config.settings.prod`, `SECRET_KEY` (generate), `ALLOWED_HOSTS=<service>.onrender.com`, `CORS_ALLOWED_ORIGINS=https://<project>.pages.dev`, `TOMTOM_API_KEY`, `REDIS_URL`, `TRUSTED_PROXY_HOPS=1`, `LOG_LEVEL=INFO`.
4. Auto-deploy: deploy only after CI passes. Use Render's "after CI checks pass" auto-deploy option if available; otherwise turn auto-deploy off and trigger a **deploy hook** from the CI `deploy` job on `main`.

### Cloudflare Pages (web)

1. Create a project from the repo. Root directory `frontend`, build `pnpm install --frozen-lockfile && pnpm build`, output `dist`.
2. Env: `VITE_API_BASE_URL=https://<service>.onrender.com`, `VITE_SITE_URL=https://<project>.pages.dev`, `NODE_VERSION=<LTS>`.
3. `public/_redirects`: `/* /index.html 200` (SPA). `public/_headers`: security + cache headers ([SECURITY §3](../03-architecture/SECURITY.md#3-frontend-controls), [CACHING §2](../03-architecture/CACHING.md#2-http-cache-control-and-etag)).

### GitHub

- Secrets: `RENDER_DEPLOY_HOOK_URL` (if using the hook), `API_HEALTH_URL` (for keep-warm).
- Enable Dependabot (pip + npm + github-actions) and private vulnerability reporting.

## 3. Backend Dockerfile (shape)

```dockerfile
# build stage: uv sync --frozen --no-dev into /app/.venv
# final stage: python:3.13-slim, copy .venv + app, non-root user "app",
#   ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
#   HEALTHCHECK → /api/v1/health
#   CMD uvicorn config.asgi:application --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips="*"
```

`--forwarded-allow-ips="*"` is acceptable only because Render's proxy is the only route to the container; client IPs are read from the configured header.

## 4. Release checklist

- [ ] CI green on `main`; deploy succeeded on both hosts
- [ ] `/api/v1/health` returns the release git SHA
- [ ] Smoke test in production: plan, slider, share link on another device, save trip, both themes, mobile
- [ ] Lighthouse on production `/` and `/methodology`
- [ ] Regenerate `og-image.png` from the real app; check the preview with a link debugger (Slack/LinkedIn)
- [ ] Keep-warm workflow enabled while the demo link is being shared
- [ ] README: live URL, walkthrough video URL, coverage numbers
