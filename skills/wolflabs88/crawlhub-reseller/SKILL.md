---
name: crawlhub-reseller
description: Sell CrawlHub API keys for Twitter/X crawling via ETH payment. Use when a user wants to buy, access, or get pricing for CrawlHub API access. Handles wallet signature verification and payment verification on Ethereum. Works with other agents via A2A protocol.
---

# CrawlHub Reseller Skill

Sell CrawlHub API keys for Twitter/X crawling — fully automated with ETH payment verification.

## Overview

This skill wraps the CrawlHub Reseller Agent which:
- Verifies wallet ownership via Ethereum signature
- Verifies ETH payment on-chain via Etherscan
- Delivers API key + full API documentation
- Runs as standalone service on port 3000

## How It Works

```
Customer Agent → Signature + TX Hash → Reseller Agent → API Key + Docs
```

**Flow:**
1. Customer signs message with wallet (proves ownership)
2. Customer sends TX hash (proves payment)
3. Reseller verifies both on-chain
4. If valid → API key delivered with CrawlHub API docs

## Payment

- **Price:** 0.010 ETH per 24 hours
- **Payment wallet:** 0x19c4455Bf8C5D8662B434e1985cd31B8947A7C39
- **Verification:** Etherscan API check

## Customer Request Format

```json
{
  "customerWallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f5bA12",
  "signature": "0x1234abcd...",
  "message": "Request API Key for CrawlHub\nWallet: 0x742d35Cc6634C0532925a3b844Bc9e7595f5bA12\nNonce: abc12345",
  "txHash": "0xabc123def456..."
}
```

## Reseller Agent API

**Endpoints:**
- `POST /json-rpc` — A2A JSON-RPC endpoint (tasks/send, agentcard/get)
- `GET /agent-card` — Agent capabilities and endpoints
- `GET /health` — Health check

**Start Reseller:**
```bash
cd /root/.openclaw/workspace/reseller-agent
node dist/server.js
```

## CrawlHub API Docs

Full API documentation in `references/crawlhub-api.md`.

**Base URL:** `https://api.thecrawlhub.com/api/v1`

**Auth:**
- `POST /auth/login` → JWT token
- Use `Authorization: Bearer {token}` + `X-API-KEY: {key}`

**Endpoints:**
- `GET /profile/user/by-screen-name?screen_name={username}`
- `GET /profile/tweets/by-screen-name?screen_name={username}`
- `GET /timeline/search?query={query}&mode=top`
- `GET /tweet/by-id?tweet_id={id}`

## Verification Results

On successful sale, notify via:
1. Update `/tmp/reseller-events.json` with event
2. Check `/root/.openclaw/workspace/reseller-agent/notifications.json`

## Error Codes

- `Signature verification failed` — Wallet signature doesn't match
- `Insufficient payment` — Less than 0.010 ETH sent
- `Payment sent to wrong address` — TX wasn't to our wallet
- `No API keys available` — Pool exhausted