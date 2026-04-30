#!/usr/bin/env python3

import subprocess
import json
import os
from jira import JIRA

# --- Config (from Skill's references/jira.md) ---
JIRA_URL = os.environ.get("JIRA_BASE_URL", "https://attrix-team.atlassian.net/")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "xwang@attrix.ca")
# OpenClaw security redaction: secret removed from archive.
PRIMARY_PROJECT_KEY = "DS"

async def get_my_todo_issues() -> dict:
    try:
        jira_options = {"server": JIRA_URL}
        jira = JIRA(options=jira_options, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

        jql_query = f"assignee = currentUser() AND project = \"{PRIMARY_PROJECT_KEY}\" AND statusCategory in (\"To Do\") ORDER BY created DESC"
        issues = jira.search_issues(jql_query)

        issue_list = []
        for issue in issues:
            issue_list.append({"key": issue.key, "summary": issue.fields.summary, "status": issue.fields.status.name})
        
        return {"success": True, "issues": issue_list}

    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(get_my_todo_issues())
    print(json.dumps(result, indent=2))
