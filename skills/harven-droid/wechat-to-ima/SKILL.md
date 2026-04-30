---
name: wechat-to-ima
description: Save WeChat Official Account articles into IMA notes with preserved article structure. Use when the user sends an mp.weixin.qq.com link and wants to save, archive, import, collect, or store the article in IMA/笔记/知识库. Handles parsing article metadata, preserving inline body images in order, falling back to the cover image when the body has no images, importing Markdown into IMA, and reading the note back to verify the save succeeded.
---

# WeChat to IMA

Save a WeChat article into IMA as a readable Markdown note.

## Workflow

1. Run `scripts/save_wechat_to_ima.py <url>`.
2. If the body contains inline images, keep them in original order.
3. If the body contains no inline images, insert the cover image near the top.
4. Import the generated Markdown into IMA.
5. Read the saved note back once to verify the note is not empty.

## Requirements

- `IMA_OPENAPI_CLIENTID` and `IMA_OPENAPI_APIKEY` must be available in the environment.
- Run `npm install` once inside this skill directory so the bundled extractor dependencies are available.

## Output

The script prints JSON with:

- `title`
- `account`
- `author`
- `publish_time`
- `body_img_count`
- `cover_used`
- `markdown_path`
- `note_id`
- `readback_ok`

## Notes

- Prefer this skill over ad-hoc manual parsing when the user wants the article stored in IMA.
- This skill is self-contained for article parsing and does not depend on a separate `wechat-article-extractor` installation.
- The IMA readback check uses plain text, so it confirms content landed successfully but does not visually render images in the terminal output.
- If parsing succeeds but the article body has no inline images, that is expected for some articles; use the cover-image fallback instead of treating it as a failure.
- If the original article contains code or code-block-style content, preserve it as fenced Markdown code blocks when importing into IMA; do not flatten code into ordinary prose.
