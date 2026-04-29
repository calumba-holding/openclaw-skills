#!/usr/bin/env python3
"""
Local doc consistency checks for cms-tbs-scene-create.

Design goals:
- Zero runtime impact (dev-only tool).
- No third-party dependencies.
- Deterministic checks with actionable messages.
"""

from __future__ import annotations

import re
import sys
import json
from pathlib import Path
from typing import Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = ROOT / "SKILL.md"
REF_DIR = ROOT / "references"
SCRIPTS_README = ROOT / "scripts" / "README.md"
COMMON_PARAMS = REF_DIR / "common-params.md"
OUTPUT_TEMPLATES = REF_DIR / "output-templates.md"
PARSE_RUNTIME_CONFIG = REF_DIR / "parse-runtime-config.json"
SCRIPT_DIR = ROOT / "scripts"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_lines(content: str, pattern: str) -> List[int]:
    lines: List[int] = []
    rx = re.compile(pattern)
    for idx, line in enumerate(content.splitlines(), start=1):
        if rx.search(line):
            lines.append(idx)
    return lines


def iter_md_files() -> Iterable[Path]:
    yield SKILL_MD
    if SCRIPTS_README.exists():
        yield SCRIPTS_README
    if REF_DIR.exists():
        for p in sorted(REF_DIR.glob("*.md")):
            yield p


def main() -> int:
    errors: List[Tuple[Path, int, str]] = []

    docs = {path: read_text(path) for path in iter_md_files() if path.exists()}

    for path, content in docs.items():
        for line_no in find_lines(content, r"全量\s*S4"):
            errors.append((path, line_no, "禁止使用术语“全量 S4”，请改为 scope=FULL 全量校验。"))

    for path, content in docs.items():
        for line_no in find_lines(content, r"医生关注点（建议\s*2-4\s*条"):
            errors.append((path, line_no, "医生关注点口径应为 1-2 条（聚焦最核心顾虑）。"))

    cp = docs.get(COMMON_PARAMS)
    if cp:
        for idx, line in enumerate(cp.splitlines(), start=1):
            if (
                "READY_FOR_SCENE_GENERATION" in line
                and "title" in line
                and "sceneBackground" in line
                and "不作为此阶段必显项" not in line
            ):
                errors.append(
                    (
                        COMMON_PARAMS,
                        idx,
                        "READY_FOR_SCENE_GENERATION 不应将 title/sceneBackground 定义为必显项（应为待内部生成）。",
                    )
                )

    if cp and "mustDisplayFields" in cp:
        must_display_line = next(
            (
                line
                for line in cp.splitlines()
                if "`businessDomainName`" in line
                and "`sceneBackground`" in line
                and "`title`" in line
            ),
            "",
        )
        if must_display_line and "`productKnowledgeNeeds`" not in must_display_line:
            errors.append(
                (
                    COMMON_PARAMS,
                    1,
                    "创建前 mustDisplayFields 必须包含 productKnowledgeNeeds，避免落库前漏展示产品知识主题。",
                )
            )
        if must_display_line and "`actorProfile`" not in must_display_line:
            errors.append(
                (
                    COMMON_PARAMS,
                    1,
                    "创建前 mustDisplayFields 必须包含 actorProfile，避免落库前漏展示对练对象角色。",
                )
            )

    joined = "\n".join(docs.values())
    if "mustEchoUpdatedConfirmation" in joined and "updatedConfirmationEchoed" not in joined:
        errors.append(
            (
                COMMON_PARAMS,
                1,
                "检测到 mustEchoUpdatedConfirmation，但未找到 updatedConfirmationEchoed 对称说明。",
            )
        )

    # Rule 5: Hard intercept section must exist in common-params.
    if cp and "绝对禁止直出字段（强制）" not in cp:
        errors.append(
            (
                COMMON_PARAMS,
                1,
                "缺少“绝对禁止直出字段（强制）”章节，存在内部状态外显风险。",
            )
        )

    # Rule 6: Single final user message per round rule must exist.
    if cp and "同轮用户侧最多输出 1 条最终消息" not in cp:
        errors.append(
            (
                COMMON_PARAMS,
                1,
                "缺少“同轮用户侧最多输出 1 条最终消息”约束，存在重复回显风险。",
            )
        )

    tmpl_heading = re.compile(r"^\s*####\s*模板\s*[0-4][AB]?", re.MULTILINE)
    for path, content in docs.items():
        if path == OUTPUT_TEMPLATES:
            continue
        for m in tmpl_heading.finditer(content):
            line_no = content[: m.start()].count("\n") + 1
            errors.append((path, line_no, "模板正文应只在 references/output-templates.md 定义，其他文档请仅引用。"))

    command_block = re.compile(r"```(?:bash|sh|text)?\n(.*?)```", re.DOTALL)
    script_cmd = re.compile(r"python3\s+scripts/tbs-scene-(?:parse|knowledge-check|validate|create)\.py")
    for path, content in docs.items():
        for block in command_block.finditer(content):
            body = block.group(1)
            if script_cmd.search(body) and "--output" not in body:
                line_no = content[: block.start()].count("\n") + 1
                errors.append((path, line_no, "入口脚本示例必须包含 --output，避免 stdout 暴露完整 JSON。"))
        for idx, line in enumerate(content.splitlines(), start=1):
            if script_cmd.search(line) and "--output" not in line and not line.rstrip().endswith("\\"):
                errors.append((path, idx, "入口脚本行内示例必须包含 --output。"))

    old_shared_names = (r"tbs_client\.py", r"tbs_md_sanitize\.py")
    for path, content in docs.items():
        for pattern in old_shared_names:
            for line_no in find_lines(content, pattern):
                errors.append((path, line_no, "共享库文件名已统一为连字符命名，请勿引用旧下划线文件名。"))

    for required_script in ("tbs-client.py", "tbs-md-sanitize.py"):
        if not (SCRIPT_DIR / required_script).exists():
            errors.append((SCRIPTS_README, 1, f"缺少共享库脚本：scripts/{required_script}。"))

    if not PARSE_RUNTIME_CONFIG.exists():
        errors.append((PARSE_RUNTIME_CONFIG, 1, "缺少 parse-runtime-config.json，parse 脚本文案/轻量规则不应继续硬编码。"))
    else:
        try:
            runtime_config = json.loads(PARSE_RUNTIME_CONFIG.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append((PARSE_RUNTIME_CONFIG, exc.lineno, f"parse-runtime-config.json 不是合法 JSON：{exc.msg}"))
            runtime_config = {}
        if isinstance(runtime_config, dict):
            for key in (
                "fieldLabels",
                "baseQuestionMap",
                "stageLabelText",
                "phaseTitleText",
                "bestPracticeKeywords",
            ):
                if key not in runtime_config:
                    errors.append((PARSE_RUNTIME_CONFIG, 1, f"parse-runtime-config.json 缺少关键配置：{key}。"))
            doctor_question = (
                runtime_config.get("baseQuestionMap", {}).get("doctorConcerns", "")
                if isinstance(runtime_config.get("baseQuestionMap"), dict)
                else ""
            )
            if "具体顾虑" not in str(doctor_question) and "异议" not in str(doctor_question):
                errors.append(
                    (
                        PARSE_RUNTIME_CONFIG,
                        1,
                        "doctorConcerns 追问文案必须强调“具体顾虑/异议”，避免把画像词当顾虑。",
                    )
                )
        else:
            errors.append((PARSE_RUNTIME_CONFIG, 1, "parse-runtime-config.json 顶层必须是对象。"))

    if errors:
        print("Doc consistency check failed:\n")
        for path, line_no, msg in errors:
            rel = path.relative_to(ROOT)
            print(f"- {rel}:{line_no}: {msg}")
        print(f"\nTotal issues: {len(errors)}")
        return 1

    print("OK: doc consistency checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
