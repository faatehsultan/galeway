#!/usr/bin/env bash
# pre-commit passes repo-root paths; run a frontend tool from frontend/ instead.
# Usage: run_in_frontend.sh <tool> [flags...] -- <files...>
set -euo pipefail

tool="$1"
shift
flags=()
while [[ $# -gt 0 && "$1" != "--" ]]; do
  flags+=("$1")
  shift
done
shift || true # drop the "--"

files=()
for f in "$@"; do
  files+=("${f#frontend/}")
done

cd frontend
exec pnpm exec "$tool" "${flags[@]}" "${files[@]}"
