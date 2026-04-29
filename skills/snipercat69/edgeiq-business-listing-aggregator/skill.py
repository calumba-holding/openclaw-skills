#!/usr/bin/env python3
"""
Business Listing Aggregator — EdgeIQ Labs
Version: 1.0.0

Audits a business's presence across Google Maps, Yelp, Facebook, BBB, and Apple Maps.
Reports discrepancies in name, address, phone, and hours.

Usage:
    python skill.py --business "Joe's Pizza" --location "Brooklyn, NY"
    python skill.py --business "Joe's Pizza" --location "Brooklyn, NY" --output html --outfile report.html
    python skill.py --help
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ---------------------------------------------------------------------------
# Platform config
# ---------------------------------------------------------------------------
PLATFORMS = {
    "google_maps": {
        "name": "Google Maps",
        "url_template": "https://www.google.com/maps/search/{business}+{location}",
        "tier": "free",
    },
    "yelp": {
        "name": "Yelp",
        "url_template": "https://www.yelp.com/search?find_desc={business}&find_loc={location}",
        "tier": "free",
    },
    "facebook": {
        "name": "Facebook",
        "url_template": "https://www.facebook.com/search/top?q={business}+{location}",
        "tier": "free",
    },
    "bbb": {
        "name": "Better Business Bureau",
        "url_template": "https://www.bbb.org/search?find_loc={location}&find_text={business}",
        "tier": "pro",
    },
    "apple_maps": {
        "name": "Apple Maps",
        "url_template": "https://maps.apple.com/?q={business}+{location}",
        "tier": "pro",
    },
}

TIER_PLATFORMS = {
    "free": ["google_maps", "yelp", "facebook"],
    "pro": ["google_maps", "yelp", "facebook", "bbb", "apple_maps"],
    "bundle": ["google_maps", "yelp", "facebook", "bbb", "apple_maps"],
}

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT = 10  # seconds
RATE_LIMIT_DELAY = 1.5  # seconds between requests


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def build_search_url(platform_key, business, location):
    """Build a search URL for a given platform."""
    tmpl = PLATFORMS[platform_key]["url_template"]
    b = business.replace(" ", "+")
    l = location.replace(" ", "+")
    return tmpl.format(business=b, location=l)


def fetch_page(url, headers=None):
    """Fetch a page's HTML using urllib (stdlib). Returns raw HTML or None."""
    if headers is None:
        headers = dict(DEFAULT_HEADERS)
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except HTTPError as e:
        return None
    except URLError:
        return None
    except Exception:
        return None


def extract_business_name(html):
    """Try to pull a business name from page HTML (best-effort)."""
    # Look for OpenGraph title
    m = re.search(r'<meta property="og:title" content="([^"]+)"', html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # Look for <title>
    m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    if m:
        return m.group(1).strip().split(" - ")[0].split(" | ")[0]
    return None


def extract_address(html):
    """Best-effort address extraction from page HTML."""
    patterns = [
        r'<address[^>]*>([^<]+)</address>',
        r'"streetAddress"\s*:\s*"([^"]+)"',
        r'<span[^>]+itemprop="streetAddress"[^>]*>([^<]+)</span>',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def extract_phone(html):
    """Best-effort phone extraction from page HTML."""
    patterns = [
        r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    ]
    for pat in patterns:
        m = re.search(pat, html)
        if m:
            phone = re.sub(r'[^\d+]', '', m.group())
            if len(phone) >= 10:
                # Format nicely
                digits = re.sub(r'\D', '', phone)[-10:]
                return f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return None


def extract_hours(html):
    """Best-effort hours extraction."""
    # Look for common hours patterns
    patterns = [
        r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[^,\n]*(?:am|pm)[^,\n]*(?:am|pm)',
        r'"openingHours"\s*:\s*"([^"]+)"',
        r'<time[^>]+datetime="[^"]+">([^<]+)</time>',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            return m.group(0)[:100]
    return None


def extract_from_html(html, platform_key):
    """Extract all business data fields from HTML."""
    return {
        "name": extract_business_name(html),
        "address": extract_address(html),
        "phone": extract_phone(html),
        "hours": extract_hours(html),
        "url": None,
        "found": html is not None and len(html) > 200,
    }


def google_places_api_check(business, location, api_key):
    """
    Use Google Places Text Search API for structured data.
    https://developers.google.com/maps/documentation/places/web-service/search-text
    Endpoint: https://maps.googleapis.com/maps/api/place/textsearch/json
    """
    import urllib.parse
    query = f"{business} {location}"
    params = urllib.parse.urlencode({
        "query": query,
        "key": api_key,
    })
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?{params}"
    try:
        req = Request(url, headers=DEFAULT_HEADERS)
        with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("results") and len(data["results"]) > 0:
            place = data["results"][0]
            return {
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "phone": place.get("formatted_phone_number"),
                "hours": None,
                "url": place.get("url"),
                "found": True,
                "source": "google_places_api",
            }
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Core auditor
# ---------------------------------------------------------------------------
class BusinessListingAggregator:
    """Audits a business listing across multiple platforms."""

    def __init__(self, tier="free", google_places_api_key=None, verbose=False):
        self.tier = tier if tier in TIER_PLATFORMS else "free"
        self.api_key = google_places_api_key
        self.verbose = verbose
        self.platforms = TIER_PLATFORMS.get(self.tier, TIER_PLATFORMS["free"])

    def _vprint(self, msg):
        if self.verbose:
            print(f"[VERBOSE] {msg}", file=sys.stderr)

    def _determine_consensus(self, field_data):
        """Determine the consensus value and which platforms differ."""
        values = {k: v for k, v in field_data.items() if v is not None}
        if not values:
            return None, [], "unknown"

        # Count occurrences of each value (normalized)
        from collections import Counter
        normalized = {}
        for k, v in values.items():
            nv = re.sub(r'\s+', ' ', v.strip().lower())
            normalized[k] = nv

        counts = Counter(normalized.values())
        consensus_val = counts.most_common(1)[0][0]
        consensus_platforms = [k for k, v in normalized.items() if v == consensus_val]
        discrepant = [k for k, v in normalized.items() if v != consensus_val]

        # Severity
        total = sum(counts.values())
        if total >= 3 and len(discrepant) == 1:
            severity = "low"
        elif len(discrepant) >= 2:
            severity = "high"
        else:
            severity = "medium"

        # Reconstruct original-case consensus
        consensus_original = values.get(consensus_platforms[0]) if consensus_platforms else None

        return consensus_original, discrepant, severity

    def _build_discrepancy(self, field, field_data, platform_names):
        """Build a single discrepancy record."""
        consensus, discrepant, severity = self._determine_consensus(field_data)
        if not consensus or len(discrepant) == 0:
            return None

        plat_key = discrepant[0] if discrepant else list(field_data.keys())[0]
        platform_name = platform_names.get(plat_key, 'discrepant platform')
        if field == "phone":
            recommendation = f"Update {platform_name} phone number to match consensus: {consensus}"
        elif field == "address":
            recommendation = f"Update address on {platform_name} to: {consensus}"
        elif field == "name":
            recommendation = f"Verify business name on {platform_name} — consensus is: {consensus}"
        elif field == "hours":
            recommendation = f"Update hours on {platform_name} to match consensus"

        return {
            "field": field,
            "platforms": field_data,
            "consensus": consensus,
            "discrepant_platforms": discrepant,
            "severity": severity,
            "recommendation": recommendation,
        }

    def audit(self, business, location):
        """
        Main entry point. Takes business name and location.
        Returns a dict report.
        """
        self._vprint(f"Starting audit for: {business} @ {location}")
        self._vprint(f"Tier: {self.tier} | Platforms: {self.platforms}")

        results = {}
        platform_names = {k: v["name"] for k, v in PLATFORMS.items()}

        # If we have a Google Places API key, use it for Google Maps
        if self.api_key and "google_maps" in self.platforms:
            self._vprint("Using Google Places API for Google Maps data...")
            api_result = google_places_api_check(business, location, self.api_key)
            if api_result:
                results["google_maps"] = api_result
                self._vprint(f"Google Places API returned: {api_result.get('name')}")

        # Scrape all configured platforms
        for platform_key in self.platforms:
            if platform_key in results:
                continue  # already got via API
            url = build_search_url(platform_key, business, location)
            self._vprint(f"Fetching {platform_names[platform_key]}: {url}")
            html = fetch_page(url)
            if html:
                results[platform_key] = extract_from_html(html, platform_key)
                self._vprint(f"  → found={results[platform_key]['found']}, name={results[platform_key].get('name')}")
            else:
                results[platform_key] = {"found": False, "name": None, "address": None, "phone": None, "hours": None, "url": None}
            time.sleep(RATE_LIMIT_DELAY)

        # Extract per-field data across platforms
        fields = ["name", "address", "phone", "hours"]
        discrepancies = []

        for field in fields:
            field_data = {}
            for pk in self.platforms:
                if pk in results and results[pk].get("found"):
                    val = results[pk].get(field)
                    if val:
                        field_data[pk] = val
            if field_data:
                disc = self._build_discrepancy(field, field_data, platform_names)
                if disc and len(disc["discrepant_platforms"]) > 0:
                    discrepancies.append(disc)

        # Build summary
        platforms_with_issues = len(set(d for d in discrepancies for d in d.get("discrepant_platforms", [])))
        total_platforms = len(self.platforms)
        if platforms_with_issues == 0:
            overall_health = "excellent"
        elif platforms_with_issues <= 1:
            overall_health = "good"
        elif platforms_with_issues <= 2:
            overall_health = "fair"
        else:
            overall_health = "poor"

        report = {
            "business_name": business,
            "location": location,
            "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            "tier": self.tier,
            "platforms_checked": self.platforms,
            "results": results,
            "discrepancies": discrepancies,
            "summary": {
                "total_platforms": total_platforms,
                "platforms_with_issues": platforms_with_issues,
                "overall_health": overall_health,
            },
            "legal_notice": "Only monitor businesses you own or have explicit written permission to audit.",
        }

        return report


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------
def format_json(report):
    return json.dumps(report, indent=2)


def format_html(report):
    """Generate a clean HTML report."""
    disc_count = len(report["discrepancies"])
    health = report["summary"]["overall_health"]
    health_color = {"excellent": "#22c55e", "good": "#84cc16", "fair": "#f59e0b", "poor": "#ef4444"}.get(health, "#6b7280")

    platform_names = {k: v["name"] for k, v in PLATFORMS.items()}

    rows = ""
    for d in report["discrepancies"]:
        sev_color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}.get(d["severity"], "#6b7280")
        plat_vals = "<br>".join(f"<strong>{platform_names.get(k,k)}:</strong> {v}" for k, v in d["platforms"].items())
        rows += f"""
        <tr>
          <td>{d['field'].capitalize()}</td>
          <td>{plat_vals}</td>
          <td>{d['consensus']}</td>
          <td>{', '.join(platform_names.get(p,p) for p in d['discrepant_platforms'])}</td>
          <td style="color:{sev_color};font-weight:bold">{d['severity'].upper()}</td>
          <td>{d['recommendation']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Business Listing Audit — {report['business_name']}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f9fafb; color: #111827; }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    h1 {{ color: #1f2937; }}
    .badge {{ display: inline-block; padding: 4px 12px; border-radius: 99px; font-weight: 600; font-size: 13px; }}
    .badge-success {{ background: #dcfce7; color: #166534; }}
    .badge-warning {{ background: #fef9c3; color: #854d0e; }}
    .badge-danger {{ background: #fee2e2; color: #991b1b; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 24px; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    th {{ background: #f3f4f6; text-align: left; padding: 12px 16px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; }}
    td {{ padding: 12px 16px; border-top: 1px solid #f3f4f6; font-size: 14px; }}
    .legal {{ margin-top: 40px; padding: 16px; background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; font-size: 13px; color: #92400e; }}
    .meta {{ margin-top: 20px; font-size: 13px; color: #6b7280; }}
  </style>
</head>
<body>
<div class="container">
  <h1>🏪 Business Listing Audit</h1>

  <p><strong>{report['business_name']}</strong> &mdash; {report['location']}</p>
  <p>
    Audited: {report['audit_timestamp']} &nbsp;|&nbsp;
    Tier: <span class="badge badge-success">{report['tier'].upper()}</span> &nbsp;|&nbsp;
    Health:
    <span class="badge" style="background:{health_color}20;color:{health_color}">{health.upper()}</span>
  </p>

  <h2>Discrepancies ({disc_count} found)</h2>
  <table>
    <thead>
      <tr>
        <th>Field</th>
        <th>Values by Platform</th>
        <th>Consensus</th>
        <th>Discrepant</th>
        <th>Severity</th>
        <th>Recommendation</th>
      </tr>
    </thead>
    <tbody>{rows}
    </tbody>
  </table>

  <h2>Platform Status</h2>
  <table>
    <thead>
      <tr><th>Platform</th><th>Found</th><th>Name</th><th>Address</th><th>Phone</th><th>Hours</th></tr>
    </thead>
    <tbody>"""

    for pk in report["platforms_checked"]:
        r = report["results"].get(pk, {})
        found = "✅" if r.get("found") else "❌"
        html += f"""<tr>
          <td><strong>{platform_names.get(pk, pk)}</strong></td>
          <td>{found}</td>
          <td>{r.get('name') or '—'}</td>
          <td>{r.get('address') or '—'}</td>
          <td>{r.get('phone') or '—'}</td>
          <td>{r.get('hours') or '—'}</td>
        </tr>"""

    html += """</tbody>
  </table>

  <div class="legal">
    ⚠️ <strong>Legal Notice:</strong> Only monitor businesses you own or have explicit written permission to audit.
    Scraping or automated access to third-party platforms may violate those platforms' Terms of Service.
    EdgeIQ Labs and the skill authors accept no liability for misuse.
  </div>

  <p class="meta">Generated by Business Listing Aggregator v1.0.0 · EdgeIQ Labs</p>
</div>
</body>
</html>"""
    return html


def format_text(report):
    """Plain-text terminal output."""
    lines = [
        f"=== Business Listing Audit ===",
        f"Business : {report['business_name']}",
        f"Location : {report['location']}",
        f"Timestamp: {report['audit_timestamp']}",
        f"Tier     : {report['tier']}",
        f"Health   : {report['summary']['overall_health']}",
        f"",
    ]

    disc = report["discrepancies"]
    if disc:
        lines.append(f"⚠️  Discrepancies found ({len(disc)}):")
        for d in disc:
            lines.append(f"  [{d['severity'].upper()}] {d['field']}")
            for pk, val in d["platforms"].items():
                marker = " ← DISCREPANT" if pk in d["discrepant_platforms"] else ""
                lines.append(f"    {PLATFORMS.get(pk, {}).get('name', pk)}: {val}{marker}")
            lines.append(f"    Recommendation: {d['recommendation']}")
            lines.append("")
    else:
        lines.append("✅ No discrepancies found — listing is consistent across all checked platforms.")

    lines.append("\nPlatform Status:")
    for pk in report["platforms_checked"]:
        r = report["results"].get(pk, {})
        status = "FOUND" if r.get("found") else "NOT FOUND"
        lines.append(f"  [{status}] {PLATFORMS.get(pk, {}).get('name', pk)}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Business Listing Aggregator — audit business listings across major platforms.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python skill.py --business "Joe's Pizza" --location "Brooklyn, NY"
  python skill.py --business "Joe's Pizza" --location "Brooklyn, NY" --output html --outfile report.html
  python skill.py --business "Joe's Pizza" --location "Brooklyn, NY" --tier pro --verbose

Environment variables:
  GOOGLE_PLACES_API_KEY  Optional API key for structured Google Places data
  TIER                   free | pro | bundle (default: free)
  LOG_LEVEL              DEBUG | INFO | WARNING | ERROR
        """,
    )
    parser.add_argument("--business", required=True, help="Business name to audit")
    parser.add_argument("--location", required=True, help="Business location (city, state/city)")
    parser.add_argument("--output", default="text", choices=["text", "json", "html"], help="Output format")
    parser.add_argument("--outfile", help="Write output to file instead of stdout")
    parser.add_argument("--tier", default=os.getenv("TIER", "free"), choices=["free", "pro", "bundle"], help="Monitoring tier")
    parser.add_argument("--verbose", action="store_true", help="Verbose debug output")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    # Check for Google Places API key
    api_key = os.getenv("GOOGLE_PLACES_API_KEY") or None

    aggregator = BusinessListingAggregator(tier=args.tier, google_places_api_key=api_key, verbose=args.verbose)

    if args.interactive:
        print("Business Listing Aggregator — Interactive Mode")
        print("=" * 50)
        business = input("Business name: ").strip()
        location = input("Location: ").strip()
        tier = input("Tier [free/pro/bundle] (default: free): ").strip() or "free"
        output = input("Output format [text/json/html] (default: text): ").strip() or "text"
        aggregator = BusinessListingAggregator(tier=tier, google_places_api_key=api_key, verbose=args.verbose)
        args.output = output

    report = aggregator.audit(args.business, args.location)

    # Format output
    if args.output == "json":
        formatted = format_json(report)
    elif args.output == "html":
        formatted = format_html(report)
    else:
        formatted = format_text(report)

    if args.outfile:
        with open(args.outfile, "w", encoding="utf-8") as f:
            f.write(formatted)
        print(f"Report written to: {args.outfile}")
    else:
        print(formatted)


if __name__ == "__main__":
    main()