---
name: telegram-history
description: Fetch Telegram chat message history via MTProto user API (Telethon). Use when needing to read old messages from any Telegram chat, group, or forum topic that the bot API can't access. Supports fetching by chat ID, forum topic/thread, message count, pagination, and JSON output. Requires one-time user login with phone number + 2FA.
---

# Telegram History

Fetch message history from any Telegram chat using MTProto (Telethon). The Bot API cannot read chat history — this skill uses the user API instead.

## Setup

### 1. Install Telethon
```bash
pip3 install telethon
```

### 2. Get API credentials
Go to https://my.telegram.org/apps and create an app. Save credentials:
```bash
cat > skills/telegram-history/api_credentials.json << 'EOF'
{"api_id": YOUR_API_ID, "api_hash": "YOUR_API_HASH"}
EOF
```

### 3. Login (one-time, interactive)
```bash
python3 scripts/login.py send
# Telegram sends a code to your phone
# Write code to a file (don't send via Telegram — it blocks shared codes):
echo YOUR_CODE > /tmp/tgcode.txt
# Then verify:
python3 scripts/login.py verify <CODE> <HASH>
# If 2FA enabled:
python3 scripts/login.py verify <CODE> <HASH> <2FA_PASSWORD>
```

Session persists in `session/` — no need to re-login.

## Usage

```bash
# Fetch last 50 messages from a chat
python3 scripts/tg_history.py history <chat_id> --limit 50

# Fetch from a forum topic
python3 scripts/tg_history.py history <chat_id> --topic <topic_id> --limit 30

# JSON output
python3 scripts/tg_history.py history <chat_id> --json

# Paginate (messages before a specific ID)
python3 scripts/tg_history.py history <chat_id> --offset-id <msg_id> --limit 50
```

## Notes

- Group chat IDs use `-100` prefix (e.g., `-1001234567890`)
- Forum topic IDs = the thread/topic message ID
- Sender names are resolved automatically
- **Don't send Telegram login codes through Telegram** — it detects sharing and blocks the login. Use a file or another channel.
