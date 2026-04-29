"""
Check confirmed product knowledge topics before scene content generation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
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
check_or_create_knowledge_for_topics = _tbs_client.check_or_create_knowledge_for_topics
resolve_or_create_business_domain = _tbs_client.resolve_or_create_business_domain
resolve_or_create_drug = _tbs_client.resolve_or_create_drug


STEP = "tbs-scene-knowledge-check"
DEFAULT_TBS_ADMIN_BASE_URL = "https://sg-al-cwork-web.mediportal.com.cn/tbs-admin"
DEFAULT_BASE_URL = os.getenv("TBS_ADMIN_BASE_URL", DEFAULT_TBS_ADMIN_BASE_URL).strip() or DEFAULT_TBS_ADMIN_BASE_URL
_PLACEHOLDER_KNOWLEDGE_ID = re.compile(r"^new-\d+$", re.IGNORECASE)
OUTPUT_PATH: str | None = None


def _is_placeholder_knowledge_id(value: str) -> bool:
    text = str(value).strip()
    if not text:
        return True
    return bool(_PLACEHOLDER_KNOWLEDGE_ID.match(text))


def _normalize_topics(value: Any) -> list[str]:
    if isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        items = []
    normalized = [str(item).strip() for item in items if str(item).strip()]
    seen: set[str] = set()
    out: list[str] = []
    for item in sorted(normalized, key=lambda x: x.lower()):
        k = item.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(item)
    return out


def _knowledge_fingerprint(scene: dict[str, Any]) -> str:
    knowledge = scene.get("knowledge")
    items: list[dict[str, str]] = []
    if isinstance(knowledge, list):
        for raw in knowledge:
            if isinstance(raw, dict):
                items.append(
                    {
                        "category": str(raw.get("category") or "").strip(),
                        "title": str(raw.get("title") or "").strip(),
                        "content": str(raw.get("content") or "").strip(),
                    }
                )
            elif isinstance(raw, str) and raw.strip():
                items.append({"category": "", "title": raw.strip(), "content": ""})
    elif isinstance(knowledge, dict):
        items.append(
            {
                "category": str(knowledge.get("category") or "").strip(),
                "title": str(knowledge.get("title") or "").strip(),
                "content": str(knowledge.get("content") or "").strip(),
            }
        )
    elif isinstance(knowledge, str) and knowledge.strip():
        items.append({"category": "", "title": knowledge.strip(), "content": ""})

    canonical = [
        item
        for item in items
        if item.get("title") or item.get("content") or item.get("category")
    ]
    text = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_knowledge_key(scene: dict[str, Any]) -> str:
    canonical = {
        "businessDomainName": str(scene.get("businessDomainName") or "").strip(),
        "drugName": str(scene.get("drugName") or "").strip(),
        "drugId": str(scene.get("drugId") or "").strip(),
        "productKnowledgeNeeds": _normalize_topics(scene.get("productKnowledgeNeeds")),
        "knowledgeFingerprint": _knowledge_fingerprint(scene),
    }
    text = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _can_skip_network_check(scene: dict[str, Any], draft_meta: dict[str, Any]) -> tuple[bool, str, str]:
    expected_key = str(draft_meta.get("lastKnowledgeKey") or "").strip()
    current_key = compute_knowledge_key(scene)
    if not expected_key:
        return False, "draft_meta_lastKnowledgeKey_missing", current_key
    if current_key != expected_key:
        return False, "knowledge_key_changed", current_key
    if scene.get("knowledgeReady") is not True:
        return False, "scene_knowledgeReady_not_true", current_key
    knowledge_ids = [str(x).strip() for x in (scene.get("knowledgeIds") or []) if str(x).strip()]
    if not knowledge_ids:
        return False, "scene_knowledgeIds_empty", current_key
    if any(_is_placeholder_knowledge_id(x) for x in knowledge_ids):
        return False, "scene_knowledgeIds_contains_placeholder", current_key
    if not str(scene.get("drugId") or "").strip():
        return False, "scene_drugId_missing", current_key
    return True, "reused_previous_knowledge_check", current_key


def _merge_knowledge_ids(scene_ids: list[str], server_ids: list[str]) -> list[str]:
    """Drop agent-side placeholders (e.g. new-001); keep real ids; append server ids in order without dupes."""
    kept = [x for x in scene_ids if x and not _is_placeholder_knowledge_id(x)]
    seen = set(kept)
    merged = list(kept)
    for item in server_ids:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        merged.append(text)
    return merged


def _write_output_json(payload: dict[str, Any]) -> None:
    if not OUTPUT_PATH:
        return
    parent = os.path.dirname(OUTPUT_PATH)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def _summary(payload: dict[str, Any], *, ok: bool) -> str:
    parts = ["OK" if ok else "ERROR", STEP]
    if payload.get("knowledgeReady") is not None:
        parts.append(f"knowledgeReady={str(payload['knowledgeReady']).lower()}")
    report = payload.get("knowledgeCheckReport")
    if isinstance(report, dict):
        parts.append(f"missing={len(report.get('missingTopics') or [])}")
        parts.append(f"existing={len(report.get('existingTopics') or [])}")
        parts.append(f"created={len(report.get('createdTopics') or [])}")
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


def read_payload(input_path: str, params_file: str | None) -> dict[str, Any]:
    path = params_file or input_path
    if path and path != "-":
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    else:
        data = json.load(sys.stdin)
    if not isinstance(data, dict):
        raise ValueError("输入 JSON 须为对象")
    return data


def _access_token_looks_unresolved_placeholder(token: str) -> bool:
    text = token.strip()
    if not text:
        return True
    lowered = text.lower()
    if lowered in {"<access_token>", "access_token", "your_access_token", "${access_token}"}:
        return True
    return (text.startswith("<") and text.endswith(">")) or (
        text.startswith("${") and text.endswith("}")
    )


def _read_draft_object(draft_path: str) -> dict[str, Any]:
    if not draft_path or not os.path.isfile(draft_path):
        return {}
    try:
        with open(draft_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def maybe_write_draft(
    draft_path: str | None,
    scene: dict[str, Any],
    meta: dict[str, Any],
    knowledge_report: dict[str, Any],
    resolved_ids: dict[str, Any],
    resolution_report: dict[str, Any],
) -> None:
    if not draft_path:
        return
    parent = os.path.dirname(draft_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    existing = _read_draft_object(draft_path.strip())
    prior_meta = existing.get("meta") if isinstance(existing.get("meta"), dict) else {}
    prior_resolved_ids = (
        existing.get("resolvedIds") if isinstance(existing.get("resolvedIds"), dict) else {}
    )
    prior_resolution_report = (
        existing.get("resolutionReport")
        if isinstance(existing.get("resolutionReport"), dict)
        else {}
    )
    payload = {
        **existing,
        "scene": scene,
        "knowledgeCheckReport": knowledge_report,
        "resolvedIds": {**prior_resolved_ids, **resolved_ids},
        "resolutionReport": {
            **prior_resolution_report,
            **resolution_report,
        },
        "meta": {**prior_meta, **meta},
    }
    tmp_path = draft_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(tmp_path, draft_path)


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

    access_token = str(args.access_token or "").strip()
    if _access_token_looks_unresolved_placeholder(access_token):
        emit_error("access_token_invalid", exit_code=2)

    scene = payload.get("scene") if isinstance(payload.get("scene"), dict) else {}
    if not scene:
        emit_error("缺少 scene", exit_code=2)

    topics = _normalize_topics(scene.get("productKnowledgeNeeds"))
    if not topics:
        emit_error("缺少 productKnowledgeNeeds", exit_code=2)

    business_domain_name = str(scene.get("businessDomainName") or "").strip()
    drug_name = str(scene.get("drugName") or "").strip()
    if not business_domain_name:
        emit_error("缺少 businessDomainName", exit_code=2)
    if not drug_name:
        emit_error("缺少 drugName", exit_code=2)

    draft_path = payload.get("draftPath")
    draft_obj: dict[str, Any] = {}
    draft_meta: dict[str, Any] = {}
    if isinstance(draft_path, str) and draft_path.strip():
        draft_obj = _read_draft_object(draft_path.strip())
        if isinstance(draft_obj.get("meta"), dict):
            draft_meta = dict(draft_obj.get("meta") or {})

    skip_ok, skip_reason, knowledge_key = _can_skip_network_check(scene, draft_meta)
    if skip_ok:
        knowledge_ids = [str(x).strip() for x in (scene.get("knowledgeIds") or []) if str(x).strip()]
        knowledge_report = {
            "action": "skipped",
            "reason": skip_reason,
            "totalTopics": len(topics),
            "existingTopics": topics,
            "missingTopics": [],
            "createdTopics": [],
            "pendingTopics": [],
            "knowledgeIds": knowledge_ids,
        }
        # Best-effort reuse; not required for skip path correctness.
        resolved = draft_meta.get("resolvedIds") if isinstance(draft_meta.get("resolvedIds"), dict) else {}
        business_domain_id = str(resolved.get("businessDomainId") or "").strip()
        drug_id = str(scene.get("drugId") or "").strip()
        business_domain_report = {"action": "reused_from_draft", "input": business_domain_name}
        drug_report = {"action": "reused_from_scene", "input": drug_id or drug_name}
    else:
        client = TBSClient(base_url=args.base_url, access_token=access_token)
        try:
            business_domain_id, business_domain_report = resolve_or_create_business_domain(
                client, business_domain_name, allow_create=False
            )
            drug_id, drug_report = resolve_or_create_drug(
                client,
                drug_name,
                business_domain_id,
                business_domain_name,
                allow_create=True,
            )
            knowledge_ids, knowledge_report = check_or_create_knowledge_for_topics(
                client, scene, drug_id
            )
        except Exception as exc:  # noqa: BLE001
            emit_error(str(exc), exit_code=1)
        # Ensure key includes canonical drugId once resolved.
        knowledge_key = compute_knowledge_key({**scene, "drugId": str(drug_id)})

    missing_topics = knowledge_report.get("missingTopics") or []
    knowledge_ready = not missing_topics
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    meta = {
        **meta,
        "knowledgeChecked": True,
        "knowledgeReady": knowledge_ready,
        "knowledgeIds": knowledge_ids,
        "knowledgeCheckReport": knowledge_report,
        "lastKnowledgeKey": knowledge_key,
        "knowledgeCheckSkipped": bool(skip_ok),
        "knowledgeCheckSkipReason": skip_reason if skip_ok else "",
        "resolvedIds": {
            "businessDomainId": business_domain_id,
            "drugId": drug_id,
        },
        "resolutionReport": {
            "businessDomain": business_domain_report,
            "drug": drug_report,
        },
    }
    scene = {**scene}
    scene["drugId"] = str(drug_id)
    raw_knowledge_ids = [str(item) for item in scene.get("knowledgeIds") or [] if str(item).strip()]
    if knowledge_ids:
        scene["knowledgeIds"] = _merge_knowledge_ids(raw_knowledge_ids, knowledge_ids)
    else:
        scene["knowledgeIds"] = [x for x in raw_knowledge_ids if not _is_placeholder_knowledge_id(x)]
    scene["knowledgeChecked"] = True
    scene["knowledgeReady"] = knowledge_ready
    scene["missingKnowledgeTopics"] = list(missing_topics)
    if isinstance(draft_path, str) and draft_path.strip():
        maybe_write_draft(
            draft_path.strip(),
            scene,
            meta,
            knowledge_report,
            {"businessDomainId": business_domain_id, "drugId": drug_id},
            {"businessDomain": business_domain_report, "drug": drug_report},
        )

    emit_success(
        {
            "step": STEP,
            "scene": scene,
            "knowledgeReady": knowledge_ready,
            "knowledgeIds": knowledge_ids,
            "knowledgeKey": knowledge_key,
            "knowledgeCheckSkipped": bool(skip_ok),
            "knowledgeCheckSkipReason": skip_reason if skip_ok else "",
            "knowledgeCheckReport": knowledge_report,
            "resolvedIds": {
                "businessDomainId": business_domain_id,
                "drugId": drug_id,
            },
            "resolutionReport": {
                "businessDomain": business_domain_report,
                "drug": drug_report,
            },
            "missingKnowledgeTopics": missing_topics,
            "nextAction": (
                "补充缺失产品知识正文后重新检查"
                if missing_topics
                else "继续进入场景内容生成"
            ),
            "meta": meta,
        }
    )


if __name__ == "__main__":
    main()
