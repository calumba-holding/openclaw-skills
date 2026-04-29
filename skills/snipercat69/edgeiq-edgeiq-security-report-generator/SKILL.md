# EdgeIQ Labs Security Report Generator — SKILL.md

**Version:** 1.0.0  
**Category:** Security Intelligence / Reporting  
**Author:** EdgeIQ Labs  
**Status:** Stable

---

**Price:** **Lifetime: $39** / Optional Monthly: $7/mo (all Pro features permanently)


## What It Does

The **Security Report Generator** aggregates scan output from EdgeIQ Labs tools — XSS Scanner, Network Scanner, SSL Watcher, and Alerting System — into professional formatted security reports delivered by email, Telegram, or file download.

Designed for automated cron-driven operation (weekly/monthly), this skill transforms raw scan data into a recurring-revenue report product for MSSP resale or internal security posture tracking.

---

## Tiers

| | Free | **Lifetime ($39)** | Optional Monthly ($7/mo) |
| **Price** | Free | **$39 (lifetime)** | **$7/mo (optional)** |
| **Targets** | Up to 5 | ✅ (unlimited) | ✅ (unlimited) |
| **Frequency** | 1/month | Any | Any |
| **Output** | Text summary | ✅ (all formats) | ✅ (all formats) |
| **Delivery** | File only | ✅ (all) | ✅ (all) |
| **Branding** | Generic | ✅ (branded) | ✅ (branded) |
| **Multi-tool aggregation** | Single tool | ✅ (all tools) | ✅ (all tools) |

👉 [Buy Lifetime — $39](https://buy.stripe.com/3cI8wR51N6d7g6EdUY7wA0W)
👉 [Subscribe Monthly — $7/mo](https://buy.stripe.com/28EfZj9i35938EcbMQ7wA14)
👉 [Subscribe Monthly — $7/mo](https://buy.stripe.com/28EfZj9i35938EcbMQ7wA14)

---

## Features

- **Multi-tool aggregation** — Combines output from XSS Scanner, Network Scanner, SSL Watcher, and Alerting System
- **Output formats** — JSON (machine-readable), HTML (branded/colorful), TEXT (plain)
- **Delivery channels** — SMTP email (MIME multipart), Telegram Bot API, local file
- **Executive summary** — Risk score, total issues, severity breakdown
- **Prioritized recommendations** — Fix list ranked by severity and impact
- **Cron-friendly** — One-shot run, outputs, exits; perfect for `cron` or CI pipelines
- **Input flexibility** — Reads structured scan result JSON from a configurable input directory
- **Rate throttling** — Configurable delay between targets to avoid hammering live systems
- **Template system** — Placeholder-based HTML/text templates for easy branding customization
- **Alert history** — Parses EdgeIQ Alerting System JSON to include triggered alerts in report
- **CVE matching** — Network scan results include CVE lookups against known CVEs
- **Brand footer** — EdgeIQ Labs logo placeholder + footer on all HTML/PDF output

---

## Usage Examples

### Basic — Generate report from scan data

```bash
python3 scripts/report_generator.py --config config.json --format html
```

### From other EdgeIQ tools (piped input)

```bash
# Run XSS scan, save output, then generate report
python3 scripts/xss_scanner.py --target https://example.com --json > /data/scans/xss_example.com.json
python3 scripts/report_generator.py --config config.json --targets example.com
```

### Cron — Monthly HTML report to email

```cron
0 9 1 * * python3 /opt/edgeiq/report_generator.py --config /opt/edgeiq/config.json --format html --delivery email
```

### Telegram delivery with file attachment

```bash
python3 scripts/report_generator.py --config config.json --format html --delivery telegram --chat-id @yourchannel
```

---

## How It Integrates with Other EdgeIQ Tools

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ XSS Scanner │   │   Network   │   │ SSL Watcher │   │Alert System │
│             │   │   Scanner   │   │             │   │             │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │                 │
       ▼                 ▼                 ▼                 ▼
   JSON files dropped into input/ directory (configured in config.json)
       │                 │                 │                 │
       └─────────────────┼─────────────────┼─────────────────┘
                         ▼
              ┌──────────────────┐
              │  Report Generator │
              │  (this skill)     │
              └────────┬─────────┘
                       ▼
         ┌────────────┴────────────┐
         │  Email / Telegram / File │
         └──────────────────────────┘
```

Each tool saves its output as structured JSON to the configured `scan_input_dir`. The report generator reads all JSON files from that directory, correlates findings by target, and produces a unified report.

---

## Legal Notice

**DISCLAIMER:** This tool processes security scan data and generates reports. The report generator itself does not perform network reconnaissance or vulnerability scanning. All scan data must be gathered through authorized, legitimate means only.

EdgeIQ Labs accepts no liability for misuse of this tool or data it processes. Users are solely responsible for ensuring they have explicit authorization to scan and assess any systems referenced in report input data.

Report findings are advisory only. EdgeIQ Labs does not guarantee the accuracy, completeness, or timeliness of generated reports. Always validate findings through secondary investigation before taking remediation action.

---

*EdgeIQ Labs — Security Intelligence for the Modern Web*

---

## 🔗 More from EdgeIQ Labs

**edgeiqlabs.com** — Security tools, OSINT utilities, and micro-SaaS products for developers and security professionals.

- 🛠️ **Subdomain Hunter** — Passive subdomain enumeration via Certificate Transparency
- 📸 **Screenshot API** — URL-to-screenshot API for developers
- 🔔 **uptime.check** — URL uptime monitoring with alerts
- 🛡️ **headers.check** — HTTP security headers analyzer

👉 [Visit edgeiqlabs.com →](https://edgeiqlabs.com)
