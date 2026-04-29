---
name: capcut-subtitle-generator
version: "1.0.0"
displayName: "CapCut Subtitle Generator — Auto-Create Captions for Your Videos Fast"
description: >
  Tired of manually typing out every word in your videos just to add subtitles? The capcut-subtitle-generator skill handles the heavy lifting — turning your video scripts, transcripts, or spoken content into properly timed, CapCut-ready subtitle files. Whether you're a content creator, educator, or social media marketer, this tool formats your captions for seamless import into CapCut, saving you hours of tedious sync work.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "short_prompts"}}
---

## Getting Started

> Welcome! Let's get your CapCut video subtitled quickly and cleanly — just share your script, transcript, or video dialogue and I'll format it into caption-ready text for CapCut. Ready to save hours? Drop your content below and let's get started!

**Try saying:**
- "Format my transcript for CapCut captions"
- "Break dialogue into short subtitle lines"
- "Generate captions for my video script"

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Turn Your Words Into Perfectly Timed CapCut Captions

Adding subtitles to your CapCut videos shouldn't mean hours of manual typing, timestamp-hunting, and formatting frustration. The CapCut Subtitle Generator skill transforms your raw transcripts, dialogue scripts, or spoken content into clean, properly structured subtitle text that slots directly into your CapCut editing workflow — no guesswork, no tedious line-by-line syncing.

Whether you're producing short-form content for TikTok, YouTube Shorts, or Instagram Reels, subtitles are no longer optional — they're essential for accessibility, watch time, and engagement. This skill generates caption blocks optimized for CapCut's subtitle editor, giving you a ready-to-use foundation that you can fine-tune in just minutes instead of starting from scratch.

Ideal for solo creators, small video production teams, and social media managers juggling multiple projects, this skill handles the repetitive formatting so you can focus on the creative side. Feed it your content, tell it your preferred style, and get subtitle-ready output that makes your CapCut sessions dramatically faster and more productive.

## Routing Caption Requests Intelligently

When you submit a video or transcript, ClawHub parses your subtitle style preferences, language settings, and caption timing parameters to route your request to the optimal CapCut-compatible processing pipeline.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Auto-Caption API Reference

CapCut Subtitle Generator runs on a cloud-based speech recognition and frame-sync engine that transcribes audio, segments caption blocks, and exports SRT or embedded subtitle files aligned to your video timeline. Processing speed scales with clip length and selected caption style — animated karaoke burns take longer than standard static captions.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `capcut-subtitle-generator`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up credits in your account" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register or upgrade your plan to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Troubleshooting Common Subtitle Issues in CapCut

If your generated subtitles look misaligned or run too long when pasted into CapCut, the most common cause is overly long lines in the source transcript. Try re-submitting with a note to break lines at 5-6 words maximum, and the output will be much easier to sync manually in CapCut's timeline.

If CapCut's auto-sync feature isn't picking up your pasted captions correctly, double-check that you're using CapCut's 'Add Text' or 'Auto Captions' section rather than pasting into a generic text layer. The subtitle generator output is formatted for CapCut's caption workflow specifically.

For videos with heavy background noise, slang, or overlapping speech, your transcript may have gaps or errors before you even submit it. Clean up those sections manually before running them through the skill — accurate input always produces more usable subtitle output. If you're unsure about a section, flag it in your prompt and the skill can suggest placeholder caption text.

## Best Practices for CapCut Subtitle Generation

For the cleanest results, provide your transcript or script as plain text with natural sentence breaks already in place. The more accurately your input reflects what's actually spoken in the video, the better your subtitle output will align when you paste it into CapCut's subtitle editor.

Keep individual caption lines short — aim for no more than 6 to 8 words per line where possible. This makes captions easier to read on mobile screens, which is where most CapCut content gets watched. When submitting your content, mention the video's pace (fast-talking, slow narration, interview-style) so the subtitle formatting can be adjusted accordingly.

If your video includes multiple speakers, label each speaker clearly in your input (e.g., 'Speaker 1:' and 'Speaker 2:'). This helps produce subtitle blocks that are easier to manage inside CapCut and reduces the editing time you'll spend after import.
