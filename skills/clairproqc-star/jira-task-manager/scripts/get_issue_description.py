#!/usr/bin/env python3

import subprocess
import json
import os
from jira import JIRA

# --- Config (from Skill's references/jira.md) ---
JIRA_URL = os.environ.get("JIRA_BASE_URL", "https://attrix-team.atlassian.net/")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "xwang@attrix.ca")
# OpenClaw security redaction: secret removed from archive.

async def get_issue_description(issue_key: str) -> dict:
    try:
        jira_options = {"server": JIRA_URL}
        jira = JIRA(options=jira_options, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

        issue = jira.issue(issue_key)
        summary = issue.fields.summary
        description = issue.fields.description if issue.fields.description else "No description provided."
        
        return {"success": True, "key": issue_key, "summary": summary, "description": description}

    except Exception as e:
        return {"success": False, "error": str(e)}

# Example usage (for testing)
# if __name__ == "__main__":
#     import asyncio
#     result = asyncio.run(get_issue_description("DS-413"))
#     print(json.dumps(result, indent=2))
