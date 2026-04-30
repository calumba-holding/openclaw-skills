#!/usr/bin/env python3
import os
"""
add_comment.py — Add a comment to an existing Jira issue.

Usage (CLI):
    python add_comment.py --key DS-123 --body "This is a comment"
"""

import json
import argparse
from jira import JIRA

# --- Config (from Skill's references/jira.md) ---
JIRA_URL = os.environ.get("JIRA_BASE_URL", "https://attrix-team.atlassian.net/")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "xwang@attrix.ca")
# OpenClaw security redaction: secret removed from archive.


def add_comment(issue_key: str, body: str) -> dict:
    """Add a text comment to the specified Jira issue."""
    try:
        jira = JIRA(options={"server": JIRA_URL}, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        comment = jira.add_comment(issue_key.upper(), body)
        return {
            "success": True,
            "key": issue_key.upper(),
            "comment_id": comment.id,
            "url": f"{JIRA_URL.rstrip('/')}/browse/{issue_key.upper()}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_comments(issue_key: str) -> dict:
    """Retrieve all comments for the specified Jira issue."""
    try:
        jira = JIRA(options={"server": JIRA_URL}, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        comments = jira.comments(issue_key.upper())
        comment_list = [
            {
                "id": c.id,
                "author": c.author.displayName,
                "body": c.body,
                "created": c.created,
                "updated": c.updated,
            }
            for c in comments
        ]
        return {"success": True, "key": issue_key.upper(), "comments": comment_list}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a comment to a Jira issue")
    parser.add_argument("--key", required=True, help="Issue key, e.g. DS-123")
    parser.add_argument("--body", required=True, help="Comment text")
    parser.add_argument("--list", action="store_true", help="List existing comments instead of adding")
    args = parser.parse_args()

    if args.list:
        result = get_comments(args.key)
    else:
        result = add_comment(args.key, args.body)
    print(json.dumps(result, indent=2))

