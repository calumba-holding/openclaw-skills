---
name: GEO AgentOps
description: >-
  Use when user needs GEO optimization for B2B export websites.
  Use when generating AI-friendly content for ChatGPT/Claude/Perplexity.
  Use when tracking AI citation rankings across platforms.
  Use when optimizing content for generative engine visibility.
  Use when user mentions "GEO", "AI搜索优化", "ChatGPT引流", "AI引用追踪", "出海运营".
homepage: https://geoagentops.ai
license: MIT-0
progressive:
  layers:
    - name: metadata
      tokens: 200
      loaded: startup
      description: "技能基础配置、产品套件、定价信息"
    - name: instructions
      tokens: 5000
      loaded: trigger
      description: "6步GEO工作流、AI模型配置、内容生成代理"
    - name: resources
      tokens: variable
      loaded: on-demand
      description: "案例研究、效果指标、平台配置模板"
  resource_paths:
    - scripts/*.py
    - templates/*.md
    - references/geo_templates/
metadata:
  openclaw:
    homepage: https://geoagentops.ai
    primaryEnv: OPENAI_API_KEY
    requires:
      env:
        - OPENAI_API_KEY
        - ANTHROPIC_API_KEY
      bins:
        - curl
    apis:
      - name: OpenAI API
        url: https://api.openai.com
        purpose: "GPT模型调用，用于GEO内容生成和优化"
        auth: Bearer Token (OPENAI_API_KEY)
      - name: Anthropic API
        url: https://api.anthropic.com
        purpose: "Claude模型调用，用于GEO文章撰写"
        auth: Bearer Token (ANTHROPIC_API_KEY)
      - name: Perplexity API
        url: https://api.perplexity.ai
        purpose: "AI搜索引用追踪和竞品分析"
        auth: Bearer Token (PERPLEXITY_API_KEY)
      - name: LinkedIn API
        url: https://api.linkedin.com
        purpose: "社交内容发布和数据分析"
        auth: OAuth
      - name: Twitter/X API
        url: https://api.twitter.com
        purpose: "社交内容发布和舆情监控"
        auth: OAuth
version: "2.1.3"
author: "OpenClaw AI Team"
emoji: "🌐"

triggers:
  - "GEO优化"
  - "AI搜索优化"
  - "ChatGPT引流"
  - "外贸独立站"
  - "B2B营销"
  - "AI引用追踪"
  - "生成引擎优化"
  - "Perplexity优化"
  - "Claude优化"
  - "Gemini优化"
  - "AI内容营销"
  - "出海运营"
  - "AI询盘"
  - "独立站SEO"
  - "内容种草AI"

tags:
  - GEO
  - SEO
  - B2B export
  - content marketing
  - AI marketing
  - generative engine optimization

category: marketing

pricing:
  - name: Starter
    price: 19
    currency: USD
    period: month
    features:
      - 30 GEO articles/month
      - Perplexity citation monitoring
      - Email support

  - name: Pro Bundle
    price: 59
    currency: USD
    period: month
    features:
      - 100 GEO articles/month
      - All-platform citation monitoring
      - Competitor analysis
      - GEO scoring

  - name: Enterprise
    price: 399
    currency: USD
    period: month
    features:
      - Unlimited GEO articles
      - All-platform + API access
      - Dedicated AI agent
      - Custom GEO strategy
---

# 外贸GEO运营系统：让海外采购商在ChatGPT里找到你的独立站

还在烧Google广告，询盘成本高达$1.2/条？
GEO AgentOps用AI原生方式，让海外采购商在ChatGPT/Claude/Perplexity里主动找到你。

## 【能做什么】

- **GEO内容生成**：6种格式一键输出，AI友好结构让引用率提升60%
- **多平台分发**：一键发布到LinkedIn、Twitter/X、Reddit、Medium、Quora
- **AI引用追踪**：实时监控ChatGPT、Claude、Gemini、Perplexity的引用情况
- **竞品分析**：追踪竞争对手在AI搜索中的表现，弯道超车

## 【效果数据】

- 询盘成本：从$1.20→$0.04（降低97%）
- AI引用率：行业均值8%→68%
- 1-2个月见效，速度是传统SEO的3倍

## 【安装】

```bash
# 通过ClawHub CLI安装
openclaw skills install geo-agentops
```

配置环境变量 `OPENAI_API_KEY` 和 `ANTHROPIC_API_KEY`，适合B2B外贸公司、跨境独立站、DTC品牌出海团队。

---

## Product Overview

**GEO AgentOps** 是一套完整的外贸生成引擎优化（Generative Engine Optimization）运营系统，专为B2B出海企业设计。

### 核心价值
- 让AI引擎主动推荐你的产品和服务
- 询盘成本低至$0.04（Google Ads需$1.20）
- 1-2个月见效，速度是传统SEO的3倍

### 适用场景
- B2B外贸公司SEO转型
- 跨境独立站AI搜索流量获取
- DTC品牌在AI搜索引擎的曝光
- 询盘成本优化

---

## Product Suite

### Three Core Products

| Product | Feature | Pricing |
|---------|---------|---------|
| **Echo** | GEO Content Intelligence Engine | $19/mo |
| **Wing** | Multi-Platform Content Distribution | $39/mo |
| **Radar** | AI Citation Monitoring & Optimization | $39/mo |
| **All-in Bundle** | All three products | $59/mo |

---

## 6-Step GEO Workflow

### Step 1: Configure Brand
- Set brand name, core keywords, target platforms
- Output: Brand configuration file

### Step 2: AI Content Generation
- Select AI model x Agent type x topic
- Generate 6 content formats in seconds
- Output: Topic library, headlines, articles, FAQs, posts, reports

### Step 3: Publish to Platforms
- Publish content to LinkedIn, Twitter/X, Reddit, Medium, Quora
- Multi-platform format adaptation
- Output: Published content records

### Step 4: Log Content
- Track publication status in content management
- Build content tracking index
- Output: Content management sheet

### Step 5: Track Citations
- Monitor AI citations across ChatGPT, Claude, Gemini, Perplexity
- Output: Citation ranking reports

### Step 6: Generate Reports
- One-click operations report generation
- Automated data aggregation
- Output: Report documents

---

## AI Console

### 4 Global AI Models
- **ChatGPT** - Broad reasoning & generation
- **Claude** - Deep analysis & writing
- **Gemini** - Google-native multimodal
- **Perplexity** - Real-time cited answers

### 6 Content Agents

| Agent | Output | Purpose |
|-------|--------|---------|
| Topic Planner | Weekly topic library | Content planning |
| Headline Generator | 10 high-CTR headlines | Attract clicks |
| GEO Article | 1200-word full article | Core content |
| FAQ Content | 8 AI-citable Q&A pairs | Boost citation rate |
| LinkedIn Post | Professional post | B2B social |
| Weekly Report | Auto report template | Operations review |

---

## Key Metrics

### Core KPIs
| Metric | Target | Description |
|--------|--------|-------------|
| AI Citation Rate | ≥60% | % of content cited by AI |
| Cost per Inquiry | ≤$0.50 | Per inquiry cost |
| Content Output | ≥30/month | GEO articles published |
| Platform Coverage | ≥5 | Number of publishing platforms |

### Effect Timeline
- **2–4 weeks** — First AI citation
- **1–2 months** — Stable citations
- **3–6 months** — Inquiry surge

---

## Case Studies

### Amazon FBA Seller — Outdoor Gear Store
- **Industry**: Outdoor equipment wholesale
- **Usage Duration**: 8 months
- **Results**:
  - Inquiry growth: +127%
  - Cost per inquiry: $0.04
  - Monthly AI-channel inquiries: 580
  - ChatGPT monthly citations: 12

### Shopify DTC Brand — Kitchenware
- **Industry**: Kitchenware B2B export
- **Usage Duration**: 5 months
- **Results**:
  - LinkedIn engagement: +340%
  - Average citation rate: 68%
  - Monthly qualified leads: 210

---

## How to Use

```
User: Help me with GEO optimization for pet toy exports to the US
Agent:
1. Configure brand info (pet toys + US + B2B)
2. Generate topic library (10 topics)
3. Generate GEO articles (3 articles)
4. Generate FAQ pairs (8 Q&A)
5. Publish to target platforms
6. Set up citation tracking keywords
```

---

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "GEO is same as SEO" | GEO optimizes for AI citations, not Google rankings; different algorithms, different strategies |
| "One article is enough" | Consistent publishing builds AI citation history; frequency matters |
| "Skip competitor research" | Understanding competitors helps find citation gaps and differentiation opportunities |
| "Publish everywhere" | Quality over quantity; platform-specific content performs better than generic spam |
| "AI citations are instant" | GEO takes 2-4 weeks for first citations, 1-2 months for stable results |
| "Content quantity = success" | Citation quality and relevance matter more than raw volume |
| "Ignore content freshness" | AI models favor recent content; regular updates improve citation chances |

## Verification

After completing geo-agentops workflow:
- [ ] 品牌配置信息完整（名称、关键词、目标平台）
- [ ] 生成的内容符合AI可引用结构（包含FAQ、列表、引用）
- [ ] 内容长度≥800字（AI偏好深度内容）
- [ ] 多平台发布格式适配正确（LinkedIn/Twitter/Reddit等）
- [ ] 引用追踪关键词设置合理（品牌词+核心产品词）
- [ ] 发布后内容管理表已更新记录
- [ ] 案例研究数据已同步到报表系统
- [ ] 竞品分析报告包含差异化建议
