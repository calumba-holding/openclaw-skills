# Multi-Platform Social Caption Kit

## Purpose

This skill takes one core brand message or product brief and generates platform-optimized captions for six major social platforms simultaneously: WeChat Moments (朋友圈), Weibo, Instagram, Facebook, Twitter/X, and LinkedIn. Each caption is adapted to the platform's unique tone norms, length constraints, hashtag conventions, emoji culture, and audience expectations — while preserving a consistent brand voice. "Kit" signals a bundled, all-in-one caption package rather than single-platform generation.

## Triggers

- "生成朋友圈文案"
- "social caption pack"
- "多平台配文"
- "caption for all platforms"
- "brand caption"
- "社交媒体配文"
- "cross-platform post"
- "品牌配文"
- "hashtag strategy"
- "平台适配文案"

## Workflow

1. Receive the core message/product brief from user: what to communicate, brand voice description, campaign type, and which platforms to cover.
2. If brand voice is not specified, ask clarifying questions about tone, formality, and personality before generation.
3. Generate platform-adapted captions:
   - **WeChat Moments (朋友圈)**: Conversational, personal tone, 1–2 emoji, no hashtags, optional @mentions
   - **Weibo**: More public-facing, hashtag-heavy (#话题#), can be longer, trending topic integration
   - **Instagram**: Visual-first context, heavy emoji usage, hashtag block (up to 30), Story-friendly format
   - **Facebook**: Community-oriented, engagement-driving questions, link-friendly, longer form OK
   - **Twitter/X**: Concise within 280 chars, trending hashtag, thread-compatible
   - **LinkedIn**: Professional tone, thought-leadership framing, minimal hashtags (3–5)
4. Apply platform-specific best practices: link handling (URL placement differs), emoji density, @mention conventions, and hashtag norms.
5. Include a hashtag strategy section per platform: which hashtags, how many, and why.
6. Add engagement hooks appropriate to each platform's interaction patterns (questions, polls, CTAs).
7. Output as a unified caption pack with clear platform labels.

## Prompt Templates

### 1. Caption Pack (`caption_pack`)
**Purpose:** Generate cross-platform captions from one core message.
**Input:**
- `${core_message}` — The key message or announcement
- `${brand_voice}` — Tone descriptors (e.g., "warm humorous professional")
- `${media_type}` — Text-only / image post / video post / carousel
- `${platforms}` — Which platforms to generate for (default: all 6)

**Output:** Platform-labeled caption pack with: Platform | Caption | Character Count | Hashtags | Engagement Hook.

### 2. Brand Voice Presets (`brand_voice_presets`)
**Purpose:** Guide the user through defining a consistent brand voice, then generate sample captions.
**Input:**
- `${brand_description}` — Free-text brand personality (e.g., "a DTC skincare brand that feels like a knowledgeable older sister")
- `${sample_message}` — One test message to generate sample captions for

**Output:** Brand voice definition (3 adjectives + example sentences) + 3 platform-adapted sample captions in the defined voice.

### 3. Campaign Caption Suite (`campaign_caption_suite`)
**Purpose:** Generate a multi-platform caption rollout for a campaign.
**Input:**
- `${campaign_name}` — Campaign name or theme
- `${campaign_duration}` — Timeline (launch day, mid-campaign, closing)
- `${assets_available}` — Types of media available (images, video, UGC)

**Output:** Campaign caption calendar: Date/Phase | Platform | Caption | Media Note.

### 4. Platform Hashtag Strategy (`platform_hashtag_strategy`)
**Purpose:** Generate a hashtag strategy tailored per platform for a given topic.
**Input:**
- `${topic}` — Content topic or product category
- `${target_platforms}` — Which platforms need hashtag strategies

**Output:** Per-platform hashtag sets: Platform | Niche Hashtags (3–5) | Broad Hashtags (2–3) | Trending (1–2) | Count Guidance.

### 5. Engagement Booster (`engagement_booster`)
**Purpose:** Enhance an existing caption for higher engagement.
**Input:**
- `${existing_caption}` — Current caption text
- `${platform}` — Platform it's intended for
- `${engagement_goal}` — Comments/Shares/Saves/Clicks

**Output:** Enhanced caption with: improved hook, engagement question, CTA, optimized hashtags, emoji placement.

## Output Format

**Caption Pack format:**

| Platform | Caption | Chars | Hashtags | Engagement |
|----------|---------|-------|----------|------------|
| WeChat Moments | 文案... | 120 | N/A | 互动问题 |

Each caption is self-contained and ready to copy-paste into the respective platform.

## Safety Rules

- **NEVER** suggest engagement bait tactics that violate platform TOS (e.g., "tag 3 friends to win")
- **NEVER** create content that impersonates individuals or brands
- **NEVER** use a fake persona or fabricated identity in brand voice
- **ALWAYS** maintain authentic, human tone — the caption should sound like a real person wrote it
- **ALWAYS** include disclosure reminders for sponsored/paid content
- **ALWAYS** respect per-platform content policies, age restrictions, and sensitive topic rules

## Examples

### Example 1: Caption Pack for Product Launch
**Input:** Core message="新品咖啡豆上市，单一产地哥伦比亚，中深烘", Brand voice="casual coffee nerd", Platforms="all 6"
**Output:** Six captions: WeChat Moments (day-in-life style), Weibo (hashtag-heavy announcement), Instagram (visual tasting notes), Facebook (community question), Twitter/X (sharp one-liner), LinkedIn (sourcing story with professional angle).

### Example 2: Brand Voice Presets
**Input:** Brand="婴儿护肤品牌，走成分安全、妈妈放心路线", Test message="新品婴儿润肤乳上市"
**Output:** Brand voice defined as "gentle, knowledgeable, reassuring" with sample captions demonstrating each tone.

## Related Skills

- [viral-xiaohongshu-notes](../viral-xiaohongshu-notes/) — For Xiaohongshu-specific content (platform-native format)
- [ad-copy-ab-tester](../ad-copy-ab-tester/) — For paid ad copy (different intent: ads vs. organic)
- [promo-email-writer](../promo-email-writer/) — For email channel (different medium)
