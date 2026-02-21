---
name: publora-facebook
description: >
  Post or schedule content to Facebook using the Publora API. Use this skill
  when the user wants to publish or schedule Facebook posts via Publora.
---

# Publora — Facebook

Post and schedule Facebook content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Get Your Facebook Platform ID

```bash
GET https://api.publora.com/api/v1/platform-connections
# Look for entries like "facebook-111222333"
```

## Post to Facebook Immediately

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Big news! We just launched our new product. Check it out 👇',
    platforms: ['facebook-111222333']
  })
});
```

## Schedule a Facebook Post

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Happy Friday! Here\'s what we shipped this week...',
    platforms: ['facebook-111222333'],
    scheduledTime: '2026-03-20T12:00:00.000Z'
  })
});
```

## Facebook Post with Image

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'Meet the team behind the product 👋',
    'platforms': ['facebook-111222333'],
    'scheduledTime': '2026-03-16T12:00:00.000Z'
}).json()

upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'team.jpg', 'contentType': 'image/jpeg',
    'type': 'image', 'postGroupId': post['postGroupId']
}).json()

with open('team.jpg', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/jpeg'}, data=f)
```

## Cross-post: Facebook + Instagram + Threads

```javascript
body: JSON.stringify({
  content: 'Your content here',
  platforms: ['facebook-111222333', 'instagram-456', 'threads-789'],
  scheduledTime: '2026-03-16T12:00:00.000Z'
})
```

## Tips for Facebook

- **Best times:** Wednesday 11 AM–1 PM, Thursday/Friday 1–3 PM
- **Video gets 3x reach** of static images on Facebook currently
- **Link posts:** Facebook suppresses external links — put the link in comments instead
- **Optimal length:** 40–80 characters for max engagement (short, punchy)
- **Pages vs profiles:** Publora connects to Pages for business use
