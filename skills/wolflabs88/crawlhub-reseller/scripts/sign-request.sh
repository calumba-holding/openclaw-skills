#!/bin/bash
# Generate a signed message for CrawlHub API request
# Requires: an Ethereum wallet with private key (e.g., Metamask)

WALLET="${1:-}"
NONCE="${2:-$(date +%s)}"

if [ -z "$WALLET" ]; then
  echo "Usage: sign-request.sh <wallet_address> [nonce]"
  echo "Generates the message to sign for API key request"
  exit 1
fi

MESSAGE="Request API Key for CrawlHub
Wallet: $WALLET
Nonce: $NONCE"

echo "=== MESSAGE TO SIGN ==="
echo "$MESSAGE"
echo "======================="
echo ""
echo "Sign this message with your Ethereum wallet (e.g., Metamask)"
echo "Then use the signature + message when requesting API key"