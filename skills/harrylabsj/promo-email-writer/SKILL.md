# Promotional Email Writer

## Purpose

This skill generates complete promotional email copy for marketing campaigns — subject lines, preview text, body copy, and CTAs — across multiple campaign types: product launches, flash sales, abandoned cart recovery, newsletters, seasonal campaigns, and email drip sequences. Every output is structured for conversion and includes CAN-SPAM/GDPR compliance checks. Unlike social media skills, this is purpose-built for the email channel with its unique constraints: preview pane optimization, deliverability concerns, and legal compliance requirements.

## Triggers

- "写营销邮件"
- "promotional email"
- "email subject line"
- "abandoned cart email"
- "newsletter copy"
- "邮件营销"
- "email drip sequence"
- "邮件A/B测试"
- "促销邮件"
- "email campaign"

## Workflow

1. Receive campaign context from user: campaign type (launch/sale/abandoned cart/newsletter/seasonal), product details, target audience, and email goal.
2. Generate subject line(s) optimized for open rate: under 50 characters, preview-pane friendly, no deceptive language.
3. Write preview text that complements (not repeats) the subject line.
4. Structure body copy for scannability: headline → greeting → hook paragraph → product value → offer details → urgency (ethical) → CTA button → footer.
5. Craft primary CTA button copy with clear action language.
6. Include unsubscribe mechanism language and sender identity in footer.
7. Run compliance review: deceptive subject line check, missing unsubscribe check, misleading claim check.
8. Deliver complete email ready for ESP (Email Service Provider) upload.

## Prompt Templates

### 1. Full Email (`full_email`)
**Purpose:** Generate a complete promotional email from campaign context.
**Input:**
- `${campaign_type}` — launch / flash_sale / seasonal / newsletter / re-engagement
- `${product_name}` — Product or offer
- `${promotion_details}` — Discount, bundle, or offer specifics
- `${target_audience}` — Subscriber segment
- `${brand_voice}` — Tone: formal / casual / playful / luxury

**Output:** Complete email: Subject Line | Preview Text | Body Copy (with sections) | CTA Button | Footer (with unsubscribe).

### 2. Subject Line A/B (`subject_line_ab`)
**Purpose:** Generate subject line variants for open rate testing.
**Input:**
- `${campaign_context}` — Brief campaign description
- `${audience_segment}` — Who is receiving
- `${count}` — How many variants (default 5)

**Output:** 5 subject lines labeled by approach (curiosity, benefit, urgency, personalization, question) with character counts and predicted open-rate rationale.

### 3. Email Sequence (`email_sequence`)
**Purpose:** Design a multi-email drip sequence for a customer journey stage.
**Input:**
- `${journey_stage}` — Welcome / Nurture / Abandoned cart / Post-purchase / Win-back
- `${product_name}` — Product or brand
- `${sequence_length}` — Number of emails (typically 3–5)

**Output:** Email sequence table: Email # | Timing | Subject | Body Summary | CTA | Goal.

### 4. Abandoned Cart Email (`abandoned_cart_email`)
**Purpose:** Generate a recovery email for cart abandoners.
**Input:**
- `${product_name}` — Item(s) left in cart
- `${cart_value}` — Total cart value
- `${abandonment_window}` — Hours since abandonment
- `${incentive}` — Optional discount or free shipping offer

**Output:** Recovery email with: gentle reminder subject, product image description placeholders, benefit recap, urgency (if incentive), CTA back to cart.

### 5. Email Compliance Review (`email_compliance_review`)
**Purpose:** Review draft email for deliverability and legal risks.
**Input:**
- `${email_draft}` — Complete email: subject + body + footer
- `${target_region}` — GDPR (EU), CAN-SPAM (US), CASL (Canada), or PIPL (China)

**Output:** Compliance report: Check | Status (Pass/Flag) | Issue | Suggested Fix.

## Output Format

Every full email follows this deliverable structure:

```
SUBJECT LINE: [under 50 chars]
PREVIEW TEXT: [complements subject, under 100 chars]

[BODY]
Header/Logo space
Headline
Greeting
Hook paragraph
Product/Offer section
Social proof (if applicable)
CTA Button → [Button text]
Urgency/Scarcity note (ethical)
Closing

[FOOTER]
Unsubscribe link language
Company info
Privacy policy link
```

## Safety Rules

- **NEVER** write deceptive subject lines (e.g., "Re: Your order" when it's not a reply, fake "Urgent" flags)
- **NEVER** make misleading discount claims or hidden conditions
- **NEVER** omit unsubscribe mechanism language — it must be clearly present
- **ALWAYS** include proper sender identity (company name, physical address for CAN-SPAM)
- **ALWAYS** remind user about GDPR consent requirements for EU subscribers
- **ALWAYS** flag potential spam-trigger words in subject lines (e.g., "FREE!!!", "ACT NOW!!!")

## Examples

### Example 1: Full Email for Flash Sale
**Input:** Campaign="618大促", Product="XX护肤品套装", Discount="满300减50", Audience="女性25-40岁", Voice="亲切温暖"
**Output:** Subject "你的618专属护肤清单来了 ✨", preview "满300减50，这套搭配我们准备了很久", body with hero image placeholder, product trio showcase, discount breakdown, countdown urgency, CTA "立即抢购", full footer.

### Example 2: Abandoned Cart
**Input:** Product="一双运动鞋 ¥499", Cart value="¥499", Abandonment="24小时", Incentive="包邮"
**Output:** Subject "它还在等你 👟 — 免邮提醒", gentle reminder tone, product benefit recap, free shipping highlight, CTA "回到购物车".

## Related Skills

- [ad-copy-ab-tester](../ad-copy-ab-tester/) — For ad copy variants (paid channel vs. owned email)
- [social-caption-kit](../social-caption-kit/) — For social media promotion of the same campaign
- [landing-page-copy-pro](../landing-page-copy-pro/) — For the landing page that email CTAs link to
