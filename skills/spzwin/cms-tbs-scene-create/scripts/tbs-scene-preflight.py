#!/usr/bin/env python3
"""
Read-only session preflight for TBS scene creation.

Use this before running parse/validate/create when the orchestrator only needs to
know the next step. This script never writes session files and never calls TBS APIs.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Callable


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _infer_session_dir(path_text: str) -> Path:
    p = Path(path_text).expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    return p


def _load_hash_helpers() -> tuple[Callable[[dict[str, Any]], str], Callable[[dict[str, Any]], str]]:
    path = Path(__file__).with_name("tbs-scene-create.py")
    spec = importlib.util.spec_from_file_location("_tbs_scene_create_hash", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load hash helpers from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    scene_hash = getattr(mod, "compute_scene_hash")
    display_hash = getattr(mod, "compute_display_hash")
    if not callable(scene_hash) or not callable(display_hash):
        raise RuntimeError("Missing hash helpers in tbs-scene-create.py")
    return scene_hash, display_hash


def _fallback_hash(value: dict[str, Any]) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _status(
    *,
    session_dir: Path,
    compute_scene_hash: Callable[[dict[str, Any]], str],
    compute_display_hash: Callable[[dict[str, Any]], str],
) -> dict[str, Any]:
    draft_path = session_dir / "latest-draft.json"
    validate_path = session_dir / "latest-validate-result.json"
    create_path = session_dir / "latest-create-result.json"
    knowledge_path = session_dir / "latest-knowledge-check-result.json"

    if not draft_path.is_file():
        return {
            "status": "NEED_PARSE",
            "nextAction": "先创建会话草稿并执行 tbs-scene-parse.py",
            "canWrite": False,
        }

    draft = _read_json(draft_path)
    scene = draft.get("scene") if isinstance(draft.get("scene"), dict) else {}
    meta = draft.get("meta") if isinstance(draft.get("meta"), dict) else {}
    if not scene:
        return {
            "status": "NEED_PARSE",
            "nextAction": "latest-draft.json 缺少 scene，请重新执行 parse",
            "canWrite": False,
        }

    create_result = _read_json(create_path)
    if create_result.get("success") is True and create_result.get("sceneId"):
        return {
            "status": "ALREADY_CREATED",
            "nextAction": "场景已创建，无需重复落库",
            "sceneId": create_result.get("sceneId"),
            "canWrite": False,
        }

    last_stage = str(meta.get("lastParseStage") or "").strip()
    if last_stage != "READY_FOR_VALIDATE":
        return {
            "status": "NEED_PARSE",
            "nextAction": "继续 parse/内部生成，直到 latest-draft.meta.lastParseStage=READY_FOR_VALIDATE",
            "lastParseStage": last_stage,
            "canWrite": True,
        }

    has_topics = bool(scene.get("productKnowledgeNeeds"))
    defer_kc = meta.get("deferKnowledgeCmsCheckUntilPreCreate") is True
    knowledge_ready = meta.get("knowledgeChecked") is True and meta.get("knowledgeReady") is True
    if has_topics and not knowledge_ready and not defer_kc:
        kc = _read_json(knowledge_path)
        report = kc.get("knowledgeCheckReport") if isinstance(kc.get("knowledgeCheckReport"), dict) else {}
        return {
            "status": "NEED_KNOWLEDGE_CHECK",
            "nextAction": "执行 tbs-scene-knowledge-check.py；若缺正文，先补齐正文",
            "missingKnowledgeTopics": kc.get("missingKnowledgeTopics") or report.get("missingTopics") or [],
            "canWrite": True,
        }

    validate = _read_json(validate_path)
    report = validate.get("validationReport") if isinstance(validate.get("validationReport"), dict) else {}
    if report.get("passed") is not True:
        return {
            "status": "NEED_VALIDATE",
            "nextAction": "执行 tbs-scene-validate.py --scope full",
            "canWrite": True,
        }

    expected_scene_hash = str(report.get("sceneHash") or "").strip()
    expected_display_hash = str(report.get("displayHash") or "").strip()
    try:
        current_scene_hash = compute_scene_hash(scene)
        current_display_hash = compute_display_hash(scene)
    except Exception:
        current_scene_hash = _fallback_hash(scene)
        current_display_hash = ""

    if expected_scene_hash != current_scene_hash:
        return {
            "status": "NEED_VALIDATE",
            "nextAction": "当前 scene 与 latest-validate-result.json 不一致，重新 FULL validate",
            "sceneHashMismatch": True,
            "canWrite": True,
        }
    if expected_display_hash and current_display_hash and expected_display_hash != current_display_hash:
        return {
            "status": "NEED_VALIDATE",
            "nextAction": "最终确认展示内容 hash 已变化，重新 FULL validate 并重新展示",
            "displayHashMismatch": True,
            "canWrite": True,
        }

    if defer_kc:
        return {
            "status": "READY_TO_FINALIZE",
            "nextAction": "用户确认后调用 tbs-scene-finalize-from-session.py；该入口会先 knowledge-check 再创建",
            "deferKnowledgeCmsCheckUntilPreCreate": True,
            "canWrite": True,
        }

    return {
        "status": "READY_TO_CONFIRM",
        "nextAction": "可展示模板 3；用户确认后调用 tbs-scene-finalize-from-session.py",
        "displayHash": expected_display_hash,
        "canWrite": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-dir", required=True)
    args = parser.parse_args()

    session_dir = _infer_session_dir(args.session_dir)
    scene_hash, display_hash = _load_hash_helpers()
    payload = {
        "success": True,
        "step": "tbs-scene-preflight",
        "sessionDir": str(session_dir),
        **_status(
            session_dir=session_dir,
            compute_scene_hash=scene_hash,
            compute_display_hash=display_hash,
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
