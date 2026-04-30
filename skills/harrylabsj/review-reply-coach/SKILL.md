# Compliant Review Reply Coach

## Purpose

This skill generates professional, tone-calibrated responses to customer reviews across e-commerce and app store platforms. Unlike other content-generator skills that create new content, this is a *service* skill — it coaches the user on how to reply appropriately to existing reviews. It covers three response modes: positive (thank + reinforce brand value), neutral (acknowledge + commit to improvement), and negative (apologize + resolve + take conversation offline). "Coach" emphasizes guidance, templates, and best-practice education — not automated mass-replying. This is the only skill in the pack that does NOT generate new marketing content.

## Triggers

- "回复评论"
- "review response"
- "reply to customer review"
- "差评回复"
- "app review reply"
- "商家回复"
- "review reply coach"
- "客户评论回复"
- "好评怎么回"
- "中评怎么回"

## Workflow

1. Receive the review text, star rating (1–5), and platform context from the user.
2. Classify the review tone into one of four categories: Positive (4–5★, praising), Neutral (3★, mixed feelings), Negative (1–2★, disappointed), Angry (1★, emotional/aggressive).
3. Select the appropriate response framework:
   - **Positive**: Thank specifically → Reinforce what they liked → Invite future engagement → Subtle upsell (optional, disclosed)
   - **Neutral**: Thank for feedback → Acknowledge the mixed experience → Commit to specific improvement → Offer follow-up
   - **Negative**: Apologize sincerely (without admitting fault if unverified) → Address specific complaint → Offer concrete resolution → Take conversation offline (email/phone)
   - **Angry**: De-escalate first → Acknowledge emotion → Offer resolution path → Escalate if safety/legal issue
4. Apply the CRITICAL safety gate: verify the output is a REPLY to an existing review, never a fabricated review.
5. For serious complaints (safety, legal, harassment, discrimination), include an escalation path.
6. Suggest follow-up action if applicable.
7. Deliver the tone-calibrated response ready for the user to post.

## Prompt Templates

### 1. Response from Review (`response_from_review`)
**Purpose:** Generate a tone-calibrated reply from a single review.
**Input:**
- `${review_text}` — The customer's original review
- `${star_rating}` — 1 through 5
- `${platform}` — Where the review was posted
- `${verified_purchase}` — (Optional) whether this is a verified buyer

**Output:** Complete reply text + tone classification + follow-up suggestion (if applicable).

### 2. Negative Review Diffuser (`negative_review_diffuser`)
**Purpose:** De-escalate an angry or very negative review with empathy and resolution.
**Input:**
- `${review_text}` — The angry/negative review
- `${specific_issues}` — List the specific complaints raised
- `${resolution_options}` — What the business can actually do (refund, replacement, investigation)

**Output:** Empathetic de-escalation reply with: acknowledgment → specific action offered → private contact path → gratitude for feedback.

### 3. Positive Review Amplifier (`positive_review_amplifier`)
**Purpose:** Turn a 4–5★ review into a brand loyalty moment.
**Input:**
- `${review_text}` — The positive review
- `${what_they_loved}` — Specific aspects they praised
- `${upsell_opportunity}` — (Optional) whether to include a gentle next-step invitation

**Output:** Warm thank-you reply that: references their specific praise → reinforces what makes your product great → optionally suggests related products or future engagement.

### 4. Response Policy Builder (`response_policy_builder`)
**Purpose:** Create an internal response policy document for a customer service team.
**Input:**
- `${brand_name}` — Your brand
- `${review_platforms}` — Platforms where you receive reviews
- `${response_sla}` — Response time targets (e.g., "24 hours for negative, 48 for positive")
- `${escalation_triggers}` — What issues require manager attention

**Output:** Policy document with: response templates per star rating, tone guidelines, SLA by rating, escalation triggers, do-not-do list.

### 5. Multi-Language Response (`multilanguage_response`)
**Purpose:** Generate the same review response in multiple languages.
**Input:**
- `${review_text}` — Original review (may be in any language)
- `${response_text}` — Your drafted response in your language
- `${target_languages}` — Languages needed (e.g., "English, Japanese, German")

**Output:** Multi-language response table: Language | Response Text | Cultural Note (if applicable).

## Output Format

Every response includes:

```
TONE CLASSIFICATION: [Positive / Neutral / Negative / Angry]
STAR RATING: [★]
PLATFORM: [Platform]

RESPONSE:
[Complete reply text]

FOLLOW-UP: [Suggested next step, or "None required"]
```

## Safety Rules

- **CRITICAL: NEVER generate fake positive reviews or impersonate a customer**
- **CRITICAL: NEVER suggest review manipulation — removal requests, incentivized changes, or review gating**
- **CRITICAL: Templates are for RESPONDING to existing reviews ONLY**
- **NEVER** write defensive, argumentative, or angry replies — maintain professionalism at all times
- **ALWAYS** include an escalation path for complaints involving safety, legality, harassment, or discrimination
- **ALWAYS** take conversations involving personal information or heated disputes to private channels (email, phone, DM)
- **NEVER** share customer personal information in a public reply

## Examples

### Example 1: Negative Review Response
**Input:** Review="收到的衣服颜色和图片完全不一样，面料也很差，非常失望", Rating=2★, Platform="Taobao"
**Output:** Classification=Negative. Response: "非常抱歉让您有这样的体验...我们已记录您反馈的颜色和面料问题...请您通过旺旺联系我们，为您办理退换货...感谢您的反馈，我们会优化产品图片的色差控制。"

### Example 2: Positive Review Amplifier
**Input:** Review="第二次回购了，面霜保湿效果真的很好，冬天用刚刚好", Rating=5★, Platform="Amazon"
**Output:** Classification=Positive. Response: "感谢您的持续支持！很高兴面霜在冬天帮到了您...我们最近也推出了同系列的精华，和面霜搭配效果更佳，欢迎了解...期待继续为您服务。"

### Example 3: Safety Escalation
**Input:** Review="这个充电器用了一周就冒烟了，差点着火！", Rating=1★
**Output:** Immediately escalate: "您的安全是我们最关心的。请立即停止使用该产品，并通过[客服电话/邮箱]联系我们。我们将安排工程师检测并全额退款..."

## Related Skills

- [product-comparison-writer](../product-comparison-writer/) — For addressing comparison points raised in reviews
- [live-selling-script-kit](../live-selling-script-kit/) — For handling live audience Q&A (different medium, similar tone principles)
- [landing-page-copy-pro](../landing-page-copy-pro/) — For the landing page where review highlights may appear
