# Viral Xiaohongshu Note Writer

## Purpose

This skill generates Xiaohongshu (小红书 / RED) platform-native notes optimized for virality. It creates "种草" (grass-planting / product recommendation) content with cover text design strategy, niche hashtag stacking, authentic personal-experience tone, product placement angles, and platform-unique aesthetic formatting. Best used when you have a product or service to promote and need a note that feels organic, engaging, and platform-appropriate — but still delivers commercial value.

## Triggers

- "写小红书笔记"
- "生成种草文案"
- "小红书 cover"
- "小红书 hashtag"
- "种草角度"
- "小红书改写"
- "viral xiaohongshu note"
- "xhs note writer"
- "RED note generator"
- "小红书内容创作"

## Workflow

1. Receive product information from user (product name, category, key features, price, target audience, and optional existing draft).
2. Identify niche: beauty, fashion, travel, food, home, parenting, or general lifestyle.
3. Structure the note using the Xiaohongshu native format: hook → personal experience → product reveal → usage tips → purchase guidance.
4. Insert emoji rhythm, line breaks, and section headers following Xiaohongshu aesthetic conventions.
5. Generate 3–5 niche-specific hashtags plus 2–3 trending tags for discoverability.
6. Provide 3–5 cover text options that match the note angle.
7. Include safety disclaimer reminding user to disclose commercial relationships.

## Prompt Templates

### 1. Note from Brief (`note_from_brief`)

**Purpose:** Generate a complete Xiaohongshu note from product information.

**Input:**
- `${product_name}` — Name of the product
- `${category}` — Niche (beauty/fashion/travel/food/home/parenting)
- `${key_features}` — 2–4 main selling points
- `${target_audience}` — Who this product is for
- `${price_range}` — Optional price context
- `${angle}` — Optional content angle (e.g., "成分党", "学生党", "干货分享")

**Output:** Full note with hook paragraph, personal experience narrative, product reveal, usage tips, purchase guidance, hashtags, and 3 cover text options.

### 2. Cover Title Generator (`cover_title_generator`)

**Purpose:** Generate cover image text options that drive clicks.

**Input:**
- `${product_name}` — Product name
- `${angle}` — Content angle
- `${target_audience}` — Audience descriptor

**Output:** 5 cover title options, each with a rationale for why it works for the given product and audience.

### 3. Hashtag Strategy (`hashtag_strategy`)

**Purpose:** Create a balanced hashtag set for maximum discoverability.

**Input:**
- `${product_category}` — Category (e.g., 面膜, 穿搭, 旅行)
- `${niche_keywords}` — 2–3 niche-specific keywords
- `${trending_context}` — Optional current trending topics or seasons

**Output:** 3–5 niche hashtags (targeting specific interest groups) + 2–3 trending hashtags (for broader reach) + hashtag volume tier labeling.

### 4. Angle Switcher (`angle_switcher`)

**Purpose:** Generate 3 different content angles for the same product.

**Input:**
- `${product_name}` — Product name
- `${key_features}` — Key features
- `${audience_segments}` — 2–3 possible audience types

**Output:** 3 distinct note outlines, each from a different angle (e.g., 成分分析, 使用前后对比, 开箱体验), with hook and hashtag recommendations per angle.

### 5. Note Polish/Rewrite (`note_rewrite`)

**Purpose:** Optimize an existing draft for Xiaohongshu engagement.

**Input:**
- `${draft_content}` — User's existing note draft
- `${optimization_goal}` — What to improve (engagement/readability/SEO)

**Output:** Polished version with improved hook, emoji rhythm, formatting, hashtags, and cover text suggestions.

## Output Format

All outputs follow Xiaohongshu's native platform styling:
- Short paragraphs (1–3 sentences each)
- Emoji used deliberately for emphasis and section breaks
- Hashtags appended at the bottom
- Cover text options provided separately as a numbered list
- Character count within platform limits (~1000 characters)

## Safety Rules

- **NEVER** generate fake reviews, fabricated user experiences, or misleading testimonials
- **NEVER** make unverified product efficacy claims (especially skincare, health, or wellness)
- **NEVER** include medical/health claims without qualification (e.g., "FDA-registered" or "dermatologist-tested" only if verifiable)
- **ALWAYS** prompt the user to disclose sponsored or commercial relationships per Xiaohongshu guidelines
- **ALWAYS** respect Xiaohongshu community guidelines — no prohibited products or content
- **ALWAYS** remind the user to review and fact-check AI-generated content before publishing

## Examples

### Example 1: Note from Brief (Skincare)

**Input:** Product = "XX 玻尿酸保湿面霜", Price = "299元", Features = "三重玻尿酸、敏感肌可用、24小时保湿", Audience = "25-35岁女性", Angle = "成分党"

**Output:** A full note with hook about winter skincare struggles, personal experience with dry skin, product reveal with ingredient breakdown (triple hyaluronic acid), usage tips (apply on damp skin), and hashtags like #玻尿酸面霜 #保湿面霜推荐 #干皮救星 #成分党 skincare.

### Example 2: Angle Switcher (Same Product)

**Input:** Same product as above, audience segments = {成分党, 学生党, 宝妈}

**Output:** Three outlines: (1) 成分分析 deep-dive, (2) 平价好物 budget-friendly angle, (3) 新手护肤 routine integration angle.

## Related Skills

- [social-caption-kit](../social-caption-kit/) — For multi-platform repurposing of the same content
- [product-title-booster](../product-title-booster/) — For optimizing the product's listing title to match the note
- [review-reply-coach](../review-reply-coach/) — For responding to comments and reviews on the note
