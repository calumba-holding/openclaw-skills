# Live Commerce Sales Script Kit

## Purpose

This skill generates professional live-streaming sales scripts for live commerce hosts on platforms like Douyin Live (抖音直播), Kuaishou Live (快手直播), and Taobao Live. It covers every aspect: product introduction flow, pricing reveal cadence, urgency-building phrases (ethically constrained), audience interaction triggers, Q&A preparation, segment timing, and full-session outlines. Think of it as a director's script for your live commerce show — "Kit" signals a ready-to-use bundle of templates and frameworks, not a single monolithic output.

## Triggers

- "直播带货话术"
- "直播脚本"
- "直播话术"
- "带货脚本"
- "live selling script"
- "flash sale script"
- "直播互动"
- "单品直播"
- "整场直播规划"
- "逼单话术"

## Workflow

1. Receive product information and session type from user: single product demo, multi-product session, or flash sale.
2. For single product: structure the 3–8 minute product introduction flow (hook → demonstration → benefits → pricing → urgency → CTA).
3. For multi-product: build a time-allocated session outline with product sequence, transition monologues, and energy management.
4. Insert audience interaction triggers at regular intervals: polls, Q&A prompts, comment callouts, engagement games.
5. Add urgency-building phrases and transitional language — always with ethical constraints on scarcity and pricing claims.
6. Prepare anticipated audience Q&A pairs for each product.
7. Include pacing notes, segment timing, and host energy level guidance.
8. Deliver script with anchor monologue, interaction triggers, Q&A branches, and timing guide.

## Prompt Templates

### 1. Single Product Live Script (`single_product_live_script`)
**Purpose:** Generate a complete 3–8 minute script for showcasing one product.
**Input:**
- `${product_name}` — Product name
- `${price}` — Selling price (and optional original price)
- `${key_features}` — 3–5 key selling points
- `${target_audience}` — Who's watching
- `${duration_minutes}` — Target segment length (3–8)

**Output:** Timed script with sections: Opening Grab → Product Reveal → Feature Demo → Comparison → Pricing Reveal → Urgency Build → CTA → Transition.

### 2. Full Session Flow (`full_session_flow`)
**Purpose:** Design a complete multi-product 1–4 hour live session.
**Input:**
- `${product_list}` — List of products with selling order priority
- `${session_duration}` — Total session length in hours
- `${flow_style}` — Energy curve: high-low-high / sustained / gradual build

**Output:** Time-allocated outline with: Warm-up, Product 1-n, Intermission moments, Flash sales, Closing. Each with estimated duration, transition monologue, and energy level.

### 3. Urgency Phrase Bank (`urgency_phrase_bank`)
**Purpose:** Generate a categorized bank of urgency phrases for live selling.
**Input:**
- `${scenario}` — Situation: limited-time offer / low stock / exclusive deal / first-time buyer bonus
- `${count}` — Number of phrase variants per category

**Output:** Phrases organized by category (timing-based / quantity-based / exclusivity-based), each with an ethical constraint note.

### 4. Audience Q&A Prep (`audience_qa_prep`)
**Purpose:** Anticipate and prepare responses for common audience questions.
**Input:**
- `${product_name}` — Product
- `${product_details}` — Specs, materials, sizes, guarantees
- `${common_concerns}` — Typical buyer hesitations for this product type

**Output:** 15–20 Q&A pairs organized by question type: product/details, pricing/value, logistics/after-sales, objections/skepticism.

### 5. Flash Sale Countdown (`flash_sale_countdown`)
**Purpose:** Generate a high-energy countdown script for a limited-time offer.
**Input:**
- `${product_name}` — Product
- `${flash_price}` — Flash sale price
- `${original_price}` — Regular price
- `${quantity_available}` — Actual available quantity
- `${duration_seconds}` — Countdown window (typically 60–180s)

**Output:** Countdown script with: Price Reveal → Quantity Mention → 30s Reminder → 10s Final Call → Sold Out / Next Product.

## Output Format

All scripts follow a formatted broadcast table:

| Time | Segment | Anchor Monologue | Interaction Trigger | Energy Level |
|------|---------|-----------------|---------------------|--------------|
| 0:00–1:00 | Opening | "Welcome..." | Ask where watching from | 🔥 High |
| ... | ... | ... | ... | ... |

## Safety Rules

- **NEVER** fabricate false scarcity (e.g., "only 3 left" when stock is ample)
- **NEVER** invent fake original prices or price anchors to make discounts look bigger
- **NEVER** use high-pressure tactics targeting vulnerable consumers (elderly, financially distressed)
- **ALWAYS** prompt host to verify and disclose actual stock levels
- **ALWAYS** comply with platform-specific live commerce regulations
- **ALWAYS** maintain honest product descriptions — no exaggerated efficacy claims

## Examples

### Example 1: Single Product Script
**Input:** Product = "XX面霜", Price = "299元 (原价399)", Features = "保湿、修护、敏感肌可用", Duration = "5分钟"
**Output:** 5-minute script with opening hook about winter skin, ingredient demo, texture test, pricing reveal with savings calculation, limited-time urgency, and link click CTA.

### Example 2: Flash Sale Countdown
**Input:** Product = "蓝牙耳机", Flash = "99元 (原价199)", Qty = "50件", Duration = "120s"
**Output:** Countdown script with Qty count decrements at 50, 30, 10 remaining, 30s and 10s reminders, final call, and transition.

## Related Skills

- [douyin-script-studio](../douyin-script-studio/) — For pre-recorded Douyin video scripts (recorded, not live)
- [product-title-booster](../product-title-booster/) — For optimizing product listing titles used during live segments
- [review-reply-coach](../review-reply-coach/) — For handling post-live customer feedback and reviews
