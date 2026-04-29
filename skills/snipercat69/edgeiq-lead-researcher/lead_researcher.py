#!/usr/bin/env python3
"""
Lead Researcher by EdgeIQ Labs — v1.0.0
Business Intelligence / Lead Generation

Takes a company name, LinkedIn URL, or domain and returns enriched lead data:
  company size, industry, tech stack, news, social links, contacts.

Usage:
  python3 lead_researcher.py "Acme Corp"
  python3 lead_researcher.py "https://www.linkedin.com/company/acme-corp"
  python3 lead_researcher.py "acme.com"
  python3 lead_researcher.py "acme.com" --format json --tier pro --output acme.csv
"""

import argparse
import csv
import json
import os
import re
import socket
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import date, datetime
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; LeadResearcherBot/1.0; +https://edgeiq.dev)"
    )
}

# Tier-based lookup limits
TIER_LIMITS = {"free": 3, "pro": 50, "bundle": 9999}

# Common tech signatures (header -> name, then JS/meta -> name)
TECH_SIGNATURES: list[dict] = [
    # HTTP headers
    {"type": "header", "key": "server", "pattern": re.compile(r"nginx", re.I), "name": "Nginx"},
    {"type": "header", "key": "server", "pattern": re.compile(r"apache", re.I), "name": "Apache"},
    {"type": "header", "key": "server", "pattern": re.compile(r"iis", re.I), "name": "Microsoft IIS"},
    {"type": "header", "key": "server", "pattern": re.compile(r"nginx|openresty", re.I), "name": "Nginx"},
    {"type": "header", "key": "x-powered-by", "pattern": re.compile(r"php", re.I), "name": "PHP"},
    {"type": "header", "key": "x-powered-by", "pattern": re.compile(r"asp\.net", re.I), "name": "ASP.NET"},
    {"type": "header", "key": "x-powered-by", "pattern": re.compile(r"express", re.I), "name": "Express.js"},
    {"type": "header", "key": "server", "pattern": re.compile(r"cloudflare", re.I), "name": "Cloudflare"},
    {"type": "header", "key": "server", "pattern": re.compile(r"akamaighost", re.I), "name": "Akamai"},
    {"type": "header", "key": "server", "pattern": re.compile(r"nginx", re.I), "name": "Nginx"},
    {"type": "header", "key": "server", "pattern": re.compile(r"azure", re.I), "name": "Microsoft Azure"},
    {"type": "header", "key": "server", "pattern": re.compile(r"aws", re.I), "name": "AWS"},
    {"type": "header", "key": "server", "pattern": re.compile(r"cloudfront", re.I), "name": "CloudFront"},
    {"type": "header", "key": "server", "pattern": re.compile(r"LiteSpeed", re.I), "name": "LiteSpeed"},
    {"type": "header", "key": "server", "pattern": re.compile(r"GitHub", re.I), "name": "GitHub Pages"},
    {"type": "header", "key": "cf-ray", "pattern": re.compile(r".+"), "name": "Cloudflare"},
    {"type": "header", "key": "x-vercel-id", "pattern": re.compile(r".+"), "name": "Vercel"},
    {"type": "header", "key": "x-dynos", "pattern": re.compile(r".+"), "name": "Dyn"},
    {"type": "header", "key": "server", "pattern": re.compile(r"google", re.I), "name": "Google Cloud"},
    {"type": "header", "key": "server", "pattern": re.compile(r"ghs|google", re.I), "name": "GitHub Pages"},
    # HTML meta tags
    {"type": "meta", "key": "generator", "pattern": re.compile(r"wordpress", re.I), "name": "WordPress"},
    {"type": "meta", "key": "generator", "pattern": re.compile(r"drupal", re.I), "name": "Drupal"},
    {"type": "meta", "key": "generator", "pattern": re.compile(r"joomla", re.I), "name": "Joomla"},
    {"type": "meta", "key": "generator", "pattern": re.compile(r"shopify", re.I), "name": "Shopify"},
    {"type": "meta", "key": "generator", "pattern": re.compile(r"squarespace", re.I), "name": "Squarespace"},
    {"type": "meta", "key": "generator", "pattern": re.compile(r"wix", re.I), "name": "Wix"},
    {"type": "meta", "key": "generator", "pattern": re.compile(r"webflow", re.I), "name": "Webflow"},
    {"type": "meta", "key": "generator", "pattern": re.compile(r"hubspot", re.I), "name": "HubSpot CMS"},
    {"type": "meta", "key": "generator", "pattern": re.compile(r"gravity forms", re.I), "name": "Gravity Forms"},
    # JS library detection via HTML
    {"type": "script", "pattern": re.compile(r"jquery", re.I), "name": "jQuery"},
    {"type": "script", "pattern": re.compile(r"react@\d", re.I), "name": "React"},
    {"type": "script", "pattern": re.compile(r"react\."), "name": "React"},
    {"type": "script", "pattern": re.compile(r"vue", re.I), "name": "Vue.js"},
    {"type": "script", "pattern": re.compile(r"angular", re.I), "name": "Angular"},
    {"type": "script", "pattern": re.compile(r"next\.js", re.I), "name": "Next.js"},
    {"type": "script", "pattern": re.compile(r"gatsby", re.I), "name": "Gatsby"},
    {"type": "script", "pattern": re.compile(r"stripe\.com", re.I), "name": "Stripe"},
    {"type": "script", "pattern": re.compile(r"analytics\.google\.com|googletagmanager", re.I), "name": "Google Analytics"},
    {"type": "script", "pattern": re.compile(r"hotjar", re.I), "name": "Hotjar"},
    {"type": "script", "pattern": re.compile(r"segment\.com|segment.io", re.I), "name": "Segment"},
    {"type": "script", "pattern": re.compile(r"intercom\.io", re.I), "name": "Intercom"},
    {"type": "script", "pattern": re.compile(r"zendesk", re.I), "name": "Zendesk"},
    {"type": "script", "pattern": re.compile(r"hubspot", re.I), "name": "HubSpot"},
    {"type": "script", "pattern": re.compile(r"mixpanel", re.I), "name": "Mixpanel"},
    {"type": "script", "pattern": re.compile(r"heap\.io", re.I), "name": "Heap"},
    {"type": "script", "pattern": re.compile(r"klaviyo", re.I), "name": "Klaviyo"},
    {"type": "script", "pattern": re.compile(r"mailchimp", re.I), "name": "Mailchimp"},
    {"type": "script", "pattern": re.compile(r"facebook\.com/sdk|fb\.js", re.I), "name": "Facebook Pixel"},
    {"type": "script", "pattern": re.compile(r"tiktok", re.I), "name": "TikTok Pixel"},
    {"type": "script", "pattern": re.compile(r"linkedin.*insight", re.I), "name": "LinkedIn Insight"},
    {"type": "script", "pattern": re.compile(r"recaptcha|google.*recaptcha", re.I), "name": "reCAPTCHA"},
    {"type": "script", "pattern": re.compile(r"gtag|google.*analytics", re.I), "name": "Google Analytics"},
    {"type": "script", "pattern": re.compile(r"shopify.*js", re.I), "name": "Shopify"},
]

# Common file paths that reveal CMS / frameworks
PATH_SIGNATURES = [
    (re.compile(r"wp-login|wp-admin|wp-content", re.I), "WordPress"),
    (re.compile(r"sites/default", re.I), "Drupal"),
    (re.compile(r"media/backend", re.I), "Joomla"),
    (re.compile(r"_next/static", re.I), "Next.js"),
    (re.compile(r"cdn\.shopify\.com", re.I), "Shopify"),
    (re.compile(r"\.figma\.io", re.I), "Figma"),
]

# Industry keywords for classification
INDUSTRY_KEYWORDS = {
    "Software / SaaS": [
        "software", "saas", "cloud", "platform", "technology", "tech",
        "analytics", "data", "api", "devtools", "developer",
    ],
    "E-commerce / Retail": [
        "shop", "store", "retail", "marketplace", "commerce", "e-commerce",
        "fashion", "apparel", "furniture",
    ],
    "Financial Services": [
        "fintech", "financial", "banking", "payment", "investment",
        "insurance", "crypto", "blockchain",
    ],
    "Healthcare": [
        "health", "medical", "pharma", "healthcare", "biotech", "telehealth",
    ],
    "Education": [
        "education", "edtech", "learning", "university", "school", "training",
    ],
    "Marketing / Media": [
        "marketing", "advertising", "media", "agency", "creative", "content",
    ],
    "Real Estate": [
        "real estate", "property", "realty", "housing",
    ],
    "Food / Hospitality": [
        "food", "restaurant", "catering", "hospitality", "hotel", "travel",
    ],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _req(url: str, timeout: int = 8) -> tuple[str, dict[str, str], int]:
    """Fetch a URL, return (body, headers_dict, status_code)."""
    try:
        req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            headers = dict(resp.headers.items())
            return body, headers, resp.status
    except Exception:
        return "", {}, 0


def extract_domain_from_input(raw: str) -> str | None:
    """Parse domain or LinkedIn URL to extract the domain."""
    raw = raw.strip().strip('"').strip("'")
    # LinkedIn company URL
    m = re.search(r"linkedin\.com/company/([\w-]+)", raw, re.I)
    if m:
        return m.group(1).rstrip("/")
    # Strip protocol
    m = re.match(r"(?:https?://)?(www\.)?([a-zA-Z0-9.-]+)", raw)
    if m:
        return m.group(2).lower()
    return None


def detect_tech(domain: str) -> list[str]:
    """Probe a domain for technology fingerprints via HTTP."""
    found: set[str] = set()
    for scheme in ("https://", "http://"):
        url = f"{scheme}{domain}"
        body, headers, status = _req(url)
        if status == 0:
            continue

        # Header-based detection
        for sig in TECH_SIGNATURES:
            if sig["type"] == "header":
                key = sig["key"]
                if key.lower() in {k.lower() for k in headers}:
                    actual_key = next(k for k in headers if k.lower() == key.lower())
                    val = headers[actual_key]
                    if sig["pattern"].search(val):
                        found.add(sig["name"])
                elif key.lower() == "server" and sig["pattern"].search(val):
                    found.add(sig["name"])

        # Meta generator
        if body:
            mg = re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']', body, re.I)
            if not mg:
                mg = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']generator["\']', body, re.I)
            if mg:
                for sig in TECH_SIGNATURES:
                    if sig["type"] == "meta" and sig["pattern"].search(mg.group(1)):
                        found.add(sig["name"])

            # Script tag detection
            for sig in TECH_SIGNATURES:
                if sig["type"] == "script" and sig["pattern"].search(body):
                    found.add(sig["name"])

            # Path detection
            for path_pat, tech_name in PATH_SIGNATURES:
                if path_pat.search(body):
                    found.add(tech_name)

        # Detect WP admin
        if status in (301, 302, 200):
            _, h, _ = _req(f"{scheme}{domain}/wp-login.php")
            if h:
                found.add("WordPress")

        # Stop after successful HTTPS probe
        if scheme == "https://" and found:
            break

    return sorted(found)


def search_tavily(query: str, api_key: str | None, max_results: int = 5) -> list[dict]:
    """Search via Tavily API (free tier: 1000 searches/month)."""
    if not api_key:
        return []
    try:
        import urllib.request
        payload = json.dumps({"query": query, "max_results": max_results}).encode()
        req = urllib.request.Request(
            "https://api.tavily.com/search",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        results = []
        for r in data.get("results", []):
            results.append({"title": r.get("title", ""), "url": r.get("url", ""), "date": r.get("published_date", "")})
        return results
    except Exception:
        return []


def search_duckduckgo(query: str) -> list[dict]:
    """Basic DuckDuckGo HTML scrape as fallback (no API key required)."""
    try:
        q = urllib.parse.quote(query)
        body, _, status = _req(f"https://duckduckgo.com/html/?q={q}", timeout=8)
        if status != 200 or not body:
            return []
        results = []
        # Parse result blocks from ddg HTML
        for m in re.finditer(r'<a class="result__a" href="(https?://[^"]+)"[^>]*>([^<]+)</a>', body):
            results.append({"url": m.group(1), "title": re.sub(r'<[^>]+>', '', m.group(2))})
            if len(results) >= 5:
                break
        return results
    except Exception:
        return []


def enrich_news(domain: str, tavily_key: str | None) -> list[dict]:
    """Get recent news about a company via domain name."""
    queries = [f"{domain} company news 2026", f"site:news.google.com {domain}"]
    all_results = []
    for q in queries:
        if tavily_key:
            res = search_tavily(q, tavily_key, max_results=3)
        else:
            res = search_duckduckgo(q)
        all_results.extend(res)
        if len(all_results) >= 5:
            break
    # Deduplicate by URL
    seen, unique = set(), []
    for r in all_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)
    return unique[:5]


def detect_size_from_html(domain: str) -> str | None:
    """Heuristic size detection from company page hints."""
    size_keywords = [
        (re.compile(r"(?:employees?|staff)[^<]{0,80}(\d[\d,]+)\s*(?:employees?|people)", re.I), "employees"),
        (re.compile(r"(\d[\d,]+)\s*(?:employees?|people|staff)", re.I), "employees"),
        (re.compile(r"(?:1-9|10-49|50-199|200-499|500-999|1000\+)\s*employees", re.I), "range"),
        (re.compile(r"(?:stage|series)\s*[A-Z]", re.I), None),  # funding stage, ignore
    ]
    for scheme in ("https://",):
        body, _, status = _req(f"{scheme}{domain}/about")
        if status == 0:
            body, _, status = _req(f"{scheme}{domain}")
        if status != 200 or not body:
            continue
        for pat, label in size_keywords:
            m = pat.search(body)
            if m:
                return m.group(0).strip()[:60]
    return None


def detect_industry(domain: str) -> str:
    """Heuristic industry classification from homepage text."""
    for scheme in ("https://",):
        body, _, status = _req(f"{scheme}{domain}")
        if status != 200 or not body:
            continue
        text = re.sub(r'<[^>]+>', ' ', body).lower()
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score >= 2:
                return industry
    return "Unknown"


def detect_social_links(domain: str) -> dict:
    """Find social media profile links from the homepage."""
    social = {}
    patterns = [
        (r'twitter\.com/([\w]+)', "twitter"),
        (r'x\.com/([\w]+)', "twitter"),
        (r'linkedin\.com/company/([\w-]+)', "linkedin"),
        (r'facebook\.com/([\w.]+)', "facebook"),
        (r'instagram\.com/([\w.]+)', "instagram"),
        (r'youtube\.com/@([\w]+)', "youtube"),
        (r'youtube\.com/channel/([\w-]+)', "youtube"),
        (r'github\.com/([\w-]+)', "github"),
    ]
    for scheme in ("https://",):
        body, _, status = _req(f"{scheme}{domain}")
        if status != 200:
            continue
        for pat, label in patterns:
            m = re.search(pat, body, re.I)
            if m:
                social[label] = m.group(0)
        if social:
            break
    return social


def detect_employees_from_linkedin(domain: str) -> str | None:
    """Parse LinkedIn company page for employee range."""
    url = f"https://www.linkedin.com/company/{domain.replace('.com', '').split('.')[0]}"
    body, _, status = _req(url, timeout=10)
    if status != 200 or not body:
        # Try searching for LinkedIn company page via DDG
        results = search_duckduckgo(f"site:linkedin.com/company {domain}")
        if results:
            body, _, status = _req(results[0]["url"], timeout=10)
    if status == 200 and body:
        m = re.search(r"(\d{1,3}(?:,\d{3})*)\s*(?:employees|members)", body, re.I)
        if m:
            return m.group(1)
        # Range pattern
        m = re.search(r"(?:([\d,]+)\s*-\s*([\d,]+)\s*employees)", body, re.I)
        if m:
            return f"{m.group(1)} - {m.group(2)} employees"
    return None


def build_profile(domain: str, tier: str, tavily_key: str | None) -> dict:
    """Assemble a full company profile."""
    profile: dict[str, Any] = {
        "company": domain,
        "domain": domain,
        "size": "Unknown",
        "industry": detect_industry(domain),
        "description": "",
        "tech_stack": detect_tech(domain),
        "news": [],
        "social": detect_social_links(domain),
        "contacts": [],
        "lookup_date": str(date.today()),
        "tier": tier,
    }

    # Try employee size via LinkedIn
    size = detect_employees_from_linkedin(domain)
    if size:
        profile["size"] = size
    else:
        size_heur = detect_size_from_html(domain)
        if size_heur:
            profile["size"] = size_heur

    # News (Pro+ only)
    if tier in ("pro", "bundle"):
        profile["news"] = enrich_news(domain, tavily_key)

    return profile


def format_text(profile: dict) -> str:
    """Human-readable text output."""
    lines = [
        f"🔍 Lead Profile — {profile['company']}",
        f"   Domain: {profile['domain']}",
        f"   Industry: {profile['industry']}",
        f"   Size: {profile['size']}",
        f"   Lookup date: {profile['lookup_date']}",
    ]
    if profile.get("tech_stack"):
        lines.append(f"   Tech stack: {', '.join(profile['tech_stack'])}")
    if profile.get("social"):
        social_items = [f"{k}: {v}" for k, v in profile["social"].items()]
        lines.append(f"   Social: {' | '.join(social_items)}")
    if profile.get("news"):
        lines.append("   Recent news:")
        for n in profile["news"][:5]:
            lines.append(f"     • {n['title']} ({n['date']}) — {n['url']}")
    if profile.get("contacts"):
        lines.append("   Contacts:")
        for c in profile["contacts"]:
            lines.append(f"     • {c['name']} — {c.get('title', '')} ({c.get('linkedin', '')})")
    return "\n".join(lines)


def write_csv(profile: dict, path: str) -> None:
    """Export profile to CSV (Pro+ tier)."""
    rows = []
    # Flatten tech_stack
    row = {
        "company": profile.get("company", ""),
        "domain": profile.get("domain", ""),
        "industry": profile.get("industry", ""),
        "size": profile.get("size", ""),
        "tech_stack": "; ".join(profile.get("tech_stack", [])),
        "news_titles": "; ".join(n["title"] for n in profile.get("news", [])),
        "news_urls": "; ".join(n["url"] for n in profile.get("news", [])),
        "linkedin": profile.get("social", {}).get("linkedin", ""),
        "twitter": profile.get("social", {}).get("twitter", ""),
        "facebook": profile.get("social", {}).get("facebook", ""),
        "lookup_date": profile.get("lookup_date", ""),
    }
    rows.append(row)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ CSV exported to {path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Lead Researcher by EdgeIQ Labs — enrich company data from domain/LinkedIn/name",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="Company name, LinkedIn URL, or domain")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--output", help="CSV output file path (Pro tier)")
    parser.add_argument(
        "--tier", choices=["free", "pro", "bundle"], default="free",
        help="Tier: free (3/mo), pro (50/mo + CSV), bundle (unlimited)"
    )
    parser.add_argument("--tavily-key", default=os.environ.get("TAVILY_API_KEY"), help="Tavily API key")
    return parser.parse_args()


def main():
    args = parse_args()

    domain = extract_domain_from_input(args.input)
    if not domain:
        print("❌ Could not extract domain from input. Provide a domain, company name, or LinkedIn URL.")
        sys.exit(1)

    print(f"🔍 Researching: {domain}")

    profile = build_profile(domain, args.tier, args.tavily_key)

    if args.format == "json":
        print(json.dumps(profile, indent=2, ensure_ascii=False))
    else:
        print(format_text(profile))

    if args.output and args.tier in ("pro", "bundle"):
        write_csv(profile, args.output)
    elif args.output:
        print("⚠️  CSV export requires Pro or Bundle tier.")


if __name__ == "__main__":
    main()