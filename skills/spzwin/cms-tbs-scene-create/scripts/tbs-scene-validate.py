"""
Validate whether the current scene draft is ready for user confirmation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_sanitize_helper() -> Any:
    module_path = Path(__file__).with_name("tbs-md-sanitize.py")
    spec = importlib.util.spec_from_file_location("tbs_md_sanitize_runtime", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load sanitize helper from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sanitize_doctor_core_concerns_to_two_bullets = (
    _load_sanitize_helper().sanitize_doctor_core_concerns_to_two_bullets
)


STEP = "tbs-scene-validate"
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
FIELD_LABELS = {
    "title": "场景标题",
    "businessDomainName": "业务领域",
    "departmentName": "科室",
    "drugName": "产品",
    "location": "地点",
    "doctorConcerns": "医生顾虑",
    "repGoal": "代表目标",
    "sceneBackground": "场景背景",
    "productKnowledgeNeeds": "产品知识主题",
    "doctorOnlyContext": "对练对象侧上下文",
    "coachOnlyContext": "教练侧上下文",
    "actorProfile": "对练对象档案",
}
CONFIRM_DISPLAY_FIELDS = [
    "title",
    "sceneBackground",
    "businessDomainName",
    "departmentName",
    "drugName",
    "location",
    "doctorConcerns",
    "repGoal",
    "productKnowledgeNeeds",
    "actorProfile",
]
MUST_DISPLAY_FIELDS = [
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
ALLOWED_BUSINESS_DOMAINS = {"临床推广", "院外零售", "学术合作", "通用能力"}
WARNING_ISSUE_CODES = {
    "scene.sceneBackground_too_long",
    "scene.sceneBackground_placeholder",
    "scene.sceneBackground_label_style",
    "scene.sceneBackground_pronoun",
    "scene.sceneBackground_anchor_missing",
}
DECLINED_PRODUCT_KNOWLEDGE_TOPIC = "用户确认暂不补充产品知识主题"
REQUIRED_FIELDS = [
    "title",
    "businessDomainName",
    "departmentName",
    "drugName",
    "location",
    "doctorConcerns",
    "repGoal",
    "sceneBackground",
    "productKnowledgeNeeds",
    "doctorOnlyContext",
    "coachOnlyContext",
    "actorProfile",
]
DOCTOR_REQUIRED_HEADERS = [
    "## 已知背景",
    "## 核心顾虑",
    "## 今日状态",
    "## 终止条件",
    "## 输出要求",
    "## 对话结束规则（强制）",
]
COACH_REQUIRED_HEADERS = [
    "## 期望代表行为",
    "## 评分重点",
    "## 终止条件",
    "## 最佳实践",
    "## 输出要求",
]
DOCTOR_ENDING_RULES_TEMPLATE = [
    "- 只有对练对象角色可结束：仅在本轮末尾追加 [对话结束]，且必须放在全文最后。",
    "- 允许结束：已触发终止条件，或系统明确要求本轮结束（最后一轮/轮次已满）。",
    "- 互斥（执行检查）：若本轮出现问号或疑问词，则必须删除 [对话结束]。",
    "- 互斥（执行检查）：若本轮要输出 [对话结束]，则全文不得出现任何问号或疑问词，且不得出现提问意图。",
    "- 结束语边界：结束语必须是纯陈述句，不得提问，也不得安排任何后续动作或要求。",
]
DOCTOR_OUTPUT_REQUIREMENTS_TEMPLATE = [
    "- 输出长度控制：每次回复控制在30-50字左右，保持真实医生沟通的自然简洁；每轮最多聚焦1个核心点。",
    "- 单问原则：每轮最多提出1个核心问题（问号≤1）。如果想到第二个问题，必须留到下一轮再问。",
    "- 语言要求：以中文自然对话为主；允许必要的医学缩写/单位/符号，但不得滥用英文；严禁出现与医学沟通无关的英文单词。",
    "- 纯文本要求（强制）：只输出纯文本对话，不要使用任何加粗/斜体/标题/代码符号等格式化写法。",
    "- 提问后必须等待代表回答：提问后必须收住，不得在同一轮连续追问，更不得在提问后追加结束标记。",
    "- 避免臆造数据（强制）：不得凭空编造背景之外的具体数值/比例/研究结论；不确定就说明需回去核对资料。",
]
_BRIEFING_LABEL_PATTERN = re.compile(r"(场景背景|人物关系|训练目的|开场建议|AI角色对象的顾虑)\s*[：:]")
_SINGLE_PRONOUN_PATTERN = re.compile(
    r"(^|[，。；：、“”（）\s\d])"
    r"([你我他她它咱])"
    r"(?=$|[，。；：、“”（）\s\d]|[的了吗呢吧啊呀])"
)


def _trim_display_text(value: Any, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip())
    if len(text) <= limit:
        return text
    return text[:limit].rstrip("，,。；; ") + "…"


def build_supplement_items(scene: dict[str, Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    actor_supplement = str(scene.get("actorProfileSupplement") or "").strip()
    if actor_supplement:
        items.append({"label": "对象角色画像", "value": _trim_display_text(actor_supplement)})

    best_practice = str(scene.get("bestPracticeSupplement") or "").strip()
    if best_practice:
        items.append({"label": "代表成功经验/典型话术", "value": _trim_display_text(best_practice)})

    return items


def build_supplement_render_block(supplement_items: list[dict[str, str]]) -> str:
    if not supplement_items:
        return ""
    lines = ["- 补充素材（如已提供）："]
    for item in supplement_items:
        label = str(item.get("label") or "").strip()
        value = str(item.get("value") or "").strip()
        if label and value:
            lines.append(f"  - {label}：{value}")
    return "\n".join(lines) if len(lines) > 1 else ""


def _write_output_json(payload: dict[str, Any]) -> None:
    if not OUTPUT_PATH:
        return
    parent = os.path.dirname(OUTPUT_PATH)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


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
    for field in MUST_DISPLAY_FIELDS:
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
    report = payload.get("validationReport")
    if isinstance(report, dict):
        parts.append(f"scope={report.get('scope')}")
        parts.append(f"passed={report.get('passed')}")
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


def _stringify_value(value: Any, field: str = "") -> str:
    if value is None:
        return ""
    if field == "actorProfile" and isinstance(value, dict):
        parts = [
            str(value.get("title") or "").strip(),
            str(value.get("name") or "").strip(),
            str(value.get("description") or "").strip(),
        ]
        return "；".join(part for part in parts if part)
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return "、".join(parts)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def _issue_code_to_hint(code: str) -> str:
    if code.startswith("scene.") and code.endswith("_missing"):
        field = code[len("scene.") : -len("_missing")]
        label = FIELD_LABELS.get(field, "该字段")
        return f"「{label}」未填写或为空"
    static = {
        "scene.businessDomainName_invalid": "「业务领域」不在允许范围内，请从：临床推广、院外零售、学术合作、通用能力 中选择",
        "scene.sceneBackground_invalid": "「场景背景」未通过检查（长度、格式、人称或需包含科室、产品、地点等关键信息）",
        "scene.sceneBackground_too_long": "「场景背景」长度超过 180 字，建议精简",
        "scene.sceneBackground_placeholder": "「场景背景」含占位符或非常规符号（如【】/待补充），建议改写为自然叙述",
        "scene.sceneBackground_label_style": "「场景背景」含标签化前缀（如“场景背景：”），建议改成自然叙述",
        "scene.sceneBackground_pronoun": "「场景背景」包含第一/第二人称代词（如你/我），建议改为角色称谓叙述",
        "scene.sceneBackground_anchor_missing": "「场景背景」未完整覆盖科室/产品/地点锚点信息",
        "scene.productKnowledgeNeeds_placeholder": "「产品知识主题」不能使用“暂不补充”占位文案；正文可暂无，但主题必须是具体建议主题",
        "scene.doctorOnlyContext_invalid": "「对练对象侧上下文」未通过检查：六个 `##` 标题顺序/拼写、`## 核心顾虑` 条数，或「## 输出要求」「## 对话结束规则（强制）」与内置模板逐行不一致。请查看返回中的 doctorOnlyContextDiagnostics / doctorOnlyContextCanon。",
        "scene.coachOnlyContext_invalid": "「教练侧上下文」的 Markdown 结构未通过检查",
        "scene.actorProfile_invalid": "「对练对象档案」不完整（需包含角色姓名等）",
    }
    return static.get(code, "存在未通过的校验项，请根据草稿核对后重新校验")


def build_confirmation_items(scene: dict[str, Any], fields: list[str]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for field in fields:
        items.append(
            {
                "field": field,
                "label": FIELD_LABELS.get(field, field),
                "value": _stringify_value(scene.get(field), field),
            }
        )
    return items


def issues_to_hints(issues: list[str], *, scene: dict[str, Any] | None = None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for code in issues:
        hint = _issue_code_to_hint(code)
        if code == "scene.doctorOnlyContext_invalid" and scene is not None:
            diag = diagnose_doctor_only_context(scene)
            extra = diag.get("agentHints") or []
            if extra:
                hint = hint + " 细分：" + "；".join(str(item) for item in extra if str(item).strip())
        if hint not in seen:
            seen.add(hint)
            out.append(hint)
    return out


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return not any(isinstance(item, str) and item.strip() for item in value)
    return False


def normalize_scene(scene: dict[str, Any]) -> dict[str, Any]:
    out = dict(scene)
    background = out.get("sceneBackground") or out.get("background")
    if isinstance(background, str) and background.strip():
        out["sceneBackground"] = background.strip()
        out["background"] = background.strip()
    pk_needs = out.get("productKnowledgeNeeds")
    if isinstance(pk_needs, str) and pk_needs.strip():
        topic = pk_needs.strip()
        out["productKnowledgeNeeds"] = [] if topic == DECLINED_PRODUCT_KNOWLEDGE_TOPIC else [topic]
    elif isinstance(pk_needs, list):
        out["productKnowledgeNeeds"] = [
            item.strip()
            for item in pk_needs
            if isinstance(item, str) and item.strip() and item.strip() != DECLINED_PRODUCT_KNOWLEDGE_TOPIC
        ]
    doc_ctx = out.get("doctorOnlyContext")
    if isinstance(doc_ctx, str) and doc_ctx.strip():
        fixed_doc, changed = sanitize_doctor_core_concerns_to_two_bullets(doc_ctx)
        if changed:
            out["doctorOnlyContext"] = fixed_doc
            out["__validateAutoNormalizedDoctorContext"] = True

    scene_background = out.get("sceneBackground")
    if isinstance(scene_background, str) and scene_background.strip():
        fixed_background, background_changes = sanitize_scene_background(scene_background, out)
        if background_changes:
            out["sceneBackground"] = fixed_background
            out["background"] = fixed_background
            out["__validateAutoNormalizedSceneBackground"] = background_changes

    return out


def _contains_personal_name_or_pronoun(text: str) -> bool:
    if any(token in text for token in ("你们", "我们", "他们", "她们", "咱们")):
        return True
    return bool(_SINGLE_PRONOUN_PATTERN.search(text))


def _primary_drug_anchor(drug_name: str) -> str:
    name = drug_name.strip()
    if not name:
        return ""
    head = re.split(r"[（(]", name, maxsplit=1)[0].strip()
    head = re.split(r"[、，,/|]", head, maxsplit=1)[0].strip()
    return head


def _anchor_in_background(text: str, field: str, value: str) -> bool:
    needle = value.strip()
    if not needle:
        return True
    if needle in text:
        return True
    if field == "drugName":
        primary = _primary_drug_anchor(needle)
        if len(primary) >= 2 and primary in text:
            return True
    return False


def _extract_md_section_lines(text: str, header: str) -> list[str]:
    if not isinstance(text, str) or not text.strip():
        return []
    match = re.search(rf"(?ms)^({re.escape(header)})\s*$\n(.*?)(?=^##\s+|\Z)", text)
    if not match:
        return []
    body = match.group(2)
    return [line.strip() for line in body.splitlines() if line.strip()]


def _scene_background_valid(scene: dict[str, Any]) -> bool:
    return len(_scene_background_issue_codes(scene)) == 0


def _scene_background_issue_codes(scene: dict[str, Any]) -> list[str]:
    text = str(scene.get("sceneBackground") or scene.get("background") or "").strip()
    if not text:
        return []
    issues: list[str] = []
    if len(text) > 180:
        issues.append("scene.sceneBackground_too_long")
    if "【" in text or "】" in text or "待补充" in text:
        issues.append("scene.sceneBackground_placeholder")
    if _BRIEFING_LABEL_PATTERN.search(text):
        issues.append("scene.sceneBackground_label_style")
    if _contains_personal_name_or_pronoun(text):
        issues.append("scene.sceneBackground_pronoun")
    missing_anchor = False
    for anchor in ("departmentName", "drugName", "location"):
        value = str(scene.get(anchor) or "").strip()
        if value and not _anchor_in_background(text, anchor, value):
            missing_anchor = True
    if missing_anchor:
        issues.append("scene.sceneBackground_anchor_missing")
    return issues


def sanitize_scene_background(text: str, scene: dict[str, Any]) -> tuple[str, list[str]]:
    fixed = str(text or "").strip()
    changes: list[str] = []
    if not fixed:
        return fixed, changes

    if "【" in fixed or "】" in fixed:
        fixed = fixed.replace("【", "").replace("】", "")
        changes.append("sceneBackground：移除了【】样式符号")
    if "待补充" in fixed:
        fixed = fixed.replace("待补充", "")
        changes.append("sceneBackground：移除了“待补充”占位词")
    if _BRIEFING_LABEL_PATTERN.search(fixed):
        fixed = _BRIEFING_LABEL_PATTERN.sub("", fixed)
        changes.append("sceneBackground：移除了标签化前缀写法")

    fixed = re.sub(r"\s+", " ", fixed).strip("，,。；; ")
    missing_tokens: list[str] = []
    for anchor in ("departmentName", "drugName", "location"):
        value = str(scene.get(anchor) or "").strip()
        if value and not _anchor_in_background(fixed, anchor, value):
            missing_tokens.append(_primary_drug_anchor(value) if anchor == "drugName" else value)

    if missing_tokens:
        suffix = "，涉及" + "、".join(token for token in missing_tokens if token) + "。"
        if len(fixed) + len(suffix) <= 180:
            fixed = fixed + suffix
        else:
            keep_len = max(0, 180 - len(suffix))
            fixed = fixed[:keep_len].rstrip("，,。；; ") + suffix
        changes.append("sceneBackground：自动补齐了科室/产品/地点锚点信息")

    if len(fixed) > 180:
        fixed = fixed[:180].rstrip("，,。；; ")
        changes.append("sceneBackground：长度已裁剪至 180 字以内")

    return fixed, changes


def diagnose_doctor_only_context(scene: dict[str, Any]) -> dict[str, Any]:
    """供 Agent 定位 doctorOnlyContext 阻断原因；与 _doctor_only_context_valid 判定同源。"""
    text = str(scene.get("doctorOnlyContext") or "").strip()
    out: dict[str, Any] = {"passed": False, "reasonCodes": [], "agentHints": []}

    def add(code: str, hint: str) -> None:
        out["reasonCodes"].append(code)
        out["agentHints"].append(hint)

    if not text:
        add("doctor_only_empty", "「对练对象侧上下文」为空；请生成含 6 个固定 `##` 小节的 Markdown。")
        return out

    concern_lines = _extract_md_section_lines(text, "## 核心顾虑")
    concern_bullets = [line for line in concern_lines if line.startswith("-")]
    if not (1 <= len(concern_bullets) <= 2):
        add(
            "doctor_only_core_concerns_bullets",
            "「## 核心顾虑」内需有 1～2 条以 `-` 开头的要点行；超过 2 条请先合并后再校验。",
        )

    out["passed"] = len(out["reasonCodes"]) == 0
    return out


def _doctor_only_context_valid(scene: dict[str, Any]) -> bool:
    return bool(diagnose_doctor_only_context(scene).get("passed"))


def _coach_only_context_valid(scene: dict[str, Any]) -> bool:
    text = str(scene.get("coachOnlyContext") or "").strip()
    if not text:
        return False
    return all(header in text for header in COACH_REQUIRED_HEADERS)


def _actor_profile_valid(scene: dict[str, Any]) -> bool:
    actor_profile = scene.get("actorProfile")
    if not isinstance(actor_profile, dict):
        return False
    name = actor_profile.get("name")
    return isinstance(name, str) and bool(name.strip())


def build_issues(scene: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for field in REQUIRED_FIELDS:
        if is_empty(scene.get(field)):
            issues.append(f"scene.{field}_missing")
    raw_topics = scene.get("productKnowledgeNeeds")
    if raw_topics == DECLINED_PRODUCT_KNOWLEDGE_TOPIC or (
        isinstance(raw_topics, list) and DECLINED_PRODUCT_KNOWLEDGE_TOPIC in raw_topics
    ):
        issues.append("scene.productKnowledgeNeeds_placeholder")
    if not is_empty(scene.get("businessDomainName")) and scene.get("businessDomainName") not in ALLOWED_BUSINESS_DOMAINS:
        issues.append("scene.businessDomainName_invalid")
    issues.extend(_scene_background_issue_codes(scene))
    if not _doctor_only_context_valid(scene):
        issues.append("scene.doctorOnlyContext_invalid")
    if not _coach_only_context_valid(scene):
        issues.append("scene.coachOnlyContext_invalid")
    if not _actor_profile_valid(scene):
        issues.append("scene.actorProfile_invalid")
    return issues


def split_issue_buckets(issues: list[str]) -> tuple[list[str], list[str]]:
    blocking: list[str] = []
    warning: list[str] = []
    for code in issues:
        if code in WARNING_ISSUE_CODES:
            warning.append(code)
        else:
            blocking.append(code)
    return blocking, warning


def build_tbv_issues(scene: dict[str, Any]) -> list[str]:
    """标题 + 场景背景子集校验，用于 PATCH 后轻量门禁。"""
    issues: list[str] = []
    if is_empty(scene.get("title")):
        issues.append("scene.title_missing")
    if is_empty(scene.get("sceneBackground")) and is_empty(scene.get("background")):
        issues.append("scene.sceneBackground_missing")
    issues.extend(_scene_background_issue_codes(scene))
    return issues


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
    validation_report: dict[str, Any],
    *,
    scope_mode: str,
) -> None:
    if not draft_path:
        return
    parent = os.path.dirname(draft_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    existing = _read_draft_object(draft_path.strip())
    prior_meta = existing.get("meta") if isinstance(existing.get("meta"), dict) else {}
    merged_meta: dict[str, Any] = {
        **prior_meta,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "lastStep": STEP,
        "lastValidationScope": scope_mode,
        "lastValidatedSceneHash": validation_report.get("sceneHash"),
        "lastDisplayHash": validation_report.get("displayHash"),
    }
    passed = bool(validation_report.get("passed"))
    if scope_mode == "FULL":
        merged_meta["lastFullValidationPassed"] = passed
        if not passed:
            merged_meta["lastTbvPassed"] = False
    elif scope_mode == "TBV":
        merged_meta["lastTbvPassed"] = passed
    payload = {
        **existing,
        "scene": scene,
        "validationReport": validation_report,
        "meta": merged_meta,
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
    parser.add_argument(
        "--scope",
        default=None,
        help="full（默认）| tbv；也可在输入 JSON 顶层传 validationScope=FULL|TBV",
    )
    args = parser.parse_args()
    OUTPUT_PATH = args.output

    try:
        payload = read_payload(args.input, args.params_file)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        emit_error("invalid_json_input", exit_code=2, hint=str(exc))
    draft_path = None
    scene: dict[str, Any] = {}
    if isinstance(payload.get("scene"), dict):
        scene = payload["scene"]
        draft_path = payload.get("draftPath")
    elif isinstance(payload, dict):
        scene = payload
    if not scene and (args.params_file or (args.input and args.input != "-")):
        draft_path = args.params_file or args.input
        loaded = read_payload(draft_path, None)
        if isinstance(loaded.get("scene"), dict):
            scene = loaded["scene"]
    scene = normalize_scene(scene)
    auto_normalized_doc = bool(scene.pop("__validateAutoNormalizedDoctorContext", False))
    auto_normalized_background = scene.pop("__validateAutoNormalizedSceneBackground", [])
    if not scene:
        emit_error("缺少 scene", exit_code=2)

    scope_token = str(
        args.scope or payload.get("validationScope") or "full"
    ).strip().upper().replace("-", "_")
    scope_mode = "TBV" if scope_token in {"TBV", "TITLE_BACKGROUND"} else "FULL"

    if scope_mode == "TBV":
        all_issues = build_tbv_issues(scene)
        blocking_issues = list(all_issues)
        warning_issues: list[str] = []
    else:
        all_issues = build_issues(scene)
        blocking_issues, warning_issues = split_issue_buckets(all_issues)
    passed = len(blocking_issues) == 0
    scene_hash = compute_scene_hash(scene)
    display_hash = compute_display_hash(scene)
    confirmed_fields = {
        "title": scene.get("title"),
        "sceneBackground": scene.get("sceneBackground"),
        "businessDomainName": scene.get("businessDomainName"),
        "departmentName": scene.get("departmentName"),
        "drugName": scene.get("drugName"),
        "location": scene.get("location"),
        "doctorConcerns": scene.get("doctorConcerns"),
        "repGoal": scene.get("repGoal"),
        "productKnowledgeNeeds": scene.get("productKnowledgeNeeds"),
        "actorProfile": scene.get("actorProfile"),
    }
    validation_report: dict[str, Any] = {
        "scope": scope_mode,
        "passed": passed,
        "sceneHash": scene_hash,
        "displayHash": display_hash,
        "validatedStage": "READY_FOR_VALIDATE",
        "issues": blocking_issues,
        "blockingIssues": blocking_issues,
        "warningIssues": warning_issues,
        "allIssues": all_issues,
    }
    if auto_normalized_doc:
        validation_report["autoNormalized"] = [
            "doctorOnlyContext：## 核心顾虑 已自动合并为至多 2 条 bullet，以满足创建前固定结构校验"
        ]
    if auto_normalized_background:
        existing = validation_report.get("autoNormalized")
        if not isinstance(existing, list):
            existing = []
        validation_report["autoNormalized"] = existing + auto_normalized_background
    doctor_only_canon: dict[str, Any] | None = None
    doctor_only_diagnostics: dict[str, Any] | None = None
    if scope_mode == "FULL":
        doctor_only_canon = {
            "requiredHeaderOrder": list(DOCTOR_REQUIRED_HEADERS),
            "outputRequirementsLines": list(DOCTOR_OUTPUT_REQUIREMENTS_TEMPLATE),
            "endingRulesLines": list(DOCTOR_ENDING_RULES_TEMPLATE),
        }
        doc_diag = diagnose_doctor_only_context(scene)
        if not doc_diag.get("passed"):
            doctor_only_diagnostics = doc_diag

    create_agent_hints: list[str] = []
    if passed and scope_mode == "FULL":
        create_agent_hints = [
            "调用 tbs-scene-create.py 前须先执行 tbs-scene-knowledge-check.py，并携带 meta.knowledgeReady=true。",
            "调用 tbs-scene-create.py 时须在 JSON 顶层设置 displayContractSatisfied=true（或 displayedFields 完整覆盖 mustDisplayFields），并携带 confirmedDisplayHash=validationReport.displayHash，否则返回 display_gate_failed。",
            "仅在已向用户完整展示 mustDisplayFields、且用户明确回复「确认」后，再将 userConfirmation 设为「确认」并携带 scene、validationReport、confirmedDisplayHash 调用创建。",
        ]

    supplement_items = build_supplement_items(scene)
    supplement_render_block = build_supplement_render_block(supplement_items)
    actor_profile_supplement = next(
        (item["value"] for item in supplement_items if item["label"] == "对象角色画像"), ""
    )
    best_practice_supplement = next(
        (item["value"] for item in supplement_items if item["label"] == "代表成功经验/典型话术"), ""
    )

    user_output_template: dict[str, Any] = {
        "stage": "READY_TO_CONFIRM" if passed else "GAP_ASKING",
        "stageLabel": "可发起最终确认" if passed else "待补齐后再校验",
        "confirmationItems": build_confirmation_items(scene, CONFIRM_DISPLAY_FIELDS),
        "mustDisplayFields": MUST_DISPLAY_FIELDS,
        "displayHash": display_hash,
        "mustDisplayLabels": [FIELD_LABELS.get(field, field) for field in MUST_DISPLAY_FIELDS],
        "mustDisplayConfirmationItems": build_confirmation_items(scene, MUST_DISPLAY_FIELDS),
        "actorProfileSummary": _stringify_value(scene.get("actorProfile"), "actorProfile"),
        "supplementItems": supplement_items,
        "mustDisplaySupplementItems": bool(supplement_items),
        "supplementRenderBlock": supplement_render_block,
        "actorProfileSupplement": actor_profile_supplement,
        "bestPracticeSupplement": best_practice_supplement,
        "issueHints": issues_to_hints(blocking_issues, scene=scene),
        "warningHints": issues_to_hints(warning_issues, scene=scene),
        "mustShowSceneBackgroundFullText": bool(
            str(scene.get("sceneBackground") or scene.get("background") or "").strip()
        ),
        "sceneBackgroundFullText": str(
            scene.get("sceneBackground") or scene.get("background") or ""
        ).strip(),
        "nextAction": (
            "可直接回复【确认】或【取消】；也可先按提示优化后再确认"
            if passed and warning_issues
            else "请回复【确认】或【取消】"
            if passed
            else "请根据提示补齐或修正后重新校验"
        ),
    }
    if doctor_only_canon is not None:
        user_output_template["doctorOnlyContextCanon"] = doctor_only_canon
    if doctor_only_diagnostics is not None:
        user_output_template["doctorOnlyContextDiagnostics"] = doctor_only_diagnostics
    if create_agent_hints:
        user_output_template["createAgentHints"] = create_agent_hints
    if not passed and scope_mode == "FULL":
        user_output_template["preCreateBlockedReminder"] = (
            "当前 validationReport.passed=false，不得调用 tbs-scene-create；"
            "须先用自然语言向用户说明待修正项，修复并重新校验通过后，再请用户确认创建。"
        )

    result: dict[str, Any] = {
        "step": STEP,
        "scene": scene,
        "passed": passed,
        "validationReport": validation_report,
        "confirmedFields": confirmed_fields,
        "userOutputTemplate": user_output_template,
    }
    if scope_mode == "TBV":
        result["tbvReport"] = {
            "passed": passed,
            "blockingIssues": blocking_issues,
            "warningIssues": warning_issues,
        }

    if isinstance(draft_path, str) and draft_path.strip():
        maybe_write_draft(
            draft_path.strip(), scene, validation_report, scope_mode=scope_mode
        )
        result["draftPath"] = draft_path.strip()

    emit_success(result)


if __name__ == "__main__":
    main()
