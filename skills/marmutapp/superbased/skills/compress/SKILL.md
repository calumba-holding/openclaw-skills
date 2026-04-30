---
name: compress
description: Compress large text into token-efficient images using the Token Compression Engine
---

When dealing with large text content (logs, code, documents) that exceeds ~500 tokens, use `superbased_compress_text` to convert it into optimized images that cost fewer tokens.

**Theme selection:**
- `"terminal"` -- CLI output, build logs, server logs
- `"dark"` -- source code, config files
- `"paper"` -- documentation, articles, prose
- `"light"` -- general text, mixed content
- `"high-contrast"` -- accessibility, presentations

**Parameters:**
- `preset: "auto"` -- let the engine pick optimal resolution
- `columns: "auto"` -- auto-detect best column layout
- `render_style: "auto"` -- auto-detect code vs document vs terminal

**When to use:**
- Pasting large file contents into context
- Sharing build/test output
- Including documentation in conversations
- Any text block where image tokens < text tokens (typically >500 tokens)
