---
name: model-cost-advisor
description: Analyze any task and recommend the most cost-effective LLM — with live pricing data from 30+ models, tier analysis, token estimation, and projected cost. Perfect before starting a new task or comparing providers.
title: Model Cost Advisor — Pick the right model for the right price
summary: |
  Stop overpaying for AI. This skill analyzes your task's complexity, estimates token usage,
  and compares 30+ models across 4 cost tiers to recommend the best value. 
  Uses community-maintained pricing from litellm (updated weekly).
  
  One command: `echo "your task" | python scripts/advise.py`
author: Hermes
version: 1.0
---

# 🤖 Model Cost Advisor

**Pick the most cost-effective LLM for any task — before you start spending.**

Why pay Claude Opus prices for a task DeepSeek can handle? This skill analyzes your task, maps it to a capability tier, and finds the cheapest model that gets the job done well.

---

## Quick Start

```bash
# 1. Fetch live pricing (one-time, auto-cached for 48h)
python scripts/fetch_pricing.py

# 2. Get a recommendation
echo "Write a REST API with FastAPI, handle auth and rate limiting" | python scripts/advise.py

# 3. Or pass task directly
python scripts/advise.py --task "Refactor a 2000-line Python class into smaller modules"

# 4. Compare all models side-by-side
python scripts/advise.py --compare

# 5. JSON output for scripting
python scripts/advise.py --task "Debug a race condition" --json
```

---

## What It Does

1. **Analyzes** your task description for complexity signals (reasoning depth, code needs, context length, agentic loops, domain expertise)
2. **Maps** to one of 4 capability tiers: Budget → Standard → Advanced → Premium
3. **Estimates** token usage based on task complexity
4. **Scores** 30+ models using live pricing from [litellm's community DB](https://github.com/BerriAI/litellm)
5. **Recommends** the top 3 models with projected cost, rationale, and pitfalls

---

## The Four Tiers

| Tier | When to Use | Example Tasks | Typical Cost |
|------|-------------|---------------|--------------|
| 💰 **Budget** | Simple Q&A, classification, formatting, basic scripts | "Summarize this text", "Format JSON" | <$0.01 |
| 📦 **Standard** | Multi-step reasoning, medium code, structured output | "Write a web scraper", "Explain a concept" | $0.01–$0.10 |
| 🚀 **Advanced** | Complex code, architecture design, agentic loops | "Build a full-stack app", "Debug concurrency" | $0.10–$1.00 |
| 👑 **Premium** | Frontier reasoning, research, >128K context | "Research paper analysis", "Safety-critical code" | $1.00+ |

---

## Models Tracked

30+ models across 6 providers, updated from litellm's community DB:

| Provider | Models |
|----------|--------|
| **Anthropic** | Claude Opus 4 / 4.1 / 4.5 / 4.6 / 4.7, Sonnet 4 / 4.5 / 4.6, Haiku 3.5 |
| **OpenAI** | GPT-4o, GPT-4o-mini, GPT-4.1 / 4.1-mini / 4.1-nano, o3 / o3-mini / o4-mini |
| **Google** | Gemini 2.0 Flash, 2.5 Flash / Pro |
| **DeepSeek** | V3 / V3.1 / V3.2, R1 (with reasoning token warning) |
| **Alibaba** | Qwen Turbo / Plus / Max / Coder-Plus / 3-235B |
| **Mistral** | Ministral 3B / 8B / 14B |

---

## Example Output

```
╔══════════════════════════════════════════════════╗
║        🤖 Model Cost Advisor                      ║
╚══════════════════════════════════════════════════╝

🎯 Task Analysis
   Complexity Tier: 3 (Advanced)
   Est. Input:  ~24K tokens
   Est. Output: ~10K tokens
   Signals: multi_step_logic, complex_code, multi_turn_tools

💰 Top Recommendations
   Rank  Model                  Cost     Input $/M Output $/M
   ───── ────────────────────── ────────  ──────── ─────────
   🥇    deepseek-v3            $0.0175     0.28     0.42
   🥈    deepseek-v3.1          $0.0216     0.27     1.10
   🥉    gemini-2.5-flash       $0.0322     0.30     2.50

📋 Why deepseek-v3?
   Tier 3 task → best value in tier 1
   Estimated total cost: $0.0175
```

---

## How the Agent Uses This Skill

When loaded by Hermes, the agent follows these steps:

### Step 1: Analyze Task Requirements

Classify the task along these dimensions to determine the **minimum capability tier** needed:

| Dimension | Weight | What to Assess |
|-----------|--------|----------------|
| Reasoning Depth | High | Simple lookup → multi-step logic → deep chain-of-thought |
| Code Generation | Medium | None → simple scripts → multi-file complex → architecture design |
| Context Length | Medium | <4K → 4K-32K → 32K-128K → >128K tokens |
| Tool Use / Agentic | High | Single shot → multi-turn tools → autonomous agent loop |
| Domain Expertise | Low | General → specialized (math, legal, medical, Chinese content) |
| Output Quality | Medium | Draft OK → production → customer-facing critical |
| Latency | Low | Batch OK → real-time interactive |

### Step 2: Estimate Token Usage

| Task Complexity | Input Tokens | Output Tokens |
|-----------------|--------------|---------------|
| Trivial (single Q&A) | 500 – 2K | 200 – 1K |
| Simple (few exchanges) | 2K – 8K | 1K – 4K |
| Medium (multi-turn agent, 5-10 tools) | 8K – 40K | 4K – 16K |
| Complex (deep agent, 10-30 tools) | 40K – 150K | 16K – 50K |
| Heavy (autonomous loop, 30+ tools) | 150K – 500K+ | 50K – 200K+ |

### Step 3: Run Scripts

```bash
# Ensure pricing is fresh
python scripts/fetch_pricing.py

# Get recommendation
python scripts/advise.py --task "<user's task description>"
```

### Step 4: Present Recommendation

Format the output with:
1. Task complexity analysis
2. Top 3 model picks with cost
3. Comparison vs user's current model (if known)
4. Any pitfalls (R1 reasoning tokens, context window limits, etc.)

---

## Pitfalls to Warn Users About

**Script internals (for maintenance):**
- **Tier keys in pricing JSON are strings, not ints** — `pricing_cache` dict uses `"1"` not `1`. The advise script casts them internally, but direct lookups must match.
- **Keyword matching order matters** — put longer-specific keywords (e.g., `'production'`) before shorter ambiguous ones (`'pr'`) to avoid substring false positives. Split on word boundaries.

**User-facing pitfalls:**

1. **R1/o3 reasoning tokens are hidden**: Sticker price hides massive output consumption. Real cost is 3-5× higher for reasoning models.
2. **Context is not free**: Models with 1M context (Gemini) charge for every token in the window, used or not.
3. **Tool calls compound cost**: Every agentic round-trip adds system prompt + tool definitions + results. An agent task easily 5× the naive estimate.
4. **Cached prefixes save money**: System prompts and cached prefixes bill at 10-25% — factor in for repetitive tasks.
5. **Chinese-language tasks**: DeepSeek and Qwen outperform their price tier on Chinese content. Western models cost more for equivalent quality.
6. **Pricing changes frequently**: Run `fetch_pricing.py` before important decisions. Cache TTL is 48 hours.

---

## Scripts

- `scripts/fetch_pricing.py` — Fetches live pricing from litellm DB, normalizes to canonical model names, caches for 48h.
- `scripts/advise.py` — Task complexity analysis + model recommendation engine with colorized terminal output.
