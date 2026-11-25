#!/usr/bin/env python3
"""Fail when code changed in a mapped area but its docs did not.

Gate: QUALITY_GATES.md "Docs: sync" and "Docs: changelog". Standard library only.

Which files count as changed:
  * working tree vs HEAD (staged, unstaged and untracked), always;
  * plus everything since the merge-base with $BASE_REF (e.g. origin/main) when it is set (CI).
Set NO_DOCS_NEEDED=1 (CI maps this from the `no-docs-needed` PR label) to skip with a notice.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

# (code path regex, doc path regex, what to update). Mirrors QUALITY_GATES.md and AGENTS.md §9.
MAPPING: list[tuple[str, str, str]] = [
    (r"^backend/galeway/planning/domain/", r"^docs/02-domain/", "docs/02-domain/*"),
    (
        r"^backend/galeway/providers/",
        r"^docs/02-domain/ROUTING_AND_WEATHER\.md$|^docs/03-architecture/CACHING\.md$",
        "ROUTING_AND_WEATHER.md or CACHING.md",
    ),
    (r"^backend/galeway/api/", r"^docs/03-architecture/API\.md$", "docs/03-architecture/API.md"),
    (
        r"^backend/config/settings/|(^|/)\.env\.example$",
        r"^docs/05-backend/BACKEND\.md$|^docs/08-operations/",
        "BACKEND.md or docs/08-operations/*",
    ),
    (
        r"^frontend/src/lib/url-state/|^frontend/src/routes/",
        r"^docs/03-architecture/URL_STATE\.md$",
        "docs/03-architecture/URL_STATE.md",
    ),
    (
        r"^frontend/src/features/|^frontend/src/styles/",
        r"^docs/04-frontend/|^docs/06-design/",
        "docs/04-frontend/* or docs/06-design/*",
    ),
    (
        r"^frontend/public/|^frontend/index\.html$",
        r"^docs/04-frontend/SEO\.md$|^docs/03-architecture/SECURITY\.md$",
        "SEO.md or SECURITY.md",
    ),
    (
        r"^Makefile$|^docker-compose\.yml$|^\.github/workflows/",
        r"^docs/08-operations/|^docs/07-engineering/QUALITY_GATES\.md$",
        "docs/08-operations/* or QUALITY_GATES.md",
    ),
    (
        r"(^|/)package\.json$|(^|/)pyproject\.toml$",
        r"^README\.md$|^docs/07-engineering/|^docs/09-decisions/",
        "README.md, docs/07-engineering/* or an ADR",
    ),
]

CHANGELOG = "docs/10-planning/CHANGELOG.md"
# Code that needs a changelog line: anything under backend/ or frontend/ except tests and lockfiles.
CODE = re.compile(r"^(backend|frontend)/")
NOT_USER_FACING = re.compile(r"(^|/)tests?/|\.test\.|(^|/)(uv\.lock|pnpm-lock\.yaml)$")


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    return result.stdout if result.returncode == 0 else ""


def changed_files() -> set[str]:
    files = set(git("ls-files", "--others", "--exclude-standard").splitlines())
    if git("rev-parse", "--verify", "-q", "HEAD"):
        files |= set(git("diff", "--name-only", "HEAD").splitlines())
    else:  # no commit yet: everything tracked is new
        files |= set(git("ls-files", "--cached").splitlines())
    base = os.environ.get("BASE_REF")
    if base:
        merge_base = git("merge-base", "HEAD", base).strip()
        if merge_base:
            files |= set(git("diff", "--name-only", merge_base, "HEAD").splitlines())
    return {f for f in files if f}


def main() -> int:
    if os.environ.get("NO_DOCS_NEEDED") == "1":
        print("Docs sync skipped: NO_DOCS_NEEDED=1 (the PR carries the `no-docs-needed` label).")
        return 0

    changed = changed_files()
    problems: list[str] = []

    for code_re, doc_re, hint in MAPPING:
        code = sorted(f for f in changed if re.search(code_re, f))
        if code and not any(re.search(doc_re, f) for f in changed):
            problems.append(f"{', '.join(code[:3])}{' …' if len(code) > 3 else ''} changed -> update {hint}")

    user_facing = [f for f in changed if CODE.match(f) and not NOT_USER_FACING.search(f)]
    if user_facing and CHANGELOG not in changed:
        problems.append(f"code changed ({user_facing[0]} …) -> add a line under Unreleased in {CHANGELOG}")

    if problems:
        print("Docs are out of sync with code (AGENTS.md §9):")
        print("\n".join(f"  - {p}" for p in problems))
        return 1
    print(f"Docs sync OK ({len(changed)} changed file(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
