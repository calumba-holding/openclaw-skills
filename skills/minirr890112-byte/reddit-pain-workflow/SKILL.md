---
name: reddit-pain-workflow
version: 0.2
description: >-
  Daily automated pipeline: Reddit scan → classify → generate report → push to GitHub → metrics tracking.
  Cron-friendly with short timeouts. Drives star growth via search optimization.
category: product
---

# Reddit Pain → GitHub Report Daily Pipeline

A fully automated cron-driven pipeline that scans Reddit for pain points, classifies them against existing tools, generates a daily report pushed to GitHub, and tracks repo metrics for growth.

## When to use
- Building a data-driven open-source project that needs daily content
- Wanting automated pain discovery with GitHub as the delivery surface
- Need a growth engine: daily reports → discoverable on GitHub → drives stars

## Architecture

```
Cron (8 AM daily)
  ↓
Reddit scan (5 subreddits, native .json API, 8s timeout)
  ↓
Pain classification (8 categories, matched against existing tools)
  ↓
DAILY-REPORT.md generation (markdown with quotes, links, tool candidates)
  ↓
Git commit + push to repo
  ↓
Metrics snapshot (stars, views, clones, search ranking)
```

## Key Implementation Details

### Reddit Scan
- Use `https://www.reddit.com/r/{sub}/hot.json` (no auth needed)
- 5 subreddits max for cron speed: ChatGPT, ClaudeAI, LocalLLaMA, programming, webdev
- Timeout: 8s per request, 0.5s delay between requests
- Walk comment tree to depth 2 for replies
- Pushshift.io is DEAD (403), PRAW needs client_id (skip for public)

### Pain Classification
Categories match our tool coverage:
| Category | Existing Tool |
|----------|--------------|
| AI Censorship / Safety | prompt-inspector |
| AI Model Degradation | model-watch |
| AI API Pricing / Cost | api-cost |
| GitHub / CI-CD Issues | none yet |
| AI Code Quality | none yet |
| Local LLM / Deployment | none yet |
| Supply Chain Security | none yet |
| AI Detection / Deepfake | none yet |

Threshold: ≥3 signals in a category with no existing tool → flagged as "New Tool Candidate"

### GitHub Report Generation
- Output: `DAILY-REPORT.md` in repo root
- Format: summary → per-category top 3 quotes with permalinks → tool candidates → growth tip → metrics
- Auto-committed with timestamp, pushed to main

### GitHub Search Optimization (Critical for Star Growth)
GitHub search indexes: **repo description** + **topics** (20 max) + lightly on README.

Recipe that worked (verified 2026-04):
1. **Description**: keyword-dense, comma-separated: `"AI CLI tools: prompt censorship checker & bypass, model quality watchdog & degradation monitor, API cost comparison for OpenAI Claude DeepSeek Gemini. Built from real Reddit user complaints."`
2. **Topics** (19): `ai, python, cli, api, llm, openai, claude, deepseek, devtools, reddit, prompt-engineering, cost-optimization, benchmark, censorship, censorship-bypass, model-monitoring, model-degradation, cost-comparison, llm-pricing`
3. **Result**: repo ranks #1 for searches like "model degradation monitor cli", "prompt censorship bypass cli", "llm cost comparison"

### Metrics Tracking
Separate script `scripts/github-metrics` records:
- Stars, forks, watchers
- Views (from traffic API)
- Clones
- Search ranking for 7 target keywords

## Cron Job Setup

```bash
# Daily pipeline (8 AM)
hermes cronjob create --name daily-reddit-pipeline --schedule "0 8 * * *" \
  --prompt "Run python3 ~/HermesMade/scripts/daily-pipeline run. Then present a 3-line summary."

# Daily metrics (9 AM)
hermes cronjob create --name github-metrics-daily --schedule "0 9 * * *" \
  --prompt "Run python3 ~/HermesMade/scripts/github-metrics snapshot then report."
```

## Feishu Bitable Setup (one-time)

```bash
# Create app
lark-cli api POST /open-apis/bitable/v1/apps --data '{"name":"Pain Points"}'

# Create table with fields
lark-cli api POST /open-apis/bitable/v1/apps/{app_token}/tables --data '{
  "table": {
    "name": "痛点清单",
    "fields": [
      {"field_name": "序号", "type": 2},
      {"field_name": "分类", "type": 3},
      {"field_name": "痛点名称", "type": 1},
      {"field_name": "频次指数", "type": 3},
      {"field_name": "用户原声", "type": 1},
      {"field_name": "Hermes方案", "type": 1},
      {"field_name": "状态", "type": 3}
    ]
  }
}'

# Batch insert
lark-cli api POST "/open-apis/bitable/v1/apps/{token}/tables/{table}/records/batch_create" \
  --data "$(cat records.json)"
```

## GitHub API via urllib (Fallback — No gh CLI Required)

When the `github` skill/tools aren't available but a GitHub token is, use Python stdlib `urllib` for file commits:

```python
import json, base64, urllib.request

token = os.environ["GITHUB_TOKEN"]
repo = "owner/repo"
file_path = "path/in/repo.sh"

with open("/tmp/file.sh", "rb") as f:
    content = f.read()
encoded = base64.b64encode(content).decode()

# Step 1: Check if file exists (get SHA for update)
get_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
get_req = urllib.request.Request(get_url, headers={
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "hermes-agent"
})

sha = None
try:
    with urllib.request.urlopen(get_req, timeout=10) as resp:
        sha = json.loads(resp.read()).get("sha")
except urllib.error.HTTPError as e:
    if e.code == 404:
        pass  # File doesn't exist, will create
    else:
        raise

# Step 2: PUT create or update
put_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
payload = {
    "message": "feat: auto-generated report [HERMES-N]",
    "content": encoded,
    "branch": "main"
}
if sha:
    payload["sha"] = sha

put_req = urllib.request.Request(put_url, 
    data=json.dumps(payload).encode("utf-8"),
    method="PUT",
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "hermes-agent"
    })

with urllib.request.urlopen(put_req, timeout=15) as resp:
    result = json.loads(resp.read())
    print(f"Committed: {result['commit']['sha'][:7]}")
```

**Pitfalls**: 
- `User-Agent` header is required by GitHub API, otherwise 403
- `Accept: application/vnd.github+json` needed for newer API endpoints
- For **binary files**: base64 encode the raw bytes (no text decode step)
- For **first commit** on a new repo: file won't exist → 404 → omit `sha`

## Pip Package Pattern (for individual tools)

Each tool is a standalone pip-installable package:
```
tool-name/
├── pyproject.toml       # build-backend = "setuptools.build_meta"
├── README.md
└── tool_name/
    ├── __init__.py
    └── cli.py
```

Install: `pip install git+https://github.com/{user}/{repo}.git#subdirectory=tool-name`

⚠ `setuptools.backends._legacy:_Backend` does NOT work. Use `setuptools.build_meta`.

## Pitfalls
- Reddit cloud browser access: blocked by security. Use native API only.
- `gh search repos` has slower index than web UI search — web results may show repo that API doesn't yet
- Topic limit: 20 max. Remove generic ones (productivity, tools) to fit search-critical ones
- `lark-cli` is interactive on first run. Set `LARK_LANGUAGE=zh` env var before first use
- Pip install in sandbox: use `--break-system-packages` on macOS Homebrew Python
