# Product Comparison & Review Copywriter

## Purpose

This skill generates fair, structured product comparison content — head-to-head comparison tables, category buying guides, balanced pros/cons analyses, specification battles, and personalized "best for" recommendations. It is built with fairness as a first principle: the output must be useful to readers making purchase decisions, not a disguised sales pitch. Designed for e-commerce product pages, editorial content, affiliate marketing, and merchant category pages.

## Triggers

- "product comparison"
- "product VS"
- "对比评测"
- "buying guide"
- "pros and cons"
- "选购指南"
- "compare products"
- "spec comparison"
- "best for recommendation"
- "优缺点分析"

## Workflow

1. Receive products to compare from user: Product A and Product B (or a category with multiple entries), with key specs, price points, target users, and any sponsored/editorial disclosure.
2. Build a feature comparison matrix: list all comparable features across both products, note where data is missing.
3. Generate balanced pros and cons for each product — a MINIMUM of 2 pros and 2 cons per product, even for the recommended one.
4. Create "best for" recommendations based on user personas, not product superiority: "Product A is best for [persona/use case], Product B is best for [different persona/use case]."
5. Apply the fairness gate: verify no invented weaknesses, no suppressed advantages, no defamatory language.
6. Output the complete comparison package: feature table + pros/cons + buying recommendation + fairness disclosure.

## Prompt Templates

### 1. Head-to-Head Comparison (`head_to_head_comparison`)
**Purpose:** Generate a structured A vs B comparison.
**Input:**
- `${product_a_name}` — Product A name + key specs
- `${product_b_name}` — Product B name + key specs
- `${comparison_focus}` — What matters most (price/performance/quality/features/ecosystem)
- `${disclosure}` — Editorial or sponsored relationship

**Output:** Feature matrix table + balanced pros/cons per product + "best for" verdict + fairness disclosure.

### 2. Buying Guide (`buying_guide`)
**Purpose:** Create a tiered buying guide for a product category.
**Input:**
- `${category}` — Product category (e.g., "noise-canceling headphones")
- `${budget_tiers}` — Price brackets with 1–2 products per tier
- `${user_personas}` — 2–3 buyer types and what they value

**Output:** Tiered guide: Budget Tier | Product(s) | Key Feature | Best For | Pros | Cons | Price.

### 3. Pros/Cons Generator (`pros_cons_generator`)
**Purpose:** Generate an objectively balanced pros/cons list for one product.
**Input:**
- `${product_name}` — Product
- `${product_details}` — Full specs, price, user reviews context
- `${use_case}` — Intended usage context

**Output:** Pros list (minimum 3) and Cons list (minimum 2), each with a one-sentence explanation.

### 4. Spec Battle (`spec_battle`)
**Purpose:** Format raw specifications into a readable comparison.
**Input:**
- `${product_a_specs}` — Structured spec list for Product A
- `${product_b_specs}` — Structured spec list for Product B
- `${highlight_categories}` — Which spec categories to emphasize

**Output:** Spec comparison table: Feature | Product A | Product B | Winner (if clear) | Note.

### 5. Best For Matcher (`best_for_matcher`)
**Purpose:** Match products to user personas with personalized recommendations.
**Input:**
- `${product_options}` — 2–5 products in a category
- `${user_persona}` — One persona description (type, budget, priorities, constraints)

**Output:** Ranked recommendation: #1 pick with reasoning, runner-up, and "avoid if" note for each product.

## Output Format

Every comparison is delivered in a reader-friendly structure:

**Feature Comparison Table:**
| Feature | Product A | Product B | Edge |
|---------|-----------|-----------|------|
| Price | ¥299 | ¥399 | A |
| ... | ... | ... | ... |

**Pros & Cons:**
- **Product A**
  - ✅ Pro 1: ...
  - ❌ Con 1: ...
- **Product B** (same structure)

**Verdict:** Best for [persona/use case] → [which product and why]

**Fairness Disclosure:** [Editorial/Sponsored/Data sources]

## Safety Rules

- **NEVER** invent or exaggerate a competitor's weakness — if data is missing, say "data not available"
- **NEVER** suppress or omit a competitor's genuine advantage
- **NEVER** use defamatory, dismissive, or insulting language about any product
- **NEVER** present sponsored content as editorial — always label sponsorship
- **ALWAYS** generate AT LEAST 2 cons for every product, even the recommended one
- **ALWAYS** cite sources when using third-party data or reviews
- **ALWAYS** provide a fairness disclosure section

## Examples

### Example 1: Head-to-Head (Smartphones)
**Input:** A="Phone X ¥2999 6.7in 5000mAh 64MP", B="Phone Y ¥3299 6.5in 4500mAh 108MP", Focus="camera+battery"
**Output:** Feature table with 8 rows, A wins on battery/price, B wins on camera/resolution. Pros/cons for each (Phone X con: "lower camera resolution"; Phone Y con: "higher price, smaller battery"). Verdict: "Phone X best for budget-conscious battery users; Phone Y best for photography enthusiasts."

### Example 2: Buying Guide
**Input:** Category="蓝牙耳机 (Bluetooth Earbuds)", Tiers=["入门<200", "中端200-500", "高端>500"], Personas=["通勤党", "运动党", "学生党"]
**Output:** Three-tier guide with 5 products, each linked to a persona, with balanced pros/cons.

## Related Skills

- [product-title-booster](../product-title-booster/) — For optimizing titles of the compared products
- [review-reply-coach](../review-reply-coach/) — For responding to reviews that the comparison may attract
- [landing-page-copy-pro](../landing-page-copy-pro/) — For the landing page hosting the buying guide
