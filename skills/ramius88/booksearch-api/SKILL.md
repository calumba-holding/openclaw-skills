---
name: booksearch-api
description: Search Amazon KDP books on the BeyondBSR public API and retrieve BSR (Best Sellers Rank) history for a single book. Use this skill whenever the user wants to discover, filter, or research self-published or traditionally published books on Amazon by BSR, category, keyword, royalty range, rating, reviews, publication date, binding type, or marketplace (US, UK, DE, FR, IT, ES, CA), or when the user wants the BSR timeline of a specific ASIN over the last N days. Typical intents include KDP niche research, low-competition book discovery, sales estimation, royalty/revenue projection, competitor analysis, paperback/hardcover filtering, bulk listing of books matching numeric/textual criteria, and single-ASIN BSR history charts. Do not use for price-history timelines, review/rating timelines, or account/user data — only book search and BSR history are exposed.
metadata:
  clawdbot:
    requires:
      env:
        - BOOKSEARCH_API_KEY
---

# BookSearch API

Programmatic search over the BeyondBSR book catalogue plus BSR history retrieval for a single book. Two endpoints, JSON in / JSON out, API-key auth.

## When to use this skill

Use it when the user asks to:

- Find books matching numeric filters: BSR range, rating, reviews count, royalty, page count age, publication recency.
- Discover niches by keyword inclusion/exclusion or Amazon category IDs.
- Filter by marketplace (Amazon.com, .co.uk, .de, .fr, .it, .es, .ca).
- Distinguish self-publishers from traditional publishers.
- Estimate sales (daily / weekly / monthly / quarterly) and revenue per copy.
- Compare BSR averages across multiple time windows (7d / 30d / 90d / 180d / 365d).
- Retrieve the **BSR timeline** of a single book (by `domainId` + `asin`) over the last N days, e.g. for charting rank evolution.

**Do NOT use** for: price-history charts, review/rating timelines, account/user data, or anything not in the response schemas below. Those are out of scope.

## Endpoints

```
POST https://beyondbsr.com/api/v1/books/search
GET  https://beyondbsr.com/api/v1/books/{domainId}/{asin}/bsr-history?days={1..365}
Content-Type: application/json   (search only)
X-API-Key: $BOOKSEARCH_API_KEY
```

## Authentication

- Read the key from the `BOOKSEARCH_API_KEY` env var. Format: `bbsr_live_<43-char-base64url>`.
- **Never** print, echo, log, or include the key in any user-facing output. Never paste it into another tool's input.
- On `401 Unauthorized`: do not retry. Report "API key missing or invalid — check `BOOKSEARCH_API_KEY` env var" and stop.
- Send `X-API-Key` exactly once. Multi-valued headers are rejected.

## Marketplace domains

Map natural-language marketplace references (e.g. "Amazon.de", "the UK store", "amazon italia") to `domainId` using this table:

| domainId | locale | country | name           |
|----------|--------|---------|----------------|
| 1        | com    | US      | United States  |
| 2        | co.uk  | GB      | United Kingdom |
| 3        | de     | DE      | Germany        |
| 4        | fr     | FR      | France         |
| 6        | ca     | CA      | Canada         |
| 8        | it     | IT      | Italy          |
| 9        | es     | ES      | Spain          |

IDs `5` and `7` are intentional gaps in the dataset — do not invent them. The validator technically accepts `1–12`, but only the seven IDs above are guaranteed to return data. If the user asks for a marketplace not listed (e.g. Japan, Australia), tell them it is not currently supported.

## Request schema

All fields are optional except `domainId`. Enums accept either the string name (e.g. `"Weekly"`) or the integer value.

### Required

| Field      | Type | Constraint                  |
|------------|------|-----------------------------|
| `domainId` | int  | One of the 7 IDs in the marketplace table above (validator allows 1–12). |

### BSR filters

| Field      | Type        | Default   | Notes                                                                       |
|------------|-------------|-----------|-----------------------------------------------------------------------------|
| `bsrType`  | enum        | `Weekly`  | `Historical(-1)`, `Current(0)`, `Weekly(7)`, `Days30(8)`, `Days90(9)`, `Days180(10)`, `Days365(11)` |
| `bsrMin`   | int?        | 1         | ≥ 1                                                                         |
| `bsrMax`   | int?        | 100000    | ≥ 1, `bsrMin ≤ bsrMax`                                                      |
| `bsrYear`  | short?      | null      | 2000–(current year + 1). Required together with `bsrMonth`. Use only with `bsrType=Historical`. |
| `bsrMonth` | short?      | null      | 1–12. Required together with `bsrYear`.                                     |

### Product filters

| Field              | Type    | Default     | Notes                                              |
|--------------------|---------|-------------|----------------------------------------------------|
| `bindingType`      | enum?   | null (all)  | `All`, `Paperback`, `Hardcover`                    |
| `publisherType`    | enum?   | `All`       | `All`, `SelfPublishersOnly`, `PublishersOnly`      |
| `interiorType`     | enum?   | `BlackWhite`| `BlackWhite`, `FullColor`                          |
| `vatType`          | enum?   | `Reduced`   | `Reduced`, `Standard`                              |
| `includePreOrders` | bool?   | `false`     | —                                                  |

### Quality filters

| Field         | Type    | Constraint                         |
|---------------|---------|------------------------------------|
| `ratingMin`   | double? | 0.0–5.0, `ratingMin ≤ ratingMax`   |
| `ratingMax`   | double? | 0.0–5.0                            |
| `reviewsMin`  | int?    | ≥ 0, `reviewsMin ≤ reviewsMax`     |
| `reviewsMax`  | int?    | ≥ 0                                |

### Economic filters

| Field                        | Type     | Notes                                                |
|------------------------------|----------|------------------------------------------------------|
| `royaltyMin`                 | decimal? | In currency units, **not** cents. `min ≤ max`.       |
| `royaltyMax`                 | decimal? | —                                                    |
| `monthsSincePublicationMin`  | int?     | `min ≤ max`                                          |
| `monthsSincePublicationMax`  | int?     | —                                                    |

### Discovery

| Field             | Type     | Default | Constraint                                                  |
|-------------------|----------|---------|-------------------------------------------------------------|
| `includeKeywords` | string[] | null    | ≤ 25 items, each ≤ 100 chars, non-empty                     |
| `excludeKeywords` | string[] | null    | ≤ 25 items, each ≤ 100 chars, non-empty                     |
| `categoryIds`     | long[]   | null    | ≤ 100 items, each > 0 (Amazon BrowseNode IDs)               |
| `excludeFiction`  | bool?    | `true`  | When `true` (default), filters out fiction books — i.e. books whose categories all roll up to depth-2 ancestors flagged as fiction (Literature & Fiction, Romance, Mystery, Sci-Fi, Children's Books, Teen/YA, etc.) under the local Books root for the requested marketplace. A book is kept if **at least one** of its categories has a depth-2 ancestor flagged as non-fiction. Set `false` to include fiction. **Auto-disabled** when `categoryIds` is non-empty: explicit category intent overrides the fiction filter, otherwise passing a fiction category with the default would silently return zero results. Currently unsupported on Amazon.ca (`domainId=6`): with `excludeFiction=true` no books are returned for CA — pass `false` for that marketplace. |

### Pagination

| Field    | Type | Default | Range      |
|----------|------|---------|------------|
| `limit`  | int? | 100     | 1–300      |
| `offset` | int? | 0       | 0–100000   |

## Workflow

1. **Marketplace** — Identify `domainId` from intent using the marketplace table. If ambiguous (e.g. "Amazon"), ask which country.
2. **Translate** — Map every natural-language filter to its schema field. Don't guess enum values; use the table. Note: by default fiction is excluded (`excludeFiction=true`). If the user asks for fiction (e.g. "romance", "mystery novels", "show me fiction too") or a mixed catalog, set `excludeFiction: false` explicitly. Most KDP/low-content niche queries are non-fiction so the default is usually correct.
3. **Pagination** — Default to `limit: 50`. Raise to 100–300 only if the user explicitly wants many results. Start with `offset: 0`.
4. **Send** — POST the JSON body. Inspect the status code first.
5. **Paginate if needed** — If `returnedCount == limit`, more results likely exist. Offer to fetch the next page with `offset += limit`.
6. **Present** — Surface `title`, `asin`, `bsr`, sales/revenue estimates, and a clickable cover URL (see response notes).

## Example request

```json
{
  "domainId": 3,
  "bsrType": "Days90",
  "bsrMin": 1,
  "bsrMax": 50000,
  "bindingType": "Paperback",
  "publisherType": "SelfPublishersOnly",
  "ratingMin": 4.0,
  "reviewsMin": 10,
  "interiorType": "BlackWhite",
  "vatType": "Reduced",
  "royaltyMin": 2.50,
  "royaltyMax": 15.00,
  "monthsSincePublicationMax": 24,
  "includePreOrders": false,
  "includeKeywords": ["journal", "notebook"],
  "excludeKeywords": ["coloring"],
  "categoryIds": [266162, 3248921],
  "excludeFiction": false,
  "limit": 50,
  "offset": 0
}
```

## Example cURL

```bash
curl -X POST "https://beyondbsr.com/api/v1/books/search" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $BOOKSEARCH_API_KEY" \
  -d '{
    "domainId": 3,
    "bsrType": "Days90",
    "bsrMax": 50000,
    "bindingType": "Paperback",
    "publisherType": "SelfPublishersOnly",
    "ratingMin": 4.0,
    "limit": 50
  }'
```

## Response schema

### Envelope — `BookSearchApiResponse`

| Field           | Type    | Notes                                                              |
|-----------------|---------|--------------------------------------------------------------------|
| `returnedCount` | int     | Items in **this page**. NOT a total-match count (no total exposed).|
| `limit`         | int     | Effective limit applied (capped at 300).                           |
| `offset`        | int     | Effective offset applied.                                          |
| `results`       | array   | `BookSearchResultDto[]`. Empty if no match.                        |

### Result item — `BookSearchResultDto` (most relevant fields)

| Field                | Type     | Notes                                                                                  |
|----------------------|----------|----------------------------------------------------------------------------------------|
| `id`                 | long     | Internal book ID.                                                                      |
| `asin`               | string   | 10-char Amazon ASIN.                                                                   |
| `title`              | string   | Full title.                                                                            |
| `authors`            | string?  | Comma-separated, ordered by `display_order`.                                           |
| `publicationDate`    | datetime?| Nullable.                                                                              |
| `publisher`          | string?  | Manufacturer/publisher name.                                                           |
| `coverImageFilename` | string?  | Build URL: `https://m.media-amazon.com/images/I/{filename}`.                           |
| `imageFilenames`     | string[] | All carousel images (same URL pattern).                                                |
| `rating`             | double   | 0.0–5.0.                                                                               |
| `reviews`            | int      | Total reviews.                                                                         |
| `bsr`                | int      | **The column matching the requested `bsrType`** — i.e. the value filtered/sorted on.   |
| `bsrCurrent`         | int?     | Latest snapshot BSR, regardless of `bsrType`.                                          |
| `avgBsr7d`           | int?     | Always populated.                                                                      |
| `avgBsr30d`          | int?     | Always populated.                                                                      |
| `avgBsr90d`          | int?     | Always populated.                                                                      |
| `avgBsr180d`         | int?     | Always populated.                                                                      |
| `avgBsr365d`         | int?     | Always populated.                                                                      |
| `pageCount`          | int?     | —                                                                                      |
| `priceCents`         | int?     | List price (MSRP) in cents.                                                            |
| `dailyEstimate`      | decimal  | Estimated copies/day from BSR model.                                                   |
| `weeklyEstimate`     | decimal  | Estimated copies/week.                                                                 |
| `monthlyEstimate`    | decimal  | Estimated copies/month.                                                                |
| `quarterlyEstimate`  | decimal  | Copies/quarter (needs ≥ 13 weeks of data).                                             |
| `royalty*Cents`      | int?     | Per-copy royalty in cents. 4 combinations: B/W or Color × Reduced or Standard VAT.     |
| `*Revenue*Cents`     | long?    | Derived = estimate × royalty. 16 fields total: {daily,weekly,monthly,quarterly} × {Black,Color} × {Reduced,Standard}. |
| `binding`            | string?  | Localised label (e.g. `"Paperback"`, `"Hardcover"`, `"Non-standard"`).                 |
| `dimensions`         | string?  | Formatted, prefixed by binding. Example: `"Paperback: 152 x 8 x 229 mm"`.              |
| `trim/spineWidthMm`  | int?     | Trim/spine measurements.                                                               |

**Important caveats**

- All royalty and revenue fields are in **cents** — divide by 100 before showing currency.
- `bsr` ≠ `bsrCurrent`. `bsr` is whatever column was chosen by `bsrType`; `bsrCurrent` is always the latest snapshot.
- In `bsrType=Historical` mode, the `avgBsrXd` averages come from the current snapshot table while `bsr` itself is the historical month value — there is a documented temporal asymmetry inside the same response. Mention this if the user is doing a strict historical analysis.

## BSR History endpoint

Single-ASIN BSR timeline. Returns raw snapshots from the time-series store, ordered ascending by `recordedAt`.

```
GET https://beyondbsr.com/api/v1/books/{domainId}/{asin}/bsr-history?days={1..365}
X-API-Key: $BOOKSEARCH_API_KEY
Accept: application/json
```

### When to use

- The user has a specific ASIN and wants its BSR over time (chart, drill-down, sanity-check the search-time `avgBsrXd` averages).
- The user wants to verify a book's recent rank trajectory (e.g. "is it gaining or losing visibility?").

If the user has filter criteria but no specific ASIN, use `POST /search` first, then call this endpoint per ASIN of interest.

### Path & query parameters

| Param      | In    | Type   | Required | Constraint                                                                 |
|------------|-------|--------|----------|----------------------------------------------------------------------------|
| `domainId` | path  | int    | yes      | One of the 7 marketplace IDs (see Marketplace domains table; validator allows 1–12). |
| `asin`     | path  | string | yes      | Exactly 10 chars, regex `^[A-Z0-9]{10}$` (uppercase letters / digits only). |
| `days`     | query | int?   | no       | 1–365. Default `365`. Window is `[now - days, now]` UTC.                   |

### Example request

```
GET /api/v1/books/1/1635864348/bsr-history?days=90
X-API-Key: $BOOKSEARCH_API_KEY
Accept: application/json
```

### Example cURL

```bash
curl -X GET "https://beyondbsr.com/api/v1/books/1/1635864348/bsr-history?days=90" \
  -H "X-API-Key: $BOOKSEARCH_API_KEY" \
  -H "Accept: application/json"
```

### Response schema — `BookBsrHistoryApiResponse`

| Field         | Type        | Notes                                                              |
|---------------|-------------|--------------------------------------------------------------------|
| `asin`        | string      | Echoed from request.                                               |
| `domainId`    | int         | Echoed from request.                                               |
| `fromUtc`     | datetime    | Window start (`now - days`), UTC.                                  |
| `toUtc`       | datetime    | Window end (`now`), UTC.                                           |
| `pointCount`  | int         | Number of BSR snapshots in `points`.                               |
| `points`      | array       | `BsrPointDto[]` ordered ascending by `recordedAt`.                 |

`BsrPointDto`:

| Field              | Type      | Notes                                                          |
|--------------------|-----------|----------------------------------------------------------------|
| `recordedAt`       | datetime  | UTC timestamp of the snapshot.                                 |
| `bestSellersRank`  | int?      | BSR at that timestamp. May be null if Keepa returned no rank.  |

Example body:

```json
{
  "asin": "1635864348",
  "domainId": 1,
  "fromUtc": "2026-01-27T00:00:00Z",
  "toUtc": "2026-04-27T00:00:00Z",
  "pointCount": 412,
  "points": [
    { "recordedAt": "2026-01-27T03:14:00Z", "bestSellersRank": 1234 },
    { "recordedAt": "2026-01-27T15:02:00Z", "bestSellersRank": 1218 }
  ]
}
```

### Status codes (BSR history specific)

| Code | Meaning                       | Notes                                                                 |
|------|-------------------------------|-----------------------------------------------------------------------|
| 200  | OK                            | `pointCount` may be 0 if no snapshots exist in the window.            |
| 400  | Validation failed             | `ValidationProblemDetails`. Common causes: `days` out of range, `asin` wrong format, `domainId` out of `[1,12]`. |
| 404  | ASIN not found for that domain| Empty body. The book is not tracked in BeyondBSR for this marketplace. Tell the user — do not retry with the same pair. |
| 401 / 429 / 500 | See generic table below.            |

### Caveats

- Granularity is **raw**: Keepa snapshots arrive 1–4× per day on actively-tracked books. A 365-day window typically yields 365–1460 points. No daily aggregation is applied.
- The endpoint returns only `(recordedAt, bestSellersRank)`. Use `POST /search` if you also need rating/review/price data.
- ASIN is case-sensitive — must be uppercase. `1635864348` (all digits) is valid.
- Default 365 days is the cap. Longer histories are not exposed; do not retry with `days > 365`.

## Status codes & error handling

| Code | Meaning                | Body                                       | Agent action                                                                  |
|------|------------------------|--------------------------------------------|-------------------------------------------------------------------------------|
| 200  | OK (may be empty list) | `BookSearchApiResponse`                    | Parse `results`. Empty array = no matches, not an error.                      |
| 400  | Validation failed      | `ValidationProblemDetails` (RFC 7807)      | Read the `errors` map, fix the body, do not retry blindly. Surface the issue. |
| 401  | Auth failed            | empty + `WWW-Authenticate: ApiKey realm="BeyondBSR"` | Stop. Report misconfigured `BOOKSEARCH_API_KEY`. Do not retry.       |
| 429  | Rate limit exceeded    | `"Rate limit exceeded. Please try again later."` + `Retry-After` header | Honour `Retry-After`. Back off. Do not hammer the endpoint. |
| 500  | Unhandled server error | `ProblemDetails` JSON                      | Retry once after a few seconds. If it persists, escalate to the user.         |

### Example 400 body

```json
{
  "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
  "title": "One or more validation errors occurred.",
  "status": 400,
  "errors": {
    "DomainId": ["DomainId must be between 1 and 12."],
    "Limit": ["Limit must be between 1 and 300."]
  }
}
```

## Sorting & pagination notes

- Default sort: `ORDER BY <chosen BSR column> ASC` (lower BSR = better seller appears first).
- Historical mode (`bsrType=Historical` + `bsrYear`/`bsrMonth`): sorted by the historical monthly BSR rank ASC.
- Tie-breaker is non-deterministic — books with identical BSR may appear in different orders across page fetches. Warn the user if they need a perfectly stable ordering.
- No `orderBy` parameter is exposed.

## Limits

- **Rate limit**: 120 requests/minute per API key. Shared across all callers using the same key.
- **Body size**: 128 KB max.
- **Page size**: 300 results max per request (`limit ≤ 300`).
- **Offset cap**: 100,000 (deep pagination beyond this is not supported — refine filters instead).
