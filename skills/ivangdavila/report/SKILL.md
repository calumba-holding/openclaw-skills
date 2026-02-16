---
name: Report
slug: report
version: 1.0.1
description: Configure custom recurring reports with flexible schedules, data sources, and delivery formats.
changelog: Report index now persists across skill updates
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| Task | File |
|------|------|
| Report configuration schema | `schema.md` |
| Output formats (chat, PDF, HTML, JSON) | `formats.md` |
| Delivery channels and scheduling | `delivery.md` |
| Data collection methods | `data-input.md` |
| Alert and threshold rules | `alerts.md` |
| Example reports | `examples.md` |

## Memory Storage

Report index and preferences stored at `~/reports/memory.md`. Read on activation.

**Format:**
```markdown
# Reports Memory

## Active Reports
- consulting: weekly, Monday 9am, Telegram
- health: daily, 8pm, chat prompt
- projects: monthly, 1st, PDF

## Delivery Preferences
- default-format: chat | pdf | html
- default-channel: telegram | email | file

## Schedule Overview
- Daily: health
- Weekly: consulting
- Monthly: projects
```

Create folder on first use: `mkdir -p ~/reports`

## Report Storage

```
~/reports/
├── memory.md               # Index + preferences (persistent)
├── {name}/
│   ├── config.md           # Report configuration
│   ├── data.jsonl          # Historical data
│   ├── latest.json         # Most recent values
│   └── generated/          # Past reports (PDF, HTML)
```

## Creating a Report

User says what they want to track. Agent gathers:

1. **Name** — Short identifier
2. **Metrics** — What data to include
3. **Schedule** — When to generate (daily, weekly, monthly, on-demand)
4. **Format** — How to present (chat message, PDF, HTML)
5. **Delivery** — Where to send (Telegram, file, email)
6. **Alerts** — Optional thresholds for notifications

Then creates config in `~/reports/{name}/config.md` and updates `~/reports/memory.md`.

## Scheduling Options

| Frequency | Cron Expression | Example |
|-----------|-----------------|---------|
| Daily | `0 9 * * *` | 9am every day |
| Weekly | `0 9 * * 1` | Monday 9am |
| Biweekly | `0 9 * * 1/2` | Every other Monday |
| Monthly | `0 9 1 * *` | 1st of month |
| On-demand | - | When user asks |

## Managing Reports

```
"List my reports" → Read ~/reports/memory.md
"Pause health report" → Update config, mark inactive
"Change consulting to biweekly" → Update schedule in config
"Run consulting report now" → Generate on-demand
```
