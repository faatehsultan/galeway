#!/usr/bin/env python3
"""Fail on broken relative links and heading anchors in every Markdown file.

Gate: QUALITY_GATES.md "Docs: links". Standard library only.
External (http/https/mailto) links are not fetched.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "node_modules", ".venv", "dist", "coverage", "htmlcov", ".remember", ".claude"}

FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
MD_LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_REF = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""")
HTML_ANCHOR = re.compile(r"""<a\s[^>]*(?:id|name)\s*=\s*["']([^"']+)["']""")
INLINE_CODE = re.compile(r"`[^`]*`")


def markdown_files() -> list[Path]:
    return sorted(p for p in ROOT.rglob("*.md") if not SKIP_DIRS & set(p.relative_to(ROOT).parts))


def prose_lines(text: str) -> list[tuple[int, str]]:
    """Lines outside fenced code blocks, with their line numbers."""
    out: list[tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((number, line))
    return out


def slugify(heading: str) -> str:
    """GitHub's anchor rule: lowercase, drop punctuation, spaces to hyphens."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # links keep their text
    text = text.replace("`", "")
    text = re.sub(r"[*~]", "", text)
    text = text.lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors_of(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    if path not in cache:
        found: set[str] = set()
        seen: dict[str, int] = {}
        for _, line in prose_lines(path.read_text(encoding="utf-8")):
            heading = HEADING.match(line)
            if heading:
                slug = slugify(heading.group(2))
                count = seen.get(slug, 0)
                seen[slug] = count + 1
                found.add(slug if count == 0 else f"{slug}-{count}")
            found.update(HTML_ANCHOR.findall(line))
        cache[path] = found
    return cache[path]


def references(path: Path) -> list[tuple[int, str]]:
    refs: list[tuple[int, str]] = []
    for number, line in prose_lines(path.read_text(encoding="utf-8")):
        text = INLINE_CODE.sub("", line)  # links inside code spans are examples, not links
        refs.extend((number, target) for target in MD_LINK.findall(text))
        refs.extend((number, target) for target in HTML_REF.findall(text))
    return refs


def main() -> int:
    cache: dict[Path, set[str]] = {}
    errors: list[str] = []
    files = markdown_files()

    for path in files:
        rel = path.relative_to(ROOT)
        for line, target in references(path):
            if re.match(r"^(https?:|mailto:|tel:|data:)", target) or target == "#":
                continue
            raw_path, _, fragment = target.partition("#")
            dest = path if raw_path == "" else (path.parent / unquote(raw_path)).resolve()
            if not dest.exists():
                errors.append(f"{rel}:{line}: broken link -> {target}")
            elif fragment and dest.suffix == ".md" and dest.is_file():
                if unquote(fragment).lower() not in anchors_of(dest, cache):
                    errors.append(f"{rel}:{line}: missing anchor -> {target}")

    if errors:
        print("\n".join(errors))
        print(f"\n{len(errors)} broken link(s) or anchor(s) in {len(files)} Markdown files.")
        return 1
    print(f"Docs links OK ({len(files)} Markdown files).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
