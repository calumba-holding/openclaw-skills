#!/usr/bin/env python3
"""
Feishu Notifier for GitLab MR Reviews

Sends a structured review summary as a Feishu group robot card message.

Usage:
    python feishu_notifier.py \
        --webhook-url "https://open.feishu.cn/open-apis/bot/v2/hook/xxxx" \
        --mr-id 42 --mr-title "feat: add auth" \
        --mr-url "https://gitlab.example.com/group/proj/-/merge_requests/42" \
        --author "zhang.san" --verdict "request_changes" --score 62 \
        --critical 1 --high 2 --medium 3 --low 1
"""

import argparse
import json
import sys
import urllib.request
from typing import Dict, Optional
from context_config import get_config_value, load_context_config, resolve_value


VERDICT_META = {
    "approve": {"label": "Approved", "color": "green", "zh": "审核通过"},
    "approve_with_suggestions": {"label": "Approved with Suggestions", "color": "yellow", "zh": "通过（含建议）"},
    "request_changes": {"label": "Request Changes", "color": "red", "zh": "需要修改"},
    "block": {"label": "Blocked", "color": "red", "zh": "阻塞，禁止合并"},
}


def get_verdict_meta(verdict: str) -> Dict[str, str]:
    return VERDICT_META.get(verdict, {"label": verdict, "color": "grey", "zh": verdict})


def build_feishu_card(
    mr_id: int,
    mr_title: str,
    mr_url: str,
    author: str,
    verdict: str,
    score: int,
    critical: int = 0,
    high: int = 0,
    medium: int = 0,
    low: int = 0,
    extra_notes: Optional[str] = None,
) -> Dict:
    meta = get_verdict_meta(verdict)

    risk_lines = []
    if critical:
        risk_lines.append(f"🔴 Critical: **{critical}**")
    if high:
        risk_lines.append(f"🟠 High: **{high}**")
    if medium:
        risk_lines.append(f"🟡 Medium: **{medium}**")
    if low:
        risk_lines.append(f"🟢 Low: **{low}**")

    risk_text = "  |  ".join(risk_lines) if risk_lines else "无风险问题"

    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": (
                    f"**MR:** [!{mr_id} — {mr_title}]({mr_url})\n"
                    f"**作者:** {author}\n"
                    f"**审核得分:** {score}/100\n"
                    f"**风险汇总:** {risk_text}"
                ),
            },
        },
    ]
    if extra_notes:
        elements.append(
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"**备注:** {extra_notes}"},
            }
        )

    elements.append(
        {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "查看 MR"},
                    "type": "primary",
                    "url": mr_url,
                }
            ],
        }
    )

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"GitLab MR 审核结果 — {meta['zh']}"},
                "template": meta["color"],
            },
            "elements": elements,
        },
    }


def send_feishu(webhook_url: str, payload: Dict) -> bool:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url, data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            result = json.loads(body)
            if result.get("code", 0) == 0 or result.get("StatusCode") == 0:
                return True
            print(f"Feishu API error: {body}", file=sys.stderr)
            return False
    except Exception as exc:
        print(f"Failed to send Feishu message: {exc}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Send GitLab MR review notification via Feishu")
    parser.add_argument("--context-file", help="JSON config path (default: ../reviewer.config.json)")
    parser.add_argument("--webhook-url", help="Feishu robot webhook URL")
    parser.add_argument("--mr-id", type=int, required=True, help="MR IID")
    parser.add_argument("--mr-title", required=True, help="MR title")
    parser.add_argument("--mr-url", required=True, help="Full MR URL")
    parser.add_argument("--author", default="unknown", help="MR author username")
    parser.add_argument("--verdict", choices=["approve", "approve_with_suggestions", "request_changes", "block"], required=True)
    parser.add_argument("--score", type=int, default=0, help="Review score 0-100")
    parser.add_argument("--critical", type=int, default=0)
    parser.add_argument("--high", type=int, default=0)
    parser.add_argument("--medium", type=int, default=0)
    parser.add_argument("--low", type=int, default=0)
    parser.add_argument("--notes", help="Extra notes to include")
    args = parser.parse_args()
    cfg = load_context_config(args.context_file)

    webhook_url = resolve_value(
        args.webhook_url,
        get_config_value(cfg, "notifications.feishuWebhookUrl"),
        "FEISHU_WEBHOOK_URL",
        "",
    )
    if not webhook_url:
        print("Error: --webhook-url or notifications.feishuWebhookUrl/FEISHU_WEBHOOK_URL required", file=sys.stderr)
        sys.exit(1)

    payload = build_feishu_card(
        mr_id=args.mr_id, mr_title=args.mr_title, mr_url=args.mr_url,
        author=args.author, verdict=args.verdict, score=args.score,
        critical=args.critical, high=args.high, medium=args.medium,
        low=args.low, extra_notes=args.notes,
    )

    if send_feishu(webhook_url, payload):
        print(f"✅ Feishu notification sent for MR !{args.mr_id}")
    else:
        print("❌ Failed to send Feishu notification", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
