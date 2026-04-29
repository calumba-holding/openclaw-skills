#!/usr/bin/env python3
"""
GitLab Webhook Listener → OpenClaw Bridge

Receives GitLab MR webhook events and triggers the gitlab-mr-reviewer skill
via OpenClaw's /hooks/agent API.

Usage:
    python webhook_listener.py --port 18800
    python webhook_listener.py --port 18800 --secret "your-webhook-secret"

GitLab webhook configuration:
    URL:    http://your-server:18800/webhook
    Secret: (optional, recommended)
    Trigger: Merge Request Events, Push Events

Environment variables:
    GITLAB_WEBHOOK_SECRET    — Webhook secret token (alternative to --secret)
    OPENCLAW_GATEWAY_URL     — OpenClaw gateway base URL (default: http://127.0.0.1:18789)
    OPENCLAW_HOOK_PATH       — OpenClaw hooks base path (default: /webhooks/gitlab)
    OPENCLAW_HOOK_TOKEN      — Token for webhook endpoint
"""

import argparse
import hmac
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Optional
import urllib.request
import urllib.error
from context_config import get_config_value, load_context_config, resolve_value

DEFAULT_TRIGGER_ACTIONS = {"open", "reopen", "update"}
DEFAULT_PUSH_REVIEW_BRANCHES = {"main", "master", "develop", "dev"}


def _to_set(value: Any, default: set[str]) -> set[str]:
    if value in (None, ""):
        return set(default)
    if isinstance(value, str):
        items = [item.strip() for item in value.split(",")]
    elif isinstance(value, (list, tuple, set)):
        items = [str(item).strip() for item in value]
    else:
        return set(default)
    return {item for item in items if item}


def _to_list(value: Any, default: list[str]) -> list[str]:
    if value in (None, ""):
        return list(default)
    if isinstance(value, str):
        items = [item.strip() for item in value.split(",")]
    elif isinstance(value, (list, tuple)):
        items = [str(item).strip() for item in value]
    else:
        return list(default)
    return [item for item in items if item]


def _to_int(value: Any, default: int) -> int:
    if value in (None, ""):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_bool(value: Any, default: bool) -> bool:
    if value in (None, ""):
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return default


def trigger_openclaw_review(gateway_url: str, hook_path: str, token: str,
                            mr_id: int, mr_title: str, author: str,
                            target_branch: str, source_branch: str,
                            project_name: str, sender_name: str,
                            wake_mode: str, deliver: bool,
                            channel: str, timeout_sec: int):
    """Call OpenClaw webhook/agent endpoint to trigger the gitlab-mr-reviewer skill."""
    message = (
        f"审核 MR #{mr_id}\n"
        f"项目: {project_name}\n"
        f"标题: {mr_title}\n"
        f"作者: {author}\n"
        f"分支: {source_branch} -> {target_branch}\n"
        "要求: 使用 gitlab-mr-reviewer 完成审查并输出结论。"
    )
    payload = json.dumps({
        "message": message,
        "name": sender_name,
        "wakeMode": wake_mode,
        "deliver": deliver,
        "channel": channel,
    }).encode()

    url = f"{gateway_url.rstrip('/')}{hook_path}/agent"
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            status = resp.getcode()
            body = resp.read().decode("utf-8", errors="replace")
        print(f"[openclaw] MR !{mr_id} → skill triggered (status={status})")
        print(f"[openclaw] response: {body[:500]}")
        return status, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"[openclaw] MR !{mr_id} → trigger failed (status={exc.code}): {body[:500]}")
        return exc.code, body
    except Exception as exc:
        print(f"[openclaw] MR !{mr_id} → trigger error: {exc}")
        return 502, str(exc)

class WebhookHandler(BaseHTTPRequestHandler):
    secret: Optional[str] = None
    gateway_url: str = "http://127.0.0.1:18789"
    hook_path: str = "/webhooks/gitlab"
    hook_token: str = ""
    base_branch: str = "main"
    listen_path: str = "/webhook"
    health_path: str = "/health"
    max_payload_bytes: int = 5 * 1024 * 1024
    enable_mr_events: bool = True
    enable_push_events: bool = True
    mr_trigger_actions: set[str] = set(DEFAULT_TRIGGER_ACTIONS)
    mr_required_state: str = "opened"
    mr_skip_tags: list[str] = ["[skip-review]"]
    push_review_branches: set[str] = set(DEFAULT_PUSH_REVIEW_BRANCHES)
    openclaw_sender_name: str = "GitLab"
    openclaw_wake_mode: str = "now"
    openclaw_deliver: bool = True
    openclaw_channel: str = "last"
    openclaw_timeout_sec: int = 30

    def do_POST(self):
        request_path = self.path.split("?", 1)[0].rstrip("/")
        if request_path != self.listen_path:
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0 or content_length > self.max_payload_bytes:
            self.send_error(400, "Invalid content length")
            return

        payload = self.rfile.read(content_length)

        if self.secret:
            sig = self.headers.get("X-Gitlab-Token", "")
            if not hmac.compare_digest(sig, self.secret):
                self.send_error(403, "Invalid token")
                return

        event = self.headers.get("X-Gitlab-Event", "")

        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        if event == "Merge Request Hook" and self.enable_mr_events:
            self._handle_mr_event(data)
        elif event == "Push Hook" and self.enable_push_events:
            self._handle_push_event(data)
        else:
            self._respond(200, {"status": "ignored", "reason": f"event={event}"})

    def _handle_mr_event(self, data: dict):
        attrs = data.get("object_attributes", {})
        action = attrs.get("action", "")
        mr_id = attrs.get("iid")
        mr_title = attrs.get("title", "")
        state = attrs.get("state", "")
        target_branch = attrs.get("target_branch") or self.base_branch
        source_branch = attrs.get("source_branch", "")
        author = data.get("user", {}).get("name", "unknown")
        project_name = data.get("project", {}).get("path_with_namespace", "")

        lowered_title = (mr_title or "").lower()
        if any(tag.lower() in lowered_title for tag in self.mr_skip_tags):
            self._respond(200, {"status": "skipped", "reason": "title_skip_review_tag", "mr_id": mr_id})
            return

        state_allowed = (not self.mr_required_state) or (state == self.mr_required_state)
        if action not in self.mr_trigger_actions or not state_allowed:
            self._respond(200, {"status": "skipped", "action": action, "state": state})
            return

        print(f"[webhook] MR !{mr_id} '{mr_title}' action={action} → triggering OpenClaw skill")
        thread = threading.Thread(
            target=trigger_openclaw_review,
            args=(self.gateway_url, self.hook_path, self.hook_token, mr_id,
                  mr_title, author, target_branch, source_branch, project_name,
                  self.openclaw_sender_name, self.openclaw_wake_mode,
                  self.openclaw_deliver, self.openclaw_channel,
                  self.openclaw_timeout_sec),
            daemon=True,
        )
        thread.start()
        self._respond(200, {"status": "accepted", "mr_id": mr_id})

    def _handle_push_event(self, data: dict):
        ref = data.get("ref", "")
        branch = ref.replace("refs/heads/", "")
        if branch not in self.push_review_branches:
            self._respond(200, {"status": "skipped", "reason": f"push to {branch}, not in review branches"})
            return

        commits = data.get("commits", [])
        if not commits:
            self._respond(200, {"status": "skipped", "reason": "no commits"})
            return

        project_name = data.get("project", {}).get("path_with_namespace", "")
        author = data.get("user_name", "unknown")
        commit_count = len(commits)
        last_commit_msg = commits[-1].get("message", "").split("\n")[0] if commits else ""

        message = (
            f"收到 push 事件，请检查 {project_name} 的 {branch} 分支最新 {commit_count} 个提交\n"
            f"最新提交: {last_commit_msg}\n"
            f"推送者: {author}"
        )
        payload = json.dumps({
            "message": message,
            "name": self.openclaw_sender_name,
            "wakeMode": self.openclaw_wake_mode,
            "deliver": self.openclaw_deliver,
            "channel": self.openclaw_channel,
        }).encode()

        url = f"{self.gateway_url.rstrip('/')}{self.hook_path}/agent"
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {self.hook_token}")

        try:
            with urllib.request.urlopen(req, timeout=self.openclaw_timeout_sec) as resp:
                status = resp.getcode()
                body = resp.read().decode("utf-8", errors="replace")
            print(f"[openclaw] push {branch} → notified (status={status})")
            self._respond(200, {"status": "accepted", "branch": branch})
        except Exception as exc:
            print(f"[openclaw] push {branch} → notify failed: {exc}")
            self._respond(502, {"status": "error", "error": str(exc)})

    def do_GET(self):
        if self.path == self.health_path:
            self._respond(200, {"status": "ok"})
        else:
            self.send_error(404)

    def _respond(self, code: int, body: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, format, *args):
        print(f"[http] {format % args}")


def main():
    parser = argparse.ArgumentParser(description="GitLab Webhook → OpenClaw Bridge")
    parser.add_argument("--port", type=int, help="Listen port (default from reviewer.config.json: webhookListener.port)")
    parser.add_argument("--context-file", help="JSON config path (default: ../reviewer.config.json)")
    parser.add_argument("--secret", help="GitLab webhook secret token")
    parser.add_argument("--gateway-url", help="OpenClaw gateway URL")
    parser.add_argument("--hook-path", help="OpenClaw hooks base path")
    parser.add_argument("--hook-token", help="OpenClaw hook token")
    parser.add_argument("--base-branch", help="Default base branch")
    args = parser.parse_args()
    cfg = load_context_config(args.context_file)
    listener_cfg = get_config_value(cfg, "webhookListener", {})
    openclaw_cfg = get_config_value(cfg, "openclaw", {})

    WebhookHandler.secret = resolve_value(
        args.secret,
        get_config_value(openclaw_cfg, "gitlabWebhookSecret"),
        "GITLAB_WEBHOOK_SECRET",
        "",
    )
    WebhookHandler.gateway_url = resolve_value(
        args.gateway_url,
        get_config_value(openclaw_cfg, "gatewayUrl"),
        "OPENCLAW_GATEWAY_URL",
        "http://127.0.0.1:18789",
    )
    WebhookHandler.hook_path = resolve_value(
        args.hook_path,
        get_config_value(openclaw_cfg, "hookPath"),
        "OPENCLAW_HOOK_PATH",
        "/webhooks/gitlab",
    ).rstrip("/")
    WebhookHandler.hook_token = resolve_value(
        args.hook_token,
        get_config_value(openclaw_cfg, "hookToken"),
        "OPENCLAW_HOOK_TOKEN",
        "",
    )
    WebhookHandler.base_branch = resolve_value(
        args.base_branch,
        get_config_value(cfg, "gitlab.defaultBaseBranch"),
        "GITLAB_DEFAULT_BASE_BRANCH",
        "main",
    )
    WebhookHandler.listen_path = str(get_config_value(listener_cfg, "listenPath", "/webhook")).rstrip("/") or "/webhook"
    WebhookHandler.health_path = str(get_config_value(listener_cfg, "healthPath", "/health"))
    WebhookHandler.max_payload_bytes = _to_int(get_config_value(listener_cfg, "maxPayloadBytes"), 5 * 1024 * 1024)
    WebhookHandler.enable_mr_events = _to_bool(get_config_value(listener_cfg, "enableMergeRequestEvents"), True)
    WebhookHandler.enable_push_events = _to_bool(get_config_value(listener_cfg, "enablePushEvents"), True)
    WebhookHandler.mr_trigger_actions = _to_set(get_config_value(listener_cfg, "mrTriggerActions"), DEFAULT_TRIGGER_ACTIONS)
    WebhookHandler.mr_required_state = str(get_config_value(listener_cfg, "mrRequiredState", "opened"))
    WebhookHandler.mr_skip_tags = _to_list(get_config_value(listener_cfg, "mrSkipTitleTags"), ["[skip-review]"])
    WebhookHandler.push_review_branches = _to_set(get_config_value(listener_cfg, "pushReviewBranches"), DEFAULT_PUSH_REVIEW_BRANCHES)
    WebhookHandler.openclaw_sender_name = str(get_config_value(listener_cfg, "openclawSenderName", "GitLab"))
    WebhookHandler.openclaw_wake_mode = str(get_config_value(listener_cfg, "openclawWakeMode", "now"))
    WebhookHandler.openclaw_deliver = _to_bool(get_config_value(listener_cfg, "openclawDeliver"), True)
    WebhookHandler.openclaw_channel = str(get_config_value(listener_cfg, "openclawChannel", "last"))
    WebhookHandler.openclaw_timeout_sec = _to_int(get_config_value(listener_cfg, "openclawTimeoutSec"), 30)
    listen_port = _to_int(resolve_value(args.port, get_config_value(listener_cfg, "port"), "GITLAB_WEBHOOK_PORT", 18800), 18800)

    if not WebhookHandler.hook_token:
        print("[webhook] WARNING: No OPENCLAW_HOOK_TOKEN set, API calls will fail")

    server = HTTPServer(("0.0.0.0", listen_port), WebhookHandler)
    print(f"[webhook] Listening on 0.0.0.0:{listen_port}{WebhookHandler.listen_path}")
    print(f"[webhook] OpenClaw gateway: {WebhookHandler.gateway_url}")
    print(f"[webhook] OpenClaw hook endpoint: {WebhookHandler.hook_path}/agent")
    if WebhookHandler.secret:
        print("[webhook] GitLab secret token verification enabled")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[webhook] Shutting down")
        server.server_close()


if __name__ == "__main__":
    main()
