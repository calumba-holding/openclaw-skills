"""
Create a TBS scene after explicit user confirmation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_tbs_client() -> Any:
    module_path = Path(__file__).with_name("tbs-client.py")
    spec = importlib.util.spec_from_file_location("tbs_client_runtime", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load TBS client from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_tbs_client = _load_tbs_client()
TBSClient = _tbs_client.TBSClient
extract_created_entity_id = _tbs_client.extract_created_entity_id
resolve_ids_for_scene = _tbs_client.resolve_ids_for_scene


STEP = "tbs-scene-create"
DEFAULT_TBS_ADMIN_BASE_URL = "https://sg-al-cwork-web.mediportal.com.cn/tbs-admin"
DEFAULT_BASE_URL = os.getenv("TBS_ADMIN_BASE_URL", DEFAULT_TBS_ADMIN_BASE_URL).strip() or DEFAULT_TBS_ADMIN_BASE_URL
OUTPUT_PATH: str | None = None
SCENE_HASH_FIELDS = [
    "title",
    "businessDomainName",
    "departmentName",
    "drugName",
    "location",
    "doctorConcerns",
    "repGoal",
    "sceneBackground",
    "productKnowledgeNeeds",
    "knowledgeIds",
    "doctorOnlyContext",
    "coachOnlyContext",
    "actorProfile",
]
REQUIRED_CREATE_FIELDS = [
    "title",
    "businessDomainName",
    "departmentName",
    "drugName",
    "location",
    "doctorOnlyContext",
    "coachOnlyContext",
]
REQUIRED_DISPLAY_FIELDS = [
    "businessDomainName",
    "departmentName",
    "drugName",
    "location",
    "doctorConcerns",
    "repGoal",
    "productKnowledgeNeeds",
    "title",
    "sceneBackground",
    "actorProfile",
]


def _write_output_json(payload: dict[str, Any]) -> None:
    if not OUTPUT_PATH:
        return
    parent = os.path.dirname(OUTPUT_PATH)
    if parent:
        os.makedirs(parent, exist_ok=True)
    tmp_path = OUTPUT_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(tmp_path, OUTPUT_PATH)


def _canonical_scene_for_hash(scene: dict[str, Any]) -> dict[str, Any]:
    canonical: dict[str, Any] = {}
    for field in SCENE_HASH_FIELDS:
        if field == "sceneBackground":
            value = scene.get("sceneBackground") or scene.get("background")
        else:
            value = scene.get(field)
        if value is None:
            continue
        canonical[field] = value
    return canonical


def compute_scene_hash(scene: dict[str, Any]) -> str:
    canonical = _canonical_scene_for_hash(scene)
    text = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_display_for_hash(scene: dict[str, Any]) -> dict[str, Any]:
    canonical: dict[str, Any] = {}
    for field in REQUIRED_DISPLAY_FIELDS:
        if field == "sceneBackground":
            value = scene.get("sceneBackground") or scene.get("background")
        else:
            value = scene.get(field)
        canonical[field] = "" if value is None else value
    return canonical


def compute_display_hash(scene: dict[str, Any]) -> str:
    canonical = _canonical_display_for_hash(scene)
    text = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _summary(payload: dict[str, Any], *, ok: bool) -> str:
    parts = ["OK" if ok else "ERROR", STEP]
    if payload.get("sceneId"):
        parts.append(f"sceneId={payload['sceneId']}")
    if payload.get("cancelled") is True:
        parts.append("cancelled=true")
    if payload.get("error"):
        parts.append(f"error={payload['error']}")
    if OUTPUT_PATH:
        parts.append(f"result={OUTPUT_PATH}")
    return " ".join(parts)


def emit_success(payload: dict[str, Any]) -> None:
    payload = {"success": True, **payload}
    if OUTPUT_PATH:
        _write_output_json(payload)
        print(_summary(payload, ok=True))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


def emit_error(error: str, exit_code: int = 1, **extra: Any) -> None:
    payload = {"success": False, "step": STEP, "error": error, **extra}
    if OUTPUT_PATH:
        _write_output_json(payload)
        print(_summary(payload, ok=False), file=sys.stderr)
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    sys.exit(exit_code)


def _access_token_looks_unresolved_placeholder(token: str) -> bool:
    """拦截文档示例或 shell 未展开变量，避免无意义请求打满鉴权日志。"""
    t = token.strip()
    if not t:
        return True
    lowered = t.lower()
    if lowered in {"<access_token>", "access_token", "your_access_token", "${access_token}"}:
        return True
    if t.startswith("<") and t.endswith(">"):
        return True
    if t.startswith("${") and t.endswith("}"):
        return True
    return False


def read_payload(input_path: str | None, params_file: str | None) -> dict[str, Any]:
    path = params_file or input_path
    if path and path != "-":
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("输入 JSON 须为对象")
        return data
    raw = sys.stdin.read()
    data = json.loads(raw or "{}")
    if not isinstance(data, dict):
        raise ValueError("输入 JSON 须为对象")
    return data


def _read_draft_object(draft_path: str) -> dict[str, Any]:
    if not draft_path or not os.path.isfile(draft_path):
        return {}
    try:
        with open(draft_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def merged_meta(payload: dict[str, Any], explicit_path: str | None) -> dict[str, Any]:
    top = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    meta = dict(top)
    path = explicit_path
    if (not isinstance(path, str) or not path.strip()) and isinstance(
        payload.get("draftPath"), str
    ):
        path = payload.get("draftPath")
    if isinstance(path, str) and path.strip():
        existing = _read_draft_object(path.strip())
        file_meta = existing.get("meta") if isinstance(existing.get("meta"), dict) else {}
        return {**file_meta, **meta}
    return meta


def create_validation_gate_ok(
    scene: dict[str, Any], validation_report: dict[str, Any], meta: dict[str, Any]
) -> tuple[bool, str]:
    passed = validation_report.get("passed") is True
    scope = str(validation_report.get("scope") or "FULL").strip().upper()
    expected_hash = str(
        validation_report.get("sceneHash") or meta.get("lastValidatedSceneHash") or ""
    ).strip()
    if not expected_hash:
        return False, "validation_scene_hash_missing: 校验结果缺少 sceneHash，请重新执行 tbs-scene-validate.py。"
    current_hash = compute_scene_hash(scene)
    if expected_hash != current_hash:
        return (
            False,
            "validation_scene_hash_mismatch: 当前 scene 与 validationReport 不一致，请重新执行 tbs-scene-validate.py。",
        )
    if passed and scope == "FULL":
        return True, ""
    if passed and scope == "TBV":
        if meta.get("lastFullValidationPassed") is True:
            return True, ""
        return (
            False,
            "PATCH 落库路径要求草稿 meta.lastFullValidationPassed=true（曾通过全量校验），且本轮 validationReport.scope=TBV 且 passed=true。",
        )
    return False, "创建前校验未通过：需要全量校验通过，或（曾全量通过 + 本轮 TBV 通过）组合。"


def create_display_gate_ok(
    scene: dict[str, Any], validation_report: dict[str, Any], payload: dict[str, Any], meta: dict[str, Any]
) -> tuple[bool, str]:
    expected_hash = str(
        validation_report.get("displayHash") or meta.get("lastDisplayHash") or ""
    ).strip()
    confirmed_hash = str(
        payload.get("confirmedDisplayHash")
        or payload.get("userConfirmedDisplayHash")
        or meta.get("confirmedDisplayHash")
        or ""
    ).strip()
    if not expected_hash:
        return False, "display_hash_missing: 校验结果缺少 displayHash，请重新执行 validate 并重新展示最终确认。"
    if not confirmed_hash:
        return (
            False,
            "display_confirmation_hash_missing: 用户确认必须绑定本次最终确认清单，请携带 confirmedDisplayHash。",
        )
    current_hash = compute_display_hash(scene)
    if expected_hash != current_hash or confirmed_hash != current_hash:
        return (
            False,
            "display_hash_mismatch: 用户确认后场景展示内容发生变化，请重新展示最终确认清单并重新取得确认。",
        )

    if payload.get("displayContractSatisfied") is True:
        return True, ""
    if meta.get("displayContractSatisfied") is True:
        return True, ""
    displayed_fields: list[str] = []
    for source in (payload.get("displayedFields"), meta.get("displayedFields")):
        if isinstance(source, list):
            displayed_fields.extend(str(item).strip() for item in source if str(item).strip())
    if displayed_fields:
        shown = set(displayed_fields)
        missing = [field for field in REQUIRED_DISPLAY_FIELDS if field not in shown]
        if not missing:
            return True, ""
        return (
            False,
            "display_contract_incomplete: 未声明完整展示字段，缺少 "
            + ", ".join(missing),
        )
    return (
        False,
        "display_contract_missing: 创建前需声明已按 mustDisplayFields 向用户展示（传 displayContractSatisfied=true 或 displayedFields）。",
    )


def create_knowledge_gate_ok(scene: dict[str, Any], meta: dict[str, Any]) -> tuple[bool, str]:
    if _is_empty(scene.get("productKnowledgeNeeds")):
        return True, ""
    if meta.get("knowledgeChecked") is True and meta.get("knowledgeReady") is True:
        return True, ""
    return (
        False,
        "knowledge_gate_failed: 创建前必须先执行 tbs-scene-knowledge-check.py，且 knowledgeReady=true。",
    )


def create_parse_stage_gate_ok(meta: dict[str, Any]) -> tuple[bool, str]:
    if str(meta.get("lastParseStage") or "").strip() == "READY_FOR_VALIDATE":
        return True, ""
    return (
        False,
        "parse_stage_gate_failed: 创建前必须完成场景内容生成，并由 tbs-scene-parse.py 输出 READY_FOR_VALIDATE。",
    )


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return len([item for item in value if str(item).strip()]) == 0
    if isinstance(value, dict):
        return len(value) == 0
    return False


def create_scene_self_check_ok(
    scene: dict[str, Any], validation_report: dict[str, Any]
) -> tuple[bool, str]:
    missing = [field for field in REQUIRED_CREATE_FIELDS if _is_empty(scene.get(field))]
    if missing:
        return False, f"scene_required_fields_missing: {', '.join(missing)}"

    # 至少保证场景背景可落库，避免仅靠伪造 validationReport 进入创建。
    has_background = not _is_empty(scene.get("sceneBackground")) or not _is_empty(
        scene.get("background")
    )
    if not has_background:
        return False, "scene_background_missing: sceneBackground 必填"

    actor = scene.get("actorProfile")
    if not isinstance(actor, dict) or _is_empty(actor.get("name")):
        return False, "scene_actor_profile_invalid: actorProfile.name 必填"

    # 与 validate 输出做最小一致性校验，防止伪造 passed=true 但仍带阻断项。
    blocking = validation_report.get("blockingIssues")
    if isinstance(blocking, list) and len(blocking) > 0:
        return False, "validation_report_inconsistent: blockingIssues 非空"
    issues = validation_report.get("issues")
    if isinstance(issues, list) and len(issues) > 0:
        return False, "validation_report_inconsistent: issues 非空"

    return True, ""


def require_confirmation(payload: dict[str, Any]) -> str:
    value = str(payload.get("userConfirmation") or "").strip()
    if not value:
        raise RuntimeError("缺少 userConfirmation，必须为 确认 或 取消")
    if value not in {"确认", "取消"}:
        raise RuntimeError("userConfirmation 仅允许为 确认 或 取消")
    return value


def persist_result(
    draft_path: str | None,
    scene: dict[str, Any],
    validation_report: dict[str, Any],
    scene_id: str,
    resolved_ids: dict[str, Any],
    resolution_report: dict[str, dict[str, Any]],
) -> None:
    if not draft_path:
        return
    parent = os.path.dirname(draft_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    existing = _read_draft_object(draft_path)
    prior_meta = existing.get("meta") if isinstance(existing.get("meta"), dict) else {}
    meta = {
        **prior_meta,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "lastStep": STEP,
    }
    payload = {
        **existing,
        "scene": scene,
        "validationReport": validation_report,
        "persistResult": {
            "sceneId": scene_id,
            "resolvedIds": resolved_ids,
            "resolutionReport": resolution_report,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        },
        "meta": meta,
    }
    tmp_path = str(draft_path) + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(tmp_path, str(draft_path))


def main() -> None:
    global OUTPUT_PATH
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="-", help="JSON file path, or '-' for stdin")
    parser.add_argument("--params-file", default=None, help="Read params from UTF-8 JSON file")
    parser.add_argument("--output", default=None, help="Write full JSON result to this file")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--access-token", required=True)
    args = parser.parse_args()
    OUTPUT_PATH = args.output

    try:
        payload = read_payload(args.input, args.params_file)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        emit_error("invalid_json_input", exit_code=2, hint=str(exc))
    try:
        confirmation = require_confirmation(payload)
    except RuntimeError as exc:
        emit_error(str(exc), exit_code=2)
    if confirmation == "取消":
        emit_success(
            {
                "step": STEP,
                "cancelled": True,
                "message": "用户已取消，本次不执行创建。",
            }
        )
        return

    access_token = str(args.access_token or "").strip()
    if not access_token:
        emit_error("缺少 access-token", exit_code=2)
    if _access_token_looks_unresolved_placeholder(access_token):
        emit_error(
            "access_token_invalid",
            exit_code=2,
            hint="access-token 疑似占位符或未替换的模板；请先通过 cms-auth-skills 取得真实 token 后再以 --access-token 注入，勿把 <ACCESS_TOKEN> 等示例原文传入。",
        )

    scene = payload.get("scene") if isinstance(payload.get("scene"), dict) else {}
    validation_report = (
        payload.get("validationReport") if isinstance(payload.get("validationReport"), dict) else {}
    )
    draft_path = payload.get("draftPath")
    loaded_from_path: dict[str, Any] = {}
    if not scene and (args.params_file or (args.input and args.input != "-")):
        draft_path = args.params_file or args.input
        loaded_from_path = read_payload(draft_path, None)
        scene = (
            loaded_from_path.get("scene")
            if isinstance(loaded_from_path.get("scene"), dict)
            else {}
        )
        validation_report = (
            loaded_from_path.get("validationReport")
            if isinstance(loaded_from_path.get("validationReport"), dict)
            else {}
        )
    if not scene:
        emit_error("缺少 scene", exit_code=2)
    effective_payload = {**loaded_from_path, **payload} if loaded_from_path else payload
    path_for_meta = (
        draft_path.strip() if isinstance(draft_path, str) and draft_path.strip() else None
    )
    meta = merged_meta(effective_payload, path_for_meta)
    parse_stage_ok, parse_stage_hint = create_parse_stage_gate_ok(meta)
    if not parse_stage_ok:
        emit_error("parse_stage_gate_failed", exit_code=2, hint=parse_stage_hint)
    gate_ok, gate_hint = create_validation_gate_ok(scene, validation_report, meta)
    if not gate_ok:
        emit_error("validation_gate_failed", exit_code=2, hint=gate_hint)
    knowledge_ok, knowledge_hint = create_knowledge_gate_ok(scene, meta)
    if not knowledge_ok:
        emit_error("knowledge_gate_failed", exit_code=2, hint=knowledge_hint)
    display_ok, display_hint = create_display_gate_ok(
        scene, validation_report, effective_payload, meta
    )
    if not display_ok:
        emit_error("display_gate_failed", exit_code=2, hint=display_hint)
    self_ok, self_hint = create_scene_self_check_ok(scene, validation_report)
    if not self_ok:
        emit_error("scene_self_check_failed", exit_code=2, hint=self_hint)

    # Use sceneBackground as canonical background text for persistence/display.
    canonical_background = str(scene.get("sceneBackground") or scene.get("background") or "").strip()
    if canonical_background:
        scene["sceneBackground"] = canonical_background
        scene["background"] = canonical_background

    client = TBSClient(base_url=args.base_url, access_token=access_token)
    try:
        resolved_ids, resolution_report = resolve_ids_for_scene(client, scene)
        if resolved_ids.get("personaIds"):
            scene["personaIds"] = resolved_ids.get("personaIds") or []
        if resolved_ids.get("knowledgeIds"):
            scene["knowledgeIds"] = [str(item) for item in resolved_ids.get("knowledgeIds") or []]
        body = {
            "title": scene["title"],
            "businessDomainId": resolved_ids["businessDomainId"],
            "departmentId": resolved_ids["departmentId"],
            "drugId": resolved_ids["drugId"],
            "location": scene["location"],
            "doctorOnlyContext": scene["doctorOnlyContext"],
            "coachOnlyContext": scene["coachOnlyContext"],
            "repBriefing": canonical_background,
            "personaIds": resolved_ids.get("personaIds") or [],
            "knowledgeIds": resolved_ids.get("knowledgeIds") or [],
            "status": 1,
        }
        created = client.request_json("POST", "/scene/createScene", body)
        scene_id = extract_created_entity_id(created, "sceneId", "scene_id")
        if not scene_id:
            raise RuntimeError("createScene 返回中缺少 sceneId")
    except Exception as exc:  # noqa: BLE001
        emit_error(str(exc), exit_code=1)

    if isinstance(draft_path, str) and draft_path.strip():
        persist_result(
            draft_path=draft_path.strip(),
            scene=scene,
            validation_report=validation_report,
            scene_id=scene_id,
            resolved_ids=resolved_ids,
            resolution_report=resolution_report,
        )

    emit_success(
        {
            "step": STEP,
            "sceneId": scene_id,
            "resolvedIds": resolved_ids,
            "resolutionReport": resolution_report,
            "personaIds": resolved_ids.get("personaIds") or [],
            "knowledgeIds": resolved_ids.get("knowledgeIds") or [],
            "message": "场景创建成功",
        }
    )


if __name__ == "__main__":
    main()
