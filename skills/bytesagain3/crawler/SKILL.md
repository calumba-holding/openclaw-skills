---
name: crawler
version: "2.0.0"
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
license: MIT-0
tags: [crawler, tool, utility]
description: "Crawl websites, extract links, and scrape content with rate limiting. Use when scraping pages, extracting links, generating sitemaps."
---

# Crawler

Crawler v2.0.0 — a data toolkit for ingesting, transforming, querying, filtering, aggregating, and exporting structured data entries. Each command logs timestamped records locally, making Crawler ideal for tracking web scraping workflows, managing crawl data pipelines, and auditing data processing activity.

## Commands

| Command | Description |
|---------|-------------|
| `crawler ingest <input>` | Ingest a data entry (or view recent ingests with no args) |
| `crawler transform <input>` | Log a transform operation (or view recent transforms) |
| `crawler query <input>` | Record a query (or view recent queries) |
| `crawler filter <input>` | Record a filter operation (or view recent filters) |
| `crawler aggregate <input>` | Record an aggregation (or view recent aggregations) |
| `crawler visualize <input>` | Log a visualization task (or view recent visualizations) |
| `crawler export <input>` | Log an export entry (or view recent exports) |
| `crawler sample <input>` | Record a sampling operation (or view recent samples) |
| `crawler schema <input>` | Log a schema definition (or view recent schemas) |
| `crawler validate <input>` | Record a validation check (or view recent validations) |
| `crawler pipeline <input>` | Log a pipeline step (or view recent pipeline entries) |
| `crawler profile <input>` | Record a profiling run (or view recent profiles) |
| `crawler stats` | Show summary statistics across all log files |
| `crawler search <term>` | Search all entries for a keyword (case-insensitive) |
| `crawler recent` | Show the 20 most recent activity entries |
| `crawler status` | Health check — version, entry count, disk usage, last activity |
| `crawler help` | Display all available commands |
| `crawler version` | Print version string |

Each data command (ingest, transform, query, filter, aggregate, visualize, export, sample, schema, validate, pipeline, profile) works identically:

- **With arguments:** saves a timestamped entry to `~/.local/share/crawler/<command>.log` and logs to `history.log`
- **Without arguments:** displays the 20 most recent entries from that command's log file

## Data Storage

All data is stored locally in `~/.local/share/crawler/`:

| File | Contents |
|------|----------|
| `ingest.log` | Timestamped ingest records |
| `transform.log` | Transform operation records |
| `query.log` | Query records |
| `filter.log` | Filter operation records |
| `aggregate.log` | Aggregation records |
| `visualize.log` | Visualization task records |
| `export.log` | Export entry records |
| `sample.log` | Sampling records |
| `schema.log` | Schema definition records |
| `validate.log` | Validation check records |
| `pipeline.log` | Pipeline step records |
| `profile.log` | Profiling records |
| `history.log` | Unified activity log for all commands |

The `stats` command reads all `.log` files and reports line counts per file, total entries, data directory size, and the timestamp of the first recorded activity.

The `export` utility function (called internally via `_export`) can produce **JSON**, **CSV**, or **TXT** output files under the data directory.

## Requirements

- **Bash** (4.0+)
- **coreutils** — `date`, `wc`, `du`, `head`, `tail`, `grep`, `basename`, `cat`
- No external dependencies, API keys, or network access required
- Works on Linux and macOS

## When to Use

1. **Tracking web crawl data pipelines** — use `ingest` to log URLs or pages crawled, `transform` to record data cleaning steps, and `export` to track output generation
2. **Managing scraping workflows** — use `pipeline` to document each stage of a multi-step scraping pipeline, with `validate` to confirm data quality at each step
3. **Profiling and sampling crawl results** — use `profile` to log performance metrics of crawls and `sample` to record sampling decisions for large datasets
4. **Querying and filtering collected data** — use `query` and `filter` to log search criteria and filtering rules applied to crawled content
5. **Auditing and searching historical activity** — use `search <term>` to find specific entries across all logs, or `stats` for a high-level overview of all data categories

## Examples

```bash
# Ingest a crawled URL
crawler ingest "https://example.com/products — 142 items found"

# View recent ingest entries
crawler ingest

# Log a transform step
crawler transform "strip HTML tags, extract product names and prices"

# Record a filtering rule
crawler filter "exclude pages with HTTP 404 status"

# Log an aggregation
crawler aggregate "total products by category across 3 domains"

# Validate data quality
crawler validate "all price fields are numeric and > 0"

# Search across all logs
crawler search "product"

# View summary statistics
crawler stats

# Check health status
crawler status

# View the 20 most recent activities
crawler recent
```

## How It Works

Crawler uses a simple append-only log architecture. Every command writes a pipe-delimited record (`timestamp|value`) to its dedicated log file. The `history.log` file captures a unified timeline of all operations with the format `MM-DD HH:MM command: value`.

This design makes Crawler:
- **Fast** — pure bash, no database overhead
- **Transparent** — all data is human-readable plain text
- **Portable** — works anywhere bash runs, no install needed
- **Auditable** — every action is timestamped and traceable

---

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
