# Douyin Short Video Script Studio

## Purpose

This skill generates structured oral presentation scripts for Douyin (抖音 / TikTok CN) short videos. It specializes in hook-driven openings (0–3 second grab), timed content beats, visual cue suggestions, BGM mood guidance, and transition scripting. "Studio" means a complete toolkit — from brief to shoot-ready script with timing, not just flat text. Best used when you need a Douyin video that converts attention into retention, with every second engineered for the platform's algorithm and viewer behavior.

## Triggers

- "写抖音脚本"
- "抖音口播"
- "短视频脚本"
- "抖音 hook"
- "抖音 storyboard"
- "douyin script"
- "抖音文案"
- "Douyin video script"
- "口播稿"
- "抖音分镜脚本"

## Workflow

1. Receive product/topic brief from user: product name, category, key message, target audience, desired video style/tone, and video length (15s, 30s, or 60s).
2. Determine the optimal script structure based on length:
   - 15s: Single-hook, single-point, hard CTA
   - 30s: Hook → Problem/Context → Solution/Reveal → CTA
   - 60s: Hook → Story/Proof → Deep Dive → Social Proof → CTA
3. Generate 3–5 opening hook variants optimized for 0–3 second retention (visual + verbal).
4. Structure body beats with estimated timing per segment (e.g., 0–3s hook, 3–8s setup, 8–20s core message).
5. Add visual cues for each beat: shot type (close-up, product detail, face-to-camera), motion direction, text overlay suggestions, and transition type (cut, zoom, swipe).
6. Suggest BGM mood and tempo (upbeat, emotional, trending, lo-fi) matched to content energy.
7. Write the closing CTA optimized for Douyin algorithm engagement: like, follow, comment prompt, or purchase link.
8. Include safety disclaimer and compliance review for commercial content.

## Prompt Templates

### 1. Script from Brief (`script_from_brief`)

**Purpose:** Generate a complete timed Douyin oral script from a product/topic brief.

**Input:**
- `${product_name}` — Product or topic name
- `${category}` — Niche (beauty, tech, food, lifestyle, education, fitness)
- `${key_message}` — The single most important point to communicate
- `${target_audience}` — Who the video is for (age, interest, pain point)
- `${video_length}` — 15s, 30s, or 60s
- `${tone}` — Style (energetic, calm, humorous, authoritative, relatable)
- `${cta_goal}` — Desired action (follow, like, comment, buy, download)

**Output:** Full timed script with:
- Timestamped beats (0–3s, 3–8s, etc.)
- Spoken lines (口播文案)
- Visual cues per beat (shot, motion, text overlay)
- BGM mood suggestion
- Final CTA line

### 2. Hook Library (`hook_library`)

**Purpose:** Generate 5 opening hook variants for a product or topic.

**Input:**
- `${product_name}` — Product or topic
- `${hook_type}` — Optional preference (curiosity, pain point, surprise, story, number/list)
- `${target_audience}` — Audience descriptor

**Output:** 5 hook options, each with:
- Verbal hook (first 1–2 sentences)
- Visual direction (what to show in 0–3s)
- Why it works (psychology rationale)
- Best fit scenario

### 3. Storyboard Outline (`storyboard_outline`)

**Purpose:** Convert a script brief into a 3-scene visual storyboard outline.

**Input:**
- `${product_name}` — Product/topic
- `${scene_count}` — 3 or 5 scenes
- `${style}` — Visual style (clean, lifestyle, demo, testimonial, Vlog)

**Output:** Scene-by-scene breakdown:
- Scene number + timestamp range
- Shot description (angle, distance, subject)
- On-screen text overlay suggestions
- Audio notes (voiceover vs. music vs. silence)
- Transition to next scene

### 4. Trending Angle Adapter (`trending_angle_adapter`)

**Purpose:** Adapt a product/topic to a current Douyin trending format or challenge style.

**Input:**
- `${product_name}` — Product/topic
- `${trend_format}` — Trending format (e.g., "before vs after", "day in the life", "myth busting", "POV", "trending sound rewrite")
- `${original_script}` — (Optional) Existing script to adapt

**Output:** Adapted script/outline that fits the trending format while preserving the core product message, with notes on how to make it feel native to the trend rather than forced.

### 5. Script Optimizer (`script_optimizer`)

**Purpose:** Improve an existing Douyin script for retention, clarity, and conversion.

**Input:**
- `${draft_script}` — User's existing script or outline
- `${optimization_goal}` — Primary goal (retention, clarity, conversion, humor, pacing)
- `${video_length}` — Target length

**Output:** Optimized script with:
- Redlined changes (what changed and why)
- Timing adjustments
- Stronger hook alternatives
- Visual enhancement suggestions
- Pacing notes (where to speed up, where to pause)

## Output Format

All script outputs follow a structured studio format:

```
## Douyin Script: [Product/Topic]
**Length:** [15s / 30s / 60s] | **Tone:** [Tone] | **CTA Goal:** [Goal]

### Beat 1 — Hook (0–3s)
- **Script:** [Spoken line]
- **Visual:** [Shot type + motion + text overlay]
- **Audio:** [BGM mood / sound effect]

### Beat 2 — [Segment Name] (3–8s)
...

### Closing — CTA (final 3s)
- **Script:** [CTA line]
- **Visual:** [End card / product shot / follow prompt]
- **Audio:** [Music swell / silence for impact]
```

Additional outputs provided as needed:
- **Hook variants:** Bulleted list with rationale
- **Storyboard:** Table format (Scene | Time | Shot | Text | Audio | Transition)
- **Optimization notes:** Before/After comparison with reasoning

## Safety Rules

- **NEVER** generate false product efficacy claims or misleading before/after transformations
- **NEVER** suggest dangerous challenges, risky behaviors, or harmful stunts for views
- **NEVER** create scripts that impersonate real individuals without disclosure
- **ALWAYS** include explicit disclosure language for sponsored or commercial content (e.g., "本条内容为合作推广" or "#ad")
- **ALWAYS** respect Douyin content review policies — no prohibited products, medical claims, or deceptive practices
- **ALWAYS** remind the user to review and fact-check AI-generated scripts before filming and publishing
- **ALWAYS** ensure visual cues and suggested actions comply with platform safety guidelines

## Examples

### Example 1: Script from Brief (Skincare, 30s)

**Input:** Product="XX 维C精华", Category="beauty", Key Message="7天提亮肤色", Audience="20-30岁熬夜女性", Length="30s", Tone="energetic", CTA Goal="buy"

**Output:**
- Beat 1 (0–3s): Hook — "熬夜脸有救了！" + close-up of tired face → brightened face transition
- Beat 2 (3–10s): Problem — "凌晨2点睡，早上暗沉到不敢照镜子" + lifestyle shot
- Beat 3 (10–22s): Solution — "这瓶维C精华，7天提亮不是玄学" + product demo + ingredient text overlay
- Beat 4 (22–30s): CTA — "链接在左下角，现在下单立减30" + end card with price

### Example 2: Hook Library (Same Product)

**Input:** Product="XX 维C精华", Hook Type="curiosity", Audience="20-30岁女性"

**Output:** 5 hooks:
1. "我用了7天，同事问我是不是去做医美了" (surprise + social proof)
2. "这瓶精华的维C浓度，我算了3遍才敢相信" (curiosity + number)
3. "熬夜到凌晨2点，我的脸居然比以前还亮" (contrast + relatability)
4. "皮肤科朋友偷偷告诉我，提亮根本不需要贵" (insider + value)
5. "别再花冤枉钱！提亮肤色，这一瓶够了" (direct + authority)

### Example 3: Storyboard Outline (Tech Gadget, 5 scenes)

**Input:** Product="便携投影仪", Style="lifestyle"

**Output:** 5-scene storyboard from unboxing → bedroom setup → movie night → portability demo → CTA end card.

## Related Skills

- [live-selling-script-kit](../live-selling-script-kit/) — For live-streaming sales scripts when your Douyin video drives to a live room
- [ad-copy-ab-tester](../ad-copy-ab-tester/) — For testing Douyin ad creative copy derived from these scripts
- [landing-page-copy-pro](../landing-page-copy-pro/) — For landing page copy when your Douyin CTA drives traffic to a conversion page
