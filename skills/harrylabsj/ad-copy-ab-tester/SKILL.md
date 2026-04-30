# Ad Copy Variants for A/B Testing

## Purpose

This skill generates systematic, labeled ad copy variants designed for structured A/B testing across paid advertising platforms. It produces five distinct appeal-angle variants per product — Emotional, Rational, Scarcity, Social Proof, and Problem-Solution — each formatted for the target platform's constraints and policies. A built-in compliance checker flags potential ad policy violations before launch. Designed for performance marketers and media buyers who need testable, measurable creative variations, not random copy suggestions.

## Triggers

- "generate ad variants"
- "A/B test ad copy"
- "广告文案变体"
- "ad copy ab test"
- "create ad copy"
- "广告A/B测试"
- "multiple ad versions"
- "ad variant matrix"
- "headline bank"
- "CTA optimizer"

## Workflow

1. Receive product info + target ad platform(s) from user: product name, key benefits, target audience, budget tier, and campaign goal.
2. Generate the 5-angle variant matrix:
   - **Emotional**: Tap into desire, aspiration, or joy
   - **Rational**: Feature-driven, logical, value-focused
   - **Scarcity**: Limited-time, limited-quantity (ethically constrained)
   - **Social Proof**: User numbers, ratings, endorsements (only if verifiable)
   - **Problem-Solution**: Pain point → product as solution
3. Apply platform-specific constraints: character limits (e.g., WeChat Moments: 40 chars headline; Google: 30/90/90), image-text ratio rules, and forbidden content categories.
4. Run a compliance check against the target platform's ad policies, flagging: prohibited claims, missing disclosures, superlatives without substantiation, sensitive categories.
5. Generate CTA alternatives for each variant — platform-appropriate and conversion-optimized.
6. Output the full variant matrix, labeled and ready for ad platform upload.

## Prompt Templates

### 1. Variant Matrix (`variant_matrix`)
**Purpose:** Generate the full 5-angle A/B variant matrix.
**Input:**
- `${product_name}` — Product
- `${key_benefits}` — 2–3 main benefits
- `${target_audience}` — Demographic and psychographic
- `${platform}` — Ad platform name
- `${campaign_goal}` — Awareness/Consideration/Conversion

**Output:** A labeled 5-variant table: Variant Label | Headline | Body/Description | CTA | Character Counts.

### 2. Ad Compliance Check (`ad_compliance_check`)
**Purpose:** Review ad copy for platform-specific policy violations.
**Input:**
- `${ad_copy_full}` — Complete ad text (headline + body + CTA)
- `${platform}` — Target ad platform
- `${product_category}` — Product category (for restricted category checks)

**Output:** Compliance report: Flag | Severity | Issue Description | Suggested Fix.

### 3. CTA Optimizer (`cta_optimizer`)
**Purpose:** Generate alternative CTAs for existing ad copy.
**Input:**
- `${ad_copy}` — Existing ad body text
- `${platform}` — Platform context
- `${goal}` — Click/Conversion/Engagement

**Output:** 3 CTA alternatives with rationale for each and platform-fit score.

### 4. Headline Bank (`headline_bank`)
**Purpose:** Generate 10 headline angles for a product.
**Input:**
- `${product_name}` — Product
- `${target_audience}` — Audience
- `${platform}` — Platform (determines character limits)

**Output:** 10 headlines labeled by angle type (curiosity, benefit, question, statistic, comparison, emotional, how-to, direct, testimonial, news) with character count.

### 5. Ad Fatigue Refresher (`ad_fatigue_refresher`)
**Purpose:** Refresh an existing top-performing ad with new variants.
**Input:**
- `${current_top_ad}` — Currently best-performing ad copy
- `${performance_metric}` — What metric (CTR/conversion) it leads on
- `${fatigue_signal}` — Why refresh (frequency up, CTR dropping)

**Output:** 3 refreshed variants that preserve winning elements but change angle, format, or CTA.

## Output Format

All variants are delivered in a structured A/B test matrix:

| Variant # | Angle Type | Headline | Body (truncated) | CTA | Expected Audience Response |
|-----------|-----------|----------|------------------|-----|---------------------------|
| A | Emotional | ... | ... | ... | ... |
| B | Rational | ... | ... | ... | ... |

Plus compliance flags table when requested.

## Safety Rules

- **NEVER** include forbidden claims per platform ad policy (health guarantees, financial returns, weight loss promises)
- **NEVER** use discriminatory, exclusionary, or exploitative language
- **NEVER** include misleading before/after representations without verifiable data
- **NEVER** use unsubstantiated superlatives ("best", "#1", "top-rated") unless independently verifiable
- **ALWAYS** include required disclosures: "Ad", "Sponsored", "Promotion" per platform
- **ALWAYS** flag sensitive product categories (health, finance, supplements) for extra review

## Examples

### Example 1: Variant Matrix for WeChat Moments
**Input:** Product="在线英语课程", Audience="25-35岁职场人", Platform="WeChat Moments", Goal="Conversion"
**Output:** 5 variants: Emotional ("遇见更好的自己"), Rational ("每天15分钟，3个月流利对话"), Scarcity ("限时优惠，仅剩200名额"), Social Proof ("10万+学员的选择"), Problem-Solution ("开会不敢开口？试试这个方法").

### Example 2: Compliance Check
**Input:** Ad copy with "100% guaranteed results in 7 days", Platform="Google Ads", Category="Education"
**Output:** HIGH severity flag: absolute guarantee claim without substantiation. Suggested: "Join 10,000+ learners" instead.

## Related Skills

- [social-caption-kit](../social-caption-kit/) — For organic social captions (not paid ads)
- [promo-email-writer](../promo-email-writer/) — For email marketing variants (different channel)
- [landing-page-copy-pro](../landing-page-copy-pro/) — For landing page copy that the ad links to
