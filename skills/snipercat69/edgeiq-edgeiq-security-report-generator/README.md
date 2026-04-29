# EdgeIQ Labs Security Report Generator

**Version:** 1.0.0  
**Category:** Security Intelligence / Reporting  
**Stdlib only:** No pip dependencies required.

---

## Overview

The Security Report Generator aggregates scan output from EdgeIQ Labs tools — XSS Scanner, Network Scanner, SSL Watcher, and Alerting System — into professional, branded security reports delivered by **email**, **Telegram**, or **file output**.

Designed for automated cron-driven operation (weekly, monthly, or on-demand), this skill transforms raw scan data into a recurring-revenue report product for MSSP resale or internal security posture tracking.

---

## Quick Start

### 1. Install

Copy the `edgeiq-security-report-generator` directory to your deployment location:

```bash
cp -r edgeiq-security-report-generator /opt/edgeiq/
cd /opt/edgeiq/
```

### 2. Configure

```bash
cp config.json.example config.json
# Edit config.json with your SMTP/Telegram settings
cp .env.example .env
```

### 3. Drop Scan Data

Place structured JSON scan results into the input directory:

```
input/scans/
  xss_example.com.json     ← from XSS Scanner
  network_example.com.json ← from Network Scanner
  ssl_example.com.json     ← from SSL Watcher
  alert_example.com.json   ← from Alerting System
```

### 4. Generate Report

```bash
python3 scripts/report_generator.py --config config.json --format html
```

---

## Directory Structure

```
edgeiq-security-report-generator/
├── SKILL.md                       ← Skill metadata
├── README.md                      ← This file
├── config.json.example            ← Configuration template
├── .env.example                   ← Environment variables template
├── scripts/
│   └── report_generator.py        ← Main entry point (stdlib only)
├── sample-data/
│   ├── xss_example.com.json       ← Sample XSS scan data
│   ├── network_example.com.json   ← Sample network scan data
│   ├── ssl_example.com.json       ← Sample SSL scan data
│   └── alert_example.com.json     ← Sample alert data
└── sample_report.html             ← Rendered HTML report example
```

---

## Configuration

### `config.json`

| Key | Type | Description |
|-----|------|-------------|
| `scan_input_dir` | string | Directory to read scan JSON files from |
| `targets` | array | List of target URLs/domains to scan |
| `delivery.smtp` | object | SMTP email delivery settings |
| `delivery.telegram` | object | Telegram bot delivery settings |
| `edgeiq_tools` | object | Paths to EdgeIQ tool scripts (optional) |
| `rate_limit.throttle_ms` | int | Delay between targets in ms |

### SMTP Setup

```json
"delivery": {
  "smtp": {
    "enabled": true,
    "host": "smtp.gmail.com",
    "port": 587,
    "username": "your@email.com",
    "password": "your_app_password",
    "from": "security@edgeiq.io",
    "to": ["customer@example.com"],
    "attachments": true
  }
}
```

> **Gmail:** Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your main password.

### Telegram Setup

```json
"delivery": {
  "telegram": {
    "enabled": true,
    "bot_token": "123456789:ABCdefGHI...",
    "chat_id": "@your_channel"
  }
}
```

To get a bot token: message `@BotFather` on Telegram. To get your chat ID: message `@userinfobot`.

---

## Input Data Format

The report generator reads JSON files from `scan_input_dir`. Files are matched by filename prefix:

| File prefix | Tool | Expected JSON keys |
|-------------|------|--------------------|
| `xss_*.json` | XSS Scanner | `findings[]` with `vulnerability`, `severity`, `url`, `parameter`, `payload`, `description` |
| `network_*.json` | Network Scanner | `open_ports[]` with `port`, `service`, `version`, `severity`; `cves[]` with `cve_id`, `cvss`, `severity` |
| `ssl_*.json` | SSL Watcher | `issues[]`, `days_until_expiry`, `grade`, `issuer`, `valid_until`, `security_headers` |
| `alert_*.json` | Alerting System | `alerts[]` with `title`, `severity`, `target`, `timestamp` |

See the `sample-data/` directory for full examples.

---

## Integrating with Other EdgeIQ Tools

The report generator reads scan results from a directory, making it tool-agnostic. Here's how each EdgeIQ tool feeds data:

### XSS Scanner → Report Generator

```bash
# Run scan, output JSON to input directory
python3 scripts/xss_scanner.py --target https://example.com --json \
  > input/scans/xss_example.com.json
```

### Network Scanner → Report Generator

```bash
python3 scripts/network_scanner.py --target example.com --json \
  > input/scans/network_example.com.json
```

### SSL Watcher → Report Generator

```bash
python3 scripts/ssl_watcher.py --target example.com --json \
  > input/scans/ssl_example.com.json
```

### Alerting System → Report Generator

```bash
python3 scripts/alerting_system.py --export json \
  > input/scans/alert_example.com.json
```

**Automated pipeline:** Each tool can be configured to automatically drop output into the shared `input/scans/` directory after each run. The report generator then aggregates all available data.

### Running EdgeIQ tools via config

If `edgeiq_tools` paths are configured in `config.json`, the report generator will automatically call each tool as a subprocess before generating the report:

```json
"edgeiq_tools": {
  "xss_scanner": "/opt/edgeiq/scripts/xss_scanner.py",
  "network_scanner": "/opt/edgeiq/scripts/network_scanner.py",
  "ssl_watcher": "/opt/edgeiq/scripts/ssl_watcher.py"
}
```

Then run:

```bash
python3 scripts/report_generator.py --config config.json --targets example.com
```

---

## Command Line Reference

```bash
python3 scripts/report_generator.py [OPTIONS]

Options:
  --config PATH           Config file path (default: config.json)
  --format FORMAT         html | text | json (default: html)
  --delivery METHOD       email | telegram | file | both (default: file)
  --targets TARGET...     Override target list
  --input-dir PATH        Override scan input directory
  --output-dir PATH       Override output directory
  --title TEXT            Report title (default: "Monthly Security Report")
  --throttle-ms MS        Delay between targets in ms (default: 1000)
  --no-run-scans          Skip subprocess tool calls, use existing files only
```

### Output

- `output/security_report_YYYYMMDD_HHMMSS.html` (default)
- `output/security_report_YYYYMMDD_HHMMSS.txt`
- `output/security_report_YYYYMMDD_HHMMSS.json`

---

## Cron Examples

### Monthly HTML report via email

```cron
# 1st of every month at 9:00 AM
0 9 1 * * python3 /opt/edgeiq/scripts/report_generator.py \
  --config /opt/edgeiq/config.json \
  --format html \
  --delivery email
```

### Weekly summary to Telegram

```cron
# Every Monday at 8:00 AM
0 8 * * 1 python3 /opt/edgeiq/scripts/report_generator.py \
  --config /opt/edgeiq/config.json \
  --format html \
  --delivery telegram \
  --title "Weekly Security Summary"
```

### Daily text summary to file

```cron
# Daily at 6:00 AM
0 6 * * * python3 /opt/edgeiq/scripts/report_generator.py \
  --config /opt/edgeiq/config.json \
  --format text \
  --delivery file
```

### Multiple targets, throttled

```bash
# Scan 10 targets with 2-second delay between each
python3 scripts/report_generator.py \
  --config config.json \
  --targets example.com testsite.io api.example.org \
  --throttle-ms 2000 \
  --format html \
  --delivery both
```

---

## Report Sections

1. **Executive Summary** — Risk score (0-100), total issues, severity breakdown, targets scanned
2. **XSS Findings** — Sorted by severity; includes URL, parameter, payload, evidence
3. **Network Findings** — Port table, service versions, CVE table with CVSS scores
4. **SSL/Certificate Findings** — Expiry status, grade, security headers, configuration issues
5. **Alert History** — Chronological table of triggered alerts from the Alerting System
6. **Recommendations** — Prioritized fix list, sorted by severity then priority number

---

## Risk Score Calculation

The risk score (0–100) is computed as a weighted sum:

| Severity | Weight per finding |
|----------|-------------------|
| Critical | 25 |
| High | 18 |
| Medium | 10 |
| Low | 4 |
| Info | 2 |

Score is capped at 100. Thresholds:
- **80–100:** CRITICAL
- **60–79:** HIGH
- **40–59:** MEDIUM
- **20–39:** LOW
- **0–19:** MINIMAL

---

## Legal Notice

**DISCLAIMER:** This tool processes security scan data and generates reports. The report generator itself does not perform network reconnaissance or vulnerability scanning. All scan data must be gathered through authorized, legitimate means only.

EdgeIQ Labs accepts no liability for misuse of this tool or data it processes. Users are solely responsible for ensuring they have explicit authorization to scan and assess any systems referenced in report input data.

Report findings are advisory only. EdgeIQ Labs does not guarantee the accuracy, completeness, or timeliness of generated reports. Always validate findings through secondary investigation before taking remediation action.

---

*EdgeIQ Labs — Security Intelligence for the Modern Web*