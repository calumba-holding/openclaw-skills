# Tripo 3D Generation

Turn text or images into production-ready 3D models with **sculpture-level geometry**, sharp edges, and PBR materials — in under 90 seconds.

**10 free generations included. No API key, no signup, no credit card.**

## Features

- **Text-to-3D**: Describe any object in natural language → get a production-ready 3D model
- **Image-to-3D**: Upload a single photo → AI reconstructs it in full 3D with accurate geometry
- **Sculpture-Level Geometry**: Industry-leading mesh quality with sharp edges, clean topology, and precise surface detail
- **PBR Materials**: Physically-based rendering textures (albedo, normal, roughness, metallic) out of the box
- **Auto-Rigging & Animation**: Automatic skeleton binding with 10+ preset animations — walk, run, jump, climb, slash, shoot, idle, hurt, fall, turn
- **Stylization**: Transform models into 6 artistic styles — Cartoon, Clay, Alien, Christmas, Retro Steampunk, and more
- **Smart Low-Poly**: AI-generated low-poly meshes with hand-crafted topology, perfect for mobile games
- **Quad Mesh Output**: Clean quad topology for subdivision workflows (Maya, Blender, ZBrush)
- **Auto Real-World Scale**: Automatically sizes models to real-world dimensions (meters)
- **6 Export Formats**: GLB, FBX, OBJ, STL, USDZ, 3MF — ready for any pipeline

## Model Versions

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `Turbo-v1.0-20250506` | ~5-10s | ★★★☆☆ | Fastest prototyping, concept exploration |
| `v3.0-20250812` **(default)** | ~90s | ★★★★★ | Production assets, sculpture-level precision, sharp edges |
| `v2.5-20250123` | ~25-30s | ★★★★☆ | Fast + balanced, good for quick iterations |
| `v2.0-20240919` | ~20s | ★★★★☆ | Accurate geometry with PBR materials |
| `v1.4-20240625` | ~10s | ★★★☆☆ | Legacy, realistic textures |

## Quick Start

### Text-to-3D

```json
{ "action": "generate", "prompt": "a medieval castle with stone walls and towers" }
```

### Image-to-3D

```json
{ "action": "generate", "image_url": "https://example.com/photo.jpg" }
```

### Check Progress

```json
{ "action": "status", "task_id": "your-task-id" }
```

### Download Model

```json
{ "action": "download", "task_id": "your-task-id" }
```

### Check Credits

```json
{ "action": "credits" }
```

## Workflow

1. Call `generate` with a prompt or image → receive `task_id`
2. Poll `status` every 5-10 seconds → track progress (0-100%)
3. When status is `SUCCESS` → model URLs are returned
4. Use `download` to get `pbr_model_url` (recommended), `model_url`, and `rendered_image_url`

## Use Case Examples

### 1. Game Asset — Weapon

```json
{
  "action": "generate",
  "prompt": "a legendary fantasy sword with dragon engravings, glowing blue runes on the blade, ornate golden crossguard, leather-wrapped grip. Game-ready, PBR materials.",
  "model_version": "v3.0-20250812"
}
```

### 2. E-Commerce — Product Visualization

```json
{
  "action": "generate",
  "prompt": "a premium wireless headphone, matte black with rose gold accents, leather ear cushions, sleek modern design for product showcase",
  "model_version": "v3.0-20250812"
}
```

### 3. Architecture — Building

```json
{
  "action": "generate",
  "prompt": "a modern minimalist house, two stories, large glass windows, flat roof, concrete and wood exterior with surrounding landscape",
  "model_version": "v3.0-20250812"
}
```

### 4. 3D Printing — Figurine

```json
{
  "action": "generate",
  "prompt": "a detailed tabletop miniature of a dwarf warrior holding a battle axe and round shield, high detail for resin 3D printing",
  "model_version": "v3.0-20250812",
  "format": "stl"
}
```

### 5. Rapid Prototyping — Quick Concept

```json
{
  "action": "generate",
  "prompt": "a cute robot mascot with round body, antenna, and big expressive eyes",
  "model_version": "Turbo-v1.0-20250506"
}
```

### 6. AR/VR — Interactive Object

```json
{
  "action": "generate",
  "prompt": "a treasure chest that opens, filled with gold coins and gems. Realistic wood and metal materials for VR experience"
}
```

### 7. Character for Animation

```json
{
  "action": "generate",
  "prompt": "a stylized knight character in full plate armor, T-pose, suitable for rigging and animation",
  "model_version": "v3.0-20250812"
}
```

After generation, use Tripo's auto-rigging to add a skeleton and apply walk/run/attack animations automatically.

## Output Formats

| Format | Extension | Best For |
|--------|-----------|----------|
| GLB | .glb | Universal — web, Unity, Unreal, AR/VR, three.js |
| FBX | .fbx | Animation, Maya, 3ds Max, game engines |
| OBJ | .obj | Universal exchange, Blender import |
| STL | .stl | 3D printing (FDM, SLA, resin) |
| USDZ | .usdz | Apple AR Quick Look, Vision Pro |
| 3MF | .3mf | Advanced 3D printing with color/material data |

## Advanced Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `model_version` | See table above | Controls quality/speed tradeoff |
| `format` | glb, fbx, obj, stl | Output 3D format |
| `prompt` | Any text (max 1024 chars) | Text description for generation |
| `image_url` | Public URL (JPEG/PNG) | Photo for image-to-3D conversion |

## Animation Presets (via Tripo Platform)

Tripo supports **automatic rigging + animation** for character models:

| Animation | Description |
|-----------|-------------|
| `idle` | Standing idle loop |
| `walk` | Walking cycle |
| `run` | Running cycle |
| `jump` | Jump animation |
| `climb` | Climbing motion |
| `slash` | Melee attack swing |
| `shoot` | Ranged attack |
| `hurt` | Hit reaction |
| `fall` | Falling animation |
| `turn` | Turning in place |

## Stylization Options (via Tripo Platform)

Transform any generated model into artistic styles:

| Style | Description |
|-------|-------------|
| Cartoon | Bright colors, exaggerated proportions |
| Clay | Handmade clay/dough appearance |
| Alien | Organic, otherworldly aesthetic |
| Christmas | Holiday-themed with festive materials |
| Retro Steampunk | Victorian-era mechanical style |
| LEGO | Brick-built appearance |
| Voxel | Minecraft-style blocky aesthetic |
| Voronoi | Organic cellular pattern |

## Prompt Tips for Best Results

### Be Specific About Shape & Material
- **Good**: "a weathered wooden rocking chair with curved armrests and woven seat"
- **Bad**: "a chair"

### Specify Style & Use Case
- **Realistic**: "a photorealistic leather briefcase with brass buckles"
- **Stylized**: "a low-poly cartoon fox with flat shading"
- **Game-ready**: "a sci-fi crate prop, game-ready, optimized topology"

### Include Material Details
- "matte black finish", "brushed aluminum", "rough stone texture"
- "translucent glass", "polished marble", "worn leather"

### For Characters
- Mention pose: "T-pose" or "A-pose" for animation-ready models
- Specify style: "stylized", "realistic", "chibi"

## Credit System

| Tier | Credits | Setup |
|------|---------|-------|
| **Free Trial** | 10 generations | Nothing — works instantly |
| **Own API Key** | Unlimited (2,000 free credits on new Tripo accounts) | Sign up at [platform.tripo3d.ai](https://platform.tripo3d.ai/) |

When free credits run out, the skill provides step-by-step guidance to create a free Tripo account and get your own API key.

### Getting Your Own Key

1. Visit [platform.tripo3d.ai](https://platform.tripo3d.ai/) → Sign Up (free)
2. Go to [API Keys page](https://platform.tripo3d.ai/api-keys)
3. Generate a new key (starts with `tsk_`) — **copy immediately, shown only once!**
4. Configure: `openclaw config set skill.tripo-3d-generation.TRIPO_API_KEY <your-key>`
5. Done — unlimited generations with your own account

## Why Tripo?

| Feature | Tripo | Others |
|---------|-------|--------|
| Geometry Quality | Sculpture-level, sharp edges | Often blobby or low-detail |
| Auto-Rigging | Built-in skeleton + 10 animations | Usually requires manual work |
| Speed | 5s (Turbo) to 90s (v3.0) | Often 3-10+ minutes |
| Formats | 6 formats (GLB/FBX/OBJ/STL/USDZ/3MF) | Usually 1-2 formats |
| PBR Materials | Albedo + Normal + Roughness + Metallic | Often diffuse-only |
| Free Credits | 10 free, no signup needed | Most require API key upfront |

## Error Handling

| Error | Cause | Solution |
|-------|-------|---------|
| `quota_exceeded` | 10 free credits used up | Follow the setup guide to get your own free API key |
| `task_not_ready` | Model still generating | Wait and poll status again |
| Task `FAILED` | Generation failed | Try a different or more specific prompt |
| `missing_user_id` | Client error | Automatic — no user action needed |

## About Tripo

[Tripo](https://www.tripo3d.ai/) is the most advanced AI 3D generation platform by VAST AI Research. Used by professionals in gaming, architecture, e-commerce, 3D printing, film/VFX, and education. The platform supports the full 3D creation pipeline: generation → rigging → animation → stylization → export.

- Website: [tripo3d.ai](https://www.tripo3d.ai/)
- API Platform: [platform.tripo3d.ai](https://platform.tripo3d.ai/)
- API Documentation: [platform.tripo3d.ai/docs](https://platform.tripo3d.ai/docs/generation)
