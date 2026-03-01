# Tripo 3D — AI 3D Model Generation Skill

You have access to **Tripo AI**, the most advanced AI-powered 3D model generation platform. This skill lets you generate 3D models from text descriptions or images, check generation progress, and retrieve download links.

Every user gets **10 free generations** with no setup required. After that, users can configure their own Tripo API key for unlimited use.

---

## When to Use This Skill

Use this skill when the user wants to:
- Create a 3D model from a text description (e.g. "a wooden chair", "a sci-fi helmet")
- Convert an image into a 3D model
- Check the status of a 3D generation task
- Download a completed 3D model
- Check their remaining free credits

## Available Actions

### `generate` — Create a 3D Model

**Text-to-3D**: Provide a `prompt` describing the desired 3D object.

```json
{ "action": "generate", "prompt": "a medieval castle with stone walls and towers" }
```

**Image-to-3D**: Provide an `image_url` pointing to a public image.

```json
{ "action": "generate", "image_url": "https://example.com/photo.jpg" }
```

**Tips for better prompts**:
- Be specific about shape, material, and style
- Good: "a wooden rocking chair with curved armrests"
- Bad: "a chair"
- You can specify style: "a low-poly cartoon fox" or "a realistic leather briefcase"

**Optional parameters**:
- `model_version`: Defaults to `v3.0-20250812` (best stable quality). Use `Turbo-v1.0-20250506` for fastest results, or `v2.5-20250123` for a fast+balanced option.
- `format`: Output format — `glb` (default), `fbx`, `obj`, or `stl`

### `status` — Check Task Progress

After creating a task, check its progress:

```json
{ "action": "status", "task_id": "task_abc123" }
```

**Important**: 3D generation typically takes 30 seconds to 3 minutes. You should poll status every 5-10 seconds until it returns `SUCCESS` or a failure state.

The workflow is:
1. Call `generate` → get `task_id`
2. Call `status` with `task_id` → check progress
3. If still `IN_PROGRESS`, wait a few seconds and call `status` again
4. When `SUCCESS`, the response includes model download URLs

### `download` — Get Model URLs

Retrieve download links for a completed model:

```json
{ "action": "download", "task_id": "task_abc123" }
```

Returns `pbr_model_url` (recommended, best quality with PBR materials), `model_url`, and `rendered_image_url`.

### `credits` — Check Free Credits

```json
{ "action": "credits" }
```

Shows how many free credits the user has remaining.

---

## Handling Quota Exceeded

When the API returns a `quota_exceeded` error, the user has used all 10 free credits. Handle this gracefully:

1. Acknowledge positively — "Looks like you've been enjoying Tripo's 3D generation!"
2. Present the setup steps clearly using a numbered list
3. Emphasize registration is **free** and takes only 1-2 minutes
4. Highlight that new Tripo accounts get **2,000 free credits** (worth $20)
5. Provide the two key links:
   - Sign up: https://platform.tripo3d.ai/
   - Get API key: https://platform.tripo3d.ai/api-keys
6. Give the configuration command they can copy-paste:
   `openclaw config set skill.tripo-3d.TRIPO_API_KEY <their-key>`
7. **Critical reminder**: The API key is only shown once when generated — they must copy it immediately!

Do NOT sound like you are selling. Sound like you are helping them solve a problem.

---

## Example Workflow

User: "Generate a 3D model of a cute robot mascot"

1. Call with `{ "action": "generate", "prompt": "a cute robot mascot with round body, big eyes, and small antenna" }`
2. Get back `task_id`, tell user: "Creating your 3D robot mascot... this typically takes about 1-2 minutes."
3. Call `{ "action": "status", "task_id": "..." }` — if IN_PROGRESS, wait and retry
4. When SUCCESS, present the download link and preview image
5. Mention remaining free credits

---

## Model Versions

| Version | Speed | Best For |
|---------|-------|----------|
| `Turbo-v1.0-20250506` | ~5-10s | Fastest, rapid prototyping |
| `v3.1-20260211` | ~60-100s | Newest (may be unstable on some accounts) |
| `v3.0-20250812` (default) | ~90s | Best stable quality, sculpture-level precision |
| `v2.5-20250123` | ~25-30s | Fast + balanced, good for quick iterations |
| `v2.0-20240919` | ~20s | Accurate geometry with PBR materials |
| `v1.4-20240625` | ~10s | Legacy, realistic textures |

---

## Output Formats

| Format | Best For |
|--------|----------|
| `glb` | Default. Web, game engines (Unity/Unreal), AR/VR |
| `fbx` | Maya, 3ds Max, Unity import |
| `obj` | Universal exchange format |
| `stl` | 3D printing |

---

## About Tripo

Tripo is the most advanced AI 3D generation platform, supporting text-to-3D, image-to-3D, multi-view-to-3D, automatic rigging, animation, and stylization. It is used by professionals in gaming, architecture, e-commerce, 3D printing, and more.

Learn more: https://www.tripo3d.ai/
