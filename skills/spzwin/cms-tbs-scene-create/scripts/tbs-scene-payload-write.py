#!/usr/bin/env python3
"""
Write a session-scoped latest-payload.json safely (atomic + json serialization).

Why:
- Orchestrators commonly break JSON by string-concatenating long text fields
  (doctorOnlyContext/coachOnlyContext) containing unescaped quotes.
- This script makes payload persistence deterministic and JSON-safe.

What it does:
- Read an input JSON object (payload) from --input (file path) or stdin ('-')
- Optionally merge payload.scene into {sessionDir}/latest-draft.json.scene as baseline
- Atomically write {sessionDir}/latest-payload.json (or --output-name) using json.dump

Notes:
- This script does NOT run parse/validate/create; it only writes payload json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def _read_json_object(path_text: str) -> dict[str, Any]:
    if path_text == "-":
        data = json.load(sys.stdin)
    else:
        path = Path(path_text).expanduser()
        data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("输入 JSON 须为对象（object/dict）。")
    return data


def _read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(tmp, path)


def _infer_session_dir(path_text: str) -> Path:
    p = Path(path_text).expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    return p


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--session-dir",
        required=True,
        help="会话级状态目录（包含 latest-draft.json；输出写入 latest-payload.json）",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="输入 JSON（payload 对象）文件路径；传 '-' 则从 stdin 读取",
    )
    parser.add_argument(
        "--output-name",
        default="latest-payload.json",
        help='输出文件名（默认 latest-payload.json）；写入到 session-dir 下',
    )
    parser.add_argument(
        "--merge-from-draft",
        action="store_true",
        help="将 payload.scene 作为 patch 合并到 latest-draft.json.scene（草稿真源）后再写入 payload，避免丢字段",
    )
    args = parser.parse_args()

    session_dir = _infer_session_dir(str(args.session_dir))
    if not session_dir.is_dir():
        raise SystemExit(f"session-dir 不存在：{session_dir}")

    payload = _read_json_object(str(args.input))

    if args.merge_from_draft:
        draft_path = session_dir / "latest-draft.json"
        draft = _read_json_if_exists(draft_path)
        draft_scene = draft.get("scene") if isinstance(draft.get("scene"), dict) else {}
        incoming_scene = payload.get("scene") if isinstance(payload.get("scene"), dict) else {}
        payload = dict(payload)
        payload["scene"] = {**draft_scene, **incoming_scene}
        if "draftPath" not in payload:
            payload["draftPath"] = str(draft_path)

    out_path = session_dir / str(args.output_name)
    _write_json_atomic(out_path, payload)
    print(f"OK wrote {out_path}")


if __name__ == "__main__":
    main()

