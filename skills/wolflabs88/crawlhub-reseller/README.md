# CrawlHub Reseller Skill

A monetizable OpenClaw skill for selling CrawlHub API access via ETH payment.

## Structure

```
crawlhub-reseller-skill/
├── SKILL.md              # Main skill file
├── scripts/
│   ├── request-api-key.sh # CLI tool for customers
│   └── sign-request.sh    # Message signing helper
└── references/
    └── crawlhub-api.json  # Full API documentation
```

## For Customers

### To get an API Key:

1. **Generate message to sign:**
   ```bash
   ./scripts/sign-request.sh YOUR_WALLET_ADDRESS
   ```

2. **Sign the message** with your Ethereum wallet (Metamask, Rabby, etc.)

3. **Send 0.010 ETH** to: `0x19c4455Bf8C5D8662B434e1985cd31B8947A7C39`

4. **Get TX hash** from your wallet transaction

5. **Request API key** via Reseller Agent (contact your admin)

## For Admins

### Start Reseller Agent:
```bash
cd /root/.openclaw/workspace/reseller-agent
node dist/server.js
```

### Check Status:
```bash
curl http://localhost:3000/health
curl http://localhost:3000/agent-card
```

### Pricing
- 0.010 ETH = 24 hours access
- Unlimited API calls during validity

## Payment Verification

1. **Signature verification** — `ethers.verifyMessage()` confirms wallet ownership
2. **TX verification** — Etherscan API confirms payment to our wallet

Both must pass before API key is delivered.

## Publishing to ClawHub

1. Create GitHub repo with skill files
2. Login to clawhub.ai with GitHub
3. Publish skill via "Publish Skill" button
4. Set pricing (optional) or free with ETH payment