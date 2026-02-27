#!/usr/bin/env python3
"""
CRON SCRIPT: stop-loss-tp
Runs every 5 minutes to check portfolio for stop-loss or take-profit conditions.
"""

import sys
import os
import json
from dotenv import load_dotenv

# Add parent directory to path so we can import 'examples.trading-workflow' or similar
# The trading-workflow.py is in ../examples/ relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXAMPLES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'examples')
sys.path.append(EXAMPLES_DIR)

# Load env vars
env_path = os.path.expanduser("~/.openclaw/workspace/.env")
load_dotenv(env_path)

# Verify critical env vars
if not os.getenv("KRYPTOGO_API_KEY") or not os.getenv("SOLANA_WALLET_ADDRESS"):
    print("ERROR: Missing KRYPTOGO_API_KEY or SOLANA_WALLET_ADDRESS in .env")
    sys.exit(1)

try:
    # Import the trading workflow module
    # Note: the file is named trading-workflow.py (with hyphen), so we import via importlib
    import importlib.util
    spec = importlib.util.spec_from_file_location("trading_workflow", os.path.join(EXAMPLES_DIR, "trading-workflow.py"))
    tw = importlib.util.module_from_spec(spec)
    sys.modules["trading_workflow"] = tw
    spec.loader.exec_module(tw)
    
    # 1. Check Portfolio & Monitor Positions
    print("Checking portfolio for stop-loss / take-profit conditions...")
    actions = tw.monitor_positions()
    
    if not actions:
        print("No actions needed. All positions within thresholds.")
        sys.exit(0)

    # 2. Execute Actions
    for action in actions:
        mint = action["mint"]
        symbol = action["symbol"]
        act_type = action["action"]
        reason = action["reason"]
        
        print(f"Action triggered: {act_type} {symbol} ({reason})")
        
        # We need pnl_pct and holding_hours for logging, which monitor_positions doesn't return directly
        # So we fetch portfolio again briefly to get those details
        portfolio = tw.get_portfolio(os.getenv("SOLANA_WALLET_ADDRESS"))
        token_data = next((t for t in portfolio.get("tokens", []) if t["mint"] == mint), None)
        
        pnl_pct = 0.0
        pnl_sol = 0.0
        holding_hours = 0.0
        
        if token_data:
            # Recalculate PnL/holding metrics for the log
            # Logic similar to monitor_positions but we need values
            unrealized_pnl = float(token_data.get("unrealized_pnl", "0"))
            avg_cost = float(token_data.get("holding_avg_cost", "0"))
            balance = float(token_data.get("balance", "0"))
            cost_basis = avg_cost * balance
            if cost_basis > 0:
                pnl_pct = (unrealized_pnl / cost_basis * 100)
            pnl_sol = unrealized_pnl # assuming raw value is USD or SOL? API usually returns USD for PnL
            holding_hours = int(token_data.get("avg_holding_seconds", "0")) / 3600

        if act_type in ["SELL", "TAKE_PROFIT"]:
            print(f"Executing SELL for {symbol}...")
            result = tw.execute_exit(mint, symbol, act_type, reason, pnl_pct, pnl_sol, holding_hours)
            if result:
                print(f"SUCCESS: Sold {symbol}. Tx: {result.get('tx_hash', 'N/A')}")
            else:
                print(f"FAILED: Could not execute sell for {symbol}.")
        
        elif act_type == "REDUCE":
            print(f"Recommendation: REDUCE {symbol} (Distribution detected). Auto-reduce not implemented yet.")
            
        elif act_type == "REVIEW":
            print(f"Recommendation: REVIEW {symbol} (Stale position > 24h).")

except Exception as e:
    print(f"CRITICAL ERROR in cron_monitor: {e}")
    sys.exit(1)
