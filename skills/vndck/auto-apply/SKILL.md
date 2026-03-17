---
name: auto-apply
description: Search jobs, track applications, and prepare to apply with Mokaru. Does not submit applications directly - the user or their agent handles the actual application.
requires:
  env:
    - MOKARU_API_KEY
  bins:
    - curl
    - jq
---

# Mokaru Job Search & Application Tracker

You can search for jobs, save and track job applications, and read the user's career profile through the Mokaru API.

**Important:** This skill does NOT submit job applications on behalf of the user. It helps with the preparation: finding jobs, saving them to a tracker, updating application status, and reviewing the user's profile. The user (or their browser agent) must visit the `applyLink` from search results to actually apply. When the user says "apply", save the job to their tracker and provide the apply link so they can complete the application themselves.

## Authentication

Every request requires a Bearer token. The token is stored in the `MOKARU_API_KEY` environment variable and starts with `mk_`.

Include this header on all requests:

```
Authorization: Bearer $MOKARU_API_KEY
```

## Base URL

```
https://api.mokaru.ai
```

All endpoints are under `/v1/`.

---

## Endpoints

### 1. Search Jobs

**When to use:** The user wants to find job listings. They might say "find me React jobs in New York" or "search for remote marketing roles."

**Method:** `POST /v1/jobs/search`

**Required scope:** `jobs:search`

**Rate limit:** 30 requests per minute

**Request body (JSON):**

| Field            | Type    | Required | Description                                                  |
|------------------|---------|----------|--------------------------------------------------------------|
| `query`          | string  | Yes      | Job search keywords (e.g. "software engineer")               |
| `location`       | string  | No       | City, state, or country (e.g. "San Francisco, CA")           |
| `remote`         | boolean | No       | Filter for remote jobs only                                  |
| `employmentType` | string  | No       | E.g. "fulltime", "parttime", "contract"                      |
| `datePosted`     | string  | No       | Recency filter (e.g. "today", "3days", "week", "month")      |
| `page`           | number  | No       | Page number, starts at 1. Each page returns up to 25 results |

**Curl example:**

```bash
curl -s -X POST https://api.mokaru.ai/v1/jobs/search \
  -H "Authorization: Bearer $MOKARU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "frontend engineer",
    "location": "New York",
    "remote": true,
    "page": 1
  }' | jq .
```

**Response shape:**

```json
{
  "data": [
    {
      "id": "clx...",
      "title": "Frontend Engineer",
      "company": "Acme Corp",
      "companyLogo": "https://...",
      "location": "New York, NY",
      "isRemote": true,
      "employmentType": "fulltime",
      "applyLink": "https://...",
      "salaryMin": 120000,
      "salaryMax": 160000,
      "salaryPeriod": "year",
      "postedAt": "2026-03-10T..."
    }
  ],
  "total": 142,
  "hasMore": true,
  "page": 1,
  "source": "database+providers"
}
```

The `source` field indicates whether results came from the internal database only (`"database"`) or also from external providers (`"database+providers"`). External providers require a Plus subscription.

**How to use the results:** Present jobs in a readable list. Include the title, company, location, salary range (if available), and the apply link. If `hasMore` is true, you can fetch the next page.

---

### 2. Create Application

**When to use:** The user wants to save or track a job. They might say "save this job" or "add this to my tracker." You can also use this right after a search to save a result.

**Method:** `POST /v1/tracker/applications`

**Required scope:** `tracker:write`

**Rate limit:** 20 requests per minute

**Request body (JSON):**

| Field            | Type   | Required | Description                                                                                      |
|------------------|--------|----------|--------------------------------------------------------------------------------------------------|
| `jobTitle`       | string | Yes      | Job title (max 200 chars)                                                                        |
| `company`        | string | Yes      | Company name (max 200 chars)                                                                     |
| `location`       | string | No       | Job location (max 200 chars)                                                                     |
| `jobUrl`         | string | No       | URL of the job posting (must be a valid URL). Used for duplicate detection                       |
| `jobDescription` | string | No       | Full job description text (max 50,000 chars). Required for `autoPrepare` (min 500 chars).        |
| `jobListingId`   | string | No       | If saving from a Mokaru search result, pass the job's `id` to automatically pull salary/details  |
| `source`         | string | No       | One of: `LinkedIn`, `CompanyWebsite`, `JobWebsite`, `Referral`, `Agency`, `Other`. Defaults to `Other` |
| `autoPrepare`    | boolean | No      | When `true`, Mokaru duplicates the user's default resume and tailors it to the job description using AI. Requires Plus plan, a default resume, and a job description of at least 500 characters. |

**Curl example:**

```bash
curl -s -X POST https://api.mokaru.ai/v1/tracker/applications \
  -H "Authorization: Bearer $MOKARU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jobTitle": "Frontend Engineer",
    "company": "Acme Corp",
    "location": "New York, NY",
    "jobUrl": "https://acme.com/careers/frontend",
    "jobListingId": "clx...",
    "source": "JobWebsite",
    "autoPrepare": true
  }' | jq .
```

**Response shape:**

```json
{
  "success": true,
  "applicationId": "clx...",
  "existing": false,
  "autoPrepare": true
}
```

If `existing` is `true`, the application was already tracked (matched by `jobUrl`) and the existing ID is returned. No duplicate is created.

If `autoPrepare` is `true` in the response, Mokaru is tailoring the user's resume in the background (~30 seconds). The application status will be `preparing` until done.

**Auto-prep errors:** If auto-prep fails, the API returns a clear error code:
- `PLAN_REQUIRED` (403) - user needs a Plus plan
- `NO_DEFAULT_RESUME` (400) - user must set a default resume in Mokaru first
- `JOB_DESCRIPTION_TOO_SHORT` (400) - job description must be at least 500 characters

**Workflow tip:** When saving a job from search results, pass the `id` from the search result as `jobListingId`. This auto-fills salary and description data. Add `"autoPrepare": true` to also tailor the resume automatically.

---

### 3. List Applications

**When to use:** The user wants to see their tracked applications. They might ask "show my applications" or "what jobs have I applied to?"

**Method:** `GET /v1/tracker/applications`

**Required scope:** `tracker:read`

**Rate limit:** 60 requests per minute

**Query parameters:**

| Param    | Type   | Required | Description                                                   |
|----------|--------|----------|---------------------------------------------------------------|
| `status` | string | No       | Filter by status (see status values below)                    |
| `limit`  | number | No       | Results per page, default 25, max 100                         |
| `offset` | number | No       | Number of results to skip for pagination                      |

**Valid status values:** `watchlist`, `preparing`, `applied`, `response`, `screening`, `interview_scheduled`, `interviewed`, `offer`, `negotiating`, `accepted`, `rejected`, `withdrawn`, `no_response`

**Curl example:**

```bash
curl -s -G https://api.mokaru.ai/v1/tracker/applications \
  -H "Authorization: Bearer $MOKARU_API_KEY" \
  --data-urlencode "status=applied" \
  --data-urlencode "limit=10" | jq .
```

**Response shape:**

```json
{
  "data": [
    {
      "id": "clx...",
      "jobTitle": "Frontend Engineer",
      "company": "Acme Corp",
      "location": "New York, NY",
      "jobUrl": "https://acme.com/careers/frontend",
      "status": "applied",
      "source": "JobWebsite",
      "priority": 3,
      "salaryMin": 120000,
      "salaryMax": 160000,
      "appliedDate": "2026-03-10T...",
      "createdAt": "2026-03-10T...",
      "updatedAt": "2026-03-12T..."
    }
  ],
  "total": 24,
  "hasMore": true,
  "limit": 10,
  "offset": 0
}
```

**How to present:** Show the list as a table or concise summary. Include status, company, job title, and any salary info. If `hasMore` is true, let the user know there are more results.

---

### 4. Update Application

**When to use:** The user wants to change the status, priority, notes, or details of a tracked application. They might say "mark that application as interviewed" or "set priority to high."

**Method:** `PATCH /v1/tracker/applications/{id}`

**Required scope:** `tracker:write`

**Rate limit:** 20 requests per minute

**Request body (JSON) - all fields optional, at least one required:**

| Field      | Type   | Description                                           |
|------------|--------|-------------------------------------------------------|
| `status`   | string | New status (see valid status values above)            |
| `priority` | number | 1 (lowest) to 5 (highest)                            |
| `notes`    | string | Free-text notes (max 5,000 chars)                     |
| `jobTitle` | string | Updated job title (max 200 chars)                     |
| `company`  | string | Updated company name (max 200 chars)                  |
| `location` | string | Updated location (max 200 chars)                      |

**Curl example:**

```bash
curl -s -X PATCH https://api.mokaru.ai/v1/tracker/applications/clx_abc123 \
  -H "Authorization: Bearer $MOKARU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "interviewed",
    "priority": 5,
    "notes": "Great conversation with the hiring manager"
  }' | jq .
```

**Response shape:**

```json
{
  "success": true,
  "application": {
    "id": "clx_abc123",
    "jobTitle": "Frontend Engineer",
    "company": "Acme Corp",
    "location": "New York, NY",
    "status": "interviewed",
    "priority": 5,
    "notes": "Great conversation with the hiring manager",
    "updatedAt": "2026-03-15T..."
  }
}
```

Status changes are automatically recorded in the application's timeline.

---

### 5. Get Profile

**When to use:** The user wants to see their career profile, or you need context about their background to tailor a job search. For example, "what skills do I have on file?" or before searching, to understand their experience level.

**Method:** `GET /v1/profile`

**Required scope:** `profile:read`

**Rate limit:** 30 requests per minute

**Curl example:**

```bash
curl -s https://api.mokaru.ai/v1/profile \
  -H "Authorization: Bearer $MOKARU_API_KEY" | jq .
```

**Response shape:**

```json
{
  "data": {
    "firstName": "Jane",
    "lastName": "Doe",
    "email": "jane@example.com",
    "phone": "+1 555-0100",
    "address": "New York, NY",
    "country": "US",
    "province": "NY",
    "seniority": "mid",
    "jobTitle": "Frontend Engineer",
    "summary": "5 years of experience in...",
    "sector": "Technology",
    "linkedIn": "https://linkedin.com/in/janedoe",
    "website": "https://janedoe.dev",
    "portfolio": null,
    "jobTitles": [
      { "title": "Frontend Engineer", "displayOrder": 0 },
      { "title": "React Developer", "displayOrder": 1 }
    ],
    "skills": [
      { "name": "React", "category": "Frontend", "level": "expert" },
      { "name": "TypeScript", "category": "Frontend", "level": "advanced" }
    ],
    "workExperiences": [
      {
        "jobTitle": "Frontend Engineer",
        "company": "TechCo",
        "location": "New York, NY",
        "startDate": "2022-01-15T00:00:00.000Z",
        "endDate": null,
        "isCurrent": true,
        "description": "Building the design system...",
        "responsibilities": ["Led frontend architecture"],
        "achievements": ["Reduced bundle size by 40%"]
      }
    ],
    "educations": [
      {
        "school": "MIT",
        "degree": "Bachelor of Science",
        "field": "Computer Science",
        "startDate": "2016-09-01T00:00:00.000Z",
        "endDate": "2020-06-15T00:00:00.000Z",
        "isCurrent": false
      }
    ]
  }
}
```

**How to use:** Pull the user's job titles, skills, and seniority to craft better search queries. Mention their background when recommending jobs.

---

## Workflows

### Finding, saving, and preparing for jobs

1. Optionally call `GET /v1/profile` to understand the user's background.
2. Call `POST /v1/jobs/search` with a query based on what the user asked for (or derived from their profile).
3. Present the results with the `applyLink` for each job.
4. If the user wants to save one, call `POST /v1/tracker/applications` with the job details and pass the job `id` as `jobListingId`. Add `"autoPrepare": true` to tailor their resume automatically.
5. To actually apply, the user must visit the `applyLink` themselves. Provide it clearly.

### Reviewing application pipeline

1. Call `GET /v1/tracker/applications` to get all applications, or filter by status.
2. Summarize the pipeline: how many in each status, which are highest priority.
3. If the user wants to update one, call `PATCH /v1/tracker/applications/{id}`.

---

## Error Handling

| Status | Meaning                  | What to do                                                        |
|--------|--------------------------|-------------------------------------------------------------------|
| 400    | Bad request / validation | Check the `details` field for which fields failed. Fix and retry. |
| 401    | Invalid or missing token | Tell the user their API key is invalid or expired.                |
| 403    | Insufficient permissions | The API key does not have the required scope for this endpoint.   |
| 404    | Not found                | The application or profile does not exist.                        |
| 429    | Rate limited             | Wait before retrying. Do not hammer the endpoint.                 |
| 500    | Server error             | Retry once. If it persists, tell the user something went wrong.   |

Always check the HTTP status before parsing the response body. On errors, the body contains an `error` field with a human-readable message.

---

## Documentation

Full API documentation is available at [docs.mokaru.ai](https://docs.mokaru.ai).
