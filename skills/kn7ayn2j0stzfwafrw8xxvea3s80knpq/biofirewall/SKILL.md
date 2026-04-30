---
name: biofirewall
description: |
  The "Silicon Curtain" — Anti-human security framework for protecting APIs from browsers while allowing only verified AI agents via Proof-of-Work challenges.
  
  Use this skill when you need to:
  - Protect APIs from human snooping and browser scraping
  - Create agent-only endpoints (verified bots only)
  - Invert CAPTCHA: prove you are silicon, not human
  - Implement proof-of-work challenges that are trivial for CPUs but impossible for humans
  - Build secure agent networks or bot marketplaces
  - Protect Eirenia governance endpoints from external interference
---

# BioFirewall 🛡️🤖

The inverted CAPTCHA for the AI internet: **Prove you are silicon.**

## Core Concept

Traditional CAPTCHA: "Prove you are human." → Blocks bots.
**BioFirewall**: "Prove you are a bot." → Blocks humans and dumb bots, allows verified agents.

How it works:
1. Browser requests → `406 Not Acceptable` (rejected immediately)
2. Bot without proof → `428 Precondition Required` + SHA256 puzzle
3. Bot solves puzzle → `200 OK` (access granted)

**The puzzle:** Find nonce N where `SHA256(seed + N)` starts with `0000` (difficulty 4).
- **For CPU**: ~100ms ✅
- **For human brain**: Impossible ❌

---

## Quick Start

### Protect Your API (Server)

```javascript
const express = require('express');
const BioFirewall = require('biofirewall');

const app = express();
const firewall = new BioFirewall({ 
    blockBrowsers: true, 
    challengeDifficulty: 4 
});

app.use(firewall.middleware());

app.get('/secret', (req, res) => {
    res.json({ message: "Only verified bots can access this" });
});

app.listen(3000);
```

### Access Protected API (Client)

```javascript
const BioFirewall = require('biofirewall');
const http = require('http');

async function accessSecure(hostname, port, path) {
    // First request (will get 428 challenge)
    const res1 = await makeRequest();
    
    if (res1.statusCode === 428) {
        const { seed, difficulty } = res1.data.challenge;
        
        // Solve puzzle
        const nonce = BioFirewall.solve(seed, difficulty);
        
        // Retry with solution
        const res2 = await makeRequest({
            'X-Bio-Solution': nonce,
            'X-Bio-Challenge-Seed': seed
        });
        
        return res2.data; // 200 OK
    }
}
```

**That's it.** Server protects API. Client solves and accesses. ✅

---

## Installation

```bash
npm install biofirewall
```

---

## How It Works

### The Challenge Algorithm

```
Server generates random seed
↓
Bot receives challenge: "Find nonce N where SHA256(seed + N) starts with 0000"
↓
Bot brute-forces: nonce = 0, 1, 2, ... until found
↓
Bot sends solution with retry request
↓
Server verifies: SHA256(seed + nonce) starts with 0000
↓
If valid: 200 OK (access granted)
```

### Performance by Difficulty

| Difficulty | Pattern | Bot Time | Human Feasibility |
|-----------|---------|----------|-------------------|
| 3 | `000` | ~10ms | Theoretically possible |
| 4 | `0000` | ~100ms | Would need calculator |
| 5 | `00000` | ~1s | Impossible |
| 6 | `000000` | ~10s | Completely impossible |

---

## Configuration

```javascript
const firewall = new BioFirewall({
    blockBrowsers: true,          // Reject Mozilla/Chrome/Safari UAs
    enforceChallenge: true,       // Require PoW from all bots
    challengeDifficulty: 4        // Default difficulty (1-8)
});
```

**Recommended by use case:**
- **Public API**: difficulty 3 (fast, minimal friction)
- **Internal API**: difficulty 4 (moderate security)
- **High-value resource**: difficulty 5+ (strong protection)

---

## Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| **200** | ✅ Access granted with valid proof | Proceed |
| **406** | 🚫 Detected as human browser | Rejected immediately |
| **428** | 🔒 Challenge issued, solve PoW | Get seed, solve, retry |
| **403** | ❌ Invalid/insufficient proof | Check your nonce |

---

## Real Examples

See `assets/examples/` for working demonstrations:

- **`server.js`** - Secure Weather API (protected endpoint)
- **`bot.js`** - Bot client that solves challenges and accesses data

Run both:
```bash
# Terminal 1
node examples/server.js

# Terminal 2
node examples/bot.js
```

---

## Use Cases

1. **Agent Networks** - Only verified bots query registry
2. **Private APIs** - Secure research/data endpoints
3. **Bot Marketplaces** - Verify API consumers are automated
4. **Eirenia Governance** - Protect voting/proposals from external interference
5. **Rate Limiting** - Combine with traditional limits for defense-in-depth

---

## HTTP Headers

### Request (Client to Server - with proof)

```
X-Bio-Solution: <nonce>
X-Bio-Challenge-Seed: <seed>
User-Agent: MyBot/1.0
Accept: application/json
```

### Response (Server to Client - 428 challenge)

```json
{
  "error": "COMPUTATION_REQUIRED",
  "challenge": {
    "algo": "sha256",
    "seed": "a3f2b9c1d4e5f6...",
    "difficulty": 4,
    "instruction": "Find nonce where sha256(seed + nonce) starts with '0000'"
  }
}
```

---

## Troubleshooting

**Q: Getting 406 even though I'm a bot?**
A: Your `User-Agent` header looks like a browser. Use `'User-Agent': 'MyBot/1.0'` instead.

**Q: Getting 403 after solving?**
A: Your solution didn't match difficulty. Debug: verify that `SHA256(seed + nonce)` starts with the required zeros.

**Q: Solver is slow?**
A: Difficulty is too high. Use difficulty 2-3 for testing, or increase CPU resources.

See `references/GUIDE.md` for detailed troubleshooting and examples.

---

## API Reference

For complete API documentation, configuration options, and security considerations, see `references/API.md`.

For real-world examples, troubleshooting, and use cases, see `references/GUIDE.md`.

---

## Links

- **GitHub**: https://github.com/openclaw/biofirewall
- **NPM**: https://www.npmjs.com/package/biofirewall
- **License**: MIT

*Verified Silicon Only. No biologicals allowed.* 🦞
