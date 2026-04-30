#!/usr/bin/env python3
"""
get_issue_info.py — Fetch detailed information about a Jira issue.

Usage (CLI):
    python get_issue_info.py <ISSUE_KEY>
    e.g.: python get_issue_info.py DS-123
"""

import sys
import os
import json
from jira import JIRA

# --- Config (from Skill's references/jira.md) ---
JIRA_URL = os.environ.get("JIRA_BASE_URL", "https://attrix-team.atlassian.net/")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "xwang@attrix.ca")
# OpenClaw security redaction: secret removed from archive.


def get_issue_info(issue_key: str) -> dict:
    """Fetch all key fields for a given Jira issue key (e.g. DS-123)."""
    try:
        jira = JIRA(options={"server": JIRA_URL}, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        issue = jira.issue(issue_key)
        f = issue.fields

        assignee = f.assignee.displayName if f.assignee else None
        reporter = f.reporter.displayName if f.reporter else None
        labels = list(f.labels) if f.labels else []
        subtasks = [{"key": s.key, "summary": s.fields.summary, "status": s.fields.status.name}
                    for s in f.subtasks] if f.subtasks else []
        components = [c.name for c in f.components] if f.components else []

        return {
            "success": True,
            "issue": {
                "key": issue.key,
                "summary": f.summary,
                "description": f.description,
                "status": f.status.name,
                "status_category": f.status.statusCategory.name,
                "issue_type": f.issuetype.name,
                "priority": f.priority.name if f.priority else None,
                "assignee": assignee,
                "reporter": reporter,
                "labels": labels,
                "components": components,
                "created": f.created,
                "updated": f.updated,
                "due_date": f.duedate,
                "story_points": getattr(f, "story_points", None),
                "subtasks": subtasks,
                "url": f"{JIRA_URL.rstrip('/')}/browse/{issue.key}",
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: get_issue_info.py <ISSUE_KEY>"}))
        sys.exit(1)
    result = get_issue_info(sys.argv[1].upper())
    print(json.dumps(result, indent=2))

