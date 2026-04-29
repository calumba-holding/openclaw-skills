#!/usr/bin/env python3
"""
GitLab Inline Commenter

Posts diff-bound inline comments (Diff Notes) to a GitLab MR via the
Discussions API. Comments appear in the "Changes" tab next to the specific
changed line, not just in the Overview tab.

Usage:
    # Post a single inline comment
    python gitlab_inline_commenter.py \
        --host gitlab.example.com \
        --project-id 123 \
        --mr-id 42 \
        --file src/auth/token_service.py \
        --line 47 \
        --body "JWT token expiration not validated — add exp check."

    # Post from a JSON findings file (output of mr_analyzer.py --json)
    python gitlab_inline_commenter.py \
        --host gitlab.example.com \
        --project-id 123 \
        --mr-id 42 \
        --findings /tmp/mr_42_analysis.json

    # Dry-run (print what would be posted, no API calls)
    python gitlab_inline_commenter.py ... --dry-run
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Tuple
from context_config import get_config_value, load_context_config, resolve_value


# ---------------------------------------------------------------------------
# GitLab API client (stdlib only — no requests dependency)
# ---------------------------------------------------------------------------

class GitLabClient:
    def __init__(self, host: str, token: str, project_id: str):
        self.base = f"https://{host}/api/v4/projects/{project_id}"
        self.token = token

    def _request(self, method: str, path: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.base}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={
                "PRIVATE-TOKEN": self.token,
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode()
            raise RuntimeError(f"GitLab API {method} {url} → {e.code}: {body_text}") from e

    def get_mr_diff_refs(self, mr_iid: int) -> Dict:
        """Return diff_refs: {base_sha, start_sha, head_sha}."""
        mr = self._request("GET", f"/merge_requests/{mr_iid}")
        return mr.get("diff_refs", {})

    def post_inline_comment(
        self,
        mr_iid: int,
        diff_refs: Dict,
        file_path: str,
        new_line: int,
        body: str,
        old_line: Optional[int] = None,
    ) -> Dict:
        """
        Create a Diff Note bound to a specific line in the MR diff.

        new_line  — line number in the new (head) version of the file
        old_line  — line number in the old (base) version; None for added lines
        """
        position = {
            "position_type": "text",
            "base_sha": diff_refs["base_sha"],
            "start_sha": diff_refs["start_sha"],
            "head_sha": diff_refs["head_sha"],
            "new_path": file_path,
            "old_path": file_path,
            "new_line": new_line,
        }
        if old_line is not None:
            position["old_line"] = old_line

        return self._request(
            "POST",
            f"/merge_requests/{mr_iid}/discussions",
            {"body": body, "position": position},
        )

    def post_summary_note(self, mr_iid: int, body: str) -> Dict:
        """Post a general (non-diff-bound) MR note in the Overview tab."""
        return self._request(
            "POST",
            f"/merge_requests/{mr_iid}/notes",
            {"body": body},
        )


# ---------------------------------------------------------------------------
# Finding → comment body formatter
# ---------------------------------------------------------------------------

SEVERITY_EMOJI = {
    "critical": "🔴",
    "major":    "🟠",
    "high":     "🟠",
    "minor":    "🟡",
    "medium":   "🟡",
    "low":      "🟢",
    "suggestion": "💡",
}

DIMENSION_LABEL = {
    "security":     "安全",
    "logic":        "逻辑",
    "architecture": "架构",
    "quality":      "质量",
    "performance":  "性能",
    "testing":      "测试",
}


def format_comment(finding: Dict) -> str:
    """Format a finding dict into a GitLab Markdown comment body."""
    sev = finding.get("severity", "medium")
    dim = finding.get("dimension", "")
    title = finding.get("title") or finding.get("message", "")
    description = finding.get("description", "")
    suggestion = finding.get("suggestion", "")
    confidence = finding.get("confidence")

    emoji = SEVERITY_EMOJI.get(sev, "🟡")
    dim_label = DIMENSION_LABEL.get(dim, dim)

    # Low confidence: downgrade to a question rather than assertion
    low_confidence = confidence is not None and confidence < 0.6
    if low_confidence:
        emoji = "❓"
        prefix = "**[待确认]**"
    else:
        prefix = f"{emoji} **[{sev.upper()}]**"

    lines = [f"{prefix} {title}"]
    if dim_label:
        lines[0] += f"  ·  _{dim_label}_"
    if description and description != title:
        lines.append(f"\n{description}")
    if suggestion:
        if low_confidence:
            lines.append(f"\n💬 **请确认：** {suggestion}")
        else:
            lines.append(f"\n💡 **建议：** {suggestion}")
    if confidence is not None:
        lines.append(f"\n_置信度: {confidence:.0%}_")
    lines.append("\n\n> *由 GitLab MR Reviewer 自动生成*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Batch posting from findings list
# ---------------------------------------------------------------------------

def post_findings(
    client: GitLabClient,
    mr_iid: int,
    findings: List[Dict],
    dry_run: bool = False,
    max_inline: int = 20,
) -> Tuple[int, int]:
    """
    Post inline comments for each finding that has file_path + line.
    Findings without a line fall back to a summary note.

    Returns (inline_posted, fallback_posted).
    """
    diff_refs = None
    if not dry_run:
        diff_refs = client.get_mr_diff_refs(mr_iid)
        if not diff_refs.get("head_sha"):
            print("⚠️  Could not fetch diff_refs — falling back to summary notes only",
                  file=sys.stderr)
            diff_refs = None

    inline_posted = 0
    fallback_posted = 0

    for finding in findings:
        file_path = finding.get("file_path") or finding.get("file")
        line = finding.get("line") or finding.get("line_number")
        body = format_comment(finding)

        if file_path and line and diff_refs and inline_posted < max_inline:
            if dry_run:
                print(f"[DRY-RUN] inline → {file_path}:{line}\n{body}\n{'-'*60}")
            else:
                try:
                    client.post_inline_comment(mr_iid, diff_refs, file_path, int(line), body)
                    print(f"✅ inline → {file_path}:{line}")
                    inline_posted += 1
                except RuntimeError as e:
                    # Line may not exist in diff — fall back to summary note
                    print(f"⚠️  inline failed ({e}), falling back to note", file=sys.stderr)
                    if not dry_run:
                        client.post_summary_note(mr_iid, f"**{file_path}:{line}**\n\n{body}")
                    fallback_posted += 1
        else:
            # No line info or diff_refs unavailable — post as general note
            note_body = f"**{file_path}**\n\n{body}" if file_path else body
            if dry_run:
                print(f"[DRY-RUN] note → {file_path or '(no file)'}\n{note_body}\n{'-'*60}")
            else:
                client.post_summary_note(mr_iid, note_body)
                print(f"📝 note → {file_path or '(summary)'}")
            fallback_posted += 1

    return inline_posted, fallback_posted


# ---------------------------------------------------------------------------
# Load findings from mr_analyzer.py JSON output
# ---------------------------------------------------------------------------

def load_findings_from_analysis(path: str) -> List[Dict]:
    """
    Extract findings from mr_analyzer.py --json output.
    Converts risk entries to the finding schema expected by post_findings().
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    findings = []
    risks = data.get("risks", {})
    for severity in ("critical", "high", "medium", "low"):
        for risk in risks.get(severity, []):
            findings.append({
                "file_path": risk.get("file"),
                "line": None,  # static scan has no line number
                "severity": severity,
                "dimension": "security",
                "title": risk.get("message", risk.get("name", "")),
                "description": "",
                "suggestion": "",
            })
    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Post inline diff comments to a GitLab MR"
    )
    parser.add_argument("--context-file", help="JSON config path (default: ../reviewer.config.json)")
    parser.add_argument("--host", help="GitLab host")
    parser.add_argument("--token", help="GitLab PAT")
    parser.add_argument("--project-id",
                        help="GitLab project ID or URL-encoded namespace/project")
    parser.add_argument("--mr-id", type=int, required=True,
                        help="MR IID (the number shown in the GitLab UI)")

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--findings", metavar="JSON_FILE",
                        help="Path to mr_analyzer.py --json output file")
    source.add_argument("--body", help="Single comment body (use with --file and --line)")

    parser.add_argument("--file", help="File path for single comment")
    parser.add_argument("--line", type=int, help="New-file line number for single comment")
    parser.add_argument("--severity", default="medium",
                        choices=["critical", "high", "medium", "low", "suggestion"],
                        help="Severity for single comment (default: medium)")
    parser.add_argument("--dimension", default="",
                        help="Review dimension for single comment (security/logic/…)")
    parser.add_argument("--max-inline", type=int, default=20,
                        help="Max inline comments to post (default: 20)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be posted without making API calls")
    args = parser.parse_args()
    cfg = load_context_config(args.context_file)

    host = resolve_value(args.host, get_config_value(cfg, "gitlab.host"), "GITLAB_HOST", "gitlab.com")
    token = resolve_value(args.token, get_config_value(cfg, "gitlab.token"), "GITLAB_TOKEN", "")
    project_id = resolve_value(
        args.project_id,
        get_config_value(cfg, "gitlab.projectId"),
        "GITLAB_PROJECT_ID",
        "",
    )

    if not project_id:
        print("Error: --project-id or gitlab.projectId/GITLAB_PROJECT_ID required", file=sys.stderr)
        sys.exit(1)

    if not args.dry_run and not token:
        print("Error: --token or gitlab.token/GITLAB_TOKEN required", file=sys.stderr)
        sys.exit(1)

    client = GitLabClient(host, token or "", project_id)

    if args.findings:
        findings = load_findings_from_analysis(args.findings)
    else:
        findings = [{
            "file_path": args.file,
            "line": args.line,
            "severity": args.severity,
            "dimension": args.dimension,
            "title": args.body,
            "description": "",
            "suggestion": "",
        }]

    inline, fallback = post_findings(
        client, args.mr_id, findings,
        dry_run=args.dry_run,
        max_inline=args.max_inline,
    )

    if not args.dry_run:
        print(f"\n完成: {inline} 条行内评论, {fallback} 条普通评论")


if __name__ == "__main__":
    main()
