#!/usr/bin/env python3
"""
CRON SCRIPT: discovery-scan
Runs every 30 minutes to discover and analyze new tokens.
"""

import sys
import os
import importlib.util
from dotenv import load_dotenv

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# skill root is parent of scripts/
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
EXAMPLES_DIR = os.path.join(SKILL_ROOT, 'examples')
WORKFLOW_PATH = os.path.join(EXAMPLES_DIR, 'trading-workflow.py')

# Add examples dir to sys.path to allow imports if needed
sys.path.append(EXAMPLES_DIR)

# Load env vars
env_path = os.path.expanduser("~/.openclaw/workspace/.env")
load_dotenv(env_path)

# Verify critical env vars
if not os.getenv("KRYPTOGO_API_KEY") or not os.getenv("SOLANA_WALLET_ADDRESS"):
    print("ERROR: Missing KRYPTOGO_API_KEY or SOLANA_WALLET_ADDRESS in .env")
    sys.exit(1)

if not os.path.exists(WORKFLOW_PATH):
    print(f"ERROR: Workflow script not found at {WORKFLOW_PATH}")
    sys.exit(1)

try:
    # Import the trading workflow module dynamically
    spec = importlib.util.spec_from_file_location("trading_workflow", WORKFLOW_PATH)
    tw = importlib.util.module_from_spec(spec)
    sys.modules["trading_workflow"] = tw
    spec.loader.exec_module(tw)
    
    # Run Discovery Pipeline
    print(f"Starting discovery scan using logic from {WORKFLOW_PATH}...")
    result = tw.discover_and_analyze()
    
    if result:
        print("Discovery scan completed with a trade execution.")
    else:
        print("Discovery scan completed. No trades executed.")

except Exception as e:
    print(f"CRITICAL ERROR in cron_scan: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
