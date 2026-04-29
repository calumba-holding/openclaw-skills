# SKILL.md — Lead Researcher by EdgeIQ Labs

**Version:** 1.0.0  
**Category:** Business Intelligence / Lead Generation  
**Author:** EdgeIQ Labs  
**Python:** 3.12+

---

## What It Does

Lead Researcher takes a company name, LinkedIn URL, or domain as input and returns enriched lead data including company size, industry, tech stack (Wappalyzer-style HTTP header/fingerprint detection), recent news, social links, and contact enrichment.

Output is structured JSON or human-readable formatted text. Pro tier adds CSV export.

---

## Pricing Tiers

| Feature | Free | **Lifetime ($39)** | Optional Monthly ($7/mo) |
|---------|------|----------------|----------------------|
| Lookups/month | 3 | Unlimited | Unlimited |
| Basic enrichment | ✅ | ✅ | ✅ |
| Tech stack detection | ✅ | ✅ | ✅ |
| News/press articles | — | ✅ | ✅ |
| Social links | — | ✅ | ✅ |
| Contact enrichment | — | Basic | Full |
| CSV export | ✅ | ✅ | ✅ |
| Priority support | ✅ | ✅ | ✅ |

---



👉 [Buy Lifetime — $39](https://buy.stripe.com/8x25kF3XJeJD07GbMQ7wA0X)
👉 [Subscribe Monthly — $7/mo](https://buy.stripe.com/dRm8wR79V9pj7A89EI7wA12)
👉 [Subscribe Monthly — $7/mo](https://buy.stripe.com/dRm8wR79V9pj7A89EI7wA12)
## Usage

```bash
python3 /path/to/lead_researcher.py "Acme Corp"
python3 /path/to/lead_researcher.py "https://www.linkedin.com/company/acme-corp"
python3 /path/to/lead_researcher.py "acme.com"
python3 /path/to/lead_researcher.py "acme.com" --format json
python3 /path/to/lead_researcher.py "acme.com" --format csv --output acme_leads.csv
python3 /path/to/lead_researcher.py "acme.com" --tier pro
```

### Arguments
- `input` — Company name, LinkedIn URL, or domain
- `--format` — Output format: `text` (default) or `json`
- `--output` — File path for CSV export (Pro tier)
- `--tier` — Tier override: `free`, `pro`, or `bundle` (default: free behavior)
- `--tavily-key` — Override Tavily API key (defaults to env `TAVILY_API_KEY`)

---

## Legal Notice

> ⚠️ **Only research companies you have legitimate business interest in. Do not use for spam or unsolicited contact.** This tool aggregates publicly available information. Respect robots.txt and terms of service of scraped sources.

---

## Tech Stack Detection

The skill performs passive HTTP-based tech fingerprinting:
1. Makes HTTP/HTTPS requests to the target domain
2. Inspects HTTP headers (Server, X-Powered-By, CF-* headers, etc.)
3. Checks for common JavaScript framework meta tags in HTML
4. Looks at default paths (favicon, /wp-login.php, /.well-known/, etc.)
5. Compares headers and patterns against a built-in signature database

No active scanning. No port probes. Passive reconnaissance only.

---

## Output Schema

```json
{
  "company": "Acme Corp",
  "domain": "acme.com",
  "size": "50-200",
  "industry": "Software",
  "description": "...",
  "tech_stack": ["WordPress", "Cloudflare", "Google Analytics", "Stripe"],
  "news": [{"title": "...", "url": "...", "date": "..."}],
  "social": {"linkedin": "...", "twitter": "...", "facebook": "..."},
  "contacts": [{"name": "...", "title": "...", "linkedin": "..."}],
  "lookup_date": "2026-04-23"
}
```

---

## 🔗 More from EdgeIQ Labs

**edgeiqlabs.com** — Security tools, OSINT utilities, and micro-SaaS products for developers and security professionals.

- 🛠️ **Subdomain Hunter** — Passive subdomain enumeration via Certificate Transparency
- 📸 **Screenshot API** — URL-to-screenshot API for developers
- 🔔 **uptime.check** — URL uptime monitoring with alerts
- 🛡️ **headers.check** — HTTP security headers analyzer

👉 [Visit edgeiqlabs.com →](https://edgeiqlabs.com)
