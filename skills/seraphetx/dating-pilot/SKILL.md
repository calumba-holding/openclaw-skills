---
name: dating-pilot
description: Tinder dating assistant - swipe with filters (age/distance), conversation manager with smart replies, follow-up messaging. Use when user wants help managing their Tinder profile and conversations.
metadata: {"openclaw":{"emoji":"💘","requires":{"bins":["dating-pilot"]},"install":[{"id":"npm","kind":"node","package":"tinder-automation","bins":["dating-pilot"],"label":"Install dating-pilot (npm)"}]}}
---

# dating-pilot

Tinder dating assistant CLI with smart profile filtering and conversation management. All commands output JSON.

## Feature Overview

- **Smart Filtering**: Browse and like profiles by age and distance preferences
- **Conversation Manager**: Manage messages, draft smart replies, send follow-ups
- **Status Monitoring**: Query chat system status and recent activity summary

## Getting Started

Before use, configure AI parameters (only Anthropic-format APIs are supported, e.g., Claude API or compatible proxy services):

```bash
# Required: Configure AI
dating-pilot config --ai-base-url <url> --ai-api-key <key> --ai-model claude-sonnet-4-6

# Optional: Configure proxy and location
dating-pilot config --proxy socks5://127.0.0.1:1080 --latitude 32.06 --longitude 118.79 --timezone Asia/Shanghai
```

## Command Reference

### Global Options

- `--help` — Show help information

### config — Configure AI, proxy, and location

```bash
# Set AI configuration (only Anthropic-format APIs supported)
dating-pilot config --ai-base-url <url> --ai-api-key <key> --ai-model <model>

# Set proxy
dating-pilot config --proxy socks5://127.0.0.1:1080

# Set location
dating-pilot config --latitude 32.06 --longitude 118.79 --timezone Asia/Shanghai

# Can be combined
dating-pilot config --ai-base-url <url> --ai-api-key <key> --proxy socks5://127.0.0.1:1080

# View current configuration
dating-pilot config --show
```

| Parameter | Required | Description |
|------|------|------|
| `--ai-base-url` | Required on first use | AI API endpoint (Anthropic format) |
| `--ai-api-key` | Required on first use | AI API key |
| `--ai-model` | No | AI model name (e.g., `claude-sonnet-4-6`) |
| `--proxy` | No | Proxy server (e.g., `socks5://127.0.0.1:1080`) |
| `--latitude` | No | Latitude |
| `--longitude` | No | Longitude |
| `--timezone` | No | Timezone (e.g., `Asia/Shanghai`) |
| `--show` | No | Show current configuration |

### swipe — Batch swipe with filters

```bash
dating-pilot swipe --like-count <N> [--min-age <N>] [--max-age <N>] [--max-distance <N>]
```

| Parameter | Required | Description |
|------|------|------|
| `--like-count` | Yes | Target number of likes |
| `--min-age` | No | Minimum age |
| `--max-age` | No | Maximum age |
| `--max-distance` | No | Maximum distance (km) |

Output example:
```json
{
  "success": true,
  "message": "Filtered swipe complete: liked 10, skipped 5, matched 2",
  "data": {
    "likedCount": 10,
    "skippedCount": 5,
    "matchedCount": 2
  }
}
```

### chat start — Start conversation manager

**⚠️ Long-running task**: Once started, the conversation manager runs in the background. Use `exec background:true` to invoke.
Automatically checks configuration and launches the browser on startup (no manual launch needed).

```bash
dating-pilot chat start [--max-chats <N>] [--user-preferences "<preferences>"]
```

| Parameter | Required | Description |
|------|------|------|
| `--max-chats` | No | Maximum number of chats to handle (default: all) |
| `--user-preferences` | No | User preferences (injected into AI personality, e.g., "girls who like sports") |

### chat stop — Stop conversation manager

```bash
dating-pilot chat stop
```

Stops the conversation manager and releases resources.

### chat status — Query chat status

```bash
dating-pilot chat status [--since <minutes>]
```

| Parameter | Required | Description |
|------|------|------|
| `--since` | No | Query activity summary for the last N minutes |

Output example (with `--since 30`):
```json
{
  "success": true,
  "data": {
    "initialized": true,
    "browserId": "tinder",
    "recentActivity": {
      "since": "2026-03-11T10:00:00.000Z",
      "newMessagesReceived": 5,
      "aiRepliesSent": 3,
      "activeChats": [
        {
          "sessionId": "abc123",
          "userName": "Alice",
          "lastMessage": "Haha okay, see you this weekend!",
          "lastMessageTime": "2026-03-11T10:25:00.000Z",
          "direction": "in"
        }
      ]
    }
  }
}
```

### chat proactive — Send follow-up messages

```bash
dating-pilot chat proactive
```

Analyzes conversations and sends follow-up messages to active matches. Requires the conversation manager to be initialized.

### open — Open a specific user's chat

```bash
dating-pilot open --user "<username>"
```

### send — Send a message

```bash
dating-pilot send --message "<message content>" [--user "<username>"]
```

If `--user` is specified, it will first open that user's chat before sending.

## Typical Workflow

```bash
# 0. First use: Configure AI (only Anthropic-format APIs supported)
dating-pilot config --ai-base-url http://your-api.com/claude --ai-api-key sk-xxx --ai-model claude-sonnet-4-6

# 1. Filtered swipe: Like 10 users aged 22-28 within 30km
dating-pilot swipe --like-count 10 --min-age 22 --max-age 28 --max-distance 30

# 2. Start conversation manager (long-running task, runs in background, auto-launches browser)
dating-pilot chat start --user-preferences "Goal: serious relationship, Style: casual and humorous"

# 3. Check chat status
dating-pilot chat status --since 30

# 4. Trigger proactive chat
dating-pilot chat proactive

# 5. Stop chat
dating-pilot chat stop
```

## Heartbeat Monitoring

Used together with HEARTBEAT.md. The Agent periodically calls `dating-pilot chat status --since 30` to get recent activity:

- **Activity detected**: Summarize new message count, AI reply count, and active chat list, then report to user
- **No activity**: Return `HEARTBEAT_OK`

Recommended heartbeat interval: `heartbeat.every: "30m"`

## Notes

1. **Configuration required before first use** — Run `dating-pilot config` to set AI parameters before using `chat start`
2. **Smart replies only support Anthropic-format APIs** — e.g., Claude API or compatible proxy services
3. **chat start is a long-running task** — Use `exec background:true` to run in the background, otherwise it will block the Agent
4. **chat start auto-launches the browser** — No manual launch needed, but Tinder must already be logged in
5. **Conflict detection** — While conversation manager is running, commands that operate the browser (swipe/open/send) will be rejected; run `chat stop` first
6. **Like limit** — Free users have a daily like limit; operate in batches (10-20 per batch)
