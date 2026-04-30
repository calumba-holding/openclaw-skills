#!/usr/bin/env python3
"""
advise.py — Task-to-model cost advisor.

Analyzes a task description, estimates token usage, and recommends
the most cost-effective model with projected cost.

Usage:
    echo "Write a REST API in FastAPI" | python advise.py
    python advise.py --task "Refactor a 500-line Python class"
    python advise.py --task "Simple Q&A bot" --json
    python advise.py --compare          # Compare all models side-by-side

Environment:
    HERMES_CURRENT_MODEL — If set, compares against user's current model.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

CACHE_PATH = Path.home() / ".hermes" / "model_pricing.json"

# ── Task complexity rubric ──────────────────────────────────────────
# Each signal adds points; tier is determined by total score.

TIER_THRESHOLDS = {
    1: (0, 5),       # Budget
    2: (5, 10),      # Standard
    3: (10, 18),     # Advanced
    4: (18, 99),     # Premium
}

# Signals that force minimum tier regardless of score
TIER_FLOOR_SIGNALS = {
    "autonomous_agent": 3,
    "architecture_design": 3,
    "deep_reasoning": 3,
    "research_analysis": 4,
    "codebase_analysis": 3,
    "production_critical": 3,  # production tasks need Advanced
    "customer_facing": 3,
}

# Signal combinations that force minimum tier
COMBO_TIER_FLOORS = [
    ({"complex_code", "production_critical"}, 3),
    ({"complex_code", "debugging"}, 3),
    ({"multi_file_project", "production_critical"}, 3),
]

TIER_NAMES = {1: "Budget", 2: "Standard", 3: "Advanced", 4: "Premium"}

SIGNALS = {
    # Reasoning depth (0-6)
    "deep_reasoning": 6,
    "multi_step_logic": 4,
    "chain_of_thought": 5,
    "architecture_design": 5,
    "research_analysis": 6,
    "simple_lookup": 1,
    "classification": 2,
    "summarization": 2,

    # Code complexity (0-6)
    "complex_code": 5,
    "multi_file_project": 4,
    "debugging": 3,
    "refactoring": 3,
    "simple_script": 2,
    "code_review": 3,
    "no_code": 0,

    # Context needs (0-4)
    "large_context": 4,
    "long_document": 3,
    "codebase_analysis": 3,
    "normal_context": 1,

    # Tool/Agent use (0-5)
    "autonomous_agent": 5,
    "multi_turn_tools": 3,
    "few_tool_calls": 1,
    "single_shot": 0,

    # Domain specificity (0-3)
    "chinese_content": 1,
    "math_heavy": 2,
    "specialized_domain": 2,
    "general_task": 0,

    # Quality needs (0-3)
    "production_critical": 3,
    "customer_facing": 3,
    "draft_ok": 0,
}

# Token estimation by tier
TOKEN_ESTIMATES = {
    1: {"input": (500, 2000), "output": (200, 1000)},
    2: {"input": (2000, 8000), "output": (1000, 4000)},
    3: {"input": (8000, 40000), "output": (4000, 16000)},
    4: {"input": (40000, 150000), "output": (16000, 50000)},
}

# Reasoning model multiplier (R1, o3, etc. consume hidden thinking tokens)
REASONING_OUTPUT_MULTIPLIER = 4.0

REASONING_MODELS = {
    "deepseek-r1", "o3", "o3-mini", "o4-mini",
}


def load_pricing() -> dict:
    """Load cached pricing data."""
    if not CACHE_PATH.exists():
        print("❌ No pricing cache found. Run: python fetch_pricing.py", file=sys.stderr)
        sys.exit(1)
    with open(CACHE_PATH) as f:
        data = json.load(f)
    # Convert string tier keys to integers
    if "tiers" in data:
        data["tiers"] = {int(k): v for k, v in data["tiers"].items()}
    return data


# Keyword mapping: words → signals they trigger (with points)
KEYWORD_SIGNALS = {
    # Code complexity
    "api": ("complex_code", 5),
    "rest": ("complex_code", 4),
    "full-stack": ("multi_file_project", 5),
    "fullstack": ("multi_file_project", 5),
    "refactor": ("refactoring", 3),
    "debug": ("debugging", 3),
    "database": ("complex_code", 3),
    "postgres": ("complex_code", 3),
    "sql": ("complex_code", 3),
    "docker": ("complex_code", 3),
    "deploy": ("complex_code", 3),
    "microservice": ("architecture_design", 5),
    "script": ("simple_script", 2),
    "function": ("simple_script", 1),
    "class": ("complex_code", 2),
    "module": ("complex_code", 2),
    "package": ("complex_code", 2),
    "bug": ("debugging", 3),
    "fix": ("debugging", 2),
    "error": ("debugging", 2),
    "race condition": ("debugging", 4),
    "concurrency": ("debugging", 3),
    "test": ("code_review", 1),
    "review code": ("code_review", 2),
    "code review": ("code_review", 2),
    "pull request": ("code_review", 1),

    # Reasoning
    "analyze": ("multi_step_logic", 3),
    "analysis": ("multi_step_logic", 3),
    "design": ("architecture_design", 4),
    "architecture": ("architecture_design", 5),
    "plan": ("multi_step_logic", 3),
    "evaluate": ("multi_step_logic", 3),
    "compare": ("multi_step_logic", 2),
    "reason": ("chain_of_thought", 4),
    "research": ("research_analysis", 5),
    "investigate": ("research_analysis", 4),
    "explain": ("multi_step_logic", 2),
    "tutorial": ("multi_step_logic", 3),

    # Context
    "codebase": ("codebase_analysis", 4),
    "repository": ("codebase_analysis", 3),
    "repo": ("codebase_analysis", 3),
    "document": ("long_document", 3),
    "pdf": ("long_document", 2),
    "large": ("large_context", 3),

    # Tool/Agent
    "agent": ("autonomous_agent", 5),
    "autonomous": ("autonomous_agent", 5),
    "loop": ("autonomous_agent", 4),
    "multi-turn": ("multi_turn_tools", 4),
    "tool": ("multi_turn_tools", 2),
    "search": ("few_tool_calls", 1),
    "fetch": ("few_tool_calls", 1),
    "scrape": ("multi_turn_tools", 2),

    # Quality
    "production": ("production_critical", 3),
    "customer": ("customer_facing", 3),
    "client": ("customer_facing", 2),
    "enterprise": ("production_critical", 3),
    "critical": ("production_critical", 3),
    "security": ("production_critical", 3),
    "auth": ("production_critical", 2),
    "jwt": ("production_critical", 2),

    # Domain
    "chinese": ("chinese_content", 2),
    "中文": ("chinese_content", 2),
    "math": ("math_heavy", 2),
    "algorithm": ("math_heavy", 2),

    # Simple
    "summarize": ("summarization", 2),
    "summary": ("summarization", 2),
    "classify": ("classification", 2),
    "categorize": ("classification", 2),
    "translate": ("summarization", 1),
    "format": ("classification", 1),
    "convert": ("classification", 1),
}


def analyze_task(description: str) -> tuple[int, int, dict]:
    """
    Analyze task description and return (tier, score, analysis).

    Uses keyword matching against the SIGNALS rubric.
    """
    desc_lower = description.lower()
    score = 0
    matched = {}

    # Check each signal from rubric
    for signal, points in SIGNALS.items():
        keywords = signal.lower().replace("_", " ")
        words = keywords.split()
        # For multi-word signals, require ALL words to match
        if len(words) > 1:
            if all(w in desc_lower for w in words):
                score += points
                matched[signal] = points
        else:
            if words[0] in desc_lower:
                score += points
                matched[signal] = points

    # Keyword-based matching (more granular)
    seen_signals = set(matched.keys())
    for keyword, (signal, points) in KEYWORD_SIGNALS.items():
        if signal in seen_signals:
            continue  # Already matched by rubric
        if keyword in desc_lower:
            score += points
            matched[signal] = points
            seen_signals.add(signal)

    # Fallback: check common patterns
    if score == 0:
        if len(description.split()) < 10:
            score = 1
        elif any(w in desc_lower for w in ["code", "function", "script", "program"]):
            score = 3
        elif any(w in desc_lower for w in ["system", "architecture", "design"]):
            score = 8
        else:
            score = 2

    # Determine tier from score
    tier = 1
    for t, (lo, hi) in TIER_THRESHOLDS.items():
        if lo <= score < hi:
            tier = t
            break

    # Apply tier floor from high-criticality signals
    for signal in matched:
        floor = TIER_FLOOR_SIGNALS.get(signal, 0)
        if floor > tier:
            tier = floor

    # Apply combo floors (multiple signals together)
    matched_set = set(matched.keys())
    for signals_combo, floor in COMBO_TIER_FLOORS:
        if signals_combo.issubset(matched_set) and floor > tier:
            tier = floor

    return tier, score, matched


def estimate_tokens(tier: int) -> tuple[int, int]:
    """Estimate input/output tokens for a given tier."""
    est = TOKEN_ESTIMATES[tier]
    # Use midpoint
    inp = (est["input"][0] + est["input"][1]) // 2
    out = (est["output"][0] + est["output"][1]) // 2
    return inp, out


def compute_cost(model_info: dict, input_tokens: int, output_tokens: int) -> float:
    """Compute cost in USD."""
    inp_price = model_info["input_price_per_M"]
    out_price = model_info["output_price_per_M"]

    effective_output = output_tokens
    model_name = model_info.get("name", "")
    if model_name in REASONING_MODELS:
        effective_output = int(output_tokens * REASONING_OUTPUT_MULTIPLIER)

    cost = (input_tokens / 1_000_000) * inp_price
    cost += (effective_output / 1_000_000) * out_price
    return cost


def recommend(
    pricing: dict, tier: int, input_tokens: int, output_tokens: int
) -> list[dict]:
    """Generate ranked recommendations."""
    models = pricing.get("models", {})

    # Collect candidates: models in target tier ± 1
    candidates = []
    tiers = pricing.get("tiers", {})

    for t in [tier - 1, tier, tier + 1]:
        if t < 1 or t > 4:
            continue
        for name in tiers.get(t, []):
            info = models.get(name)
            if info:
                cost = compute_cost({**info, "name": name}, input_tokens, output_tokens)
                candidates.append({
                    "name": name,
                    "provider": info.get("provider", "unknown"),
                    "tier": t,
                    "input_price": info["input_price_per_M"],
                    "output_price": info["output_price_per_M"],
                    "context": info.get("context_window", 0),
                    "cost": cost,
                })

    # Sort: lower cost preferred, but tier match gets bonus
    def sort_key(c):
        tier_bonus = 0 if c["tier"] == tier else (1 if abs(c["tier"] - tier) == 1 else 3)
        return (tier_bonus, c["cost"])

    candidates.sort(key=sort_key)
    return candidates[:6]  # Top 6


def format_output(
    analysis: dict,
    recommendations: list[dict],
    tier: int,
    input_tokens: int,
    output_tokens: int,
    current_model: Optional[str] = None,
    json_mode: bool = False,
) -> str:
    """Format the recommendation output."""
    if json_mode:
        return json.dumps({
            "analysis": analysis,
            "recommendations": [
                {**r, "cost": round(r["cost"], 4)} for r in recommendations
            ],
        }, indent=2)

    lines = []
    lines.append("")
    lines.append("╔══════════════════════════════════════════════════╗")
    lines.append("║        🤖 Model Cost Advisor                      ║")
    lines.append("╚══════════════════════════════════════════════════╝")
    lines.append("")

    # Task analysis
    lines.append("🎯 Task Analysis")
    lines.append(f"   Complexity Tier: {tier} ({TIER_NAMES[tier]})")
    lines.append(f"   Est. Input:  ~{input_tokens // 1000}K tokens")
    lines.append(f"   Est. Output: ~{output_tokens // 1000}K tokens")
    if analysis.get("signals"):
        signals_str = ", ".join(analysis["signals"])
        lines.append(f"   Signals: {signals_str}")
    lines.append("")

    # Recommendations
    lines.append("💰 Top Recommendations")
    lines.append(f"   {'Rank':<5} {'Model':<22} {'Cost':>8}  {'Input $/M':>8} {'Output $/M':>9}")
    lines.append(f"   {'─'*5} {'─'*22} {'─'*8}  {'─'*8} {'─'*9}")

    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    for i, rec in enumerate(recommendations):
        medal = medals.get(i, f"  {i+1}.")
        cost_str = f"${rec['cost']:.4f}"
        inp_str = f"${rec['input_price']:.2f}"
        out_str = f"${rec['output_price']:.2f}"
        reasoning_tag = " ⚡" if rec["name"] in REASONING_MODELS else ""
        lines.append(
            f"   {medal:<5} {rec['name']+reasoning_tag:<22} "
            f"{cost_str:>8}  {inp_str:>8} {out_str:>9}"
        )
    lines.append("")

    # Rationale
    top = recommendations[0]
    lines.append(f"📋 Why {top['name']}?")
    lines.append(f"   Tier {TIER_NAMES[tier]} task → best value in tier {top['tier']}")
    lines.append(f"   Estimated total cost: ${top['cost']:.4f}")
    lines.append("")

    # Compare with current
    if current_model:
        current_info = None
        for rec in recommendations:
            if rec["name"] == current_model:
                current_info = rec
                break

        if current_info:
            savings = current_info["cost"] - top["cost"]
            if savings > 0:
                lines.append(f"📊 vs Current ({current_model})")
                lines.append(f"   Switching saves: ${savings:.4f} ({savings/current_info['cost']*100:.0f}%)")
            elif savings < 0:
                lines.append(f"📊 vs Current ({current_model})")
                lines.append(f"   Upgrade costs +${-savings:.4f} more for better capability")
            lines.append("")

    # Pitfalls
    if any(r["name"] in REASONING_MODELS for r in recommendations[:3]):
        lines.append("⚠️  Reasoning model caveat:")
        lines.append("   Hidden thinking tokens are billed as output.")
        lines.append(f"   Real cost may be ~{REASONING_OUTPUT_MULTIPLIER:.0f}× higher than estimated.")
        lines.append("")

    return "\n".join(lines)


def main():
    # Parse args
    task = None
    json_mode = "--json" in sys.argv
    compare_mode = "--compare" in sys.argv

    for i, arg in enumerate(sys.argv):
        if arg == "--task" and i + 1 < len(sys.argv):
            task = sys.argv[i + 1]
        elif arg == "--compare":
            compare_mode = True

    if not task and not compare_mode:
        # Read from stdin
        if not sys.stdin.isatty():
            task = sys.stdin.read().strip()
        else:
            print("Usage: echo 'task description' | python advise.py", file=sys.stderr)
            print("   or: python advise.py --task 'task description'", file=sys.stderr)
            print("   or: python advise.py --compare", file=sys.stderr)
            sys.exit(1)

    # Load data
    pricing = load_pricing()
    current_model = os.environ.get("HERMES_CURRENT_MODEL")

    if compare_mode:
        # Side-by-side comparison of all models
        models = pricing.get("models", {})
        tiers = pricing.get("tiers", {})
        print("\n📊 All Models — Cost per 10K input + 4K output\n")
        print(f"   {'Model':<22} {'Tier':>5} {'Cost':>8}  {'In $/M':>7} {'Out $/M':>8}")
        print(f"   {'─'*22} {'─'*5} {'─'*8}  {'─'*7} {'─'*8}")
        for t in sorted(tiers):
            for name in tiers[t]:
                m = models.get(name)
                if m:
                    cost = compute_cost({**m, "name": name}, 10000, 4000)
                    print(
                        f"   {name:<22} {t:>5} ${cost:>7.4f}  "
                        f"${m['input_price_per_M']:>6.2f} ${m['output_price_per_M']:>7.2f}"
                    )
        print()
        return

    # Analyze
    tier, score, matched_signals = analyze_task(task)
    input_tokens, output_tokens = estimate_tokens(tier)

    # Recommend
    recs = recommend(pricing, tier, input_tokens, output_tokens)

    # Format
    analysis = {
        "tier": tier,
        "tier_name": TIER_NAMES[tier],
        "score": score,
        "signals": list(matched_signals.keys()),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }

    output = format_output(analysis, recs, tier, input_tokens, output_tokens, current_model, json_mode)
    print(output)


if __name__ == "__main__":
    main()
