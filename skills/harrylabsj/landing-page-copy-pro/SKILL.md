# Landing Page Conversion Copy Pro

## Purpose

This skill generates complete, conversion-optimized landing page copy using established copywriting frameworks. It structures copy from hero headline to final CTA — value proposition, feature-to-benefit bridge, social proof, risk reversal, pricing clarity, FAQ, and CTA cascade. "Pro" means built-in conversion frameworks (AIDA, PAS, StoryBrand) and variant generation for A/B testing. Best used when you need a landing page that turns traffic into signups, leads, or sales, with every section engineered for persuasion and clarity.

## Triggers

- "write landing page copy"
- "landing page copywriter"
- "落地页文案"
- "conversion copy"
- "hero section"
- "landing page CTA"
- "sales page copy"
- "landing page writer"
- "转化文案"
- "高转化落地页"

## Workflow

1. Receive product/offer details from user: product name, core value proposition, target audience, page goal (lead gen, purchase, app download, webinar signup, waitlist), and any existing copy or brand voice preferences.
2. Select the optimal landing page structure based on page goal:
   - Lead Gen: Hero → Value Prop → Benefits → Social Proof → Form CTA
   - Purchase: Hero → Problem → Solution → Features → Benefits → Pricing → Guarantee → CTA
   - App Download: Hero → Hook → Feature Highlights → Social Proof → Store Buttons
   - Webinar: Hero → Topic → Speaker Credibility → Agenda → Registration CTA
3. Generate hero headline + subheadline variants (3–5 options) using proven formulas: outcome-focused, curiosity-driven, pain-agitate-solution, or social proof-led.
4. Translate feature lists into benefit-focused copy with emotional hooks — not what the product does, but what the user gains.
5. Format social proof section: testimonial selection, credibility stats, trust badges, and logo bars — with guidance on what makes proof believable.
6. Build FAQ section addressing the 3–5 most common objections for this offer type.
7. Create CTA hierarchy: primary CTA (immediate action), secondary CTA (lower commitment), fallback CTA (retention move like newsletter signup).
8. Review against conversion best practices and safety rules — no dark patterns, no false urgency.

## Prompt Templates

### 1. Full Landing Page (`full_landing_page`)

**Purpose:** Generate a complete landing page section-by-section from product/offer details.

**Input:**
- `${product_name}` — Product or offer name
- `${core_value_prop}` — One-sentence value proposition
- `${target_audience}` — Who this is for (demographics + psychographics)
- `${page_goal}` — Conversion goal (lead gen, purchase, app download, webinar, waitlist)
- `${key_features}` — 3–5 core features
- `${price_point}` — (Optional) Price or pricing model
- `${existing_copy}` — (Optional) Any current copy to improve

**Output:** Complete landing page copy organized by section:
- Hero (headline + subheadline + hero CTA)
- Value Proposition (2–3 sentence expansion)
- Feature-Benefit Bridge (feature → benefit → emotional hook per item)
- Social Proof (testimonial format + stats + trust signals)
- Pricing/Offer (if applicable)
- FAQ (3–5 objections + responses)
- CTA Cascade (primary, secondary, fallback)

### 2. Hero Section Optimizer (`hero_section_optimizer`)

**Purpose:** Generate 5 headline + subheadline variants for the hero section.

**Input:**
- `${product_name}` — Product/offer name
- `${core_value_prop}` — Core value proposition
- `${target_audience}` — Audience descriptor
- `${hero_formula}` — (Optional) Preferred formula (outcome, curiosity, PAS, social proof)

**Output:** 5 hero variants, each with:
- Headline (10 words or fewer)
- Subheadline (1–2 sentences expanding the promise)
- CTA button text
- Why it works (formula rationale)
- Best fit scenario

### 3. Feature-to-Benefit Translator (`feature_to_benefit_translator`)

**Purpose:** Convert technical features into emotionally resonant benefits.

**Input:**
- `${feature_list}` — List of product features
- `${target_audience}` — Audience pain points and desires
- `${emotional_tone}` — Desired emotional angle (relief, aspiration, confidence, belonging)

**Output:** Translated list where each item follows:
- Feature (what it is)
- Benefit (what it does for the user)
- Emotional Hook (how it makes the user feel)
- Suggested copy line for landing page

### 4. Social Proof Formatter (`social_proof_formatter`)

**Purpose:** Turn raw testimonials and stats into polished, credible social proof sections.

**Input:**
- `${testimonials}` — Raw customer quotes (2–5)
- `${stats}` — Key numbers (users, results, satisfaction rate)
- `${credibility_markers}` — Logos, awards, media mentions
- `${audience_skepticism}` — What prospects typically doubt

**Output:** Formatted social proof section with:
- Testimonial selection and ordering (most relatable first)
- Stats formatted for scannability
- Trust badge placement guidance
- Notes on avoiding over-polished or fake-sounding testimonials

### 5. CTA Hierarchy (`cta_hierarchy`)

**Purpose:** Build a strategic CTA cascade for a landing page based on conversion goal.

**Input:**
- `${page_goal}` — Conversion goal
- `${offer_urgency}` — (Optional) Time-bound or quantity-bound urgency
- `${audience_commitment_level}` — Cold, warm, or hot traffic

**Output:** CTA hierarchy:
- Primary CTA (direct action, above the fold)
- Secondary CTA (lower commitment, mid-page)
- Fallback CTA (minimum commitment, bottom of page)
- Button copy variants for each
- Placement recommendations
- Notes on avoiding dark patterns and deceptive urgency

## Output Format

All landing page outputs follow a structured pro format:

```markdown
# Landing Page: [Product/Offer Name]
**Goal:** [Goal] | **Audience:** [Audience]

## Hero Section
- **Headline:** [Headline]
- **Subheadline:** [Subheadline]
- **CTA:** [Button text]

## Value Proposition
[2–3 sentences]

## Feature → Benefit Bridge
1. **[Feature]** → [Benefit] → [Emotional hook]
   *Copy line:* [Suggested copy]

## Social Proof
[Testimonial block]
[Stats block]
[Trust signals]

## FAQ
Q: [Objection]
A: [Response]

## CTA Cascade
- **Primary:** [CTA]
- **Secondary:** [CTA]
- **Fallback:** [CTA]
```

Additional outputs:
- **Hero variants:** Numbered list with formula labels
- **Feature-benefit table:** Feature | Benefit | Emotion | Copy Line
- **Social proof notes:** Credibility best practices and red flags
- **CTA notes:** Commitment ladder logic and dark pattern warnings

## Safety Rules

- **NEVER** make false or misleading claims about product capabilities, results, or performance
- **NEVER** fabricate testimonials, statistics, or customer data
- **NEVER** use dark patterns in CTA language (e.g., fake countdowns, hidden opt-outs, manipulative guilt framing)
- **NEVER** create unsubstantiated urgency ("only 2 left" unless true)
- **ALWAYS** present pricing and terms clearly — no hidden conditions buried in copy
- **ALWAYS** recommend A/B testing before full launch; no single version is guaranteed to win
- **ALWAYS** include appropriate risk reversal (guarantee, trial, refund policy) when applicable
- **ALWAYS** remind the user to review and fact-check all claims before publishing

## Examples

### Example 1: Full Landing Page (SaaS Product, Lead Gen)

**Input:** Product="TeamFlow 项目管理工具", Value Prop="让远程团队协作像面对面一样顺畅", Audience="50-200人远程团队的负责人", Goal="lead gen", Features=[实时同步看板, 自动化周报, 集成Slack/Zoom, 权限管理]

**Output:**
- Hero: "远程团队不同步？TeamFlow让你像在同一间办公室" + "实时看板、自动周报、无缝集成 — 专为远程团队设计" + CTA "免费试用14天"
- Value Prop: 3 sentences on async transparency and time saved
- Feature-Benefit: 实时同步看板 → 每个人随时知道进度 → 不再被"进度怎么样了"打断 → "打开看板，状态一目了然"
- Social Proof: "300+远程团队已迁移到TeamFlow" + testimonial format
- FAQ: Address security, onboarding time, and free trial limits
- CTA Cascade: Primary="开始免费试用" / Secondary="预约演示" / Fallback="下载产品手册"

### Example 2: Hero Section Optimizer (Same Product)

**Input:** Product="TeamFlow", Value Prop="远程协作零摩擦", Audience="远程团队负责人"

**Output:** 5 hero variants using different formulas:
1. Outcome: "你的远程团队，终于可以同步了"
2. Curiosity: "为什么顶尖远程团队不再开早会了？"
3. PAS: "远程团队每天浪费2小时对齐进度。TeamFlow把它变成2分钟。"
4. Social Proof: "300+远程团队选择的协作方式"
5. Direct: "TeamFlow — 远程团队项目管理，像面对面一样顺畅"

### Example 3: Feature-to-Benefit Translator (E-Commerce)

**Input:** Features=["真丝面料", "可机洗", "7天无理由退换"], Audience="25-40岁职场女性", Emotional Tone="confidence"

**Output:**
- 真丝面料 → 透气亲肤，整天舒适 → 从容应对重要场合 → "真丝触感，让重要的一天从舒适开始"
- 可机洗 → 省去干洗麻烦 → 省下的时间属于自己 → "可机洗的真丝，省心不省质感"
- 7天无理由退换 → 零风险尝试 → 买得放心 → "不喜欢？7天内无理由退换，零风险体验"

## Related Skills

- [ad-copy-ab-tester](../ad-copy-ab-tester/) — For generating A/B ad variants that drive traffic to this landing page
- [promo-email-writer](../promo-email-writer/) — For email sequences that nurture leads captured from this landing page
- [douyin-script-studio](../douyin-script-studio/) — For short video scripts when Douyin traffic lands on this page
