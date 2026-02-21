---
name: publora-telegram
description: >
  Post or schedule content to a Telegram channel using the Publora API. Use this
  skill when the user wants to publish or schedule posts to a Telegram channel via Publora.
---

# Publora — Telegram

Post and schedule content to Telegram channels via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Get Your Telegram Platform ID

```bash
GET https://api.publora.com/api/v1/platform-connections
# Look for entries like "telegram-1001234567890"
```

## Post to Telegram Immediately

Telegram supports **Markdown formatting** in post content:

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: '**Product Update v2.5**\n\nWe shipped:\n\n- Faster API response times (avg 45ms)\n- New `batch` endpoint\n- Better error messages\n\nFull changelog: [docs.example.com/changelog](https://docs.example.com/changelog)',
    platforms: ['telegram-1001234567890']
  })
});
```

## Schedule a Telegram Post

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: '📢 Weekly digest is coming tomorrow at 9 AM. Stay tuned!',
    platforms: ['telegram-1001234567890'],
    scheduledTime: '2026-03-15T18:00:00.000Z'
  })
});
```

## Telegram + Image

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': '📊 **Monthly Stats**\n\nHere\'s how we did in February:',
    'platforms': ['telegram-1001234567890'],
    'scheduledTime': '2026-03-01T09:00:00.000Z'
}).json()

upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'stats.png', 'contentType': 'image/png',
    'type': 'image', 'postGroupId': post['postGroupId']
}).json()

with open('stats.png', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/png'}, data=f)
```

## Tips for Telegram

- **Markdown is supported** — use `**bold**`, `_italic_`, `` `code` ``, and `[links](url)`
- **No character limit** — Telegram allows very long posts
- **Channels vs groups:** Publora connects to Channels (broadcast), not groups
- **Notification-heavy** — subscribers get push notifications; post quality matters
- **Best for:** Technical updates, newsletters, product announcements, curated content
- **Emojis 🚀** are widely used and expected in Telegram content
