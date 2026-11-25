# Security

No accounts, no database, no personal data on the server. The real risks for this app are **leaking the provider key**, **abuse that burns free quotas**, **injection through inputs** and **cross-site attacks on the frontend**. Controls below are mapped to those.

## 1. Threat model (short)

| Asset | Threat | Control |
|---|---|---|
| TomTom API key | Leaked from client, logs, git, fixtures | Server-side only; redaction filter; `gitleaks` in CI; fixtures scrubbed |
| Free quotas (TomTom, Upstash, Open-Meteo) | Scripted abuse, scraping, cache-busting | Per-IP rate limits; input normalization so cache keys can't be varied; bounds on every numeric input |
| API availability | Large/slow requests, upstream hangs | Strict param limits; httpx timeouts; retry caps; circuit breaker |
| Users' browsers | XSS via place labels or URL params | React escaping; no `dangerouslySetInnerHTML`; strict CSP; labels length-limited and sanitized server-side |
| Saved trips | Tampered or corrupt `localStorage` | zod validation on read; bad entries dropped with a toast; no executable content stored |

## 2. Backend controls

- **Validation**: Pydantic schemas with ranges, enums, max lengths (`label ≤ 120 chars`, `q ≤ 100`), US bounding box. Unknown query params are ignored, never passed through.
- **Outbound HTTP** (`providers/http.py`): one shared `httpx.AsyncClient`, connect timeout 3 s, read timeout 10 s, 2 retries on 5xx/network errors with full-jitter backoff, no retry on 4xx, circuit breaker (open for 30 s after 5 consecutive failures).
- **Secrets**: from environment only (`django-environ`). `.env` is git-ignored; `.env.example` lists names only.
- **Logging**: structured JSON. A filter removes `key=` query values and `Authorization` headers before anything is written. No request bodies are logged.
- **Django settings (prod)**: `DEBUG=False`, explicit `ALLOWED_HOSTS`, `SECURE_PROXY_SSL_HEADER` for the host's proxy, `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS=31536000` (+ subdomains, preload), `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS="DENY"`, `SECURE_REFERRER_POLICY="strict-origin-when-cross-origin"`. Unused apps removed: admin, auth, sessions, messages, contenttypes.
- **CORS** (`django-cors-headers`): allow only the frontend origin(s) from env, `GET` only, no credentials.
- **No CSRF surface**: GET-only API, no cookies.
- **Rate limiting**: see [API §6](API.md#6-rate-limits). Client IP is read only from the trusted proxy header for the host.
- **Errors**: problem+json with a request id; stack traces only in logs.
- **Container**: slim base image, non-root user, no build tools in the final stage, read-only app directory, `HEALTHCHECK`.

## 3. Frontend controls

Cloudflare Pages `_headers`:

```text
/*
  Content-Security-Policy: default-src 'self'; script-src 'self' 'sha256-<theme-script-hash>'; style-src 'self'; img-src 'self' data: blob: https://tiles.openfreemap.org; font-src 'self'; connect-src 'self' https://<api-host> https://tiles.openfreemap.org; worker-src 'self' blob:; child-src blob:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()
  Cross-Origin-Opener-Policy: same-origin
```

- `public/_headers` is a template. `build/pagesHeaders.ts` fills in `<api-host>` (from `VITE_API_BASE_URL`) and the sha256 of the inline theme script in `index.html` when `vite build` runs, and writes `dist/_headers`. The build fails if the inline script is missing.
- Fonts are **self-hosted** (Fontsource), so no Google Fonts requests and no third-party origins in the CSP.
- If a UI library injects `<style>` tags at runtime (some toast and animation libraries do), use its plain-CSS build instead. If that's impossible, allow `'unsafe-inline'` for **`style-src` only** (never `script-src`) and note why in this doc.
- MapLibre needs `worker-src blob:`. Check the CSP in the Playwright run (fail on any CSP violation in the console).
- No analytics or third-party scripts.
- `localStorage` holds only saved trips (public trip params) and the theme choice.

## 4. Supply chain and CI

- Lockfiles committed; exact versions pinned.
- CI runs `pip-audit` and `pnpm audit --prod` (fail on high/critical), `gitleaks`, and GitHub Dependabot for both ecosystems.
- GitHub Actions pinned to commit SHAs; `permissions: contents: read` by default.

## 5. Reporting

The README points to the repository's "Report a vulnerability" (GitHub private advisories).
