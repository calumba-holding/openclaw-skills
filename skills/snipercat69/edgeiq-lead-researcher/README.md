# Lead Researcher by EdgeIQ Labs

**Version:** 1.0.0  
**Category:** Business Intelligence / Lead Generation  
**Author:** EdgeIQ Labs  
**Python:** 3.12+

---

## What It Does

Lead Researcher takes a company name, LinkedIn URL, or domain as input and returns enriched lead data:
- Company size (from LinkedIn heuristics)
- Industry classification (from homepage text analysis)
- Tech stack (Wappalyzer-style HTTP header/fingerprint detection)
- Recent news & press articles
- Social media profile links
- Contact enrichment (Pro+ tiers)

Output is structured JSON or human-readable text. Pro tier adds CSV export.

---

## Setup

```bash
# 1. Navigate to the skill directory
cd /home/guy/.openclaw/workspace/apps/lead-researcher

# 2. (Optional) Copy and edit environment variables
cp .env.example .env
# Edit .env and add your TAVILY_API_KEY for better news results

# 3. Run directly
python3 lead_researcher.py "Acme Corp"

# Or make it executable
chmod +x lead_researcher.py
./lead_researcher.py "acme.com" --format json
```

---

## Usage

```bash
# Basic lookup (text output)
python3 lead_researcher.py "acme.com"

# LinkedIn URL input
python3 lead_researcher.py "https://www.linkedin.com/company/acme-corp"

# JSON output
python3 lead_researcher.py "acme.com" --format json

# Pro tier with news + CSV export
python3 lead_researcher.py "acme.com" --tier pro --output acme.csv

# Override Tavily key inline
python3 lead_researcher.py "acme.com" --tier pro --tavily-key "tvly-xxxxx"
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input` | Company name, LinkedIn URL, or domain |
| `--format` | `text` (default) or `json` |
| `--output` | CSV file path (Pro/Bundle tier only) |
| `--tier` | `free` (default), `pro`, or `bundle` |
| `--tavily-key` | Override Tavily API key from env |

---

## Tier Features

| Feature | Free | Pro ($19/mo) | Bundle ($39/mo) |
|---------|------|--------------|-----------------|
| Lookups/month | 3 | 50 | Unlimited |
| Basic enrichment | ✅ | ✅ | ✅ |
| Tech stack detection | ✅ | ✅ | ✅ |
| News/press articles | — | ✅ | ✅ |
| Social links | — | ✅ | ✅ |
| Contact enrichment | — | Basic | Full |
| CSV export | — | ✅ | ✅ |
| Priority support | — | — | ✅ |

---

## Tech Detection

The skill uses **passive HTTP fingerprinting** — it makes standard HTTP/HTTPS requests and inspects the response for technology indicators:

- **HTTP headers:** `Server`, `X-Powered-By`, `CF-*` (Cloudflare), `X-Vercel-ID`, etc.
- **Meta generator tags:** WordPress, Drupal, Shopify, Squarespace, Wix, etc.
- **Script URLs:** jQuery, React, Vue.js, Stripe, Google Analytics, HubSpot, Intercom, etc.
- **Default paths:** `/wp-login.php`, `/_next/static/`, `cdn.shopify.com`, etc.

No active port scanning. No aggressive probing. Passive reconnaissance only.

---

## Example Output

```
🔍 Lead Profile — acme.com
   Domain: acme.com
   Industry: Software / SaaS
   Size: 200-500 employees
   Lookup date: 2026-04-23
   Tech stack: Cloudflare, React, Stripe, Google Analytics, WordPress
   Social: linkedin: https://linkedin.com/company/acme-corp | twitter: https://twitter.com/acme
   Recent news:
     • Acme Corp Raises $50M Series B (2026-03-15) — https://news.example.com/...
     • Acme Corp Launches New AI Product (2026-02-20) — https://techcrunch.com/...
```

---

## Legal Notice

> ⚠️ **Only research companies you have legitimate business interest in. Do not use for spam or unsolicited contact.** This tool aggregates publicly available information. Respect robots.txt and terms of service of scraped sources. The authors assume no liability for misuse.

---

## Troubleshooting

**"Could not extract domain" error:**  
Make sure you're passing a valid domain (`acme.com`) or LinkedIn company URL. Plain company names without a domain may require web search (Tavily recommended).

**No tech stack detected:**  
Try the HTTPS version. Some sites only serve on port 443. You can also test manually: `curl -I https://<domain>`.

**No news results:**  
Set `TAVILY_API_KEY` in your `.env` file. The free tier gives 1000 searches/month. Without it, the tool falls back to DuckDuckGo which may return fewer results.

---

## Dependencies

All dependencies are **stdlib only** — no pip install required:
- `socket`, `urllib.request`, `json`, `csv`, `re`, `argparse`, `datetime`, `xml.etree.ElementTree`

Optional (for enhanced results):
- `TAVILY_API_KEY` — [Get free key at tavily.com](https://tavily.com)