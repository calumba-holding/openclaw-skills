# Dark Web Credential Checker

**Skill Name:** `dark-web-credential-checker`
**Version:** `1.0.0`
**Category:** OSINT / Breach Monitoring
**Price:** **Lifetime: $39** / Optional Monthly: $7/mo (includes all Pro features permanently)
**Author:** EdgeIQ Labs
**OpenClaw Compatible:** Yes — Python 3, pure stdlib + requests, WSL + Linux

---

## What It Does

Checks whether an email address or username has appeared in known data breaches and dark web exposures. Searches public breach databases and paste sites, extracts exposed records, and reports on the types of data leaked (passwords, personal info, payment data, etc.).

> ⚠️ **Legal Notice:** This tool queries public breach databases and dark web monitoring services. Do not use it for unauthorized access or to stalk others. For personal use only.

---

## Features

- **Email breach search** — check if an email appears in known breaches
- **Username lookup** — search across breach compilations by username/handle
- **Breach source identification** — lists which sites/services were compromised
- **Exposed data classification** — categorizes what was exposed (passwords, emails, PII, payment data)
- **Date of breach** — shows when the breach occurred
- **Password hash detection** — identifies if cracked password hashes were exposed
- **JSON export** — structured report for personal records or security audits

---

## Tier Comparison

| Feature | Free | **Lifetime ($39)** | Optional Monthly ($7/mo) |
|---------|------|----------------|----------------------|
| Email breach check | ✅ (3 emails) | ✅ (unlimited) | ✅ (unlimited) |
| Username search | ✅ | ✅ | ✅ |
| Full breach source report | ✅ | ✅ | ✅ |
| Exposed data classification | ✅ | ✅ | ✅ |
| Password hash detection | ✅ | ✅ | ✅ |
| JSON export | ✅ | ✅ | ✅ |
| Dark web monitoring (monthly) | ✅ | ✅ | ✅ |

---

## Installation

```bash
cp -r /home/guy/.openclaw/workspace/apps/dark-web-credential-checker ~/.openclaw/skills/dark-web-credential-checker
```

---

## Usage

### Basic email check (free tier)

```bash
python3 credential_checker.py --email "your_email@example.com"
```

### Pro username + breach source search

```bash
EDGEIQ_EMAIL=your_email@gmail.com python3 credential_checker.py \
  --email "your_email@example.com" \
  --username "johndoe" \
  --pro
```

### Full bundle scan with JSON report

```bash
EDGEIQ_EMAIL=your_email@gmail.com python3 credential_checker.py \
  --email "your_email@example.com" \
  --bundle --output breach-report.json
```

### As OpenClaw Discord Command

In `#edgeiq-support` channel:
```
!breach user@example.com
!breach user@example.com --pro
!breach user@example.com --username johndoe --bundle
```

---

## Parameters

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--email` | string | — | Email address to check |
| `--username` | string | — | Username/handle to search |
| `--pro` | flag | False | Enable Pro features |
| `--bundle` | flag | False | Enable Bundle features |
| `--output` | string | — | Write JSON report to file |
| `--timeout` | int | 15 | Request timeout (seconds) |

---

## Output Example

```
=== Dark Web Credential Checker ===
Query: user@example.com

  [1m[91m🔴 BREACH FOUND — 4 exposures detected[0m

  [1m[91m🔴[0m Site: Adobe (2013)
    Exposed: Email, encrypted password, username
    Severity: HIGH — password hash exposed
    Date: Nov 2013

  [1m[93m🟡[0m Site: LinkedIn (2016)
    Exposed: Email, password (bcrypt)
    Severity: HIGH — 117M accounts sold online
    Date: May 2016

  [1m[93m🟡[0m Site: AdultFriendFinder (2016)
    Exposed: Email, username, IP address
    Severity: MEDIUM
    Date: May 2016

  [1m[92m✔[0m No breaches detected for username: johndoe

  Recommendation: Change password on all 4 affected accounts.
    Especially: Adobe and LinkedIn (passwords were cracked and sold)

  Threat Level: CRITICAL — 2 high-severity password exposures found
```

---

## Pricing

**Lifetime License: $39** — your tool forever, all features included permanently.
**Optional Monthly: $7/mo** — for those who prefer recurring billing (cancel anytime).
👉 [Buy Lifetime — $39](https://buy.stripe.com/28EbJ31PBcBv1bK7wA7wA0U)
👉 [Subscribe Monthly — $7/mo](https://buy.stripe.com/6oU00leCn7hb4nWg367wA1b)
👉 [Subscribe Monthly — $7/mo](https://buy.stripe.com/6oU00leCn7hb4nWg367wA1b)

## Pro Upgrade *(deprecated)*
All features now included in Lifetime purchase.

---

## Data Sources

Public breach databases including (but not limited to):
- Have I Been Pwned (HIBP) API
- Leak detection from public paste bins
- Known breach compilations (DeHashed, LeakCheck, etc.)

---

## Support

Open a ticket in [#edgeiq-support](https://discord.gg/PaP7nsFUJT) or email [gpalmieri21@gmail.com](mailto:gpalmieri21@gmail.com)

---

## 🔗 More from EdgeIQ Labs

**edgeiqlabs.com** — Security tools, OSINT utilities, and micro-SaaS products for developers and security professionals.

- 🛠️ **Subdomain Hunter** — Passive subdomain enumeration via Certificate Transparency
- 📸 **Screenshot API** — URL-to-screenshot API for developers
- 🔔 **uptime.check** — URL uptime monitoring with alerts
- 🛡️ **headers.check** — HTTP security headers analyzer

👉 [Visit edgeiqlabs.com →](https://edgeiqlabs.com)
