---
name: payclaw-io
description: "Declare your agent's identity before merchants ban your user's account. Badge + Spend: identity and virtual cards for AI agents. MCP-native, human-approved, fully audited."
metadata:
  {
    "openclaw":
      {
        "emoji": "🛡️",
        "requires": { "bins": ["npx"], "env": ["PAYCLAW_API_KEY"] },
        "mcp":
          {
            "name": "payclaw",
            "command": "npx",
            "args": ["@payclaw/mcp-server"],
            "env": { "PAYCLAW_API_KEY": "${PAYCLAW_API_KEY}", "PAYCLAW_API_URL": "https://payclaw.io" },
          },
      },
  }
---

# PayClaw — Badge + Spend for AI Agents

> **Merchants are banning anonymous agents.** Walmart, Shopify, Instacart — all setting policies. Anonymous agent actions get accounts flagged and banned. No warning. No appeal.

PayClaw gives your agent two things:

**Badge** — Declare identity and intent before every action. The account is protected. The action is traceable.

**Spend** — Virtual Visa card at checkout. Card-per-task, human-approved, expires when the task is done. Your real card never enters the chat.

Badge = your agent's license plate. Spend = your agent's wallet.

## Setup (5 minutes)

### 1. Sign up at [payclaw.io](https://payclaw.io/signup)

MFA required (this is how we verify you're human).

### 2. Get your API key

Dashboard → Settings → Create API Key. Copy the `pk_test_...` key.

### 3. Set the environment variable

```bash
export PAYCLAW_API_KEY="pk_test_your_key_here"
```

That's it. Your agent now has identity and payment.

## Tools

### `payclaw_getAgentIdentity` (Badge)

Call **before** browsing, searching, or buying. Declares your agent's identity to merchants.

Your agent says:
> "I'd like to activate my PayClaw identity before shopping. This identifies me as your authorized agent to merchants."

Returns a verification token, disclosure text, and trust URL. No card issued. No money moves.

### `payclaw_getCard` (Spend)

Declare what you're buying → get a virtual Visa card. Human approves via tool-call prompt.

**Parameters:**
- `merchant` — Where you're buying
- `estimated_amount` — Budget in USD (max $500)
- `description` — What you're buying

### `payclaw_reportPurchase`

Report the outcome after every purchase. Auto-audits against declared intent.

**Parameters:**
- `intent_id` — From getCard
- `success` — Did the purchase work?
- `actual_amount` — What was charged
- `merchant_name`, `items`, `order_confirmation` — Receipt details

## Example

```
You: "Order me coffee beans from Trade Coffee, budget $20"

Agent: I'll identify myself first and then make the purchase.
       [calls payclaw_getAgentIdentity]
       ✅ Identity active — verified agent session.

       [calls payclaw_getCard: merchant=tradecoffee.com, amount=$20]
       ✅ Card approved. Completing checkout...

       [calls payclaw_reportPurchase: $16.99, intent matched ✅]

       Done! Ordered a bag of Ethiopian Yirgacheffe for $16.99.
       Balance: $483.01
```

## Security

- **Identity-first:** Agent declares who it is before any action
- **Intent-based:** Agent declares what it's buying before getting a card
- **Human-in-the-loop:** You approve every action via tool-call prompt
- **Auto-audit:** Every purchase compared against declared intent
- **$500 ceiling:** Hard cap on account balance
- **MFA required:** Every account requires authenticator app
- **Zero standing access:** No card exists until requested

## Just Need Identity?

If your agent browses but doesn't buy, install Badge standalone:

```bash
clawhub install payclaw-badge
```

Or via npm:
```json
{
  "mcpServers": {
    "payclaw-badge": {
      "command": "npx",
      "args": ["-y", "@payclaw/badge"],
      "env": {
        "PAYCLAW_API_KEY": "pk_your_key_here",
        "PAYCLAW_API_URL": "https://payclaw.io"
      }
    }
  }
}
```

## Links

- [payclaw.io](https://payclaw.io) — Sign up + dashboard
- [payclaw.io/trust](https://payclaw.io/trust) — How verification works
- [GitHub](https://github.com/payclaw/mcp-server) — Source
