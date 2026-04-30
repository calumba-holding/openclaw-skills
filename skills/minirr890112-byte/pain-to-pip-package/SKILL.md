---
name: pain-to-pip-package
version: 0.1.0
description: >-
  Complete pipeline: Reddit pain scan → cluster → build pip-installable CLI tool → push to GitHub.
  5 tools shipped using this pattern. Proven with 343 pain signals across 6 subreddits.
category: product
---

# Pain-to-Pip-Package Pipeline

End-to-end workflow for turning Reddit complaints into standalone pip-installable CLI tools.

## When to use
- You've scanned Reddit and found a recurring pain point (≥3 signals)
- You want to build a tool that solves it
- You want the tool discoverable via GitHub search
- You want it pip-installable as a standalone package

## Pipeline Steps

### 1. Scan Reddit for pain signals

```bash
python3 scripts/daily-pipeline run
```

Uses Reddit's public `.json` API (no auth needed for reading). Key lessons:
- **Pushshift is dead** (403 Forbidden) — use `reddit.com/r/{sub}/hot.json` directly
- **Rate limits**: 429 errors after ~5 subs. Keep SCAN_TIMEOUT ≤ 8s, sleep 0.5s between requests
- **5 subreddits max** for <2 minute scans. More = diminishing returns + rate limits
- Use a realistic User-Agent header

### 2. Classify pain signals into clusters

Keywords-based clustering into 8 categories:
- AI Censorship / Safety Overreach
- AI Model Degradation
- AI API Pricing / Cost
- GitHub / CI-CD Issues
- AI Code Quality
- Local LLM / Deployment
- Supply Chain Security
- AI Detection / Deepfake

Existing tools are matched via keyword map to avoid duplicates.

### 3. Build the tool as a standalone pip package

Every tool follows this structure:
```
tool-name/
  pyproject.toml         # setuptools.build_meta, entry point
  README.md              # install + usage + pain source quote
  tool_package/
    __init__.py          # from .cli import main; __version__
    cli.py               # all logic, main() at bottom
```

**pyproject.toml template**:
```toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "tool-name"
version = "0.1.0"
description = "..."
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.8"
keywords = ["relevant", "search", "terms"]
urls = { repository = "https://github.com/OWNER/REPO" }

[project.scripts]
tool-command = "tool_package.cli:main"

[tool.setuptools.packages.find]
include = ["tool_package*"]
```

**CRITICAL**: `build-backend` must be `"setuptools.build_meta"` NOT `"setuptools.backends._legacy:_Backend"`. The latter causes `BackendUnavailable` on pip install.

### 4. Test the install

```bash
pip install --break-system-packages ./tool-name
tool-command  # verify entry point works
```

### 5. Push + Release

```bash
git add tool-name/
git commit -m "feat: tool-name — description"
git push
gh release create vX.Y.Z --title "vX.Y.Z — N Tools" --notes "..."
```

### 6. Update root README

- Add tool to the Tools section with demo output
- Update install section with new pip command
- Update roadmap table
- Add stars badge: `![Stars](https://img.shields.io/github/stars/OWNER/REPO)`

## Pitfalls

1. **Never use `execute_code` to read+write files in the same script** — `read_file` returns line-numbered content like `1|content`. If you pass that to `write_file`, the file gets literal `1|` prefixes, breaking TOML parsers.

2. **Reddit browser access blocked** — Cloud browsers get "blocked by network security" on Reddit. Only API access works. Posting requires user credentials (praw or OAuth).

3. **pip in newer macOS** — Use `--break-system-packages` flag or create venvs.

4. **GitHub topic limit** — 20 topics max. Remove generic ones (`tools`, `productivity`) to make room for search-specific ones.

## SEO: Making tools discoverable

GitHub search indexes: repo name, **description**, **topics**, README content (lower weight).

**Description formula**: `"AI CLI tools: [keyword1] & [keyword2], [keyword3] & [keyword4], [keyword5] for [providers]. [unique hook]."`

Example: `"AI CLI tools: prompt censorship checker & bypass, model quality watchdog & degradation monitor, API cost comparison for OpenAI Claude DeepSeek Gemini. Built from real Reddit user complaints."`

**Topics**: Prioritize search-intent keywords over generic ones. Every topic is a search facet.

**Validation**: After updating, search GitHub for the exact phrases users would type. Verify the repo appears in top 3.

## Daily Automation

Two cron jobs drive continuous improvement:
1. **daily-reddit-pipeline** (8:00 AM): scan → classify → report → push to GitHub
2. **github-metrics-daily** (9:00 AM): record stars/views/search rankings
