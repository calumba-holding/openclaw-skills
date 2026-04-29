# Business Listing Aggregator — SKILL.md

**Skill Name:** Business Listing Aggregator  
**Version:** 1.0.0  
**Category:** Business Intelligence / Monitoring  
**Author:** EdgeIQ Labs  
**Python:** 3.8+

---

## What It Does

Takes a business name + location and audits its presence across major platforms (Google Maps, Yelp, BBB, Facebook, Apple Maps). It detects and reports discrepancies in business name, address, phone number, and operating hours — producing a clean structured report in JSON or HTML format.

Designed for business owners, agency marketers, and reputation managers who need to catch listing drift before it damages SEO or drives away customers.

---

## Tier Comparison

| Feature | Free | Pro ($19/mo) | Bundle ($39/mo) |
|---|---|---|---|
| Businesses monitored | 1 | 10 | Unlimited |
| Check frequency | Monthly | Weekly | Daily |
| Platforms checked | Google Maps, Yelp, Facebook | Google Maps, Yelp, Facebook, BBB, Apple Maps | All 5 platforms |
| Output formats | Terminal text | JSON + HTML | JSON + HTML + PDF |
| Exportable report | No | Yes | Yes |
| API access | No | Yes | Yes |
| Priority support | No | No | Yes |

---

## Features

- **Multi-platform citation check** — Google Maps, Yelp, Facebook, BBB, Apple Maps
- **Field-level discrepancy detection** — flags mismatches in name, address, phone, hours
- **Consensus determination** — highlights which platform differs from the majority
- **Structured output** — JSON (machine-readable) and HTML (human-readable) formats
- **Optional Google Places API** — pass a key for enriched, structured data; falls back to web scraping when not provided
- **Confidence scoring** — each check includes a confidence rating (High/Medium/Low)
- **Tier-based platform coverage** — Free checks 3 platforms; Pro adds BBB + Apple Maps; Bundle covers all

---

## Usage

### Command Line

```bash
python skill.py --business "Joe's Pizza" --location "Brooklyn, NY"
python skill.py --business "Joe's Pizza" --location "Brooklyn, NY" --output json --outfile report.json
python skill.py --business "Joe's Pizza" --location "Brooklyn, NY" --output html --outfile report.html
python skill.py --business "Joe's Pizza" --location "Brooklyn, NY" --tier pro --verbose
python skill.py --help
```

### Python API

```python
from skill import BusinessListingAggregator

aggregator = BusinessListingAggregator(tier="pro", google_places_api_key=None)
report = aggregator.audit("Joe's Pizza", "Brooklyn, NY")
print(report)
```

### Interactive

```bash
python skill.py --interactive
```

---

## Output Example (JSON)

```json
{
  "business_name": "Joe's Pizza",
  "location": "Brooklyn, NY",
  "audit_timestamp": "2026-04-23T11:15:00Z",
  "tier": "pro",
  "platforms_checked": ["google_maps", "yelp", "facebook", "bbb", "apple_maps"],
  "discrepancies": [
    {
      "field": "phone",
      "platforms": {
        "google_maps": "+1-718-555-1234",
        "yelp": "+1-718-555-9999",
        "facebook": "+1-718-555-1234"
      },
      "consensus": "+1-718-555-1234",
      "discrepant_platforms": ["yelp"],
      "severity": "high",
      "recommendation": "Update Yelp listing to match consensus"
    },
    {
      "field": "hours",
      "platforms": {
        "google_maps": "Mon-Sat 10am-10pm",
        "yelp": "Mon-Sat 11am-9pm",
        "facebook": "Mon-Sat 10am-10pm"
      },
      "consensus": "Mon-Sat 10am-10pm",
      "discrepant_platforms": ["yelp"],
      "severity": "medium",
      "recommendation": "Update Yelp hours to match consensus"
    }
  ],
  "summary": {
    "total_platforms": 5,
    "platforms_with_issues": 1,
    "overall_health": "good"
  }
}
```

---

## Pricing

**Lifetime License: $39** — your tool forever, all features included permanently.
**Optional Monthly: $7/mo** — for those who prefer recurring billing (cancel anytime).
👉 [Buy Lifetime — $39](https://buy.stripe.com/7sYcN79i3fNHaMkg367wA0N)
👉 [Subscribe Monthly — $7/mo](https://buy.stripe.com/cNi8wR3XJgRL3jSdUY7wA1e)
👉 [Subscribe Monthly — $7/mo](https://buy.stripe.com/cNi8wR3XJgRL3jSdUY7wA1e)

## Pro Upgrade *(deprecated)*
All features now included in Lifetime purchase.

---

## Legal Notice

**IMPORTANT:** Only monitor businesses you own or have explicit written permission to audit. Scraping or automated access to third-party platforms may violate those platforms' Terms of Service. EdgeIQ Labs and the skill authors accept no liability for misuse. Comply with all applicable laws and platform policies.

---

## Environment Variables

See `.env.example` for required and optional configuration.

```
GOOGLE_PLACES_API_KEY=   # Optional — enables structured Google Places data
TIER=free                 # free | pro | bundle
DEFAULT_LOCATION=         # Optional default location
LOG_LEVEL=INFO            # DEBUG | INFO | WARNING | ERROR
```

---

## Dependencies

- Python 3.8+
- `requests` (optional — for Google Places API; falls back to stdlib urllib)
- Standard library: `json`, `re`, `time`, `sys`, `argparse`, `datetime`, `os`, `html`

Install optional dependencies:
```bash
pip install requests
```

---

## 🔗 More from EdgeIQ Labs

**edgeiqlabs.com** — Security tools, OSINT utilities, and micro-SaaS products for developers and security professionals.

- 🛠️ **Subdomain Hunter** — Passive subdomain enumeration via Certificate Transparency
- 📸 **Screenshot API** — URL-to-screenshot API for developers
- 🔔 **uptime.check** — URL uptime monitoring with alerts
- 🛡️ **headers.check** — HTTP security headers analyzer

👉 [Visit edgeiqlabs.com →](https://edgeiqlabs.com)
