# Product Title & Selling-Point Booster

## Purpose

This skill optimizes e-commerce product titles for search visibility and conversion across five major platforms: Taobao (淘宝), JD (京东), Pinduoduo (拼多多), Amazon, and Shopify/independent stores. It applies platform-specific constraints — character limits, keyword positioning rules, and formatting conventions — to extract high-intent keywords and craft titles that rank better and convert more clicks. "Booster" signals immediate, measurable listing improvement.

## Triggers

- "优化商品标题"
- "生成淘宝标题"
- "Amazon title optimizer"
- "product title booster"
- "标题优化"
- "listing title"
- "电商标题"
- "title A/B test"
- "多平台标题"
- "标题评分"

## Workflow

1. Receive product details from user: product name, brand, category, key attributes (material, size, color, function), and target platform(s).
2. Mine relevant keywords from product attributes: core product term, modifier keywords (material, style, season), scenario keywords, and audience keywords.
3. Apply platform-specific constraints:
   - Taobao: 60 characters max, keyword-stacking style, core term early
   - JD: Brand first, spec-dense, model numbers prominent
   - PDD: Value/price keywords prominent, benefit language
   - Amazon: 200 characters max, no promotional language, backend search terms separate
   - Shopify: SEO-optimized, H1-friendly, conversion-focused
4. Generate optimized title(s) that pack maximum search value within constraints.
5. Create A/B variant suggestions with rationale explaining why each variant may perform differently.
6. Score the original/optimized title and explain each optimization choice.

## Prompt Templates

### 1. Title from Product Info (`title_from_product_info`)
**Purpose:** Generate an optimized title from raw product details.
**Input:**
- `${brand}` — Brand name
- `${product_type}` — Core product term
- `${key_attributes}` — Material, size, color, function, style
- `${target_platform}` — Platform name
- `${current_title}` — (Optional) Existing title to improve

**Output:** Optimized title + character count + keyword analysis table showing which keywords were included and why.

### 2. Multi-Platform Title Pack (`multi_platform_title_pack`)
**Purpose:** Generate titles for 5 platforms from one product.
**Input:**
- `${product_details}` — Same as above
- `${platforms}` — List of target platforms

**Output:** Title per platform, each with character count and platform-specific optimization notes.

### 3. Title A/B Variants (`title_ab_variants`)
**Purpose:** Generate 3 alternative titles with rationale.
**Input:**
- `${current_title}` — Current title
- `${hypothesis}` — What to test (keyword order, emotional appeal, specificity)

**Output:** 3 variant titles, each with: variant title, character count, hypothesis tested, expected click/ranking impact.

### 4. Keyword Extractor (`keyword_extractor`)
**Purpose:** Mine keywords from competitor titles for strategy.
**Input:**
- `${competitor_titles}` — 3–5 competitor listing titles
- `${target_platform}` — Platform context

**Output:** Keyword frequency table, gap analysis (what competitors use that you don't), and suggested keyword additions.

### 5. Title Grader (`title_grader`)
**Purpose:** Score a title and suggest improvements.
**Input:**
- `${title}` — Title to evaluate
- `${platform}` — Platform rules apply

**Output:** Score out of 100 + breakdown by dimension (keyword coverage, readability, platform compliance, conversion appeal) and specific improvement suggestions.

## Output Format

Titles are delivered with:
- **Optimized title** (bolded)
- **Character count** (with platform limit noted)
- **Keyword analysis table:** Keyword | Search Intent | Position | Reason
- **A/B variants** (when requested): Variant | Hypothesis | Expected Impact

## Safety Rules

- **NEVER** stuff keywords in a way that violates specific platform listing policies
- **NEVER** include trademarked competitor brand names in titles
- **NEVER** make misleading claims about product attributes, materials, or certifications
- **ALWAYS** verify proposed titles against platform-specific restricted term lists
- **ALWAYS** remind user to check platform's latest title guidelines (policies change)

## Examples

### Example 1: Taobao Title Optimization
**Input:** Brand="XX", Type="真丝连衣裙", Attributes="中长款、修身、2024新款、桑蚕丝", Platform="Taobao"
**Output:** "XX2024新款桑蚕丝真丝连衣裙女中长款修身显瘦高级感气质" (38 chars / 60 limit) with keyword analysis.

### Example 2: Multi-Platform Pack
**Input:** Same product, Platforms=[Taobao, Amazon, Shopify]
**Output:** Three titles with different structural approaches: keyword-stacked (Taobao), brand-spec (Amazon), SEO-optimized (Shopify).

## Related Skills

- [product-comparison-writer](../product-comparison-writer/) — For comparison tables after titles are optimized
- [ad-copy-ab-tester](../ad-copy-ab-tester/) — For testing which title performs better in ads
- [viral-xiaohongshu-notes](../viral-xiaohongshu-notes/) — For promoting the product with content marketing
