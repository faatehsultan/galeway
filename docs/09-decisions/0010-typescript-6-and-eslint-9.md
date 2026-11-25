# 0010. TypeScript 6 and ESLint 9 instead of the newest majors

- Status: Accepted
- Date: 2026-11-25

## Context

[AGENTS §6](../../AGENTS.md#6-versions-policy) says to pin the latest stable version of everything and to check compatibility first. At scaffold time the latest were TypeScript 7.0.2 and ESLint 10.15.0. The lint stack does not support them yet:

- `typescript-eslint` 8.74.0 declares `typescript >=4.8.4 <6.1.0`.
- `eslint-plugin-jsx-a11y` 6.10.2 declares `eslint ^9` at most.

Our coding standards require strict-type-checked linting and accessibility linting, so neither can be dropped.

## Decision

Fall back one step, as AGENTS §6 prescribes: **TypeScript 6.0.3** and **ESLint 9.39.5** (with `@eslint/js` 9.39.5). Everything else uses the latest stable version.

## Consequences

- Lint and type checks are fully supported and green.
- Revisit when `typescript-eslint` and `eslint-plugin-jsx-a11y` declare support. Dependabot will surface the new versions.
- The README stack table lists the pinned versions.

## Alternatives considered

- TypeScript 7 with `--legacy-peer-deps`: unsupported combination, risks silent rule breakage in the linter.
- Dropping `eslint-plugin-jsx-a11y`: weakens the accessibility gate, which is a stated requirement.
