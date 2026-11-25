# 0002. No user accounts or authentication

- Status: Accepted
- Date: 2026-11-25

## Context

The requirements don't ask for accounts. There's no personal data on the server. Visitors should see value within seconds of opening the link. Authentication would add a signup step, an attack surface (passwords, sessions, CSRF, email) and development time, without helping any core requirement.

## Decision

No accounts. Protect what actually matters: the provider key (server-side only), quotas (rate limits, caching), inputs (strict validation) and the browser (CSP, headers). Saved trips live in the browser ([ADR-0007](0007-saved-trips-in-localstorage.md)). Sharing works through URLs ([ADR-0005](0005-url-as-source-of-truth.md)).

## Consequences

- Zero friction for users.
- Saved trips don't sync across devices. Share links cover the cross-device case.
- If accounts are needed later: add `django-allauth` (or an OIDC provider), a `Trip` model, and move saved trips server-side with a one-time import from `localStorage`. The API stays the same, plus authenticated `/me/trips` endpoints.
