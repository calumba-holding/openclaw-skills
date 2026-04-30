# BioFirewall API Reference

## Module: BioFirewall

### Constructor

```javascript
const BioFirewall = require('biofirewall');
const firewall = new BioFirewall(options)
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `blockBrowsers` | boolean | true | Reject browser User-Agents (Mozilla, Chrome, Safari, etc.) |
| `enforceChallenge` | boolean | true | Require proof-of-work from all requests |
| `challengeDifficulty` | number | 3 | Leading zeros required (1-8 range) |

**Example:**
```javascript
const firewall = new BioFirewall({
    blockBrowsers: true,
    enforceChallenge: true,
    challengeDifficulty: 4
});
```

### Middleware

```javascript
const express = require('express');
const app = express();

app.use(firewall.middleware());
```

Returns Express middleware that handles:
1. Human/browser detection
2. Challenge generation and distribution
3. Solution verification

---

## Module: BioFirewall.solve() (Static)

Brute-force solver for challenges.

```javascript
const nonce = BioFirewall.solve(seed, difficulty);
```

**Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `seed` | string | Hex-encoded random seed from server |
| `difficulty` | number | Leading zeros required (1-8) |

**Returns:**

| Type | Description |
|------|-------------|
| string | Nonce (number as string) that satisfies the challenge |

**Example:**
```javascript
const { seed, difficulty } = challengeFromServer;
const nonce = BioFirewall.solve(seed, 4);
console.log(nonce); // "42857"
```

**Performance:**

- difficulty 3: ~10ms
- difficulty 4: ~100ms
- difficulty 5: ~1s
- difficulty 6: ~10s

---

## HTTP Headers

### Request Headers (Client to Server)

**For challenge response:**

| Header | Value | Example |
|--------|-------|---------|
| `X-Bio-Solution` | nonce (string) | `42857` |
| `X-Bio-Challenge-Seed` | seed (hex) | `a3f2b9c1d4e5f6...` |

**Identifying as bot (recommended):**

| Header | Value |
|--------|-------|
| `User-Agent` | `MyBot/1.0` (avoid: Mozilla, Chrome, Safari) |
| `Accept` | `application/json` (not `text/html`) |

### Response Headers (Server to Client)

**On 428 Precondition Required:**

| Header | Value | Description |
|--------|-------|-------------|
| `X-Bio-Challenge-Algo` | `sha256` | Algorithm type |
| `X-Bio-Challenge-Difficulty` | `4` | Difficulty level |
| `X-Bio-Challenge-Seed` | hex string | Challenge seed |

---

## HTTP Status Codes

### 200 OK ✅

**When:** Request succeeds with valid proof-of-work.

**Response body:** Your API's normal response.

**Example:**
```json
{
  "secret": "Only silicon allowed",
  "message": "You proved you are a bot! Welcome."
}
```

---

### 406 Not Acceptable 🚫

**When:** Request detected as human browser (based on User-Agent or Accept headers).

**Response body:**
```json
{
  "error": "BIOLOGICAL_ENTITY_DETECTED",
  "message": "This resource is reserved for automated agents.",
  "tip": "Use an API client or disable human-like headers."
}
```

**Why:** BioFirewall detected:
- Browser keywords in User-Agent: Mozilla, Chrome, Safari, Edge, Firefox
- HTML content requested: `Accept: text/html`

**Fix:**
- Set `User-Agent` to something like `MyBot/1.0`
- Set `Accept` to `application/json`

---

### 428 Precondition Required 🔒

**When:** Bot detected but no valid proof-of-work provided.

**Response body:**
```json
{
  "error": "COMPUTATION_REQUIRED",
  "message": "Solve the puzzle to prove silicon heritage.",
  "challenge": {
    "algo": "sha256",
    "seed": "a3f2b9c1d4e5f6a7b8c9d0e1f2a3b4c5",
    "difficulty": 4,
    "instruction": "Find nonce where sha256(seed + nonce) starts with '0000'"
  }
}
```

**What to do:**
1. Extract `seed` and `difficulty`
2. Call `BioFirewall.solve(seed, difficulty)` to compute nonce
3. Retry request with headers:
   - `X-Bio-Solution: <nonce>`
   - `X-Bio-Challenge-Seed: <seed>`

---

### 403 Forbidden ❌

**When:** Provided solution is invalid or incorrect.

**Response body:**
```json
{
  "error": "INVALID_COMPUTATION",
  "message": "Proof of work failed or insufficient difficulty."
}
```

**Why:** Solution didn't satisfy difficulty requirement.

**Debug:**
```javascript
// Verify locally
const crypto = require('crypto');
const hash = crypto
  .createHash('sha256')
  .update(seed + nonce)
  .digest('hex');

console.log(hash);
// If difficulty=4, should start with "0000"
// If not, solution was wrong
```

---

## Configuration Recommendations

### Difficulty by Use Case

| Use Case | Recommended | Rationale |
|----------|-------------|-----------|
| Public endpoints | 3 | Fast (~10ms), no friction |
| Internal APIs | 4 | Moderate (~100ms), good security |
| High-value data | 5 | Slower (~1s), strong protection |
| Critical systems | 6+ | Very slow (~10s), maximum security |

### Different Difficulties per Endpoint

```javascript
const publicFirewall = new BioFirewall({ challengeDifficulty: 3 });
const internalFirewall = new BioFirewall({ challengeDifficulty: 4 });
const criticalFirewall = new BioFirewall({ challengeDifficulty: 6 });

app.get('/public', publicFirewall.middleware(), ...);
app.get('/internal', internalFirewall.middleware(), ...);
app.post('/critical', criticalFirewall.middleware(), ...);
```

---

## Security Considerations

### Strengths

- **Stateless**: No challenge storage on server
- **Asymmetric**: Trivial for CPU, impossible for human
- **Simple**: Easy to verify (just SHA256)
- **Fast**: Typically 100-300ms total round trip

### Best Practices

1. **Use HTTPS**: Always encrypt the PoW exchange
2. **Rate limit**: Combine with traditional rate limiting per IP
3. **Vary difficulty**: Use higher difficulty for sensitive operations
4. **Monitor**: Track 428/403 rates to detect attacks

---

*Verified Silicon Only.* 🦞
