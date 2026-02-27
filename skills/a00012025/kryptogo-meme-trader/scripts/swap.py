#!/usr/bin/env python3
"""
KryptoGO Meme Trader — Swap Executor

Builds, signs locally, and submits a token swap transaction via the
KryptoGO Agent Trading API (Solana only).

Usage:
  python3 scripts/swap.py <output_mint> [amount_sol]
  python3 scripts/swap.py <output_mint> [amount_sol] --sell
  python3 scripts/swap.py <output_mint> [amount_sol] --slippage 500

Examples:
  # Buy 0.1 SOL worth of a token
  python3 scripts/swap.py So11...token_mint_address 0.1

  # Sell tokens back to SOL (--sell flag)
  python3 scripts/swap.py So11...token_mint_address 1000000 --sell

  # Custom slippage (basis points, default: 300 = 3%)
  python3 scripts/swap.py So11...token_mint_address 0.1 --slippage 500

Environment (from ~/.openclaw/workspace/.env):
  KRYPTOGO_API_KEY       - API key for authentication
  SOLANA_WALLET_ADDRESS  - Agent wallet public address
  SOLANA_PRIVATE_KEY     - Agent wallet private key (base58, never sent to server)

SECURITY:
  - Private key is loaded from .env and used ONLY for local signing
  - Key is never sent to any server or logged to output
  - Transaction is signed locally with `solders` library
"""

import argparse
import base64
import json
import os
import sys

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

load_dotenv(os.path.expanduser("~/.openclaw/workspace/.env"))

API_BASE = "https://wallet-data.kryptogo.app"
API_KEY = os.environ.get("KRYPTOGO_API_KEY")
WALLET = os.environ.get("SOLANA_WALLET_ADDRESS")
PRIVATE_KEY = os.environ.get("SOLANA_PRIVATE_KEY")

SOL_MINT = "So11111111111111111111111111111112"

if not all([API_KEY, WALLET, PRIVATE_KEY]):
    sys.exit("ERROR: Missing required env vars. Run scripts/setup.py first.")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="KryptoGO Swap Executor")
parser.add_argument("token_mint", help="Token mint address to buy or sell")
parser.add_argument(
    "amount",
    type=float,
    nargs="?",
    default=0.1,
    help="Amount in SOL (buy) or token units (sell). Default: 0.1 SOL",
)
parser.add_argument(
    "--sell",
    action="store_true",
    help="Sell tokens back to SOL (default is buy)",
)
parser.add_argument(
    "--slippage",
    type=int,
    default=300,
    help="Slippage tolerance in basis points (default: 300 = 3%%)",
)
parser.add_argument(
    "--max-impact",
    type=float,
    default=10.0,
    help="Max price impact %% before aborting (default: 10)",
)
args = parser.parse_args()

# ---------------------------------------------------------------------------
# Step 1: Build swap transaction
# ---------------------------------------------------------------------------

if args.sell:
    input_mint = args.token_mint
    output_mint = SOL_MINT
    # Need to fetch decimals to convert UI amount to raw units
    try:
        token_overview_resp = requests.get(
            f"{API_BASE}/token-overview",
            params={"address": args.token_mint},
            headers=HEADERS
        )
        if token_overview_resp.status_code == 200:
            decimals = token_overview_resp.json().get("decimals", 6)
        else:
            print(f"Warning: Could not fetch decimals (HTTP {token_overview_resp.status_code}). Defaulting to 6.")
            decimals = 6
    except Exception as e:
        print(f"Warning: Error fetching decimals: {e}. Defaulting to 6.")
        decimals = 6
        
    amount = int(args.amount * (10 ** decimals))
    print(f"=== SELL: {args.amount} {args.token_mint[:8]}... ({amount} raw units, decimals={decimals}) → SOL ===")
else:
    input_mint = SOL_MINT
    output_mint = args.token_mint
    amount = int(args.amount * 1_000_000_000)  # SOL → lamports
    print(f"=== BUY: {args.amount} SOL → {args.token_mint[:8]}... ===")

print("\nStep 1: Building swap transaction...")
swap_resp = requests.post(
    f"{API_BASE}/agent/swap",
    headers=HEADERS,
    json={
        "input_mint": input_mint,
        "output_mint": output_mint,
        "amount": amount,
        "slippage_bps": args.slippage,
        "wallet_address": WALLET,
    },
)

if swap_resp.status_code != 200:
    sys.exit(f"Swap build failed (HTTP {swap_resp.status_code}): {swap_resp.text}")

swap_data = swap_resp.json()
fee_payer = swap_data.get("fee_payer")
price_impact = float(swap_data.get("quote", {}).get("price_impact_pct", 0))

print(f"  Fee payer: {fee_payer}")
print(f"  Price impact: {price_impact}%")
print(f"  Platform fee: {swap_data.get('platform_fee_lamports', '?')} lamports")

# Verify fee payer matches our wallet
if fee_payer and fee_payer != WALLET:
    sys.exit(f"ABORT: Fee payer mismatch! Expected {WALLET}, got {fee_payer}")

# Check price impact
if price_impact > args.max_impact:
    sys.exit(f"ABORT: Price impact {price_impact}% exceeds max {args.max_impact}%")
elif price_impact > 5:
    print(f"  ⚠ WARNING: Price impact {price_impact}% is high (>5%)")

# ---------------------------------------------------------------------------
# Step 2: Sign locally
# ---------------------------------------------------------------------------

print("\nStep 2: Signing transaction locally...")
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

tx_bytes = base64.b64decode(swap_data["transaction"])
tx = VersionedTransaction.from_bytes(tx_bytes)
keypair = Keypair.from_base58_string(PRIVATE_KEY)
signed_tx = VersionedTransaction(tx.message, [keypair])
signed_tx_b64 = base64.b64encode(bytes(signed_tx)).decode()
print("  Signed successfully.")

# ---------------------------------------------------------------------------
# Step 3: Submit
# ---------------------------------------------------------------------------

print("\nStep 3: Submitting signed transaction...")
submit_resp = requests.post(
    f"{API_BASE}/agent/submit",
    headers=HEADERS,
    json={"signed_transaction": signed_tx_b64},
)

if submit_resp.status_code != 200:
    sys.exit(f"Submit failed (HTTP {submit_resp.status_code}): {submit_resp.text}")

result = submit_resp.json()
tx_hash = result.get("tx_hash", result.get("signature", "?"))
print(f"\n  Status: {result.get('status', '?')}")
print(f"  Tx Hash: {tx_hash}")
print(f"  Explorer: https://solscan.io/tx/{tx_hash}")
