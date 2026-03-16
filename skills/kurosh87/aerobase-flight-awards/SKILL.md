version: 3.1.6
name: aerobase-flight-awards
description: Search 24+ airline loyalty programs for award space with miles cost, seat availability, and jetlag scores
metadata: {"openclaw": {"emoji": "✈️", "primaryEnv": "AEROBASE_API_KEY", "user-invocable": true, "homepage": "https://aerobase.app"}}
---

# Aerobase Flight Awards ✈️

Use this skill when users want fast, practical award options for a route. It turns a route + date into ranked redemption choices with mileage cost, availability, and recovery context.

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

- Find available award seats and seat scarcity by cabin.
- Prioritize low-mileage and high-confidence options.
- Give jetlag context so users choose trips that are easier to recover from.

## Search

**POST /api/v1/awards/search** — Search cached award availability by route.

Body:
`{ from, to, cabin?, date?, date_from?, date_to?, limit? }`

Required:
- `from`, `to` (3-letter IATA codes)

Optional:
- `cabin` (`economy`, `business`, `premium`, `first`)
- `date` (single departure date: `YYYY-MM-DD`)
- `date_from`, `date_to` (range search, both `YYYY-MM-DD`)
- `limit` (max results, capped at 100)

Returns array items:
- `from`, `to`, `date`
- `cabin`, `miles`, `seats_remaining`
- `program` (program source)
- `departure_time`, `arrival_time`
- `jetlag_score_k2` (higher is better)

## Alerts

- **POST /api/awards/alerts** — create alert for a route/date band.
- **GET /api/awards/alerts** — list user alerts.
- **PATCH /api/awards/alerts/{id}** — activate/deactivate alert.
- **DELETE /api/awards/alerts/{id}** — remove alert.

## Trip detail

**GET /api/v1/awards/trips** — fetch segment-level trip details for a cache hit.

Use either:
- `id` from `/api/v1/awards/search` results, or
- `origin`, `destination`, `date`, `source` as query params.

## Marketing/UX guidance

- Lead with: value, scarcity, and recovery quality in one short line.
- Keep follow-up options limited and concrete:
  - "Show best 3 in business"
  - "Track this route daily"
  - "Compare with one alternate date"
- If no results return: "No data yet for this window; I can retry in X minutes."

## Safety

- Do not request or store passwords, OTP, cookies, loyalty logins, or any secrets.
- Use only the API key flow in setup.

## Usage limits

- Free: 5 requests/day
- Pro: 500 API calls/month (upgrade at $10.99/month)
- Lifetime: $149.99 for 500 API calls/month


## Ranking logic

- Compare by `miles` within same cabin/date band first.
- Use `seats_remaining` to rank hard-to-find options higher.
- Use `jetlag_score_k2` as a supporting quality signal.
- If user shares a cash fare, compute cents-per-point:
  `cash_price_usd * 100 / miles`.
