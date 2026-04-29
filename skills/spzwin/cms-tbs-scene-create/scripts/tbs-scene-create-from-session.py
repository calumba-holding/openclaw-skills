#!/usr/bin/env python3
"""
Create a TBS scene using a session state directory as the single source of truth.

Why:
- In real usage there are multiple JSON artifacts (payload/parse/validate/draft).
- The most common field-missing errors happen when the orchestrator calls
  `tbs-scene-create.py` with the wrong --params-file or without required top-level
  confirmation/display binding fields.

This wrapper makes creation deterministic:
- Read {sessionDir}/latest-draft.json for the canonical scene + meta.
- Read {sessionDir}/latest-validate-result.json for validationReport (displayHash/sceneHash).
- Write {sessionDir}/create-payload.json with all required top-level fields.
- Invoke `tbs-scene-create.py` with that payload.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:  # noqa: PERF203
        raise RuntimeError(f"无法读取文件：{path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"JSON 解析失败：{path}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON 须为对象：{path}")
    return data


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _require_confirmation(value: str) -> str:
    v = (value or "").strip()
    if v not in {"确认", "取消"}:
        raise RuntimeError("userConfirmation 必须为：确认 / 取消")
    return v


def _infer_session_dir(path_text: str) -> Path:
    p = Path(path_text).expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    return p


def _load_scene_hash_helpers() -> tuple[Callable[..., str], frozenset[str]]:
    """Reuse hashing rules from tbs-scene-create.py (same SCENE_HASH_FIELDS)."""
    path = Path(__file__).with_name("tbs-scene-create.py")
    spec = importlib.util.spec_from_file_location("_tbs_scene_create_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载：{path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    compute = getattr(mod, "compute_scene_hash")
    fields = getattr(mod, "SCENE_HASH_FIELDS")
    if not callable(compute) or not isinstance(fields, list):
        raise RuntimeError("tbs-scene-create.py 缺少 compute_scene_hash / SCENE_HASH_FIELDS")
    return compute, frozenset(str(x) for x in fields)


def _resolve_scene_for_create(
    draft_scene: dict[str, Any],
    validate_doc: dict[str, Any],
    validation_report: dict[str, Any],
    *,
    compute_scene_hash: Callable[..., str],
    hash_fields: frozenset[str],
) -> tuple[dict[str, Any], str]:
    """
    Prefer draft.scene when its hash matches validationReport.

    When the orchestrator overwrote latest-draft.json after validate (e.g. parse round-trip
    dropping normalized sceneBackground), recover using validate output's `scene` — the exact
    snapshot that produced sceneHash — then overlay draft-only fields that do not participate
    in SCENE_HASH_FIELDS (e.g. drugId).
    """
    expected = str(validation_report.get("sceneHash") or "").strip()
    if not expected:
        raise SystemExit(
            "latest-validate-result.json 缺少 validationReport.sceneHash，请重新执行 tbs-scene-validate.py。"
        )

    if compute_scene_hash(draft_scene) == expected:
        return draft_scene, ""

    validated = validate_doc.get("scene")
    if isinstance(validated, dict) and compute_scene_hash(validated) == expected:
        # Validate-after-knowledge-check without re-validate: draft may carry new knowledgeIds while
        # latest-validate-result.json still reflects an older sceneHash — do not silently drop IDs.
        v_ids = validated.get("knowledgeIds")
        d_ids = draft_scene.get("knowledgeIds")
        if v_ids != d_ids and isinstance(d_ids, list) and len(d_ids) > 0:
            raise SystemExit(
                "latest-draft.json 的 knowledgeIds 与最近一次 FULL 校验快照不一致。"
                "若刚执行过 tbs-scene-knowledge-check.py，请先对当前 latest-draft.json 再执行一次 "
                "tbs-scene-validate.py（FULL），再创建。"
            )

        merged: dict[str, Any] = dict(validated)
        for key, value in draft_scene.items():
            if key not in hash_fields:
                merged[key] = value
        if compute_scene_hash(merged) != expected:
            raise SystemExit(
                "草稿中的 scene 与校验快照无法安全合并：参与哈希的字段在 validate 之后发生变化"
                "（例如 knowledgeIds）。请重新执行 tbs-scene-validate.py（FULL）后再创建。"
            )
        return merged, (
            "注意：已用 latest-validate-result.json 中的 scene 对齐 sceneHash，并合并草稿里非哈希字段；"
            "建议避免在 FULL validate 之后再次运行 parse 覆盖 latest-draft.json。"
        )

    raise SystemExit(
        "validation_scene_hash_mismatch：latest-draft.json 与 validationReport 不一致，且无法在"
        " latest-validate-result.json 中找到匹配的 scene 快照。请重新执行 tbs-scene-validate.py（FULL）。"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--session-dir",
        required=True,
        help="会话级状态目录（包含 latest-draft.json / latest-validate-result.json）",
    )
    parser.add_argument(
        "--user-confirmation",
        required=True,
        help='必须为 "确认" 或 "取消"（来自用户最终确认）',
    )
    parser.add_argument(
        "--access-token",
        required=False,
        help="TBS Admin access-token（由 cms-auth-skills 注入；不要传占位符）",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="可选：TBS Admin base url（默认沿用 tbs-scene-create.py 内置/环境变量）",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="可选：写入 create-result.json 的路径（默认写到 session-dir/latest-create-result.json）",
    )
    parser.add_argument(
        "--only-write-payload",
        action="store_true",
        help="仅生成 {sessionDir}/create-payload.json，不调用 tbs-scene-create.py 落库（用于展示/审计/确认前快照）",
    )
    args = parser.parse_args()

    session_dir = _infer_session_dir(args.session_dir)
    user_confirmation = _require_confirmation(str(args.user_confirmation))

    draft_path = session_dir / "latest-draft.json"
    validate_path = session_dir / "latest-validate-result.json"
    if not draft_path.is_file():
        raise SystemExit(f"缺少 latest-draft.json：{draft_path}")
    if not validate_path.is_file():
        raise SystemExit(f"缺少 latest-validate-result.json：{validate_path}")

    draft = _read_json(draft_path)
    draft_scene = draft.get("scene") if isinstance(draft.get("scene"), dict) else {}
    meta = draft.get("meta") if isinstance(draft.get("meta"), dict) else {}
    if not draft_scene:
        raise SystemExit("latest-draft.json 缺少 scene 或 scene 为空，无法创建。")

    validate = _read_json(validate_path)
    validation_report = validate.get("validationReport") if isinstance(validate.get("validationReport"), dict) else {}
    display_hash = str(validation_report.get("displayHash") or "").strip()
    if not display_hash:
        raise SystemExit("latest-validate-result.json 缺少 validationReport.displayHash，无法绑定最终确认。")

    compute_scene_hash, hash_fields = _load_scene_hash_helpers()
    scene, recovery_note = _resolve_scene_for_create(
        draft_scene,
        validate,
        validation_report,
        compute_scene_hash=compute_scene_hash,
        hash_fields=hash_fields,
    )
    if recovery_note:
        print(recovery_note, file=sys.stderr)

    # Create payload for tbs-scene-create.py
    create_payload_path = session_dir / "create-payload.json"
    output_path = Path(args.output).expanduser() if args.output else (session_dir / "latest-create-result.json")
    payload: dict[str, Any] = {
        "userConfirmation": user_confirmation,
        "scene": scene,
        "validationReport": validation_report,
        "confirmedDisplayHash": display_hash,
        "displayContractSatisfied": True,
        "draftPath": str(draft_path),
        # keep meta for traceability (create script will merge with draft meta)
        "meta": meta,
    }
    _write_json(create_payload_path, payload)

    if args.only_write_payload:
        print(f"OK wrote create-payload.json {create_payload_path}")
        raise SystemExit(0)

    script_path = Path(__file__).with_name("tbs-scene-create.py")
    if not script_path.is_file():
        raise SystemExit(f"找不到脚本：{script_path}")

    access_token = str(args.access_token or "").strip()
    if not access_token:
        raise SystemExit("缺少 --access-token：落库时必须提供真实 access-token（确认前仅生成 payload 可加 --only-write-payload）。")

    cmd = [
        sys.executable,
        str(script_path),
        "--params-file",
        str(create_payload_path),
        "--access-token",
        access_token,
        "--output",
        str(output_path),
    ]
    if args.base_url:
        cmd.extend(["--base-url", str(args.base_url)])

    proc = subprocess.run(cmd, cwd=str(script_path.parent), capture_output=True, text=True)
    # Forward one-line summary to stdout/stderr, keep result JSON on disk
    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()

