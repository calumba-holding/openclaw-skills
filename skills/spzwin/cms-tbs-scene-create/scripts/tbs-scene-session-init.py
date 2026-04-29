#!/usr/bin/env python3
"""
Initialize a stable session state directory for cms-tbs-scene-create.

Motivation:
- The state directory should be: workspace/.cms-log/state/cms-tbs-scene-create/{sessionId}/
- Using a literal "$$" as {sessionId} is confusing in shells (it expands to PID) and
  makes it hard to correlate runs.

This script creates a new session directory name like:
  sess-20260428-150501-8f3a

And prints the absolute path. Callers can then write:
  latest-payload.json / latest-draft.json / latest-parse-result.json / ...
into that directory consistently for the whole conversation/run.
"""

from __future__ import annotations

import argparse
import os
import secrets
from datetime import datetime
from pathlib import Path


def _default_root(workspace: Path) -> Path:
    return workspace / ".cms-log" / "state" / "cms-tbs-scene-create"


def _parse_created_at(marker: Path) -> datetime | None:
    try:
        for line in marker.read_text(encoding="utf-8").splitlines():
            if line.startswith("createdAt="):
                return datetime.fromisoformat(line.split("=", 1)[1].strip())
    except (OSError, ValueError):
        return None
    return None


def _is_empty_session(session_dir: Path) -> bool:
    try:
        names = {item.name for item in session_dir.iterdir()}
    except OSError:
        return False
    return names == {"SESSION.txt"}


def _latest_reusable_empty_session(root: Path, prefix: str, within_seconds: int) -> Path | None:
    if within_seconds <= 0 or not root.is_dir():
        return None
    now = datetime.now()
    candidates: list[tuple[datetime, Path]] = []
    for item in root.iterdir():
        if not item.is_dir() or not item.name.startswith(f"{prefix}-"):
            continue
        marker = item / "SESSION.txt"
        if not marker.is_file() or not _is_empty_session(item):
            continue
        created_at = _parse_created_at(marker)
        if created_at is None:
            continue
        age_seconds = (now - created_at).total_seconds()
        if 0 <= age_seconds <= within_seconds:
            candidates.append((created_at, item))
    if not candidates:
        return None
    return max(candidates, key=lambda x: x[0])[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workspace",
        default=str(Path(__file__).resolve().parents[3]),
        help="OpenClaw workspace 根目录（默认从脚本路径推断到 .../workspace）",
    )
    parser.add_argument(
        "--prefix",
        default="sess",
        help='sessionId 前缀（默认 "sess"）',
    )
    parser.add_argument(
        "--reuse-empty-within-seconds",
        type=int,
        default=120,
        help="若最近 N 秒内已有空 session（仅 SESSION.txt），直接复用，防止审批/重试生成多个空目录；0 表示禁用",
    )
    parser.add_argument(
        "--force-new",
        action="store_true",
        help="强制创建新 session，忽略空 session 复用",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser()
    if not workspace.is_absolute():
        workspace = (Path.cwd() / workspace).resolve()

    root = _default_root(workspace)
    root.mkdir(parents=True, exist_ok=True)

    if not args.force_new:
        reusable = _latest_reusable_empty_session(
            root, args.prefix, args.reuse_empty_within_seconds
        )
        if reusable is not None:
            print(str(reusable))
            return

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = secrets.token_hex(2)  # 4 hex chars
    session_id = f"{args.prefix}-{ts}-{suffix}"
    session_dir = root / session_id
    session_dir.mkdir(parents=True, exist_ok=False)

    # Helpful: touch a marker file for humans
    (session_dir / "SESSION.txt").write_text(
        f"sessionId={session_id}\ncreatedAt={datetime.now().isoformat()}\nuser={os.getenv('USER','')}\n",
        encoding="utf-8",
    )

    print(str(session_dir))


if __name__ == "__main__":
    main()

