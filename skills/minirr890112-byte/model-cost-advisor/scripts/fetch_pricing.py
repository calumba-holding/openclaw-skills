#!/usr/bin/env python3
"""
fetch_pricing.py — Fetch live model pricing from litellm's community-maintained DB.

Pulls the canonical model_prices_and_context_window.json from GitHub,
extracts a curated subset of the most-used models with normalized fields,
and caches to ~/.hermes/model_pricing.json.

Usage:
    python fetch_pricing.py              # Fetch + save cache
    python fetch_pricing.py --json       # Output JSON to stdout
    python fetch_pricing.py --force      # Skip cache, force re-fetch
    python fetch_pricing.py --ttl 24     # Cache TTL in hours (default: 48)
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen

LITELLM_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/"
    "model_prices_and_context_window.json"
)
CACHE_PATH = Path.home() / ".hermes" / "model_pricing.json"
DEFAULT_TTL_HOURS = 48


# ── Canonical model mapping ──────────────────────────────────────────
# Maps our friendly names → litellm keys (ordered by preference)
CANONICAL_MODELS = {
    # Anthropic
    "claude-opus-4": [
        "claude-opus-4-20250514",
        "anthropic.claude-opus-4-20250514-v1:0",
    ],
    "claude-opus-4.1": [
        "claude-opus-4-1-20250805",
        "claude-opus-4-1",
    ],
    "claude-opus-4.5": [
        "claude-opus-4-5-20251101",
        "claude-opus-4-5",
    ],
    "claude-opus-4.6": [
        "claude-opus-4-6",
        "claude-opus-4-6-20260205",
    ],
    "claude-opus-4.7": [
        "claude-opus-4-7",
        "claude-opus-4-7-20260416",
    ],
    "claude-sonnet-4": [
        "claude-sonnet-4-20250514",
        "anthropic.claude-sonnet-4-20250514-v1:0",
    ],
    "claude-sonnet-4.5": [
        "claude-sonnet-4-5-20250929",
        "claude-sonnet-4-5",
    ],
    "claude-sonnet-4.6": [
        "claude-sonnet-4-6",
    ],
    "claude-haiku-3.5": [
        "claude-3-5-haiku-20241022",
        "anthropic.claude-3-5-haiku-20241022-v1:0",
    ],

    # OpenAI
    "gpt-4o": ["gpt-4o"],
    "gpt-4o-mini": ["gpt-4o-mini"],
    "gpt-4.1": ["gpt-4.1"],
    "gpt-4.1-mini": ["gpt-4.1-mini"],
    "gpt-4.1-nano": ["gpt-4.1-nano"],
    "o3": ["o3"],
    "o3-mini": ["o3-mini"],
    "o4-mini": ["o4-mini"],
    "gpt-4.5-preview": ["gpt-4.5-preview"],

    # Google
    "gemini-2.0-flash": [
        "gemini-2.0-flash",
        "gemini-2.0-flash-001",
        "gemini/gemini-2.0-flash",
    ],
    "gemini-2.5-flash": [
        "gemini-2.5-flash",
        "gemini/gemini-2.5-flash",
    ],
    "gemini-2.5-pro": [
        "gemini-2.5-pro",
        "gemini/gemini-2.5-pro",
    ],

    # DeepSeek (official)
    "deepseek-v3": [
        "deepseek/deepseek-chat",
        "deepseek-chat",
    ],
    "deepseek-v3.1": [
        "deepseek/deepseek-v3",
        "deepseek-v3",
    ],
    "deepseek-v3.2": [
        "deepseek/deepseek-v3.2",
        "deepseek.v3.2",
    ],
    "deepseek-r1": [
        "deepseek/deepseek-reasoner",
        "deepseek-reasoner",
        "deepseek/deepseek-r1",
    ],

    # Qwen (Alibaba DashScope)
    "qwen-turbo": [
        "dashscope/qwen-turbo-latest",
        "dashscope/qwen-turbo",
    ],
    "qwen-plus": [
        "dashscope/qwen-plus-latest",
        "dashscope/qwen-plus-2025-09-11",
    ],
    "qwen-max": [
        "dashscope/qwen-max",
    ],
    "qwen-coder-plus": [
        "dashscope/qwen3-coder-plus",
    ],
    "qwen3-235b": [
        "dashscope/qwen3-235b-a22b",
    ],

    # Mistral
    "ministral-3b": [
        "mistral/ministral-3-3b-2512",
        "mistral.ministral-3-3b-instruct",
    ],
    "ministral-8b": [
        "mistral/ministral-3-8b-2512",
        "mistral.ministral-3-8b-instruct",
    ],
    "ministral-14b": [
        "mistral/ministral-3-14b-2512",
        "mistral.ministral-3-14b-instruct",
    ],
}

# Tier assignment for display grouping
MODEL_TIERS = {
    1: [  # Budget
        "deepseek-v3", "deepseek-v3.1", "deepseek-v3.2",
        "qwen-turbo", "qwen-plus",
        "ministral-3b", "ministral-8b",
        "gemini-2.0-flash", "gpt-4o-mini",
    ],
    2: [  # Standard
        "deepseek-r1", "qwen-max", "qwen-coder-plus",
        "ministral-14b", "claude-haiku-3.5",
        "gemini-2.5-flash",
    ],
    3: [  # Advanced
        "claude-sonnet-4", "claude-sonnet-4.5", "claude-sonnet-4.6",
        "gpt-4o", "gpt-4.1",
        "gemini-2.5-pro", "qwen3-235b",
    ],
    4: [  # Premium
        "claude-opus-4", "claude-opus-4.1", "claude-opus-4.5",
        "claude-opus-4.6", "claude-opus-4.7",
        "gpt-4.5-preview", "o3", "o4-mini",
    ],
}


def fetch_litellm_data(timeout: int = 30) -> dict:
    """Download and parse the litellm pricing JSON."""
    req = Request(LITELLM_URL, headers={"User-Agent": "model-cost-advisor/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_cache() -> Optional[dict]:
    """Load cached pricing if it exists and is fresh."""
    if not CACHE_PATH.exists():
        return None
    try:
        with open(CACHE_PATH) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    fetched_at = data.get("_fetched_at")
    if not fetched_at:
        return None

    age_hours = (time.time() - fetched_at) / 3600
    ttl = data.get("_ttl_hours", DEFAULT_TTL_HOURS)
    if age_hours > ttl:
        return None

    return data


def save_cache(data: dict, ttl_hours: int = DEFAULT_TTL_HOURS):
    """Save pricing data to cache file."""
    data["_fetched_at"] = time.time()
    data["_ttl_hours"] = ttl_hours
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def normalize_pricing(litellm_data: dict) -> dict:
    """Extract canonical models from litellm's raw data."""
    result = {
        "_source": "litellm",
        "_fetched_at": time.time(),
        "models": {},
        "tiers": MODEL_TIERS,
    }

    for name, litellm_keys in CANONICAL_MODELS.items():
        for key in litellm_keys:
            entry = litellm_data.get(key)
            if entry:
                inp = entry.get("input_cost_per_token", 0) * 1_000_000
                out = entry.get("output_cost_per_token", 0) * 1_000_000
                ctx = entry.get("max_tokens", entry.get("max_input_tokens", 0))
                # Skip entries with no pricing
                if inp == 0 and out == 0:
                    continue
                result["models"][name] = {
                    "input_price_per_M": round(inp, 4),
                    "output_price_per_M": round(out, 4),
                    "context_window": ctx,
                    "litellm_key": key,
                    "provider": _guess_provider(name),
                }
                break  # Use first matching key with pricing

    return result


def _guess_provider(name: str) -> str:
    if name.startswith("claude"): return "anthropic"
    if name.startswith("gpt") or name.startswith("o3") or name.startswith("o4"): return "openai"
    if name.startswith("gemini"): return "google"
    if name.startswith("deepseek"): return "deepseek"
    if name.startswith("qwen"): return "alibaba"
    if name.startswith("ministral"): return "mistral"
    return "unknown"


def main():
    force = "--force" in sys.argv
    json_out = "--json" in sys.argv

    # Parse TTL
    ttl = DEFAULT_TTL_HOURS
    for i, arg in enumerate(sys.argv):
        if arg == "--ttl" and i + 1 < len(sys.argv):
            ttl = int(sys.argv[i + 1])

    # Try cache first
    if not force:
        cached = load_cache()
        if cached:
            if json_out:
                print(json.dumps(cached, indent=2))
            else:
                print(f"✅ Using cached pricing (fetched {_age_str(cached['_fetched_at'])})")
                _print_summary(cached)
            return

    # Fetch live
    print("📡 Fetching live pricing from litellm...", file=sys.stderr)
    try:
        raw = fetch_litellm_data()
    except Exception as e:
        print(f"⚠️  Fetch failed: {e}", file=sys.stderr)
        cached = load_cache()
        if cached:
            print("📦 Falling back to cached data.", file=sys.stderr)
            if json_out:
                print(json.dumps(cached, indent=2))
            else:
                _print_summary(cached)
        else:
            print("❌ No cache available. Cannot proceed.", file=sys.stderr)
            sys.exit(1)
        return

    data = normalize_pricing(raw)
    save_cache(data, ttl_hours=ttl)

    model_count = len(data["models"])
    print(f"✅ Fetched {model_count} model prices → cached at {CACHE_PATH}", file=sys.stderr)

    if json_out:
        print(json.dumps(data, indent=2))
    else:
        _print_summary(data)


def _age_str(ts: float) -> str:
    hours = (time.time() - ts) / 3600
    if hours < 1:
        return f"{int(hours * 60)}min ago"
    elif hours < 24:
        return f"{hours:.0f}h ago"
    else:
        return f"{hours / 24:.0f}d ago"


def _print_summary(data: dict):
    """Print a compact pricing summary table."""
    models = data.get("models", {})
    tiers = data.get("tiers", {})

    print("\n📊 Model Pricing Summary\n")
    print(f"{'Model':<22} {'Input $/M':>10} {'Output $/M':>11} {'Context':>10}")
    print("-" * 55)

    for tier_num in sorted(tiers):
        tier_names = ["", "💰 Budget", "📦 Standard", "🚀 Advanced", "👑 Premium"]
        t = int(tier_num) if isinstance(tier_num, str) else tier_num
        print(f"\n── {tier_names[t]} ──")

        for name in tiers[tier_num]:
            m = models.get(name)
            if m:
                inp = m["input_price_per_M"]
                out = m["output_price_per_M"]
                ctx = m["context_window"]
                ctx_str = f"{ctx // 1000}K" if ctx > 1000 else str(ctx)
                print(f"  {name:<20} ${inp:>8.2f}  ${out:>9.2f}  {ctx_str:>9}")
    print()


if __name__ == "__main__":
    main()
