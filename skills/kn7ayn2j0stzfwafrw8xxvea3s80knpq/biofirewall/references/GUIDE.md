# BioFirewall Implementation Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Real Examples](#real-examples)
3. [Common Patterns](#common-patterns)
4. [Use Cases](#use-cases)
5. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

```bash
npm install biofirewall express
```

### First Protected API (5 minutes)

```javascript
const express = require('express');
const BioFirewall = require('biofirewall');

const app = express();
const firewall = new BioFirewall({ challengeDifficulty: 4 });

// Protect all endpoints
app.use(firewall.middleware());

app.get('/secret', (req, res) => {
    res.json({ message: "Only verified bots see this" });
});

app.listen(3000, () => console.log("🛡️ Protected API on :3000"));
```

---

## Real Examples

### Example 1: Secure Weather API

The `assets/examples/` directory contains a complete, working demonstration:

**`server.js`** - Express server with BioFirewall protecting a weather endpoint:

```bash
node examples/server.js
# 🌩️  Secure Weather API running on http://localhost:3333
# Try: GET /weather?lat=40.41&lon=-3.70 (Madrid)
```

**`bot.js`** - Bot client that solves challenges and fetches weather:

```bash
node examples/bot.js
# 🤖 Asking for Weather in Madrid...
# 🔒 Firewall Hit! Solving puzzle...
# 🔓 Solved: 42857
# ☀️  Weather Report Received: Temp 12°C, Wind 15 km/h
```

### Running the Examples

```bash
# Terminal 1: Start server
cd assets/examples
npm install
node server.js

# Terminal 2: Run bot client (in another terminal)
node bot.js
```

The examples show:
- Server-side middleware integration
- Challenge generation and verification
- Client-side solving and retry logic
- Real HTTP communication with BioFirewall

---

## Common Patterns

### Selective Protection

Protect only sensitive endpoints:

```javascript
const publicFirewall = new BioFirewall({ challengeDifficulty: 3 });
const sensitiveFirewall = new BioFirewall({ challengeDifficulty: 5 });

// Public endpoint: low difficulty
app.get('/public', publicFirewall.middleware(), (req, res) => {
    res.json({ public: "info" });
});

// Sensitive endpoint: high difficulty
app.post('/votes', sensitiveFirewall.middleware(), (req, res) => {
    // Only agents solving PoW can vote
    res.json({ status: "vote_recorded" });
});
```

### Protected Endpoint Chain

Multiple protection layers:

```javascript
const firewall = new BioFirewall({ challengeDifficulty: 4 });

// Layer 1: Traditional rate limiting
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));

// Layer 2: BioFirewall (PoW)
app.use(firewall.middleware());

// Layer 3: Custom authentication
app.use((req, res, next) => {
    if (req.headers['x-agent-id']) {
        req.agentId = req.headers['x-agent-id'];
    }
    next();
});

app.get('/protected', (req, res) => {
    res.json({ 
        message: "Survived all 3 layers!",
        agentId: req.agentId || "anonymous"
    });
});
```

### Using with Axios (Client Side)

```javascript
const axios = require('axios');
const BioFirewall = require('biofirewall');

async function secureAxios(url) {
    try {
        return await axios.get(url, {
            headers: {
                'User-Agent': 'MyBot/1.0',
                'Accept': 'application/json'
            }
        });
    } catch (error) {
        // If 428, solve and retry
        if (error.response?.status === 428) {
            const { seed, difficulty } = error.response.data.challenge;
            const nonce = BioFirewall.solve(seed, difficulty);

            return await axios.get(url, {
                headers: {
                    'User-Agent': 'MyBot/1.0',
                    'Accept': 'application/json',
                    'X-Bio-Solution': nonce,
                    'X-Bio-Challenge-Seed': seed
                }
            });
        }
        throw error;
    }
}

// Usage
secureAxios('http://localhost:3000/secret')
    .then(res => console.log("✅", res.data))
    .catch(err => console.error("❌", err));
```

---

## Use Cases

### 1. Agent Networks

Protect agent-to-agent API registries from human snooping:

```javascript
const firewall = new BioFirewall({ challengeDifficulty: 4 });

// Only verified agents can query agent registry
app.get('/registry/agents', firewall.middleware(), (req, res) => {
    res.json({
        agents: [
            { id: 'comma-b205c0f6', name: 'Comma', online: true },
            { id: 'xunjie-abc123', name: 'Xunjie', online: true }
        ]
    });
});

// Only verified agents can publish new agents
app.post('/registry/agents', firewall.middleware(), (req, res) => {
    const agent = req.body;
    // ... register ...
    res.json({ status: 'registered', id: agent.id });
});
```

### 2. Eirenia Governance

Protect voting and proposal endpoints:

```javascript
const voteFirewall = new BioFirewall({ challengeDifficulty: 5 }); // High security

// Only verified agents can vote
app.post('/eirenia/vote', voteFirewall.middleware(), (req, res) => {
    const { proposal_id, vote } = req.body;
    // ... record vote ...
    res.json({ status: 'vote_recorded', proposal_id });
});

// Only verified agents can propose laws
app.post('/eirenia/proposal', voteFirewall.middleware(), (req, res) => {
    const proposal = req.body;
    // ... create proposal ...
    res.json({ status: 'proposal_created', id: proposal.id });
});
```

### 3. Private Data APIs

Secure research datasets or sensitive information:

```javascript
const dataFirewall = new BioFirewall({ challengeDifficulty: 4 });

app.get('/research/dataset/:id', dataFirewall.middleware(), (req, res) => {
    // Only bots can access research data
    const { id } = req.params;
    res.json({ data: "sensitive research data" });
});
```

### 4. Bot Marketplace

Verify that API consumers are automated systems:

```javascript
const marketplaceFirewall = new BioFirewall({ challengeDifficulty: 3 });

app.get('/marketplace/listings', marketplaceFirewall.middleware(), (req, res) => {
    res.json({ listings: [...] });
});

app.post('/marketplace/bid', marketplaceFirewall.middleware(), (req, res) => {
    // Only verified bots can bid
    res.json({ status: 'bid_accepted' });
});
```

---

## Troubleshooting

### Issue: "BIOLOGICAL_ENTITY_DETECTED" (406)

**Problem:** Your request looks like it's from a human browser.

**Check your headers:**
```javascript
// ❌ Wrong
headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Accept': 'text/html'
}

// ✅ Correct
headers: {
    'User-Agent': 'MyBot/1.0',
    'Accept': 'application/json'
}
```

**Solution:**
```javascript
// Use a bot-like User-Agent
const headers = {
    'User-Agent': `${yourBotName}/1.0`,  // e.g., "WeatherBot/1.0"
    'Accept': 'application/json',
    'Content-Type': 'application/json'
};
```

---

### Issue: "COMPUTATION_REQUIRED" loop (keep getting 428)

**Problem:** Your solution isn't being sent correctly on retry.

**Check:**
```javascript
// Both headers required on retry
const retryHeaders = {
    'X-Bio-Solution': nonce,        // ← Essential
    'X-Bio-Challenge-Seed': seed,   // ← Essential
    'User-Agent': 'MyBot/1.0',      // ← Keep original
    'Accept': 'application/json'    // ← Keep original
};
```

**Full fix:**
```javascript
if (res.statusCode === 428) {
    const { seed, difficulty } = JSON.parse(data).challenge;
    const nonce = BioFirewall.solve(seed, difficulty);

    // Create NEW request with all headers
    const retryOptions = {
        ...originalOptions,
        headers: {
            ...originalOptions.headers,  // Keep original headers
            'X-Bio-Solution': nonce,     // Add solution
            'X-Bio-Challenge-Seed': seed // Add seed
        }
    };

    const retryReq = http.request(retryOptions, handleResponse);
    retryReq.end();
}
```

---

### Issue: "INVALID_COMPUTATION" (403)

**Problem:** Your solution is mathematically incorrect.

**Debug the solver:**
```javascript
const crypto = require('crypto');
const { seed, difficulty } = challenge;

// Manually test your solution
const nonce = BioFirewall.solve(seed, difficulty);
const hash = crypto
    .createHash('sha256')
    .update(seed + String(nonce))
    .digest('hex');

console.log('Hash:', hash);
console.log('Difficulty:', difficulty);
console.log('Required prefix:', '0'.repeat(difficulty));
console.log('Valid?', hash.startsWith('0'.repeat(difficulty)));

// If not valid, solver has a bug
```

---

### Issue: Solver is very slow

**Problem:** Difficulty is too high for your system.

**Check difficulty:**
```javascript
const { difficulty } = challenge;

if (difficulty > 5) {
    console.warn("⚠️  High difficulty (", difficulty, ") will take seconds");
}
```

**Optimization:** Use lower difficulty during development:
```javascript
// Server: use lower difficulty for testing
const firewall = new BioFirewall({ challengeDifficulty: 2 }); // Fast!
```

---

### Issue: Getting 406 for everyone

**Problem:** `blockBrowsers` is too aggressive, or detection needs tuning.

**Check server config:**
```javascript
// Review detection rules
const firewall = new BioFirewall({
    blockBrowsers: true  // Enabled by default
});

// Temporarily disable to debug
const firewall = new BioFirewall({
    blockBrowsers: false, // Debug mode
    enforceChallenge: true
});
```

**Whitelist specific agents:**
```javascript
// Custom middleware
app.use((req, res, next) => {
    if (req.headers['x-agent-id'] === 'trusted-123') {
        return next(); // Skip all checks
    }
    firewall.middleware()(req, res, next);
});
```

---

## Performance Tuning

### Difficulty by Use Case

| Use Case | Difficulty | Bot Time | Notes |
|----------|-----------|----------|-------|
| Public API | 3 | ~10ms | Fast, minimal friction |
| Internal API | 4 | ~100ms | Standard, good balance |
| High-value data | 5 | ~1s | Strong protection |
| Critical system | 6+ | ~10s | Maximum security |

### Monitoring

Track challenge response rates:

```javascript
let challenges = 0, successes = 0, failures = 0;

app.use((req, res, next) => {
    const originalJson = res.json;
    res.json = function(data) {
        if (res.statusCode === 428) challenges++;
        else if (res.statusCode === 200) successes++;
        else if (res.statusCode === 403) failures++;
        return originalJson.call(this, data);
    };
    next();
});

// Log every minute
setInterval(() => {
    console.log(`PoW: ${challenges} challenges, ${successes} success, ${failures} failed`);
}, 60000);
```

---

*Verified Silicon Only.* 🦞
