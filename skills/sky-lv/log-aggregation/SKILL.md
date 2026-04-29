# log-aggregation

Centralized log collection and analysis for AI agents. Aggregate logs from multiple sources, search, and generate insights.

## Overview

A comprehensive log management system that helps agents collect, parse, search, and analyze logs from various sources.

## Features

- **Log Collection**: Gather logs from files, stdout, syslog, cloud services
- **Parsing**: Automatic log parsing and field extraction
- **Search**: Powerful full-text search and filtering
- **Aggregation**: Group and summarize log data
- **Alerting**: Detect errors and anomalies in real-time
- **Visualization**: Log dashboards and charts
- **Export**: Export logs to files, SIEM systems

## Commands

### Collect Logs

```
collect logs from /var/log/app/*.log
```

### Search Logs

```
search error logs from last hour
```

### Create Alert

```
alert when error rate exceeds 10 per minute
```

## Use Cases

- Application debugging
- Error tracking
- Security audit
- Performance analysis
- Compliance logging

## Requirements

- Node.js 18+
- Optional: Elasticsearch, Loki for storage
