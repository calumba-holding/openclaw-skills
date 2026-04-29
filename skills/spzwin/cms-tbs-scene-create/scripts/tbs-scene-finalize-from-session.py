#!/usr/bin/env python3
"""
Finalize a TBS scene session after the user explicitly confirms creation.

This is the Gate-5 orchestration entrypoint for OpenClaw:
- Never call tbs-scene-create.py directly from the agent/orchestrator.
- For path B (meta.deferKnowledgeCmsCheckUntilPreCreate=true), run knowledge-check
  after confirmation, then re-run FULL validate, then create.
- Stop early with a structured result when knowledge is still incomplete.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"无法读取文件：{path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON 解析失败：{path}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"JSON 须为对象：{path}")
    return data


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _infer_session_dir(path_text: str) -> Path:
    p = Path(path_text).expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    return p


def _run_json_stdin(
    script_path: Path,
    payload: dict[str, Any],
    *,
    output_path: Path,
    access_token: str | None = None,
    base_url: str | None = None,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(script_path), "--output", str(output_path)]
    if access_token is not None:
        cmd.extend(["--access-token", access_token])
    if base_url:
        cmd.extend(["--base-url", base_url])
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(
        cmd,
        cwd=str(script_path.parent),
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
    )


def _forward_process_output(proc: subprocess.CompletedProcess[str]) -> None:
    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)


def _emit_blocked(output_path: Path, error: str, **extra: Any) -> None:
    _write_json(
        output_path,
        {
            "success": False,
            "step": "tbs-scene-finalize",
            "error": error,
            **extra,
        },
    )
    print(f"ERROR tbs-scene-finalize error={error} result={output_path}", file=sys.stderr)


def _cancel(output_path: Path) -> None:
    _write_json(
        output_path,
        {
            "success": True,
            "step": "tbs-scene-finalize",
            "cancelled": True,
            "message": "用户已取消，本次不执行创建。",
        },
    )
    print(f"OK tbs-scene-finalize cancelled=true result={output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-dir", required=True)
    parser.add_argument("--user-confirmation", required=True, help='必须为 "确认" 或 "取消"')
    parser.add_argument("--access-token", required=False)
    parser.add_argument("--base-url", default=None)
    parser.add_argument(
        "--output",
        default=None,
        help="默认写入 {sessionDir}/latest-create-result.json",
    )
    args = parser.parse_args()

    session_dir = _infer_session_dir(args.session_dir)
    output_path = Path(args.output).expanduser() if args.output else session_dir / "latest-create-result.json"
    user_confirmation = str(args.user_confirmation or "").strip()
    if user_confirmation not in {"确认", "取消"}:
        _emit_blocked(output_path, "user_confirmation_invalid", hint="userConfirmation 必须为：确认 / 取消")
        raise SystemExit(2)
    if user_confirmation == "取消":
        _cancel(output_path)
        return

    access_token = str(args.access_token or "").strip()
    if not access_token:
        _emit_blocked(output_path, "access_token_missing", hint="确认落库时必须提供真实 access-token。")
        raise SystemExit(2)

    draft_path = session_dir / "latest-draft.json"
    validate_path = session_dir / "latest-validate-result.json"
    if not draft_path.is_file():
        _emit_blocked(output_path, "draft_missing", hint=f"缺少 latest-draft.json：{draft_path}")
        raise SystemExit(2)
    if not validate_path.is_file():
        _emit_blocked(output_path, "validate_result_missing", hint=f"缺少 latest-validate-result.json：{validate_path}")
        raise SystemExit(2)

    draft = _read_json(draft_path)
    scene = draft.get("scene") if isinstance(draft.get("scene"), dict) else {}
    meta = draft.get("meta") if isinstance(draft.get("meta"), dict) else {}
    if not scene:
        _emit_blocked(output_path, "scene_missing", hint="latest-draft.json 缺少 scene。")
        raise SystemExit(2)

    script_dir = Path(__file__).parent
    defer_kc = meta.get("deferKnowledgeCmsCheckUntilPreCreate") is True
    has_topics = bool(scene.get("productKnowledgeNeeds"))

    if defer_kc:
        kc_payload = {**draft, "draftPath": str(draft_path)}
        kc_proc = _run_json_stdin(
            script_dir / "tbs-scene-knowledge-check.py",
            kc_payload,
            output_path=session_dir / "latest-knowledge-check-result.json",
            access_token=access_token,
            base_url=args.base_url,
        )
        _forward_process_output(kc_proc)
        if kc_proc.returncode != 0:
            kc_result = _read_json(session_dir / "latest-knowledge-check-result.json")
            _emit_blocked(
                output_path,
                "knowledge_check_failed",
                hint="产品知识检查失败，已停止创建；请先处理知识检查问题后重试。",
                knowledgeCheckError=kc_result.get("error") or "",
            )
            raise SystemExit(kc_proc.returncode)

        kc_result = _read_json(session_dir / "latest-knowledge-check-result.json")
        if kc_result.get("knowledgeReady") is not True:
            _emit_blocked(
                output_path,
                "knowledge_not_ready",
                hint="产品知识仍有缺失，已停止创建；请补充正文后重新执行最终落库。",
                missingKnowledgeTopics=kc_result.get("missingKnowledgeTopics") or [],
                pendingTopics=(kc_result.get("knowledgeCheckReport") or {}).get("pendingTopics") or [],
            )
            raise SystemExit(2)

        # knowledgeIds participate in sceneHash, so refresh FULL validation after knowledge-check.
        refreshed = _read_json(draft_path)
        validate_payload = {**refreshed, "draftPath": str(draft_path), "validationScope": "FULL"}
        old_validate = _read_json(validate_path)
        old_display_hash = str((old_validate.get("validationReport") or {}).get("displayHash") or "").strip()
        validate_proc = _run_json_stdin(
            script_dir / "tbs-scene-validate.py",
            validate_payload,
            output_path=validate_path,
        )
        _forward_process_output(validate_proc)
        if validate_proc.returncode != 0:
            validate_result = _read_json(validate_path)
            _emit_blocked(
                output_path,
                "validation_failed_after_knowledge_check",
                hint="knowledge-check 后 FULL validate 执行失败，禁止创建。",
                validationError=validate_result.get("error") or "",
            )
            raise SystemExit(validate_proc.returncode)
        new_validate = _read_json(validate_path)
        new_report = new_validate.get("validationReport") if isinstance(new_validate.get("validationReport"), dict) else {}
        if new_report.get("passed") is not True:
            _emit_blocked(
                output_path,
                "validation_failed_after_knowledge_check",
                hint="knowledge-check 后 FULL validate 未通过，禁止创建。",
                validationReport=new_report,
            )
            raise SystemExit(2)
        new_display_hash = str(new_report.get("displayHash") or "").strip()
        if old_display_hash and new_display_hash and old_display_hash != new_display_hash:
            _emit_blocked(
                output_path,
                "display_hash_changed_after_knowledge_check",
                hint="knowledge-check 后最终确认展示内容发生变化，请重新展示最终确认清单并重新取得确认。",
                previousDisplayHash=old_display_hash,
                currentDisplayHash=new_display_hash,
            )
            raise SystemExit(2)
    elif has_topics and not (meta.get("knowledgeChecked") is True and meta.get("knowledgeReady") is True):
        _emit_blocked(
            output_path,
            "knowledge_not_ready",
            hint="创建前必须先执行 tbs-scene-knowledge-check.py，且 meta.knowledgeReady=true；或启用路径 B 后通过本 finalize 入口执行。",
        )
        raise SystemExit(2)

    create_cmd = [
        sys.executable,
        str(script_dir / "tbs-scene-create-from-session.py"),
        "--session-dir",
        str(session_dir),
        "--user-confirmation",
        user_confirmation,
        "--access-token",
        access_token,
        "--output",
        str(output_path),
    ]
    if args.base_url:
        create_cmd.extend(["--base-url", str(args.base_url)])
    create_proc = subprocess.run(
        create_cmd,
        cwd=str(script_dir),
        capture_output=True,
        text=True,
    )
    _forward_process_output(create_proc)
    raise SystemExit(create_proc.returncode)


if __name__ == "__main__":
    main()
