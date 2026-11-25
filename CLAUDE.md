# CLAUDE.md

@AGENTS.md

## Notes specific to Claude Code

- `AGENTS.md` (imported above) is the single source of truth for rules. Don't duplicate rules here.
- Work one phase of [docs/10-planning/ROADMAP.md](docs/10-planning/ROADMAP.md) at a time. Start each phase in plan mode, then implement.
- Before a UI task, open the matching PNGs in `docs/06-design/mockups/light/` and `docs/06-design/mockups/dark/` and build to them.
- Before a logic task, re-read [docs/02-domain/RISK_MODEL.md](docs/02-domain/RISK_MODEL.md). Its test table is the minimum test set.
- **After every task (not just every phase), do the docs sync in AGENTS.md §9**: update the affected docs and `README.md`, add a CHANGELOG entry, tick ROADMAP boxes, and run `make docs-check`. Then run `make check`, and summarize what changed, which docs you updated, what was assumed and what is left.
- A Stop hook (set up in Phase 0, see ROADMAP) runs `make docs-check` when you finish. If it fails, fix the docs before stopping.
- When finishing a phase, use a fresh subagent to review the diff against `AGENTS.md` §8 (Definition of done) before committing.
- Never run commands that need real provider keys inside tests. Never print environment variables.
