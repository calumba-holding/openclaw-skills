---
name: redact
description: Auto-redact sensitive information from screenshots before sharing
---

Before sharing screenshots that may contain sensitive data, use `superbased_redact` to automatically detect and blur secrets.

**Parameters:**
- `secrets: true` -- redacts API keys, tokens, passwords, connection strings (default on)
- `pii: true` -- redacts emails, phone numbers, names, addresses (default off, enable when needed)
- Provide either `captureId` (from a gallery capture) or `screenshotPath` (file on disk)

**When to use:**
- Before sharing terminal screenshots that may show environment variables or API keys
- Before sharing browser screenshots with logged-in sessions
- When the user asks to share a screenshot externally
- Any capture of settings, config files, or dashboards

The tool returns the redacted image with sensitive regions blurred and a count of regions found.
