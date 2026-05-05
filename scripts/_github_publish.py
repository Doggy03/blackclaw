"""Create GitHub repository (if missing) and push current ``main`` branch."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def _request_json(*, method: str, url: str, token: str, data: bytes | None = None) -> tuple[int, object]:
    """
    Perform a GitHub REST call and return ``(status, parsed_json_or_text)``.

    Args:
        method: HTTP verb.
        url: Full URL.
        token: Bearer token.
        data: Optional JSON body bytes.

    Returns:
        Status code and parsed JSON (``list``/``dict``) or raw response text.
    """
    req = urllib.request.Request(url, method=method, data=data)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            status = int(resp.status)
            try:
                return status, json.loads(body) if body else {}
            except json.JSONDecodeError:
                return status, body
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode() if exc.fp else ""
        try:
            return int(exc.code), json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return int(exc.code), raw


def main() -> int:
    """
    Entry point: create repo and ``git push`` from repository root.

    Returns:
        Process exit code.
    """
    owner = os.environ.get("GH_OWNER", "").strip()
    repo = os.environ.get("GH_REPO", "IronClaw-Macro-Agent").strip()
    token = os.environ.get("GH_TOKEN", "").strip()
    if not owner or not token:
        print("GH_OWNER / GH_TOKEN missing.", file=sys.stderr)
        return 1

    root = Path(__file__).resolve().parents[1]
    api_repo = f"https://api.github.com/repos/{owner}/{repo}"

    status, payload = _request_json(method="GET", url=api_repo, token=token)
    if status not in {200, 404}:
        print(f"Unexpected probe status {status}: {payload}", file=sys.stderr)
        return 2

    if status == 404:
        create_url = "https://api.github.com/user/repos"
        desc = (
            "Black metals multi-agent research pipeline: Python + optional Chroma + "
            "OpenClaw Gateway."
        )
        body = json.dumps({"name": repo, "description": desc, "private": False}).encode()
        c_status, created = _request_json(method="POST", url=create_url, token=token, data=body)
        if c_status not in {200, 201}:
            print(f"Repo create failed ({c_status}): {created}", file=sys.stderr)
            return 3
        html = created.get("html_url") if isinstance(created, dict) else None
        print(f"Created {html}")
    else:
        print(f"Repo exists: https://github.com/{owner}/{repo}")

    enc_token = urllib.parse.quote(token, safe="")
    remote_with_token = f"https://{owner}:{enc_token}@github.com/{owner}/{repo}.git"
    remote_clean = f"https://github.com/{owner}/{repo}.git"

    subprocess.run(["git", "remote", "remove", "origin"], cwd=root, check=False)
    subprocess.run(["git", "remote", "add", "origin", remote_with_token], cwd=root, check=True)

    env = os.environ.copy()
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=root, check=True, env=env)

    subprocess.run(["git", "remote", "set-url", "origin", remote_clean], cwd=root, check=True)
    print("Push complete; origin URL scrubbed (no PAT embedded).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
