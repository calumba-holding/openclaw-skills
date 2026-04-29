# Business Listing Aggregator

**Author:** EdgeIQ Labs  
**Version:** 1.0.0  
**Category:** Business Intelligence / Monitoring  
**Python:** 3.8+

---

## Overview

Audits a business's presence across major platforms (Google Maps, Yelp, Facebook, BBB, Apple Maps), detects discrepancies in name, address, phone, and hours, and outputs a clean structured report in text, JSON, or HTML format.

Designed for business owners, agency marketers, and reputation managers.

---

## Quick Start

```bash
# No install needed — pure Python stdlib
python skill.py --business "Joe's Pizza" --location "Brooklyn, NY"
```

### Full example with output formats

```bash
# Text output (default)
python skill.py --business "Joe's Pizza" --location "Brooklyn, NY"

# JSON output
python skill.py --business "Joe's Pizza" --location "Brooklyn, NY" --output json --outfile report.json

# HTML report
python skill.py --business "Joe's Pizza" --location "Brooklyn, NY" --output html --outfile report.html

# Pro tier (includes BBB + Apple Maps)
python skill.py --business "Joe's Pizza" --location "Brooklyn, NY" --tier pro --output html --outfile report.html

# Verbose mode
python skill.py --business "Joe's Pizza" --location "Brooklyn, NY" --verbose
```

---

## Installation

### Requirements

- Python 3.8+
- `requests` (optional — only needed if using Google Places API; falls back to stdlib urllib if not installed)

```bash
# Optional: install requests for more reliable HTTP
pip install requests

# Or use entirely without it — stdlib only
```

### Clone / Copy

```bash
# Copy the skill directory to your OpenClaw workspace
cp -r business-listing-aggregator ~/.openclaw/workspace/apps/
```

### Environment Setup

```bash
cd ~/.openclaw/workspace/apps/business-listing-aggregator
cp .env.example .env
# Edit .env if you want to set GOOGLE_PLACES_API_KEY or TIER defaults
```

---

## Usage

### Command Line

```
python skill.py --business "Business Name" --location "City, State"
python skill.py --business "Business Name" --location "City, State" --output json
python skill.py --business "Business Name" --location "City, State" --tier pro
python skill.py --help
```

| Argument | Description |
|---|---|
| `--business` | Business name (required) |
| `--location` | Location string, e.g. "Brooklyn, NY" (required) |
| `--output` | Output format: `text` (default), `json`, `html` |
| `--outfile` | Write output to file instead of stdout |
| `--tier` | `free` \| `pro` \| `bundle` (default: from env or `free`) |
| `--verbose` | Show debug output |
| `--interactive` | Interactive prompt mode |

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `GOOGLE_PLACES_API_KEY` | Google Places API key (optional) | None |
| `TIER` | Default tier | `free` |
| `DEFAULT_LOCATION` | Default location | None |
| `LOG_LEVEL` | Logging level | `INFO` |

### Python API

```python
from skill import BusinessListingAggregator

# Free tier (Google Maps, Yelp, Facebook)
aggregator = BusinessListingAggregator(tier="free")
report = aggregator.audit("Joe's Pizza", "Brooklyn, NY")
print(report)

# Pro tier with Google Places API
aggregator = BusinessListingAggregator(
    tier="pro",
    google_places_api_key="YOUR_API_KEY",
    verbose=True
)
report = aggregator.audit("Joe's Pizza", "Brooklyn, NY")
print(report["summary"])
```

---

## Tier Comparison

| Feature | Free | Pro ($19/mo) | Bundle ($39/mo) |
|---|---|---|---|
| Platforms | Google Maps, Yelp, Facebook | + BBB, Apple Maps | All 5 |
| Businesses | 1 | 10 | Unlimited |
| Check frequency | Monthly | Weekly | Daily |
| Output formats | Terminal text | JSON + HTML | JSON + HTML + PDF |
| API access | No | Yes | Yes |

---

## Output Formats

### Text (default)
Plain terminal output with color-coded severity indicators.

### JSON
Machine-readable structure with full per-platform data, discrepancies, and summary.

```json
{
  "business_name": "Joe's Pizza",
  "location": "Brooklyn, NY",
  "audit_timestamp": "2026-04-23T11:15:00Z",
  "tier": "pro",
  "discrepancies": [...],
  "summary": {"total_platforms": 5, "platforms_with_issues": 1, "overall_health": "good"}
}
```

### HTML
Styled, printable report — ideal for sharing with clients or stakeholders.

---

## Google Places API (Optional)

For more reliable Google Maps data, set your API key:

1. Get a key at [Google Cloud Console](https://console.cloud.google.com/google/maps-apis/places)
2. Enable the **Places API** (Text Search)
3. Set the environment variable:
   ```bash
   export GOOGLE_PLACES_API_KEY="your_key_here"
   ```
   Or add it to `.env`:
   ```
   GOOGLE_PLACES_API_KEY=your_key_here
   ```

The skill falls back to web scraping if no key is provided.

---

## Legal Notice

⚠️ **Only monitor businesses you own or have explicit written permission to audit.** Scraping or automated access to third-party platforms may violate those platforms' Terms of Service. EdgeIQ Labs and the skill authors accept no liability for misuse. Comply with all applicable laws and platform policies.

---

## Troubleshooting

**"Google Maps page returned no data"**
- Try with `--verbose` to see raw page content
- Google Maps may block automated requests; add a Google Places API key for reliable data

**"Yelp / Facebook not returning content"**
- Some platforms actively block scraping; this is expected
- The skill logs what was found vs not found in the report

**Want more platforms?**
- Edit `PLATFORMS` dict in `skill.py` to add new platforms
- Each platform needs: `name`, `url_template`, `tier`

---

## Publish to ClawHub

```bash
clawhub publish --path /home/guy/.openclaw/workspace/apps/business-listing-aggregator
```

Or use the skill-creator skill for guidance on publishing.