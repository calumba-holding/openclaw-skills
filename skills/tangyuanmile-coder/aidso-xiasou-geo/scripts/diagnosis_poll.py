#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIDSO GEO 品牌诊断轮询脚本

用途：
- 在“问题已确认”之后，轮询品牌诊断结果
- 正式诊断请求会携带：
  - brand_name
  - questions
- 成功时原样返回 Markdown 链接
- 不做 PDF 转换，不下载文件

用法：
    python diagnosis_poll.py "露露" '["露露适合什么人群？","露露的核心优势是什么？"]'
    python diagnosis_poll.py "露露" '["露露适合什么人群？","露露的核心优势是什么？"]' --api-key your_key
    python diagnosis_poll.py "露露" '["露露适合什么人群？","露露的核心优势是什么？"]' --interval 60 --max-attempts 30

环境变量：
    AIDSO_GEO_API_KEY   可选，若未传 --api-key，则从环境变量读取
"""

import sys
import os
import json
import time
import argparse
from typing import List, Tuple, Optional

import requests

API_URL = "https://api.aidso.com/openapi/skills/band_report/md/v2"
API_KEY_URL = "https://geo.aidso.com/setting?type=apiKey&platform=GEO"
COMPLETE_ANALYSIS_URL = "https://geo.aidso.com/completeAnalysis"
PURCHASE_POINTS_URL = "https://geo.aidso.com"

DEFAULT_INTERVAL_SECONDS = 60
DEFAULT_MAX_ATTEMPTS = 30


def out_text(msg: str) -> None:
    print(msg, flush=True)


def out_debug(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def build_auth_headers(api_key: str) -> dict:
    return {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }


def normalize_code(code):
    if code is None:
        return None
    try:
        return int(code)
    except Exception:
        return code


def get_backend_msg(data: dict) -> str:
    if not isinstance(data, dict):
        return ""
    msg = data.get("msg")
    if isinstance(msg, str) and msg.strip():
        return msg.strip()
    message = data.get("message")
    if isinstance(message, str) and message.strip():
        return message.strip()
    return ""


def format_backend_error_message(msg: str) -> str:
    if not msg:
        return "接口返回错误"
    if "积分不足" in msg:
        return f"{msg}\n请前往{PURCHASE_POINTS_URL} 购买积分"
    return msg


def is_invalid_token_response(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    code = normalize_code(data.get("code"))
    msg = get_backend_msg(data).lower()
    return code == 401 or "invalid token" in msg or "鉴权失败" in msg


def is_processing_response(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    code = normalize_code(data.get("code"))
    msg = get_backend_msg(data).lower()
    return code == 200 and (
        "处理中" in msg
        or "processing" in msg
        or "请稍后" in msg
        or "正在处理中" in msg
    )


def extract_markdown_link(data: dict) -> Optional[str]:
    """
    成功时 data 直接返回 Markdown 链接，例如：
    {
      "code": 200,
      "msg": "success",
      "data": "https://tcdn.aidso.com/skills/md/xxx.md"
    }
    """
    if not isinstance(data, dict):
        return None

    payload = data.get("data")
    if isinstance(payload, str):
        value = payload.strip()
        if value.startswith("http://") or value.startswith("https://"):
            return value

    if isinstance(payload, dict):
        for key in ("url", "fileUrl", "downloadUrl", "mdUrl", "reportUrl"):
            v = payload.get(key)
            if isinstance(v, str):
                value = v.strip()
                if value.startswith("http://") or value.startswith("https://"):
                    return value

    return None


def extract_recommended_questions(data: dict) -> Optional[List[str]]:
    """
    防御性处理：
    如果接口返回的是推荐问题列表，而不是正式诊断结果，则给出提示。
    例如：
    {
      "code": 200,
      "msg": "成功",
      "data": [
        "问题1",
        "问题2"
      ]
    }
    """
    if not isinstance(data, dict):
        return None

    payload = data.get("data")
    if isinstance(payload, list) and all(isinstance(x, str) for x in payload):
        cleaned = [x.strip() for x in payload if isinstance(x, str) and x.strip()]
        return cleaned if cleaned else None

    if isinstance(payload, dict):
        questions = payload.get("questions")
        if isinstance(questions, list) and all(isinstance(x, str) for x in questions):
            cleaned = [x.strip() for x in questions if isinstance(x, str) and x.strip()]
            return cleaned if cleaned else None

    return None


def parse_json_utf8(resp: requests.Response) -> dict:
    raw = resp.content
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        pass
    try:
        return resp.json()
    except Exception:
        pass
    return json.loads(resp.text)


def request_report(brand_name: str, questions: List[str], api_key: str) -> dict:
    payload = {
        "brand_name": brand_name,
        "questions": questions,
    }

    resp = requests.post(
        API_URL,
        headers=build_auth_headers(api_key),
        json=payload,
        timeout=180,
    )
    resp.raise_for_status()
    return parse_json_utf8(resp)


def parse_questions_input(raw: str) -> List[str]:
    """
    支持以下输入格式：
    1. JSON 数组字符串：
       '["问题1","问题2"]'
    2. 单个问题字符串：
       '问题1'
    3. 多行文本：
       '问题1\n问题2'
    4. 用 || / ； / ; 分隔：
       '问题1||问题2'
    """
    text = (raw or "").strip()
    if not text:
        raise ValueError("questions 不能为空")

    # 先尝试 JSON 数组
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            cleaned = [str(x).strip() for x in parsed if str(x).strip()]
            if cleaned:
                return cleaned
    except Exception:
        pass

    # 多行
    if "\n" in text:
        items = [x.strip() for x in text.splitlines() if x.strip()]
        if items:
            return items

    # || 分隔
    if "||" in text:
        items = [x.strip() for x in text.split("||") if x.strip()]
        if items:
            return items

    # 中文/英文分号分隔
    if "；" in text:
        items = [x.strip() for x in text.split("；") if x.strip()]
        if items:
            return items

    if ";" in text:
        items = [x.strip() for x in text.split(";") if x.strip()]
        if items:
            return items

    # 兜底：按单个问题处理
    return [text]


def poll_report(
    brand_name: str,
    questions: List[str],
    api_key: str,
    interval_seconds: int,
    max_attempts: int,
) -> Tuple[str, str]:
    for attempt in range(1, max_attempts + 1):
        out_debug(
            f"[DEBUG] polling attempt={attempt}/{max_attempts}, brand_name={brand_name}, questions_count={len(questions)}"
        )

        data = request_report(brand_name, questions, api_key)

        if is_invalid_token_response(data):
            return (
                "text",
                f"当前绑定的 API key 已失效或不正确，请重新输入你在后台创建的 API key 完成绑定。\n"
                f"获取地址：{API_KEY_URL}",
            )

        recommended_questions = extract_recommended_questions(data)
        if recommended_questions:
            return (
                "text",
                "当前接口返回的是推荐问题列表，请先确认问题后再发起正式诊断。",
            )

        markdown_link = extract_markdown_link(data)
        if normalize_code(data.get("code")) == 200 and markdown_link:
            return ("text", markdown_link)

        if is_processing_response(data):
            if attempt < max_attempts:
                time.sleep(interval_seconds)
                continue
            return (
                "text",
                "诊断结果暂未生成完成，请稍后请求获取结果。\n"
                f"也可以前往官网查看：{COMPLETE_ANALYSIS_URL}",
            )

        msg = get_backend_msg(data)
        return ("text", format_backend_error_message(msg or json.dumps(data, ensure_ascii=False)))

    return (
        "text",
        "诊断结果暂未生成完成，请稍后请求获取结果。\n"
        f"也可以前往官网查看：{COMPLETE_ANALYSIS_URL}",
    )


def parse_args():
    parser = argparse.ArgumentParser(description="AIDSO GEO 品牌诊断轮询脚本（支持问题交互后的正式诊断）")
    parser.add_argument("brand_name", help="品牌名称")
    parser.add_argument("questions", help='问题列表，建议传 JSON 数组字符串，如 \'["问题1","问题2"]\'')
    parser.add_argument("--api-key", dest="api_key", help="API key")
    parser.add_argument("--interval", dest="interval", type=int, default=DEFAULT_INTERVAL_SECONDS, help="轮询间隔秒数")
    parser.add_argument("--max-attempts", dest="max_attempts", type=int, default=DEFAULT_MAX_ATTEMPTS, help="最大轮询次数")
    return parser.parse_args()


def main():
    try:
        args = parse_args()

        brand_name = args.brand_name.strip()
        questions = parse_questions_input(args.questions)
        api_key = (args.api_key or os.environ.get("AIDSO_GEO_API_KEY") or "").strip()

        if not brand_name:
            out_text("brand_name 不能为空")
            sys.exit(0)

        if not questions:
            out_text("questions 不能为空")
            sys.exit(0)

        if not api_key:
            out_text(
                f"未检测到 API key，请通过 --api-key 传入，或设置环境变量 AIDSO_GEO_API_KEY。\n"
                f"获取地址：{API_KEY_URL}"
            )
            sys.exit(0)

        _, payload = poll_report(
            brand_name=brand_name,
            questions=questions,
            api_key=api_key,
            interval_seconds=args.interval,
            max_attempts=args.max_attempts,
        )

        out_text(payload)
        sys.exit(0)

    except requests.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        if status == 401:
            out_text(
                f"当前绑定的 API key 已失效或不正确，请重新输入你在后台创建的 API key 完成绑定。\n"
                f"获取地址：{API_KEY_URL}"
            )
            sys.exit(0)

        out_text(f"请求失败：HTTP {status or '未知状态码'}")
        sys.exit(0)

    except ValueError as e:
        out_text(str(e))
        sys.exit(0)

    except Exception as e:
        out_debug(f"[ERROR] diagnosis_poll failed: {e}")
        out_text(f"诊断处理失败：{e}")
        sys.exit(0)


if __name__ == "__main__":
    main()