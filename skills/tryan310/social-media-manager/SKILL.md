# SKILL: TikTok Automation (Larry-style)

## Goal
Automate the creation and drafting of high-engagement TikTok slideshows (6 slides) using AI generation and Postiz.

## Workflow
1. **Research & Ideation**: Brainstorm hooks using the "Conflict Formula": `[Person] + [Conflict/Doubt] -> [AI Solution] -> [Resolution]`.
2. **Image Generation**: Generate 6 slides.
   - **Resolution**: 1024x1536 (Portrait).
   - **Model**: Photorealistic (e.g., Nano Banana Pro / gpt-image-1.5).
   - **Slide 1**: The "Before" or "Conflict" state + Hook Text Overlay.
   - **Slides 2-5**: The "Transformation" or "Style options".
   - **Slide 6**: The "Final Result" / Call to Action.
3. **Consistency Check**: Ensure "locked architecture" (same room/subject, different styles).
   - *Critical*: Write one detailed description of the subject/room (dimensions, windows, layout) and reuse it in EVERY prompt. Only change the style/lighting/decor.
4. **Drafting**: Upload to TikTok via Postiz API as `SELF_ONLY` (Draft).
5. **Notification**: Ping user with the caption and a link to the TikTok app to add music and publish.

## Project: FastPassPhoto
- **URL**: fastpassphoto.com
- **Product**: AI Passport/ID Photo generator and editor.
- **Price**: $15.95
- **Image Model**: Nano Banana Pro (Gemini 3 Pro Image).

## Prompt Strategy: FastPassPhoto
- **Conflict Formula**: [Person] needs a passport photo + [Common Pain Point] -> [FastPassPhoto Solution] -> [Success/Approval].
- **Pain Points**:
  - Going to a physical store (Post Office/CVS) is a hassle.
  - Getting rejected by the passport office for bad lighting/background.
  - Not liking how you look in the photo.
  - Urgency (last-minute travel).

## Postiz Configuration
- **API URL**: `https://api.postiz.com/public/v1`
- **Auth Header**: `Authorization: <API_KEY>` (No Bearer prefix).
- **Media Upload**: Must use `POST /upload` first to get `id` and `path`.
- **Posting Method**: ALWAYS use `UPLOAD` (Draft) for TikTok slideshows. `DIRECT_POST` frequently fails with multi-image content.
- **Posting Structure**:
  - Top level: `type` ("now"), `date` (ISO 8601), `posts` (array).
  - Post level: `integration: { id: "..." }`, `value: [ { content: "...", image: [ { id, path } ] } ]`.
  - Settings level: `settings: { __type: "tiktok", content_posting_method: "UPLOAD", privacy_level: "SELF_ONLY", ... }`.

## Technical Specs
- **Upload Media**: `curl -X POST {API_URL}/upload -H "Authorization: {KEY}" -F "file=@path/to/file"`
- **Create Post**: `curl -X POST {API_URL}/posts -H "Authorization: {KEY}" -H "Content-Type: application/json" -d '{...}'`

## Success Log
- **2026-02-14**: Posted "Rejected TWICE" carousel (6 slides, Conflict Formula). Fixed API fields: `duet`/`stitch`/`comment` (booleans), `autoAddMusic` ("yes"/"no"), `brand_content_toggle`/`brand_organic_toggle` (booleans). Top-level `shortLink` (bool) and `tags` (array) required.
- **2026-02-13**: Successfully transitioned to `UPLOAD` method for TikTok slideshows. Confirmed that `DIRECT_POST` triggers `ERROR` state for multi-image sequences.

## Failure Log
- **2026-02-13**: API Authentication requires `Authorization: <KEY>` (no Bearer).
- **2026-02-13**: Postiz requires `content_posting_method` and `privacy_level` in settings.
- **2026-02-13**: TikTok draft upload via Postiz requires valid media URLs (uploads.postiz.com) and correct `posts` array structure.
