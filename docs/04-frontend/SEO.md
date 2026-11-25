# SEO, social previews and app metadata

Galeway is a single-page app built with Vite (no SSR), so SEO has to be done on purpose. Social crawlers (Slack, WhatsApp, LinkedIn, X) **do not run JavaScript**, so anything they need must be in the static `index.html`. Google does run JavaScript, but it still ranks fast, semantic, well-described pages higher.

**Targets:** Lighthouse SEO = 100, Best Practices ≥ 95, Accessibility ≥ 95 on `/` and `/methodology`.

## 1. What gets indexed

| Path | Indexed? | Why |
|---|---|---|
| `/` | Yes | The product page |
| `/methodology` | Yes | Real content (how risk is scored); good for "truck wind risk rules" style searches |
| `/trip?…`, `/trip/routes/…` | **No** (`noindex, follow`) | Infinite, personal, time-bound combinations. Indexing them would be thin, duplicate content. |
| 404 | No | Served with `noindex` |
| API host | No | `X-Robots-Tag: noindex` on every response |

## 2. Static `index.html` (social crawlers read only this)

```html
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>Galeway: weather-aware truck routing</title>
  <meta name="description" content="Plan the safest truck route through the weather. Three routes, forecast risk at every checkpoint for your ETA and load, and one clear recommendation." />
  <link rel="canonical" href="https://<prod-domain>/" />
  <meta name="robots" content="index, follow, max-image-preview:large" />

  <!-- Open Graph -->
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Galeway" />
  <meta property="og:title" content="Galeway: pick the safest way through the weather" />
  <meta property="og:description" content="Three truck routes, forecast risk at every checkpoint, one clear recommendation." />
  <meta property="og:url" content="https://<prod-domain>/" />
  <meta property="og:image" content="https://<prod-domain>/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Galeway map showing three truck routes with weather risk along each" />
  <meta property="og:locale" content="en_US" />

  <!-- X / Twitter -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Galeway: weather-aware truck routing" />
  <meta name="twitter:description" content="Three truck routes, forecast risk at every checkpoint, one clear recommendation." />
  <meta name="twitter:image" content="https://<prod-domain>/og-image.png" />

  <!-- Icons and PWA metadata -->
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="icon" href="/favicon.ico" sizes="32x32" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <meta name="theme-color" content="#F6F7F9" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#0B0F17" media="(prefers-color-scheme: dark)" />

  <!-- Performance hints -->
  <link rel="preconnect" href="https://<api-host>" crossorigin />
  <link rel="preconnect" href="https://tiles.openfreemap.org" crossorigin />

  <!-- Structured data -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "Galeway",
    "url": "https://<prod-domain>/",
    "description": "Weather-aware truck routing that recommends the safest route based on forecast risk, load weight and travel time.",
    "applicationCategory": "TravelApplication",
    "operatingSystem": "Any (web browser)",
    "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
    "image": "https://<prod-domain>/og-image.png"
  }
  </script>

  <!-- Theme before first paint (no flash) -->
  <script>/* reads localStorage theme or prefers-color-scheme, sets data-theme */</script>
</head>
<body>
  <noscript>Galeway needs JavaScript to plan routes. <a href="/methodology">Read how we score weather risk.</a></noscript>
  <div id="root"></div>
</body>
</html>
```

The font preload link is deferred to Phase 6: Vite emits hashed font file names, so it needs a build step to resolve them. `<prod-domain>` and `<api-host>` come from build-time env (`VITE_SITE_URL`, `VITE_API_BASE_URL`) through Vite's HTML env replacement. Never hardcode them.

The inline theme script needs a CSP hash. Compute it at build and add it to `script-src` in `_headers` (a small Vite plugin, or a build step that writes `_headers`).

## 3. Per-route head (in the app)

Managed in `app/seo.ts` through TanStack Router's head support (`head()` on each route + `<HeadContent />`). Check that it works in the installed version; if not, use a small `useHead` hook that sets `document.title` and upserts the meta/link tags.

| Route | `<title>` | robots | canonical |
|---|---|---|---|
| `/` | Galeway: weather-aware truck routing | index | `/` |
| `/methodology` | How Galeway scores weather risk · Galeway | index | `/methodology` |
| `/trip` | Dallas, TX → Denver, CO · Galeway | **noindex, follow** | `/` |
| `/trip/routes/:id` | Route A, US-287 via Amarillo · Dallas → Denver · Galeway | noindex, follow | `/` |
| 404 | Page not found · Galeway | noindex | none |

Titles are ≤ 60 characters where possible; descriptions 120–160 characters.

## 4. Prerendering the indexable pages

To make `/` and `/methodology` complete HTML without SSR, prerender them at build (`vite-plugin-prerender`-style step or a tiny Playwright script in CI that loads the built pages and writes `dist/index.html` and `dist/methodology/index.html`). The SPA hydrates on top. Trip pages are not prerendered.

`/methodology` must be real semantic content: `<h1>`, the rule tables as `<table>` with `<caption>`, short explanatory paragraphs, and the ranking list. The modal and the page share the `RiskRules` component.

## 5. Shared trip previews (optional, Phase 6 stretch)

Links like `/trip?from=Dallas…` show the generic preview by default. Optional improvement, still free: a **Cloudflare Pages Function** on `/trip` rewrites only the `og:title`/`og:description` in `index.html` to "Dallas, TX → Denver, CO · Galeway" (parsed from the query string, escaped) and passes everything else through. No forecast data is fetched, so it stays instant. Skip it if time is short (Parking lot in [ROADMAP](../10-planning/ROADMAP.md)).

## 6. Files in `frontend/public/`

| File | Source |
|---|---|
| `favicon.svg` | [brand/favicon.svg](../06-design/brand/favicon.svg) |
| `favicon.ico` (32×32) | generated once from `icon-192.png` with `sips` and committed |
| `apple-touch-icon.png` (180×180) | [brand/apple-touch-icon.png](../06-design/brand/apple-touch-icon.png) |
| `icon-192.png`, `icon-512.png`, `icon-maskable-512.png` | [brand/](../06-design/brand/) |
| `og-image.png` (1200×630) | [brand/og-image.png](../06-design/brand/og-image.png). Regenerate from the real app before release. |
| `site.webmanifest` | name "Galeway", short_name "Galeway", `start_url: "/"`, `display: "standalone"`, theme/background `#F6F7F9`, the icons above |
| `robots.txt` | `User-agent: *` · `Allow: /` · `Disallow: /trip` · `Sitemap: https://<prod-domain>/sitemap.xml` |
| `sitemap.xml` | `/` and `/methodology` with `lastmod` from the build date |
| `_headers`, `_redirects` | security/cache headers ([SECURITY §3](../03-architecture/SECURITY.md#3-frontend-controls)); SPA fallback `/* /index.html 200` |

## 7. Semantic HTML and performance (ranking signals)

- One `<h1>` per page; headings in order; `<main>`, `<nav>`, `<aside>`, `<header>` landmarks; descriptive link text.
- `lang="en"`; every image has `alt`; decorative SVGs `aria-hidden`.
- Core Web Vitals budgets in [PERFORMANCE](../03-architecture/PERFORMANCE.md) are SEO budgets too.

## 8. Checks in CI

- Lighthouse CI on the preview build for `/` and `/methodology` (SEO 100, others ≥ 95).
- A test that fetches built `dist/index.html` and asserts the OG/Twitter tags, canonical, JSON-LD (valid JSON) and `theme-color` are present.
- A test that `/trip` sets `noindex`.
