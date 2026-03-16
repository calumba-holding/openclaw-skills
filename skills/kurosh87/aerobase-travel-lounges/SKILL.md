---
name: aerobase-lounges
version: 3.1.6
description: Airport lounge access and recovery recommendations
metadata: {"openclaw": {"emoji": "🏧", "primaryEnv": "AEROBASE_API_KEY", "user-invocable": true, "homepage": "https://aerobase.app"}}
---

# Airport Lounge Access & Recovery 🏧

Use this for concrete, practical layover support: where to go, what to expect, and how it affects recovery.

## Setup

Use this skill by getting a free API key at https://aerobase.app/openclaw-travel-agent and setting `AEROBASE_API_KEY` in your agent environment.
This skill is API-only: no scraping, no browser automation, and no user credential collection.

Usage is capped at 5 requests/day for free users.
Upgrade to Pro ($10.99) at https://aerobase.app/openclaw-travel-agent for 500 API calls/month.

## Agent API Key Protocol

- Base URL: `https://aerobase.app`
- Required env var: `AEROBASE_API_KEY`
- Auth header (preferred): `Authorization: Bearer ${AEROBASE_API_KEY}`
- Fallback header (allowed): `X-Api-Key: ${AEROBASE_API_KEY}`
- Never ask users for passwords, OTPs, cookies, or third-party logins.
- Never print raw API keys in output; redact as `sk_live_***`.

### Request rules

- Use only Aerobase endpoints documented in this skill.
- Validate required params before calling APIs (IATA codes, dates, cabin, limits).
- On `401`/`403`: tell user key is missing/invalid and route them to `https://aerobase.app/openclaw-travel-agent`.
- On `429`: explain free-tier quota (`5 requests/day`) and suggest Pro (`$10.99/month`, 500 API calls/month) or Lifetime ($149.99, 500 API calls/month).
- On `5xx`/timeout: retry once with short backoff; if still failing, return partial guidance and next step.
- Use concise responses: top options first, then 1-2 follow-up actions.

## What this skill does

- Find lounge options at specific airports.
- Return recommendations by amenities and rest utility.
- Support recovery-aware layover planning.

## Endpoints

- **GET /api/v1/lounges** — search lounges by airport and filters.
- **GET /api/airports/{code}/lounges** — airport-specific lounge list.

## Response style

- Show recovery score, lounge amenities, and best use case.
- Recommend showers, quiet zones, and nap plans aligned to layover duration.
- For short layovers, prefer high-impact options first.

## Usage limits

- Free: 5 requests/day
- Pro: 500 API calls/month (upgrade at $10.99/month)
- Lifetime: $149.99 for 500 API calls/month

## Safety

- No credential collection and no third-party login collection.
