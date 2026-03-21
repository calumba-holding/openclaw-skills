---
name: builder
version: "2.0.0"
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
license: MIT-0
tags: [builder, tool, utility]
description: "Scaffold new projects, generate boilerplate, and configure build systems. Use when starting repos, generating structures, or setting up build tools."
---

# Builder

Gaming toolkit — track rolls, scores, ranks, challenges, leaderboards, rewards, and more. Each command logs entries with timestamps for full traceability and historical review.

## Commands

| Command | Description |
|---------|-------------|
| `builder roll <input>` | Log a roll entry (no args = view recent rolls) |
| `builder score <input>` | Log a score entry (no args = view recent scores) |
| `builder rank <input>` | Log a rank entry (no args = view recent ranks) |
| `builder history <input>` | Log a history entry (no args = view recent history) |
| `builder stats <input>` | Log a stats entry (no args = view recent stats) |
| `builder challenge <input>` | Log a challenge entry (no args = view recent challenges) |
| `builder create <input>` | Log a create entry (no args = view recent creates) |
| `builder join <input>` | Log a join entry (no args = view recent joins) |
| `builder track <input>` | Log a track entry (no args = view recent tracks) |
| `builder leaderboard <input>` | Log a leaderboard entry (no args = view recent leaderboard) |
| `builder reward <input>` | Log a reward entry (no args = view recent rewards) |
| `builder reset <input>` | Log a reset entry (no args = view recent resets) |
| `builder export <fmt>` | Export all data (json, csv, or txt) |
| `builder search <term>` | Search across all log entries |
| `builder recent` | Show last 20 history entries |
| `builder status` | Health check — version, entry count, disk usage |
| `builder help` | Show usage info |
| `builder version` | Show version string |

## Data Storage

All data is stored locally in `~/.local/share/builder/`. Each command writes to its own `.log` file (e.g., `roll.log`, `score.log`, `challenge.log`). A unified `history.log` records every action with timestamps. No external services or databases required.

**Log format:** `YYYY-MM-DD HH:MM|<value>`

## Requirements

- **bash** (version 4+ recommended)
- Standard POSIX utilities: `date`, `wc`, `du`, `grep`, `tail`, `head`, `cat`, `sed`
- No external dependencies, no network access needed
- Works on Linux, macOS, and WSL

## When to Use

1. **Tracking game scores and rankings** — Log scores, ranks, and rolls for tabletop games, video game sessions, or competitive events
2. **Running challenges and competitions** — Create challenges, track participants with `join`, monitor progress with `track`, and display results on the `leaderboard`
3. **Managing rewards and resets** — Record rewards for achievements and reset counters or sessions when starting fresh
4. **Exporting gaming data for analysis** — Export all logged data in JSON, CSV, or TXT format for external analysis or sharing
5. **Reviewing activity history** — Use `recent`, `search`, and `stats` to audit past sessions, find specific entries, or get summary statistics

## Examples

```bash
# Log a dice roll
builder roll "d20 = 17, critical hit"

# Record a game score
builder score "Round 3: 2450 points"

# Track a challenge
builder challenge "Speed run: complete level 5 in under 2 minutes"

# Join a game session
builder join "Tournament #42 — Team Alpha"

# Update the leaderboard
builder leaderboard "Player1: 9800 | Player2: 9200 | Player3: 8700"

# Search for specific entries across all logs
builder search "critical"

# Export everything as JSON
builder export json

# View overall stats
builder stats

# Check system status
builder status
```

## How It Works

Builder stores all data locally in `~/.local/share/builder/`. Each command logs activity with timestamps for full traceability. Use `stats` to see a summary of entries per category, `search` to find specific entries across all logs, `recent` to view the latest activity, or `export` to back up your data in JSON, CSV, or plain text format.

---

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
