#!/usr/bin/env bash
##
# Creates a GitHub repo (REST) under **your personal account** and pushes `main`.
# Requires a PAT with **`repo`** (classic) or fine‑grained equivalent.
#
# Usage:
#   export GITHUB_OWNER="your-github-username"
#   export GITHUB_TOKEN="ghp_******"
#   export GITHUB_REPO="IronClaw-Macro-Agent"   # optional
#   bash scripts/publish_to_github.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

OWNER="${GITHUB_OWNER:-}"
TOKEN="${GITHUB_TOKEN:-}"
REPO="${GITHUB_REPO:-IronClaw-Macro-Agent}"

if [[ -z "${OWNER}" || -z "${TOKEN}" ]]; then
  echo "Set GITHUB_OWNER and GITHUB_TOKEN." >&2
  exit 1
fi

export GH_OWNER="${OWNER}"
export GH_REPO="${REPO}"
export GH_TOKEN="${TOKEN}"

python3 "${ROOT}/scripts/_github_publish.py"
