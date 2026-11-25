# Coding standards

The goal: code a senior engineer can read top to bottom without surprises.

## 1. Shared rules

- **Names say what and in which unit**: `distance_mi`, `duration_s`, `load_lb`, `wind_mph`, `departUtc`. No `data`, `info`, `tmp`, `val` for anything that lives longer than three lines.
- **Small units**: functions do one thing; files stay under ~300 lines; components under ~150.
- **Validate at the edges, trust inside.** Parse inputs once (Pydantic / zod) into typed objects; internal code never re-checks raw strings.
- **No magic numbers.** Thresholds live in `domain/risk.py` as named constants, mirrored in RISK_MODEL.md. Limits live in one config module per side.
- **Errors are values with meaning**: typed exceptions (backend) and `ApiProblem` (frontend), never bare strings.
- **Comments explain *why***, not *what*. Each domain function has a docstring that cites the RISK_MODEL section it implements.
- **No dead code, no commented-out code, no `print`/`console.log`.**
- **Conventional Commits**: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `build`, `ci` with a scope (`planning`, `api`, `providers`, `map`, `form`, `saved-trips`, …).

## 2. Python (backend)

| Topic | Rule |
|---|---|
| Format and lint | `ruff format` + `ruff check` with rule sets `E,F,W,I,N,UP,B,A,C4,SIM,PTH,RET,ARG,ERA,PL,RUF,S,ASYNC,DTZ,T20` |
| Types | `mypy --strict`; Pydantic plugin; no `Any` in domain; `# type: ignore[code]` only with a reason |
| Data | `@dataclass(frozen=True, slots=True)` for domain types; Pydantic models only at the API boundary |
| Enums | `Level(IntEnum)` so ordering and `max()` work naturally |
| Time | Timezone-aware `datetime` only (ruff `DTZ`); UTC internally; clock injected |
| Async | All I/O async; no blocking calls inside async code; `asyncio.gather` with a semaphore for fan-out; `asyncio.timeout` around provider calls |
| Imports | `planning.domain` imports only the stdlib and itself (enforced with `import-linter` contracts in CI) |
| Errors | `ApiError` subclasses carry `status`, `code`, `title`; one exception handler renders problem+json |
| Logging | `structlog` with bound context; never f-string secrets; redaction processor always on |

## 3. TypeScript / React (frontend)

| Topic | Rule |
|---|---|
| Compiler | `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride`, `verbatimModuleSyntax` |
| Lint | ESLint flat config: `typescript-eslint` strict-type-checked, `react-hooks`, `jsx-a11y`, `import` order, `@tanstack/query` plugin, no default exports except route files |
| Format | Prettier (with the Tailwind class-sorting plugin) |
| Types | No `any`, no non-null `!` without a comment; API types come from generated `schema.d.ts` only |
| Components | Function components; props typed with `type`; colocate styles; `forwardRef` only where Radix needs it |
| State | URL first, Query second, local state third (see [FRONTEND §2](../04-frontend/FRONTEND.md#2-state)) |
| Effects | `useEffect` only to sync with external systems (map, storage events). Derive everything else during render. |
| Styling | Tailwind utilities that use the tokens; no hex values in components; `cn()` helper for conditionals |
| Accessibility | Semantic elements first; Radix for complex widgets; every icon-only button has `aria-label` |
| Files | `PascalCase.tsx` for components, `camelCase.ts` for modules, `*.test.ts(x)` next to the code |

## 4. Pull requests / phase commits

- One roadmap phase or sub-feature per PR or commit group.
- The description says **what**, **why**, **how it was tested** and any **assumption** made.
- Screenshots (light and dark) for UI changes.
