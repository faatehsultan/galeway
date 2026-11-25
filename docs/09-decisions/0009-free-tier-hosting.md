# 0009. Free-tier hosting: Render + Cloudflare Pages + Upstash

- Status: Accepted
- Date: 2026-11-25

## Context

The app needs public hosting. Constraint: nothing paid and no credit card.

## Decision

- **Frontend**: Cloudflare Pages (static, CDN, headers, previews).
- **API**: Render free web service running our Docker image.
- **Redis**: Upstash free tier.

## Consequences

- $0, no card.
- Render free services sleep after 15 minutes idle and take about a minute to wake. Mitigated by a keep-warm GitHub Action during review, pre-warming from the frontend, and a calm cold-start banner ([DEPLOYMENT §1](../08-operations/DEPLOYMENT.md#1-known-free-tier-limits-and-how-we-handle-them)).
- One small instance (0.1 CPU, 512 MB): fine with async I/O and caching.
- The same Docker image runs locally and in production; moving to a paid always-on instance later is a dashboard change.

## Alternatives considered

- **Koyeb free**: faster wake-up, but asks for a credit card.
- **Fly.io**: no free allowance for new accounts at the time of writing.
- **Vercel for the API**: Python serverless works, but long SSE streams and the Django ASGI app fit a container better.
