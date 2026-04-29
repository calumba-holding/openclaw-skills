"""
Parse TBS scene input and output staged confirmation guidance.
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


STEP = "tbs-scene-parse"
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
TEXT_FIELD_LABELS = {
    "title": "场景标题",
    "businessDomainName": "业务领域",
    "departmentName": "科室",
    "drugName": "产品名称",
    "location": "地点",
    "doctorConcerns": "医生顾虑",
    "repGoal": "代表目标",
    "sceneBackground": "场景背景",
    "productKnowledgeNeeds": "产品知识主题",
    "knowledge": "产品知识正文（可选）",
    "doctorOnlyContext": "对练对象侧上下文",
    "coachOnlyContext": "教练侧上下文",
    "actorProfile": "对练对象角色",
    "generationNotes": "待确认说明",
}

TEXT_DEFAULTS = {
    "notProvidedEvidenceSource": "用户确认暂无书面证据资料",
    "declinedProductKnowledgeTopic": "用户确认暂不补充产品知识主题",
    "partialEvidenceSource": "用户已确认场景所需产品知识主题，书面证据待补充",
    "readyEvidenceSource": "用户已提供可用证据资料",
}

TEXT_PATTERN_RULES = {
    "declineRegexPatterns": [
        "产品知识暂无",
        "没有产品知识|无需产品知识|不提供产品知识",
        "不要产品知识",
        "不提供.*(产品知识|知识主题)",
        "不提供.*(资料|证据).*(产品|书面)",
        "暂不补充.*(知识|资料)",
    ],
    "blockedPhrases": [
        "确认",
        "是",
        "不是",
        "对",
        "不对",
        "好的",
        "ok",
        "yes",
        "no",
        "暂无",
        "没有",
        "不清楚",
    ],
}

TEXT_LIMITS = {
    "deriveLimits": {
        "minTopicLength": 2,
        "maxTopicLength": 30,
        "maxTopicCount": 6,
    },
    "alignmentLimits": {
        "minBackgroundLength": 40,
        "minPieceLength": 3,
        "missingPiecePreviewLength": 24,
        "maxMissingPieces": 5,
    },
    "inferReplyLimits": {
        "maxCandidateLength": 40,
    },
}

TEXT_STATUS_AND_ALIGNMENT = {
    "statusText": {
        "toFill": "待补充",
        "toConfirm": "请确认",
        "confirmed": "已确认",
        "needSupplement": "需要补充",
        "noSupplementNeeded": "无需补充",
        "ready": "已具备",
        "pendingStart": "待开始",
        "pendingConfirm": "待确认",
    },
    "alignmentText": {
        "noBackground": "场景背景尚未生成，暂不做对齐评估。",
        "backgroundTooShort": "场景背景偏短，不建议跳过场景正文生成。",
        "missingCoreInputs": "缺少医生顾虑与代表目标，无法做对齐判断。",
        "missingRepGoalLabel": "代表目标",
        "coreNotCoveredPrefix": "场景背景未完全覆盖以下要点：",
        "coveredOk": "场景背景已覆盖医生顾虑与代表目标要点，可建议跳过场景正文再生成。",
    },
    "changeSummaryText": {
        "updatedFields": "本轮字段更新：{labels}。",
        "canSkipS3": "编排提示：可跳过 scenario-json-parse 再生成，但仍须走 TBV 与 PRE。",
        "shouldRunS3": "编排提示：建议执行 scenario-json-parse 完整生成或补全后再校验。",
    },
}

TEXT_STAGE_NOTES_AND_QUESTIONS = {
    "pendingNotesText": {
        "baseInfoStage": "当前先确认业务领域、科室、产品、地点、医生顾虑、代表目标；标题、场景背景和上下文稍后统一生成。",
        "knowledgeStageBaseAck": "基础信息已由用户确认，系统已根据当前场景给出产品知识主题建议；如无调整，请回复“确认”，也可删除、改名或新增主题。产品知识正文可稍后补充。",
        "knowledgeStageBaseUnack": "基础信息字段已识别，但仍需用户核对是否准确；核对无误后请由 Agent 在下一轮解析请求中携带 baseInfoAcknowledged=true，再进入场景内容生成。",
        "knowledgeStageOptionalKnowledge": "产品知识正文补充是可选的：可以只确认知识主题关键词，也可以额外补充知识正文/资料来源供创建前解析。",
        "readyForGeneration": "基础信息与产品知识/资料已具备；此时应在内部执行场景内容生成，再进入校验。",
        "autoDerivedNeeds": "已按产品知识主题生成规范建议主题，需用户确认后再进入场景内容生成。",
        "bestPracticeAdopted": "已采纳你补充的代表话术/最佳实践内容，将归入教练侧上下文（coachOnlyContext）的“## 最佳实践”小节。",
    },
    "baseQuestionMap": {
        "businessDomainName": "这是哪个业务领域？请从临床推广、院外零售、学术合作、通用能力中选择一个。",
        "departmentName": "这次主要对应哪个科室？",
        "drugName": "这次对应的具体产品或品种是什么？",
        "location": "这个场景发生在什么地点？",
        "doctorConcerns": "医生当前最核心的顾虑是什么？",
        "repGoal": "代表本次沟通最想达成的目标是什么？",
    },
    "knowledgeQuestionText": {
        "backgroundHintAck": "已确认的业务背景",
        "backgroundHintUnack": "当前识别出的业务背景（请同时核对上方基础信息是否准确）",
        "confirmNeeds": "请核对上方“产品知识主题”：如无调整，请回复“确认”；也可以删除、改名或新增主题。正文可稍后补充。",
        "confirmBaseFirst": "请先明确确认上方基础信息是否全部准确；确认后由 Agent 在下一轮 tbs-scene-parse 请求中设置 baseInfoAcknowledged=true。",
    },
    "contentQuestionText": {
        "echoUpdated": "本轮用户已更新：{labels}。请先向用户回显更新后的确认清单并请其确认。",
        "genTitleBackground": "请在内部生成场景标题与场景背景。",
        "genActorProfile": "请在内部补齐对练对象角色画像（至少包含 name）；不向用户单独展示该字段确认项。",
        "genContexts": "请在内部生成对练对象侧上下文与教练侧上下文，用户无需逐段确认正文。",
    },
}

TEXT_ACTION_HINTS = {
    "nextActionText": {
        "baseInfo": "请先补充并确认基础信息；确认后再分析产品知识需求与资料情况。",
        "knowledgeBaseFirst": "请先引导用户核对基础信息是否准确；用户明确确认后，在下一轮解析请求 JSON 顶层设置 baseInfoAcknowledged=true，再继续确认产品知识/资料并进入内部生成。",
        "knowledge": "请展示基础信息 6 项和系统建议的产品知识主题；如无调整请用户回复“确认”，也允许删除、改名或新增。产品知识正文补充可选。",
        "readyForGenerationWithEcho": "请先向用户回显更新后的确认清单（重点：{labels}），确认无误后再内部生成场景内容；生成完成后重新运行本脚本并进入场景校验。",
        "readyForGeneration": "请在内部执行场景内容生成；生成完成后重新运行本脚本，再进入场景校验。",
        "readyForValidateWithEcho": "用户本轮已更新（{labels}），请先回显最新确认清单并确认无误，再执行场景校验。",
        "default": "请确认上述关键信息；如无误，可以继续执行场景校验。",
    },
    "systemActionHintText": {
        "baseInfo": "先与用户确认基础信息；此阶段不要提前执行 scenario-json-parse 全量生成。",
        "knowledgeBaseFirst": "先引导用户核对基础信息；未携带 baseInfoAcknowledged=true 前，不要进入 scenario-json-parse 全量生成。",
        "knowledge": "按 references/product-knowledge-topic-generate.md 基于已确认基础信息生成产品知识主题，并给用户轻确认；未收到主题确认前，不要进入场景内容生成。",
        "readyForGenerationWithEcho": "检测到用户本轮更新字段（{labels}）；先向用户回显更新后的确认清单，再内部读取 references/scenario-json-parse.md + references/*.json 生成内容。",
        "readyForGeneration": "现在再内部读取 references/scenario-json-parse.md + references/*.json，生成 title、sceneBackground、actorProfile、doctorOnlyContext、coachOnlyContext。",
        "readyForValidateWithEcho": "检测到用户本轮更新字段（{labels}）；先回显更新后的确认清单，再执行 tbs-scene-validate.py。",
        "default": "执行 tbs-scene-validate.py，确认是否达到最终创建前门禁。",
    },
}

TEXT_STAGE_TITLES_AND_ERRORS = {
    "stageLabelText": {
        "BASE_INFO_CONFIRM": "先确认基础信息",
        "KNOWLEDGE_CONFIRM": "再确认产品知识与资料",
        "READY_FOR_SCENE_GENERATION": "已可内部生成场景内容",
        "READY_FOR_VALIDATE": "已可执行场景校验",
    },
    "phaseTitleText": {
        "BASE_INFO_CONFIRM": "基础信息确认",
        "KNOWLEDGE_CONFIRM": "产品知识与资料确认",
        "READY_FOR_SCENE_GENERATION": "场景内容生成",
    },
    "errorText": {
        "missingInput": "缺少 userText 或结构化 scene",
        "patchLockedHint": "在基础信息已确认后不可再补丁修改基础字段；进入场景内容生成或校验阶段后，仅允许补丁更新场景标题与场景背景（含 background 同义键）。",
        "patchLockedPastKnowledgeSuffix": " 已进入场景内容生成或校验阶段：`parsedFields` / `userUpdates` / `userConfirmedFields` / `userProvidedFields` 仅允许 `title`、`sceneBackground`、`background`。被拒字段请改写到请求 JSON 顶层的 `scene` 对象中（与已有草稿合并）后再调用本脚本，勿再通过上述补丁键覆盖。",
        "patchLockedBaseAckSuffix": " 被拒字段属于已确认基础六字段：请先在未声明 `baseInfoAcknowledged` 的轮次纠正，或由用户明确同意回退后再改；勿再通过补丁键覆盖已锁定基础项。",
    },
}

TEXT_CONFIG: dict[str, Any] = {
    "fieldLabels": TEXT_FIELD_LABELS,
    "defaults": TEXT_DEFAULTS,
    **TEXT_PATTERN_RULES,
    **TEXT_LIMITS,
    **TEXT_STATUS_AND_ALIGNMENT,
    **TEXT_STAGE_NOTES_AND_QUESTIONS,
    **TEXT_ACTION_HINTS,
    **TEXT_STAGE_TITLES_AND_ERRORS,
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_external_text_config() -> dict[str, Any]:
    config_path = Path(__file__).resolve().parents[1] / "references" / "parse-runtime-config.json"
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("parse-runtime-config.json must contain a JSON object")
    return data


TEXT_CONFIG = _deep_merge(TEXT_CONFIG, _load_external_text_config())


def _cfg(path: str, default: Any = None) -> Any:
    cursor: Any = TEXT_CONFIG
    for key in path.split("."):
        if not isinstance(cursor, dict) or key not in cursor:
            return default
        cursor = cursor[key]
    return cursor


FIELD_LABELS = dict(_cfg("fieldLabels", {}))
BASE_CONFIRM_FIELDS = [
    "businessDomainName",
    "departmentName",
    "drugName",
    "location",
    "doctorConcerns",
    "repGoal",
]
KNOWLEDGE_CONFIRM_FIELDS = [
    "productKnowledgeNeeds",
]
KNOWLEDGE_GATE_FIELDS: list[str] = []
GENERATED_CONFIRM_FIELDS = [
    "title",
    "sceneBackground",
]
GENERATED_STAGE_FIELDS = [
    "title",
    "sceneBackground",
    "actorProfile",
]
PATCHABLE_AFTER_KNOWLEDGE_LOCK = {"title", "sceneBackground", "background"}
GENERATED_GATE_FIELDS: list[str] = []
INTERNAL_GENERATED_FIELDS = [
    "doctorOnlyContext",
    "coachOnlyContext",
]
BASE_PLUS_KNOWLEDGE_FIELDS = BASE_CONFIRM_FIELDS + KNOWLEDGE_CONFIRM_FIELDS
READY_CONFIRM_FIELDS = BASE_PLUS_KNOWLEDGE_FIELDS + GENERATED_CONFIRM_FIELDS
FINAL_MUST_DISPLAY_FIELDS = BASE_PLUS_KNOWLEDGE_FIELDS + GENERATED_CONFIRM_FIELDS + ["actorProfile"]
FINAL_REQUIRED_FIELDS = (
    BASE_CONFIRM_FIELDS
    + KNOWLEDGE_CONFIRM_FIELDS
    + KNOWLEDGE_GATE_FIELDS
    + GENERATED_STAGE_FIELDS
    + GENERATED_GATE_FIELDS
    + INTERNAL_GENERATED_FIELDS
)


def _read_output_templates_md() -> str:
    path = Path(__file__).resolve().parents[1] / "references" / "output-templates.md"
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _extract_template_block(md: str, *, template_no: int) -> str:
    """
    Extract ```text ... ``` block under '#### 模板 X' heading.
    """
    if not md:
        return ""
    marker = f"#### 模板 {template_no}："
    idx = md.find(marker)
    if idx < 0:
        return ""
    tail = md[idx:]
    fence = "```text"
    start = tail.find(fence)
    if start < 0:
        return ""
    start = start + len(fence)
    end = tail.find("```", start)
    if end < 0:
        return ""
    return tail[start:end].strip("\n")


def _format_confirmation_items_for_slots(items: list[dict[str, str]], *, prefix: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for i, it in enumerate(items, start=1):
        out[f"{prefix}_{i}_label"] = str(it.get("label") or "").strip()
        out[f"{prefix}_{i}_value"] = str(it.get("value") or "").strip() or "待补充"
    return out


def _format_topics_lines(topics: Any) -> str:
    if isinstance(topics, str):
        items = [topics]
    elif isinstance(topics, list):
        items = topics
    else:
        items = []
    clean = [str(t).strip() for t in items if str(t).strip()]
    if not clean:
        return "（无）"
    return "\n".join(f"  {i+1}. {t}" for i, t in enumerate(clean))


def _knowledge_items_if_recently_updated_else_omit(scene: dict[str, Any], *, knowledge_ready: bool) -> str:
    """
    For final confirmation: avoid misleading '当前未提供正文' when knowledge is already linked.
    """
    knowledge_ids = scene.get("knowledgeIds") if isinstance(scene.get("knowledgeIds"), list) else []
    linked = [str(x).strip() for x in knowledge_ids if str(x).strip()]
    if knowledge_ready and linked:
        return f"已关联系统知识条目（{len(linked)} 条），无需额外正文；如需更贴近真实，可选补充每个主题的要点/数据口径/注意事项（几条即可）。"
    # If user really provided content, show a short bullets list.
    knowledge = scene.get("knowledge")
    items: list[dict[str, Any]] = []
    if isinstance(knowledge, list):
        items = [x for x in knowledge if isinstance(x, dict)]
    elif isinstance(knowledge, dict):
        items = [knowledge]
    provided = []
    for it in items:
        title = str(it.get("title") or "").strip()
        content = str(it.get("content") or "").strip()
        if not title and not content:
            continue
        if content:
            preview = content if len(content) <= 120 else content[:120] + "…"
            provided.append(f"  - {title or '（未命名主题）'}：{preview}")
    if provided:
        return "\n".join(provided)
    return "可选补充正文要点（不影响推进）。"


def _render_user_visible_text_from_templates(
    *,
    template_no: int,
    stage_label: str,
    user_output: dict[str, Any],
    scene: dict[str, Any],
) -> str:
    md = _read_output_templates_md()
    tmpl = _extract_template_block(md, template_no=template_no)
    if not tmpl:
        return ""

    confirmation_items = user_output.get("confirmationItems") if isinstance(user_output.get("confirmationItems"), list) else []
    must_items = (
        user_output.get("mustDisplayConfirmationItems")
        if isinstance(user_output.get("mustDisplayConfirmationItems"), list)
        else []
    )

    # slots
    mapping: dict[str, str] = {"stageLabel": stage_label}
    mapping.update(_format_confirmation_items_for_slots(confirmation_items, prefix="field"))
    mapping.update(_format_confirmation_items_for_slots(must_items, prefix="mustDisplayField"))

    missing_labels = user_output.get("missingLabels") if isinstance(user_output.get("missingLabels"), list) else []
    mapping["missingLabels"] = "（无）" if not missing_labels else "、".join(str(x).strip() for x in missing_labels if str(x).strip())

    clarify = user_output.get("clarifyQuestions") if isinstance(user_output.get("clarifyQuestions"), list) else []
    for i, q in enumerate(clarify[:2], start=1):
        mapping[f"clarifyQuestion_{i}"] = str(q).strip()

    # knowledge
    mapping["productKnowledgeNeedsItems"] = _format_topics_lines(scene.get("productKnowledgeNeeds"))
    mapping["knowledgeItemsOrNotProvidedHint"] = "可选补充正文要点（不影响推进）。"
    mapping["knowledgeItemsIfRecentlyUpdatedElseOmit"] = _knowledge_items_if_recently_updated_else_omit(
        scene, knowledge_ready=bool(user_output.get("knowledgeReady"))
    )

    # supplements
    actor_profile_summary = ""
    actor = scene.get("actorProfile")
    if isinstance(actor, dict):
        name = str(actor.get("name") or "").strip()
        title = str(actor.get("title") or "").strip()
        desc = str(actor.get("description") or "").strip()
        actor_profile_summary = "；".join([x for x in [title, name, desc] if x])
    mapping["actorProfileSummary"] = actor_profile_summary or "（未提供）"

    mapping["actorProfileSupplementOrOmit"] = str(user_output.get("actorProfileSupplement") or "").strip() or "（未提供）"
    mapping["bestPracticeSupplementOrOmit"] = str(user_output.get("bestPracticeSupplement") or "").strip() or "（未提供）"

    # Replace placeholders
    out = tmpl
    for k, v in mapping.items():
        out = out.replace("{" + k + "}", str(v))
    # Drop any unreplaced placeholder lines to avoid leaking internals
    out_lines = []
    for line in out.splitlines():
        if "{" in line and "}" in line:
            # if still contains placeholder token, omit the line
            if re.search(r"\{[a-zA-Z0-9_]+\}", line):
                continue
        out_lines.append(line)
    return "\n".join(out_lines).strip() + "\n"
STAGE_BASE_INFO_CONFIRM = "BASE_INFO_CONFIRM"
STAGE_KNOWLEDGE_CONFIRM = "KNOWLEDGE_CONFIRM"
STAGE_READY_FOR_SCENE_GENERATION = "READY_FOR_SCENE_GENERATION"
STAGE_READY_FOR_VALIDATE = "READY_FOR_VALIDATE"
STAGE_CONFIRM_FIELDS = {
    STAGE_BASE_INFO_CONFIRM: BASE_CONFIRM_FIELDS,
    STAGE_KNOWLEDGE_CONFIRM: BASE_PLUS_KNOWLEDGE_FIELDS,
    STAGE_READY_FOR_SCENE_GENERATION: READY_CONFIRM_FIELDS,
    STAGE_READY_FOR_VALIDATE: READY_CONFIRM_FIELDS,
}
STAGE_MUST_DISPLAY_FIELDS = {
    STAGE_BASE_INFO_CONFIRM: list(BASE_CONFIRM_FIELDS),
    STAGE_KNOWLEDGE_CONFIRM: list(BASE_PLUS_KNOWLEDGE_FIELDS),
    STAGE_READY_FOR_SCENE_GENERATION: list(READY_CONFIRM_FIELDS),
    STAGE_READY_FOR_VALIDATE: list(FINAL_MUST_DISPLAY_FIELDS),
}
BEST_PRACTICE_TARGET_SECTION = "coachOnlyContext.## 最佳实践"
SUPPLEMENT_SCENE_FIELDS = (
    "actorProfileSupplement",
    "bestPracticeSupplement",
)

DEFAULT_DECLINED_PRODUCT_KNOWLEDGE_TOPIC = str(
    _cfg("defaults.declinedProductKnowledgeTopic", "")
).strip()
DECLINE_REGEX_PATTERNS = tuple(_cfg("declineRegexPatterns", []))
DERIVE_MIN_TOPIC_LENGTH = int(_cfg("deriveLimits.minTopicLength", 2))
DERIVE_MAX_TOPIC_LENGTH = int(_cfg("deriveLimits.maxTopicLength", 30))
DERIVE_MAX_TOPIC_COUNT = int(_cfg("deriveLimits.maxTopicCount", 6))
ALIGNMENT_MIN_BACKGROUND_LENGTH = int(_cfg("alignmentLimits.minBackgroundLength", 40))
ALIGNMENT_MIN_PIECE_LENGTH = int(_cfg("alignmentLimits.minPieceLength", 3))
ALIGNMENT_MISSING_PREVIEW_LENGTH = int(
    _cfg("alignmentLimits.missingPiecePreviewLength", 24)
)
ALIGNMENT_MAX_MISSING_PIECES = int(_cfg("alignmentLimits.maxMissingPieces", 5))
INFER_REPLY_MAX_CANDIDATE_LENGTH = int(_cfg("inferReplyLimits.maxCandidateLength", 40))
BLOCKED_PHRASES = {str(item).lower() for item in _cfg("blockedPhrases", [])}
BEST_PRACTICE_KEYWORDS = tuple(str(item) for item in _cfg("bestPracticeKeywords", []))
BASE_QUESTION_MAP = dict(_cfg("baseQuestionMap", {}))
STAGE_LABEL_TEXT = dict(_cfg("stageLabelText", {}))
PHASE_TITLE_TEXT = dict(_cfg("phaseTitleText", {}))
STATUS_TEXT = dict(_cfg("statusText", {}))
ALIGNMENT_TEXT = dict(_cfg("alignmentText", {}))
CHANGE_SUMMARY_TEXT = dict(_cfg("changeSummaryText", {}))
PENDING_NOTES_TEXT = dict(_cfg("pendingNotesText", {}))
KNOWLEDGE_QUESTION_TEXT = dict(_cfg("knowledgeQuestionText", {}))
CONTENT_QUESTION_TEXT = dict(_cfg("contentQuestionText", {}))
NEXT_ACTION_TEXT = dict(_cfg("nextActionText", {}))
SYSTEM_ACTION_HINT_TEXT = dict(_cfg("systemActionHintText", {}))
ERROR_TEXT = dict(_cfg("errorText", {}))


def _text(section: dict[str, Any], key: str, default: str = "") -> str:
    return str(section.get(key, default)).strip()


def _textf(section: dict[str, Any], key: str, **kwargs: Any) -> str:
    return _text(section, key).format(**kwargs)


def _validate_parse_config() -> None:
    required_text_sections = [
        "fieldLabels",
        "pendingNotesText",
        "baseQuestionMap",
        "stageLabelText",
        "phaseTitleText",
    ]
    missing_sections = [key for key in required_text_sections if _cfg(key) is None]
    if missing_sections:
        raise ValueError(
            "tbs-scene-parse config missing sections: " + ", ".join(missing_sections)
        )

    referenced_fields = set(
        BASE_CONFIRM_FIELDS
        + FINAL_MUST_DISPLAY_FIELDS
        + KNOWLEDGE_CONFIRM_FIELDS
        + KNOWLEDGE_GATE_FIELDS
        + GENERATED_CONFIRM_FIELDS
        + GENERATED_STAGE_FIELDS
        + INTERNAL_GENERATED_FIELDS
        + ["generationNotes", "knowledge", "actorProfile"]
    )
    missing_labels = sorted(field for field in referenced_fields if field not in FIELD_LABELS)
    if missing_labels:
        raise ValueError(
            "fieldLabels missing referenced fields: " + ", ".join(missing_labels)
        )

    stage_keys = {
        STAGE_BASE_INFO_CONFIRM,
        STAGE_KNOWLEDGE_CONFIRM,
        STAGE_READY_FOR_SCENE_GENERATION,
        STAGE_READY_FOR_VALIDATE,
    }
    if set(STAGE_CONFIRM_FIELDS.keys()) != stage_keys:
        raise ValueError("STAGE_CONFIRM_FIELDS keys inconsistent with stage constants")
    if set(STAGE_MUST_DISPLAY_FIELDS.keys()) != stage_keys:
        raise ValueError("STAGE_MUST_DISPLAY_FIELDS keys inconsistent with stage constants")

    for stage, fields in STAGE_CONFIRM_FIELDS.items():
        if len(fields) != len(set(fields)):
            raise ValueError(f"STAGE_CONFIRM_FIELDS[{stage}] contains duplicate fields")
        unknown = [field for field in fields if field not in FIELD_LABELS]
        if unknown:
            raise ValueError(
                f"STAGE_CONFIRM_FIELDS[{stage}] contains unknown labels: {', '.join(unknown)}"
            )
    for stage, fields in STAGE_MUST_DISPLAY_FIELDS.items():
        if len(fields) != len(set(fields)):
            raise ValueError(f"STAGE_MUST_DISPLAY_FIELDS[{stage}] contains duplicate fields")
        unknown = [field for field in fields if field not in FIELD_LABELS]
        if unknown:
            raise ValueError(
                f"STAGE_MUST_DISPLAY_FIELDS[{stage}] contains unknown labels: {', '.join(unknown)}"
            )

    missing_base_questions = sorted(
        field for field in BASE_CONFIRM_FIELDS if field not in BASE_QUESTION_MAP
    )
    if missing_base_questions:
        raise ValueError(
            "baseQuestionMap missing base fields: " + ", ".join(missing_base_questions)
        )
    extra_base_questions = sorted(
        field for field in BASE_QUESTION_MAP if field not in BASE_CONFIRM_FIELDS
    )
    if extra_base_questions:
        raise ValueError(
            "baseQuestionMap contains non-base fields: " + ", ".join(extra_base_questions)
        )

    if "title" not in FINAL_MUST_DISPLAY_FIELDS or "sceneBackground" not in FINAL_MUST_DISPLAY_FIELDS:
        raise ValueError("FINAL_MUST_DISPLAY_FIELDS must include title and sceneBackground")

    best_practice_note = _text(PENDING_NOTES_TEXT, "bestPracticeAdopted")
    if not best_practice_note:
        raise ValueError("pendingNotesText.bestPracticeAdopted must be configured")
    if not BEST_PRACTICE_TARGET_SECTION.startswith("coachOnlyContext."):
        raise ValueError("BEST_PRACTICE_TARGET_SECTION must target coachOnlyContext")


_validate_parse_config()


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


def _summary(payload: dict[str, Any], *, ok: bool) -> str:
    parts = ["OK" if ok else "ERROR", STEP]
    if payload.get("stage"):
        parts.append(f"stage={payload['stage']}")
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


def _load_draft_scene_for_merge(draft_path: str | None) -> dict[str, Any]:
    if not draft_path or not str(draft_path).strip():
        return {}
    path = str(draft_path).strip()
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    scene = data.get("scene")
    if isinstance(scene, dict):
        return dict(scene)
    # Compat: some orchestrators may overwrite draftPath with a "scene-only" JSON (no {scene, meta} wrapper).
    # Treat that top-level object as scene if it looks like one, so later merges don't lose confirmed fields.
    scene_like_keys = {
        "businessDomainName",
        "departmentName",
        "drugName",
        "location",
        "doctorConcerns",
        "repGoal",
        "productKnowledgeNeeds",
        "title",
        "sceneBackground",
        "background",
        "actorProfile",
    }
    if any(key in data for key in scene_like_keys):
        return dict(data)
    return {}


def _truthy_signal(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "确认"}
    return False


def normalize_payload_shape(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    normalized = dict(payload)
    warnings: list[str] = []
    scene = dict(normalized.get("scene")) if isinstance(normalized.get("scene"), dict) else {}

    top_level_topics = normalized.get("productKnowledgeNeeds")
    if not is_empty(top_level_topics) and is_empty(scene.get("productKnowledgeNeeds")):
        scene["productKnowledgeNeeds"] = top_level_topics
        warnings.append(
            "migrated_top_level_productKnowledgeNeeds_to_scene_productKnowledgeNeeds"
        )

    for field in SUPPLEMENT_SCENE_FIELDS:
        top_level_value = normalized.get(field)
        if not is_empty(top_level_value) and is_empty(scene.get(field)):
            scene[field] = top_level_value
            warnings.append(f"migrated_top_level_{field}_to_scene_{field}")

    draft_scene = _load_draft_scene_for_merge(normalized.get("draftPath"))
    should_merge_draft_scene = bool(draft_scene) and bool(scene) and (
        _truthy_signal(normalized.get("baseInfoAcknowledged"))
        or _truthy_signal(scene.get("baseInfoAcknowledged"))
        or _truthy_signal(normalized.get("productKnowledgeNeedsConfirmed"))
        or _truthy_signal(scene.get("productKnowledgeNeedsConfirmed"))
    )
    if should_merge_draft_scene:
        missing_confirmed_fields = [
            field
            for field in BASE_CONFIRM_FIELDS + KNOWLEDGE_CONFIRM_FIELDS
            if field in draft_scene and is_empty(scene.get(field))
        ]
        if missing_confirmed_fields:
            scene = _deep_merge(draft_scene, scene)
            warnings.append(
                "merged_scene_from_existing_draft_for_missing_fields:"
                + ",".join(missing_confirmed_fields)
            )

    normalized["scene"] = scene
    return normalized, warnings


def _user_text_declines_product_knowledge(user_text: str) -> bool:
    s = (user_text or "").strip()
    if not s:
        return False
    for pattern in DECLINE_REGEX_PATTERNS:
        if re.search(str(pattern), s):
            return True
    return False


def _should_auto_decline_product_knowledge(
    user_text: str, scene: dict[str, Any], payload: dict[str, Any]
) -> bool:
    if payload.get("declineProductKnowledge") is True:
        return True
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    if meta.get("declineProductKnowledge") is True:
        return True
    if scene.get("declineProductKnowledge") is True:
        return True
    return _user_text_declines_product_knowledge(user_text)


def _is_declined_topic_placeholder(value: str) -> bool:
    text = re.sub(r"\s+", "", str(value or ""))
    placeholder = re.sub(r"\s+", "", DEFAULT_DECLINED_PRODUCT_KNOWLEDGE_TOPIC)
    return bool(placeholder and text == placeholder)


def _has_knowledge_content(value: Any) -> bool:
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and str(item.get("content") or "").strip():
                return True
            if isinstance(item, str) and item.strip():
                return True
    if isinstance(value, dict):
        if str(value.get("content") or "").strip():
            return True
        items = value.get("items")
        if isinstance(items, list):
            return _has_knowledge_content(items)
    if isinstance(value, str):
        return bool(value.strip())
    return False


def _derive_product_knowledge_needs(scene: dict[str, Any], user_text: str) -> list[str]:
    # Primary topic generation is governed by references/product-knowledge-topic-generate.md.
    # This function only preserves user-provided knowledge headings; it does not create business topics.
    _ = user_text
    candidates: list[str] = []
    concern_values = scene.get("doctorConcerns")
    if isinstance(concern_values, list):
        concern_texts = {str(item).strip() for item in concern_values if str(item).strip()}
    elif isinstance(concern_values, str) and concern_values.strip():
        concern_texts = {concern_values.strip()}
    else:
        concern_texts = set()
    knowledge = scene.get("knowledge")
    if isinstance(knowledge, list):
        for item in knowledge:
            if isinstance(item, dict):
                for key in ("title", "category"):
                    text = str(item.get(key) or "").strip()
                    if text:
                        candidates.append(text)
            elif isinstance(item, str) and item.strip():
                candidates.append(item.strip())
    elif isinstance(knowledge, dict):
        for key in ("title", "category"):
            text = str(knowledge.get(key) or "").strip()
            if text:
                candidates.append(text)

    normalized: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        text = re.sub(r"\s+", " ", str(item or "").strip())
        if len(text) < DERIVE_MIN_TOPIC_LENGTH:
            continue
        if text in concern_texts:
            continue
        if len(text) > DERIVE_MAX_TOPIC_LENGTH:
            text = text[:DERIVE_MAX_TOPIC_LENGTH].rstrip("，,。；; ")
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(text)
        if len(normalized) >= DERIVE_MAX_TOPIC_COUNT:
            break
    return normalized


def _normalize_topic_list(value: Any) -> list[str]:
    items: list[str] = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str) and item.strip():
                items.append(item.strip())
            elif isinstance(item, dict):
                for key in ("title", "name", "topic"):
                    text = str(item.get(key) or "").strip()
                    if text:
                        items.append(text)
                        break
    elif isinstance(value, str) and value.strip():
        items.append(value.strip())

    normalized: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = re.sub(r"\s+", " ", item).strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        normalized.append(item)
    return normalized


def _resolve_existing_knowledge_topics(payload: dict[str, Any], scene: dict[str, Any]) -> list[str]:
    candidates = [
        payload.get("existingKnowledgeTopics"),
        payload.get("existingProductKnowledgeTopics"),
    ]
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    if meta:
        candidates.extend(
            [
                meta.get("existingKnowledgeTopics"),
                meta.get("existingProductKnowledgeTopics"),
            ]
        )
    if isinstance(scene, dict):
        candidates.extend(
            [scene.get("existingKnowledgeTopics"), scene.get("existingProductKnowledgeTopics")]
        )

    for candidate in candidates:
        topics = _normalize_topic_list(candidate)
        if topics:
            return topics
    return []


def _build_knowledge_topic_buckets(
    scene: dict[str, Any], payload: dict[str, Any], stage: str
) -> dict[str, Any]:
    if stage != STAGE_KNOWLEDGE_CONFIRM:
        return {}

    confirmed_topics = _normalize_topic_list(scene.get("productKnowledgeNeeds"))
    existing_topics = _resolve_existing_knowledge_topics(payload, scene)
    existing_keys = {item.lower() for item in existing_topics}
    suggested_missing_topics = [item for item in confirmed_topics if item.lower() not in existing_keys]

    return {
        "existingTopics": existing_topics,
        "suggestedMissingTopics": suggested_missing_topics,
        "existingTopicsSource": (
            "provided_by_caller" if existing_topics else "not_provided_or_empty"
        ),
    }


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        texts = [item for item in value if isinstance(item, str) and item.strip()]
        return len(texts) == 0
    return False


def normalize_scene(
    scene: dict[str, Any], user_text: str, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    out = dict(scene)
    payload = payload if isinstance(payload, dict) else {}
    base_acknowledged = _base_info_acknowledged(out, payload)
    # 证据相关字段已退出当前流程：统一移除历史草稿遗留值，避免误导后续阶段判断。
    for key in (
        "needEvidenceConfirmation",
        "needsEvidenceConfirmation",
        "productEvidenceStatus",
        "productEvidenceSource",
    ):
        out.pop(key, None)

    background = out.get("sceneBackground") or out.get("background") or ""
    if isinstance(background, str) and background.strip():
        out["sceneBackground"] = background.strip()
        out["background"] = background.strip()

    doctor_concerns = out.get("doctorConcerns")
    if isinstance(doctor_concerns, list):
        out["doctorConcerns"] = [
            item.strip() for item in doctor_concerns if isinstance(item, str) and item.strip()
        ]
    elif isinstance(doctor_concerns, str) and doctor_concerns.strip():
        out["doctorConcerns"] = doctor_concerns.strip()

    product_knowledge_needs = out.get("productKnowledgeNeeds")
    removed_declined_topic_placeholder = False
    if isinstance(product_knowledge_needs, str) and product_knowledge_needs.strip():
        topic = product_knowledge_needs.strip()
        removed_declined_topic_placeholder = _is_declined_topic_placeholder(topic)
        out["productKnowledgeNeeds"] = [] if removed_declined_topic_placeholder else [topic]
    elif isinstance(product_knowledge_needs, list):
        removed_declined_topic_placeholder = any(
            isinstance(item, str) and _is_declined_topic_placeholder(item)
            for item in product_knowledge_needs
        )
        out["productKnowledgeNeeds"] = [
            item.strip()
            for item in product_knowledge_needs
            if isinstance(item, str)
            and item.strip()
            and not _is_declined_topic_placeholder(item)
        ]
    if removed_declined_topic_placeholder:
        out["productKnowledgeNeedsConfirmed"] = False

    has_topics = not is_empty(out.get("productKnowledgeNeeds"))
    has_knowledge_content = _has_knowledge_content(out.get("knowledge"))

    if user_text.strip() and not str(out.get("sourceUserText") or "").strip():
        out["sourceUserText"] = user_text.strip()

    # Agent 按 product-knowledge-topic-generate.md 负责出题；脚本只从已提供正文标题提取主题。
    should_auto_derive_topics = (not has_topics) and has_knowledge_content
    if should_auto_derive_topics:
        derive_seed_text = user_text.strip() or str(out.get("sourceUserText") or "").strip()
        auto_topics = _derive_product_knowledge_needs(out, derive_seed_text)
        if base_acknowledged and auto_topics:
            auto_topics = auto_topics[:4]
        if auto_topics:
            out["productKnowledgeNeeds"] = auto_topics
            has_topics = True
            notes = str(out.get("generationNotes") or "").strip()
            extra = _text(PENDING_NOTES_TEXT, "autoDerivedNeeds")
            out["generationNotes"] = f"{notes}\n{extra}".strip() if notes else extra

    doc_ctx = out.get("doctorOnlyContext")
    if isinstance(doc_ctx, str) and doc_ctx.strip():
        fixed_doc, _ = sanitize_doctor_core_concerns_to_two_bullets(doc_ctx)
        out["doctorOnlyContext"] = fixed_doc

    return out


def _base_info_acknowledged(scene: dict[str, Any], payload: dict[str, Any]) -> bool:
    if payload.get("baseInfoAcknowledged") is True:
        return True
    if scene.get("baseInfoAcknowledged") is True:
        return True
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    if meta.get("baseInfoAcknowledged") is True:
        return True
    return False


def _product_knowledge_needs_confirmed(scene: dict[str, Any], payload: dict[str, Any]) -> bool:
    if is_empty(scene.get("productKnowledgeNeeds")):
        return False
    if _should_auto_decline_product_knowledge("", scene, payload):
        return False
    if scene.get("productKnowledgeNeedsConfirmed") is False:
        return False
    if payload.get("productKnowledgeNeedsConfirmed") is True:
        return True
    if scene.get("productKnowledgeNeedsConfirmed") is True:
        return True
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    if meta.get("productKnowledgeNeedsConfirmed") is True:
        return True
    return False


def _knowledge_ready(scene: dict[str, Any], payload: dict[str, Any]) -> bool:
    if payload.get("knowledgeReady") is True:
        return True
    if scene.get("knowledgeReady") is True:
        return True
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    if meta.get("knowledgeReady") is True:
        return True
    return False


def _defer_knowledge_cms_check_until_pre_create(payload: dict[str, Any]) -> bool:
    """编排层可设置：不在 Gate-2 调 CMS knowledge-check，仅在用户最终确认后、create 前调用。"""
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    return meta.get("deferKnowledgeCmsCheckUntilPreCreate") is True


def _updated_confirmation_echoed(payload: dict[str, Any]) -> bool:
    if payload.get("updatedConfirmationEchoed") is True:
        return True
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    if meta.get("updatedConfirmationEchoed") is True:
        return True
    return False


def _confirmation_status_for_field(
    field: str,
    value: Any,
    *,
    stage: str,
    base_acknowledged: bool,
    product_knowledge_needs_confirmed: bool = False,
) -> str:
    if is_empty(value):
        return _text(STATUS_TEXT, "toFill")
    if field in BASE_CONFIRM_FIELDS:
        return (
            _text(STATUS_TEXT, "confirmed")
            if base_acknowledged
            else _text(STATUS_TEXT, "toConfirm")
        )
    if field == "productKnowledgeNeeds":
        return (
            _text(STATUS_TEXT, "confirmed")
            if product_knowledge_needs_confirmed
            else _text(STATUS_TEXT, "toConfirm")
        )
    if stage == STAGE_READY_FOR_VALIDATE and field in GENERATED_CONFIRM_FIELDS:
        return _text(STATUS_TEXT, "ready")
    return _text(STATUS_TEXT, "toConfirm")


def _missing_fields(scene: dict[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if is_empty(scene.get(field))]


def _missing_bool(value: Any) -> bool:
    return not isinstance(value, bool)


def _actor_profile_missing(scene: dict[str, Any]) -> bool:
    actor = scene.get("actorProfile")
    if not isinstance(actor, dict):
        return True
    return not str(actor.get("name") or "").strip()


def _can_fast_forward_to_validate(
    scene: dict[str, Any], *, base_acknowledged: bool, product_knowledge_needs_confirmed: bool
) -> bool:
    """Fast path: all create gates ready, only need confirmation/validate handoff."""
    if not base_acknowledged:
        return False
    if not product_knowledge_needs_confirmed:
        return False
    return len(_missing_fields(scene, FINAL_REQUIRED_FIELDS)) == 0


def _normalize_incoming_patch(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {key: item for key, item in value.items() if key in FIELD_LABELS}


def _collect_scene_patch(payload: dict[str, Any]) -> dict[str, Any]:
    patch: dict[str, Any] = {}
    for key in (
        "parsedFields",
        "userUpdates",
        "userConfirmedFields",
        "userProvidedFields",
    ):
        patch.update(_normalize_incoming_patch(payload.get(key)))
    return patch


def _load_draft_meta_for_merge(draft_path: str | None) -> dict[str, Any]:
    if not draft_path or not str(draft_path).strip():
        return {}
    path = str(draft_path).strip()
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    meta = data.get("meta")
    return dict(meta) if isinstance(meta, dict) else {}


def build_patch_fields_locked_hint(
    *,
    past_knowledge_lock: bool,
    base_acknowledged: bool,
    rejected_fields: list[str],
) -> str:
    base = _text(ERROR_TEXT, "patchLockedHint")
    labels = "、".join(FIELD_LABELS.get(field, field) for field in rejected_fields)
    if past_knowledge_lock:
        return base + _text(ERROR_TEXT, "patchLockedPastKnowledgeSuffix") + f"（本轮被拒：{labels}）"
    if base_acknowledged:
        return base + _text(ERROR_TEXT, "patchLockedBaseAckSuffix") + f"（本轮被拒：{labels}）"
    return base + (f"（本轮被拒：{labels}）" if labels else "")


def collect_rejected_patch_keys(
    patch: dict[str, Any],
    *,
    base_acknowledged: bool,
    past_knowledge_lock: bool,
) -> list[str]:
    rejected: set[str] = set()
    for key in patch:
        if key not in FIELD_LABELS:
            continue
        if past_knowledge_lock:
            if key not in PATCHABLE_AFTER_KNOWLEDGE_LOCK:
                rejected.add(key)
        elif base_acknowledged and key in BASE_CONFIRM_FIELDS:
            rejected.add(key)
    return sorted(rejected)


def probe_patch_lock_state(
    base_scene: dict[str, Any],
    patch: dict[str, Any],
    user_text: str,
    payload: dict[str, Any],
) -> tuple[bool, bool]:
    probe = normalize_scene({**dict(base_scene), **patch}, user_text, payload)
    base_ack = _base_info_acknowledged(probe, payload)
    if base_ack:
        probe["baseInfoAcknowledged"] = True
    knowledge_ack = _product_knowledge_needs_confirmed(probe, payload)
    if knowledge_ack:
        probe["productKnowledgeNeedsConfirmed"] = True
    stage = determine_stage(
        probe,
        base_acknowledged=base_ack,
        product_knowledge_needs_confirmed=knowledge_ack,
        knowledge_ready=_knowledge_ready(probe, payload),
        defer_knowledge_cms_check=_defer_knowledge_cms_check_until_pre_create(payload),
    )[0]
    past_knowledge = stage in {
        STAGE_READY_FOR_SCENE_GENERATION,
        STAGE_READY_FOR_VALIDATE,
    }
    return base_ack, past_knowledge


def alignment_with_locked_core(scene: dict[str, Any]) -> tuple[bool, str]:
    bg = str(scene.get("sceneBackground") or scene.get("background") or "").strip()
    if not bg:
        return False, _text(ALIGNMENT_TEXT, "noBackground")
    if len(bg) < ALIGNMENT_MIN_BACKGROUND_LENGTH:
        return False, _text(ALIGNMENT_TEXT, "backgroundTooShort")
    concerns = scene.get("doctorConcerns")
    parts: list[str] = []
    if isinstance(concerns, list):
        parts.extend(str(item).strip() for item in concerns if str(item).strip())
    elif isinstance(concerns, str) and concerns.strip():
        parts.append(concerns.strip())
    goal = str(scene.get("repGoal") or "").strip()
    if not parts and not goal:
        return False, _text(ALIGNMENT_TEXT, "missingCoreInputs")
    missing: list[str] = []
    for piece in parts:
        if len(piece) >= ALIGNMENT_MIN_PIECE_LENGTH and piece not in bg:
            missing.append(
                piece[:ALIGNMENT_MISSING_PREVIEW_LENGTH]
                + ("…" if len(piece) > ALIGNMENT_MISSING_PREVIEW_LENGTH else "")
            )
    if goal and len(goal) >= ALIGNMENT_MIN_PIECE_LENGTH and goal not in bg:
        missing.append(_text(ALIGNMENT_TEXT, "missingRepGoalLabel"))
    if missing:
        prefix = _text(ALIGNMENT_TEXT, "coreNotCoveredPrefix")
        return False, prefix + "；".join(missing[:ALIGNMENT_MAX_MISSING_PIECES])
    return True, _text(ALIGNMENT_TEXT, "coveredOk")


def build_parse_change_summary(
    stage: str,
    *,
    updated_labels: list[str],
    alignment_ok: bool,
    alignment_note: str,
) -> dict[str, Any]:
    lines: list[str] = []
    if updated_labels:
        lines.append(_textf(CHANGE_SUMMARY_TEXT, "updatedFields", labels="、".join(updated_labels)))
    lines.append(alignment_note)
    skip_s3 = alignment_ok and stage == STAGE_READY_FOR_VALIDATE
    if skip_s3:
        lines.append(_text(CHANGE_SUMMARY_TEXT, "canSkipS3"))
    else:
        lines.append(_text(CHANGE_SUMMARY_TEXT, "shouldRunS3"))
    return {
        "lines": lines,
        "alignmentWithLockedCore": alignment_ok,
        "skipScenarioGenerationSuggested": skip_s3,
        "alignmentNote": alignment_note,
    }


def _clean_user_short_text(user_text: str) -> str:
    text = (user_text or "").strip()
    if not text:
        return ""
    text = text.strip("。！？；;，,：:、 \t\r\n")
    if len(text) >= 2 and ((text[0] == text[-1]) and text[0] in {'"', "'"}):
        text = text[1:-1].strip()
    return text


def _user_provided_best_practice(user_text: str) -> bool:
    text = (user_text or "").strip()
    if not text:
        return False
    return any(token in text for token in BEST_PRACTICE_KEYWORDS)


def _is_non_value_reply(text: str) -> bool:
    lowered = text.lower()
    return lowered in BLOCKED_PHRASES


def infer_user_reply_patch(user_text: str, missing_base_fields: list[str]) -> dict[str, Any]:
    if len(missing_base_fields) != 1:
        return {}
    field = missing_base_fields[0]
    if field != "drugName":
        return {}
    candidate = _clean_user_short_text(user_text)
    if not candidate or len(candidate) > INFER_REPLY_MAX_CANDIDATE_LENGTH:
        return {}
    if any(sep in candidate for sep in ("\n", "，", ",", "。", "；", ";", "：", ":")):
        return {}
    if _is_non_value_reply(candidate):
        return {}
    return {"drugName": candidate}


def _stringify_value(field: str, value: Any) -> str:
    if value is None:
        return ""
    if field == "actorProfile" and isinstance(value, dict):
        parts = [
            str(value.get("title") or "").strip(),
            str(value.get("name") or "").strip(),
            str(value.get("description") or "").strip(),
        ]
        return "；".join(part for part in parts if part)
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return "、".join(parts)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def _humanize_generation_notes(text: str) -> str:
    note = (text or "").strip()
    if not note:
        return ""
    for field, label in sorted(FIELD_LABELS.items(), key=lambda item: len(item[0]), reverse=True):
        note = note.replace(f"`{field}`", label)
    keys = [re.escape(field) for field in FIELD_LABELS]
    if not keys:
        return note
    pattern = re.compile(r"\b(" + "|".join(keys) + r")\b")
    return pattern.sub(lambda m: FIELD_LABELS.get(m.group(1), m.group(1)), note)


def build_confirmation_items(
    scene: dict[str, Any],
    fields: list[str],
    *,
    stage: str,
    base_acknowledged: bool,
    product_knowledge_needs_confirmed: bool = False,
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for field in fields:
        value = scene.get(field)
        items.append(
            {
                "label": FIELD_LABELS.get(field, field),
                "status": _confirmation_status_for_field(
                    field,
                    value,
                    stage=stage,
                    base_acknowledged=base_acknowledged,
                    product_knowledge_needs_confirmed=product_knowledge_needs_confirmed,
                ),
                "value": _stringify_value(field, value),
            }
        )
    return items


def _trim_display_text(value: Any, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip())
    if len(text) <= limit:
        return text
    return text[:limit].rstrip("，,。；; ") + "…"


def build_supplement_items(
    scene: dict[str, Any], *, user_text: str, best_practice_adopted: bool
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []

    actor_summary = (
        _stringify_value("actorProfile", scene.get("actorProfile"))
        or str(scene.get("actorProfileSupplement") or "").strip()
    )
    if not actor_summary:
        # 基础抽取阶段常把画像线索暂存到 generationNotes；结构化 UI 需要显式字段才能回显。
        actor_summary = str(scene.get("generationNotes") or "").strip()
    if actor_summary:
        items.append(
            {
                "label": "对象角色画像",
                "value": _trim_display_text(_humanize_generation_notes(actor_summary)),
            }
        )

    best_practice_summary = (
        str(scene.get("bestPracticeSupplement") or "").strip()
        or str(scene.get("bestPractice") or "").strip()
        or str(scene.get("coachBestPractice") or "").strip()
    )
    if not best_practice_summary and best_practice_adopted:
        best_practice_summary = user_text
    if best_practice_summary:
        items.append(
            {
                "label": "代表成功经验/典型话术",
                "value": _trim_display_text(best_practice_summary),
            }
        )

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


def build_output_blocking_requirements(
    *,
    stage: str,
    supplement_items: list[dict[str, str]],
) -> list[str]:
    requirements: list[str] = []
    if supplement_items:
        requirements.append(
            "用户可见输出必须展示“补充素材”区块，并逐条回显 userOutputTemplate.supplementItems；不得只展示产品知识主题后继续推进。"
        )
    if stage == STAGE_KNOWLEDGE_CONFIRM:
        requirements.append(
            "用户可见输出必须同时展示基础信息 6 项与产品知识主题；禁止只展示产品知识主题。"
        )
    return requirements


def _section_status(missing_fields: list[str], items: list[dict[str, str]]) -> str:
    if not missing_fields:
        return _text(STATUS_TEXT, "ready")
    if any(item["value"] for item in items):
        return _text(STATUS_TEXT, "toFill")
    return _text(STATUS_TEXT, "pendingStart")


def determine_stage(
    scene: dict[str, Any],
    *,
    base_acknowledged: bool,
    product_knowledge_needs_confirmed: bool,
    knowledge_ready: bool,
    defer_knowledge_cms_check: bool = False,
) -> tuple[str, list[str], list[str], list[str], list[str], bool]:
    missing_base_fields = _missing_fields(scene, BASE_CONFIRM_FIELDS)
    missing_knowledge_fields = _missing_fields(
        scene, KNOWLEDGE_CONFIRM_FIELDS + KNOWLEDGE_GATE_FIELDS
    )
    missing_generated_fields = _missing_fields(
        scene, GENERATED_STAGE_FIELDS + GENERATED_GATE_FIELDS
    )
    if "actorProfile" not in missing_generated_fields and _actor_profile_missing(scene):
        missing_generated_fields.append("actorProfile")
    missing_internal_fields = _missing_fields(scene, INTERNAL_GENERATED_FIELDS)
    missing_needs_evidence_confirmation = (
        product_knowledge_needs_confirmed
        and not knowledge_ready
        and not defer_knowledge_cms_check
    )

    if missing_base_fields:
        return (
            STAGE_BASE_INFO_CONFIRM,
            missing_base_fields,
            missing_knowledge_fields,
            missing_generated_fields,
            missing_internal_fields,
            missing_needs_evidence_confirmation,
        )
    if not base_acknowledged:
        return (
            STAGE_BASE_INFO_CONFIRM,
            missing_base_fields,
            missing_knowledge_fields,
            missing_generated_fields,
            missing_internal_fields,
            missing_needs_evidence_confirmation,
        )
    if (
        missing_knowledge_fields
        or missing_needs_evidence_confirmation
        or not product_knowledge_needs_confirmed
    ):
        return (
            STAGE_KNOWLEDGE_CONFIRM,
            missing_base_fields,
            missing_knowledge_fields,
            missing_generated_fields,
            missing_internal_fields,
            missing_needs_evidence_confirmation,
        )
    if missing_generated_fields or missing_internal_fields:
        return (
            STAGE_READY_FOR_SCENE_GENERATION,
            missing_base_fields,
            missing_knowledge_fields,
            missing_generated_fields,
            missing_internal_fields,
            missing_needs_evidence_confirmation,
        )
    return (
        STAGE_READY_FOR_VALIDATE,
        missing_base_fields,
        missing_knowledge_fields,
        missing_generated_fields,
        missing_internal_fields,
        missing_needs_evidence_confirmation,
    )


def build_phase_sections(
    scene: dict[str, Any],
    missing_base_fields: list[str],
    missing_knowledge_fields: list[str],
    missing_generated_fields: list[str],
    missing_internal_fields: list[str],
    *,
    stage: str,
    base_acknowledged: bool,
    product_knowledge_needs_confirmed: bool,
    missing_needs_evidence_confirmation: bool,
) -> list[dict[str, Any]]:
    base_items = build_confirmation_items(
        scene,
        BASE_CONFIRM_FIELDS,
        stage=stage,
        base_acknowledged=base_acknowledged,
        product_knowledge_needs_confirmed=product_knowledge_needs_confirmed,
    )
    knowledge_items = build_confirmation_items(
        scene,
        KNOWLEDGE_CONFIRM_FIELDS,
        stage=stage,
        base_acknowledged=base_acknowledged,
        product_knowledge_needs_confirmed=product_knowledge_needs_confirmed,
    )
    if not base_acknowledged:
        knowledge_items = []
    generated_items = build_confirmation_items(
        scene,
        GENERATED_CONFIRM_FIELDS,
        stage=stage,
        base_acknowledged=base_acknowledged,
        product_knowledge_needs_confirmed=product_knowledge_needs_confirmed,
    )
    base_section_status = _section_status(missing_base_fields, base_items)
    if not missing_base_fields and not base_acknowledged:
        base_section_status = _text(STATUS_TEXT, "pendingConfirm")

    knowledge_section_status = _text(STATUS_TEXT, "ready")
    if not base_acknowledged:
        knowledge_section_status = _text(STATUS_TEXT, "pendingConfirm")
    elif missing_needs_evidence_confirmation or missing_knowledge_fields:
        knowledge_section_status = _section_status(missing_knowledge_fields, knowledge_items)

    return [
        {
            "stage": STAGE_BASE_INFO_CONFIRM,
            "title": PHASE_TITLE_TEXT.get(STAGE_BASE_INFO_CONFIRM, STAGE_BASE_INFO_CONFIRM),
            "status": base_section_status,
            "items": base_items,
        },
        {
            "stage": STAGE_KNOWLEDGE_CONFIRM,
            "title": PHASE_TITLE_TEXT.get(STAGE_KNOWLEDGE_CONFIRM, STAGE_KNOWLEDGE_CONFIRM),
            "status": knowledge_section_status,
            "items": knowledge_items,
        },
        {
            "stage": STAGE_READY_FOR_SCENE_GENERATION,
            "title": PHASE_TITLE_TEXT.get(
                STAGE_READY_FOR_SCENE_GENERATION, STAGE_READY_FOR_SCENE_GENERATION
            ),
            "status": _section_status(missing_generated_fields + missing_internal_fields, generated_items),
            "items": generated_items,
        },
    ]


def build_pending_confirm_notes(
    scene: dict[str, Any], stage: str, *, base_acknowledged: bool
) -> list[str]:
    notes: list[str] = []
    generation_notes = str(scene.get("generationNotes") or "").strip()
    if generation_notes:
        notes.append(_humanize_generation_notes(generation_notes))
    if stage == STAGE_BASE_INFO_CONFIRM:
        notes.append(_text(PENDING_NOTES_TEXT, "baseInfoStage"))
    elif stage == STAGE_KNOWLEDGE_CONFIRM:
        if base_acknowledged:
            notes.append(_text(PENDING_NOTES_TEXT, "knowledgeStageBaseAck"))
        else:
            notes.append(_text(PENDING_NOTES_TEXT, "knowledgeStageBaseUnack"))
        notes.append(_text(PENDING_NOTES_TEXT, "knowledgeStageOptionalKnowledge"))
    elif stage == STAGE_READY_FOR_SCENE_GENERATION:
        notes.append(_text(PENDING_NOTES_TEXT, "readyForGeneration"))
    return notes


def build_base_questions(missing_fields: list[str]) -> list[str]:
    return [BASE_QUESTION_MAP[field] for field in missing_fields if field in BASE_QUESTION_MAP]


def _append_optional_enhancement_prompts(questions: list[str]) -> list[str]:
    # UI 会把 clarifyQuestions 作为“需要确认的问题/事项”展示；这里统一用“可选”标记，避免误解为门禁。
    out = list(questions)
    out.append(
        "（可选，已提供可忽略）请用 2-3 句话描述这位医生（角色/职称、沟通风格、最在意什么、最可能抛出的质疑）。"
    )
    out.append(
        "（可选，已提供可忽略）你当时最关键的一句话/应对方式是什么？医生怎么回？你如何把对话推进下去的？"
    )
    return out

def build_knowledge_questions(
    scene: dict[str, Any],
    missing_fields: list[str],
    missing_needs_evidence_confirmation: bool,
    base_acknowledged: bool,
) -> list[str]:
    hint_key = "backgroundHintAck" if base_acknowledged else "backgroundHintUnack"
    background_hint = _text(KNOWLEDGE_QUESTION_TEXT, hint_key)
    need_one_shot = bool(missing_fields) or missing_needs_evidence_confirmation
    questions: list[str] = []
    if need_one_shot:
        questions.append(_textf(KNOWLEDGE_QUESTION_TEXT, "confirmNeeds", background_hint=background_hint))
    if not base_acknowledged:
        questions.append(_text(KNOWLEDGE_QUESTION_TEXT, "confirmBaseFirst"))
    return questions


def build_content_generation_questions(
    missing_generated_fields: list[str],
    missing_internal_fields: list[str],
    *,
    must_echo_updated_confirmation: bool,
    updated_labels: list[str],
) -> list[str]:
    questions: list[str] = []
    if must_echo_updated_confirmation and updated_labels:
        labels = "、".join(updated_labels)
        questions.append(_textf(CONTENT_QUESTION_TEXT, "echoUpdated", labels=labels))
    if "title" in missing_generated_fields or "sceneBackground" in missing_generated_fields:
        questions.append(_text(CONTENT_QUESTION_TEXT, "genTitleBackground"))
    if "actorProfile" in missing_generated_fields:
        questions.append(_text(CONTENT_QUESTION_TEXT, "genActorProfile"))
    if missing_internal_fields:
        questions.append(_text(CONTENT_QUESTION_TEXT, "genContexts"))
    return questions


def build_clarify_questions(
    stage: str,
    scene: dict[str, Any],
    missing_base_fields: list[str],
    missing_knowledge_fields: list[str],
    missing_generated_fields: list[str],
    missing_internal_fields: list[str],
    missing_needs_evidence_confirmation: bool,
    base_acknowledged: bool,
    must_echo_updated_confirmation: bool,
    updated_labels: list[str],
) -> list[str]:
    if stage == STAGE_BASE_INFO_CONFIRM:
        base_qs = build_base_questions(missing_base_fields)
        return _append_optional_enhancement_prompts(base_qs)
    if stage == STAGE_KNOWLEDGE_CONFIRM:
        return build_knowledge_questions(
            scene,
            missing_knowledge_fields,
            missing_needs_evidence_confirmation,
            base_acknowledged,
        )
    if stage == STAGE_READY_FOR_SCENE_GENERATION:
        return build_content_generation_questions(
            missing_generated_fields,
            missing_internal_fields,
            must_echo_updated_confirmation=must_echo_updated_confirmation,
            updated_labels=updated_labels,
        )
    return []


def build_next_action(
    stage: str,
    *,
    base_acknowledged: bool,
    must_echo_updated_confirmation: bool,
    updated_labels: list[str],
) -> str:
    if stage == STAGE_BASE_INFO_CONFIRM:
        return _text(NEXT_ACTION_TEXT, "baseInfo")
    if stage == STAGE_KNOWLEDGE_CONFIRM:
        if not base_acknowledged:
            return _text(NEXT_ACTION_TEXT, "knowledgeBaseFirst")
        return _text(NEXT_ACTION_TEXT, "knowledge")
    if stage == STAGE_READY_FOR_SCENE_GENERATION:
        if must_echo_updated_confirmation and updated_labels:
            labels = "、".join(updated_labels)
            return _textf(NEXT_ACTION_TEXT, "readyForGenerationWithEcho", labels=labels)
        return _text(NEXT_ACTION_TEXT, "readyForGeneration")
    if stage == STAGE_READY_FOR_VALIDATE and must_echo_updated_confirmation and updated_labels:
        labels = "、".join(updated_labels)
        return _textf(NEXT_ACTION_TEXT, "readyForValidateWithEcho", labels=labels)
    return _text(NEXT_ACTION_TEXT, "default")


def build_system_action_hint(
    stage: str,
    *,
    base_acknowledged: bool,
    must_echo_updated_confirmation: bool,
    updated_labels: list[str],
) -> str:
    if stage == STAGE_BASE_INFO_CONFIRM:
        return _text(SYSTEM_ACTION_HINT_TEXT, "baseInfo")
    if stage == STAGE_KNOWLEDGE_CONFIRM:
        if not base_acknowledged:
            return _text(SYSTEM_ACTION_HINT_TEXT, "knowledgeBaseFirst")
        return _text(SYSTEM_ACTION_HINT_TEXT, "knowledge")
    if stage == STAGE_READY_FOR_SCENE_GENERATION:
        if must_echo_updated_confirmation and updated_labels:
            labels = "、".join(updated_labels)
            return _textf(SYSTEM_ACTION_HINT_TEXT, "readyForGenerationWithEcho", labels=labels)
        return _text(SYSTEM_ACTION_HINT_TEXT, "readyForGeneration")
    if stage == STAGE_READY_FOR_VALIDATE and must_echo_updated_confirmation and updated_labels:
        labels = "、".join(updated_labels)
        return _textf(SYSTEM_ACTION_HINT_TEXT, "readyForValidateWithEcho", labels=labels)
    return _text(SYSTEM_ACTION_HINT_TEXT, "default")


def maybe_write_draft(draft_path: str | None, scene: dict[str, Any], parse_result: dict[str, Any]) -> None:
    if not draft_path:
        return
    parent = os.path.dirname(draft_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    prior_meta = _load_draft_meta_for_merge(draft_path)
    meta = {
        **prior_meta,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "lastStep": STEP,
        "lastParseStage": parse_result.get("stage"),
        "sceneHash": parse_result.get("sceneHash"),
        "scenarioGenerated": parse_result.get("scenarioGenerated") is True,
    }
    payload = {
        "scene": scene,
        "parseResult": parse_result,
        "meta": meta,
    }
    with open(draft_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def main() -> None:
    global OUTPUT_PATH
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="-", help="JSON file path, or '-' for stdin")
    parser.add_argument("--params-file", default=None, help="Read params from UTF-8 JSON file")
    parser.add_argument("--output", default=None, help="Write full JSON result to this file")
    parser.add_argument(
        "--mode",
        default="default",
        choices=["default", "fast_forward"],
        help="default（默认）| fast_forward（满足条件时可直接进入 READY_FOR_VALIDATE）",
    )
    parser.add_argument(
        "--no-write-draft",
        action="store_true",
        help="仅返回解析结果，不写回 draftPath 文件（减少中间轮次 IO）",
    )
    args = parser.parse_args()
    OUTPUT_PATH = args.output

    try:
        payload = read_payload(args.input, args.params_file)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        emit_error("invalid_json_input", exit_code=2, hint=str(exc))
    payload, payload_shape_warnings = normalize_payload_shape(payload)
    user_text = str(payload.get("userText") or "").strip()
    base_scene = payload.get("scene") if isinstance(payload.get("scene"), dict) else {}
    scene_patch = _collect_scene_patch(payload)
    draft_path = payload.get("draftPath")
    if not user_text and not base_scene and not scene_patch:
        emit_error(_text(ERROR_TEXT, "missingInput"), exit_code=2)

    if scene_patch:
        base_ack_probe, past_probe = probe_patch_lock_state(
            base_scene, scene_patch, user_text, payload
        )
        rejected_patch = collect_rejected_patch_keys(
            scene_patch,
            base_acknowledged=base_ack_probe,
            past_knowledge_lock=past_probe,
        )
        if rejected_patch:
            emit_error(
                "patch_fields_locked",
                exit_code=2,
                rejectedFields=rejected_patch,
                hint=build_patch_fields_locked_hint(
                    past_knowledge_lock=past_probe,
                    base_acknowledged=base_ack_probe,
                    rejected_fields=rejected_patch,
                ),
            )

    scene = dict(base_scene)
    scene.update(scene_patch)
    scene = normalize_scene(scene, user_text, payload)
    base_acknowledged = _base_info_acknowledged(scene, payload)
    if base_acknowledged:
        scene["baseInfoAcknowledged"] = True
    product_knowledge_needs_confirmed = _product_knowledge_needs_confirmed(scene, payload)
    knowledge_ready = _knowledge_ready(scene, payload)
    defer_kc = _defer_knowledge_cms_check_until_pre_create(payload)
    if product_knowledge_needs_confirmed:
        scene["productKnowledgeNeedsConfirmed"] = True
    else:
        scene.pop("productKnowledgeNeedsConfirmed", None)

    (
        stage,
        missing_base_fields,
        missing_knowledge_fields,
        missing_generated_fields,
        missing_internal_fields,
        missing_needs_evidence_confirmation,
    ) = determine_stage(
        scene,
        base_acknowledged=base_acknowledged,
        product_knowledge_needs_confirmed=product_knowledge_needs_confirmed,
        knowledge_ready=knowledge_ready,
        defer_knowledge_cms_check=defer_kc,
    )

    inferred_reply_patch = infer_user_reply_patch(user_text, missing_base_fields)
    if inferred_reply_patch:
        scene.update(inferred_reply_patch)
        scene = normalize_scene(scene, user_text, payload)
        product_knowledge_needs_confirmed = _product_knowledge_needs_confirmed(scene, payload)
        knowledge_ready = _knowledge_ready(scene, payload)
        if product_knowledge_needs_confirmed:
            scene["productKnowledgeNeedsConfirmed"] = True
        else:
            scene.pop("productKnowledgeNeedsConfirmed", None)
        (
            stage,
            missing_base_fields,
            missing_knowledge_fields,
            missing_generated_fields,
            missing_internal_fields,
            missing_needs_evidence_confirmation,
        ) = determine_stage(
            scene,
            base_acknowledged=base_acknowledged,
            product_knowledge_needs_confirmed=product_knowledge_needs_confirmed,
            knowledge_ready=knowledge_ready,
            defer_knowledge_cms_check=defer_kc,
        )

    applied_user_patch = {**scene_patch, **inferred_reply_patch}
    confirm_fields = BASE_CONFIRM_FIELDS + KNOWLEDGE_CONFIRM_FIELDS + GENERATED_CONFIRM_FIELDS
    updated_confirm_fields = [field for field in confirm_fields if field in applied_user_patch]
    updated_labels = [FIELD_LABELS.get(field, field) for field in updated_confirm_fields]
    has_user_updates = len(updated_labels) > 0
    updated_confirmation_echoed = _updated_confirmation_echoed(payload)
    must_echo_updated_confirmation = has_user_updates and not updated_confirmation_echoed

    if (
        args.mode == "fast_forward"
        and stage != STAGE_READY_FOR_VALIDATE
        and _can_fast_forward_to_validate(
            scene,
            base_acknowledged=base_acknowledged,
            product_knowledge_needs_confirmed=product_knowledge_needs_confirmed,
        )
    ):
        stage = STAGE_READY_FOR_VALIDATE
        missing_base_fields = []
        missing_knowledge_fields = []
        missing_generated_fields = []
        missing_internal_fields = []
        missing_needs_evidence_confirmation = False

    phase_sections = build_phase_sections(
        scene,
        missing_base_fields,
        missing_knowledge_fields,
        missing_generated_fields,
        missing_internal_fields,
        stage=stage,
        base_acknowledged=base_acknowledged,
        product_knowledge_needs_confirmed=product_knowledge_needs_confirmed,
        missing_needs_evidence_confirmation=missing_needs_evidence_confirmation,
    )
    current_confirmation_items = build_confirmation_items(
        scene,
        STAGE_CONFIRM_FIELDS[stage],
        stage=stage,
        base_acknowledged=base_acknowledged,
        product_knowledge_needs_confirmed=product_knowledge_needs_confirmed,
    )
    updated_stage = (
        STAGE_KNOWLEDGE_CONFIRM
        if stage in {STAGE_READY_FOR_SCENE_GENERATION, STAGE_READY_FOR_VALIDATE}
        else stage
    )
    updated_confirmation_items = build_confirmation_items(
        scene,
        STAGE_CONFIRM_FIELDS[updated_stage],
        stage=stage,
        base_acknowledged=base_acknowledged,
        product_knowledge_needs_confirmed=product_knowledge_needs_confirmed,
    )
    must_display_fields = STAGE_MUST_DISPLAY_FIELDS.get(stage, FINAL_MUST_DISPLAY_FIELDS)
    must_display_items = build_confirmation_items(
        scene,
        must_display_fields,
        stage=stage,
        base_acknowledged=base_acknowledged,
        product_knowledge_needs_confirmed=product_knowledge_needs_confirmed,
    )
    confirm_view = {
        field: scene.get(field)
        for field in (
            BASE_CONFIRM_FIELDS + KNOWLEDGE_CONFIRM_FIELDS + GENERATED_CONFIRM_FIELDS
        )
    }
    all_missing_fields = _missing_fields(scene, FINAL_REQUIRED_FIELDS)
    missing_knowledge_confirm_fields = _missing_fields(scene, KNOWLEDGE_CONFIRM_FIELDS)
    if stage == STAGE_BASE_INFO_CONFIRM:
        user_facing_missing_fields = list(missing_base_fields)
    elif stage == STAGE_KNOWLEDGE_CONFIRM:
        user_facing_missing_fields = list(missing_base_fields + missing_knowledge_confirm_fields)
    elif stage == STAGE_READY_FOR_SCENE_GENERATION:
        user_facing_missing_fields = list(
            missing_base_fields + missing_knowledge_confirm_fields + missing_generated_fields
        )
    else:
        user_facing_missing_fields = []
    pending_confirm_notes = build_pending_confirm_notes(scene, stage, base_acknowledged=base_acknowledged)
    best_practice_adopted = _user_provided_best_practice(user_text)
    if best_practice_adopted:
        pending_confirm_notes.append(_text(PENDING_NOTES_TEXT, "bestPracticeAdopted"))
    supplement_items = build_supplement_items(
        scene, user_text=user_text, best_practice_adopted=best_practice_adopted
    )
    supplement_render_block = build_supplement_render_block(supplement_items)
    output_blocking_requirements = build_output_blocking_requirements(
        stage=stage,
        supplement_items=supplement_items,
    )
    actor_profile_supplement = next(
        (item["value"] for item in supplement_items if item["label"] == "对象角色画像"), ""
    )
    best_practice_supplement = next(
        (item["value"] for item in supplement_items if item["label"] == "代表成功经验/典型话术"), ""
    )
    clarify_questions = build_clarify_questions(
        stage,
        scene,
        missing_base_fields,
        missing_knowledge_fields,
        missing_generated_fields,
        missing_internal_fields,
        missing_needs_evidence_confirmation,
        base_acknowledged,
        must_echo_updated_confirmation,
        updated_labels,
    )
    alignment_ok, alignment_note = alignment_with_locked_core(scene)
    parse_meta = build_parse_change_summary(
        stage,
        updated_labels=updated_labels,
        alignment_ok=alignment_ok,
        alignment_note=alignment_note,
    )
    scene_hash = compute_scene_hash(scene)
    scenario_generated = stage == STAGE_READY_FOR_VALIDATE
    knowledge_topic_buckets = _build_knowledge_topic_buckets(scene, payload, stage)
    result = {
        "step": STEP,
        "stage": stage,
        "scene": scene,
        "sceneHash": scene_hash,
        "scenarioGenerated": scenario_generated,
        "confirmedFields": confirm_view,
        "missingFields": user_facing_missing_fields,
        "baseMissingFields": missing_base_fields,
        "knowledgeMissingFields": missing_knowledge_fields,
        "contentMissingFields": missing_generated_fields,
        "createGateMissingFields": all_missing_fields,
        "internalGeneratedMissingFields": missing_internal_fields,
        "readyForScenarioJsonParse": stage == STAGE_READY_FOR_SCENE_GENERATION,
        "readyForValidate": stage == STAGE_READY_FOR_VALIDATE,
        "baseInfoAcknowledged": base_acknowledged,
        "productKnowledgeNeedsConfirmed": product_knowledge_needs_confirmed,
        "knowledgeReady": knowledge_ready,
        "knowledgeCheckRequired": product_knowledge_needs_confirmed and not knowledge_ready,
        "appliedUserPatch": applied_user_patch,
        "updatedFieldLabels": updated_labels,
        "bestPracticeAdopted": best_practice_adopted,
        "bestPracticeTargetSection": (
            BEST_PRACTICE_TARGET_SECTION if best_practice_adopted else ""
        ),
        "mustEchoUpdatedConfirmation": must_echo_updated_confirmation,
        "updatedConfirmationEchoed": updated_confirmation_echoed,
        "clarifyQuestions": clarify_questions,
        "parseMeta": parse_meta,
        "knowledgeTopicBuckets": knowledge_topic_buckets,
        "payloadShapeWarnings": payload_shape_warnings,
        "supplementItems": supplement_items,
        "mustDisplaySupplementItems": bool(supplement_items),
        "supplementRenderBlock": supplement_render_block,
        "outputBlockingRequirements": output_blocking_requirements,
        "userOutputTemplate": {
            "stage": stage,
            "stageLabel": STAGE_LABEL_TEXT.get(stage, stage),
            "confirmationItems": current_confirmation_items,
            "updatedConfirmationItems": updated_confirmation_items,
            "mustEchoUpdatedConfirmation": must_echo_updated_confirmation,
            "updatedFieldLabels": updated_labels,
            "bestPracticeAdopted": best_practice_adopted,
            "bestPracticeTargetSection": (
                BEST_PRACTICE_TARGET_SECTION if best_practice_adopted else ""
            ),
            "phaseSections": phase_sections,
            "mustDisplayFields": must_display_fields,
            "mustDisplayLabels": [FIELD_LABELS.get(field, field) for field in must_display_fields],
            "mustDisplayConfirmationItems": must_display_items,
            "knowledgeReady": knowledge_ready,
            "knowledgeCheckRequired": product_knowledge_needs_confirmed and not knowledge_ready,
            "missingLabels": [FIELD_LABELS.get(field, field) for field in user_facing_missing_fields],
            "createGateMissingLabels": [
                FIELD_LABELS.get(field, field) for field in all_missing_fields
            ],
            "internalGeneratedMissingLabels": [
                FIELD_LABELS.get(field, field) for field in missing_internal_fields
            ],
            "pendingConfirmNotes": pending_confirm_notes,
            "clarifyQuestions": clarify_questions,
            "nextAction": build_next_action(
                stage,
                base_acknowledged=base_acknowledged,
                must_echo_updated_confirmation=must_echo_updated_confirmation,
                updated_labels=updated_labels,
            ),
            "systemActionHint": build_system_action_hint(
                stage,
                base_acknowledged=base_acknowledged,
                must_echo_updated_confirmation=must_echo_updated_confirmation,
                updated_labels=updated_labels,
            ),
            "changeSummaryLines": parse_meta.get("lines", []),
            "alignmentWithLockedCore": alignment_ok,
            "skipScenarioGenerationSuggested": bool(
                parse_meta.get("skipScenarioGenerationSuggested")
            ),
            "mustShowSceneBackgroundFullText": bool(
                str(scene.get("sceneBackground") or scene.get("background") or "").strip()
            ),
            "sceneBackgroundFullText": str(
                scene.get("sceneBackground") or scene.get("background") or ""
            ).strip(),
            "knowledgeTopicBuckets": knowledge_topic_buckets,
            "payloadShapeWarnings": payload_shape_warnings,
            "supplementItems": supplement_items,
            "mustDisplaySupplementItems": bool(supplement_items),
            "supplementRenderBlock": supplement_render_block,
            "outputBlockingRequirements": output_blocking_requirements,
            "actorProfileSupplement": actor_profile_supplement,
            "bestPracticeSupplement": best_practice_supplement,
        },
    }

    # Render a single user-visible text block from references/output-templates.md
    # so that hosts can display it without re-implementing the templating logic.
    template_no = 3 if stage == STAGE_READY_FOR_VALIDATE else (2 if must_echo_updated_confirmation else 1)
    user_visible_text = _render_user_visible_text_from_templates(
        template_no=template_no,
        stage_label=STAGE_LABEL_TEXT.get(stage, stage),
        user_output=result.get("userOutputTemplate", {}),
        scene=scene,
    )
    if user_visible_text:
        result["userVisibleText"] = user_visible_text

    if isinstance(draft_path, str) and draft_path.strip() and not args.no_write_draft:
        maybe_write_draft(draft_path.strip(), scene, result)
        result["draftPath"] = draft_path.strip()
    elif isinstance(draft_path, str) and draft_path.strip():
        result["draftPath"] = draft_path.strip()
        result["draftWriteSkipped"] = True

    emit_success(result)


if __name__ == "__main__":
    main()
