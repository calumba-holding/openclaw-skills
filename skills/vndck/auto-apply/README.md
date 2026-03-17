# Mokaru Job Search

Search for jobs, track applications through your pipeline, and access your career profile - all from your AI agent. Does not submit applications directly - the user visits the apply link to complete the application.

## What it does

- **Search jobs** - Find job listings by keywords, location, remote preference, and more
- **Track applications** - Save jobs to your tracker, update status as you progress, add notes and priority
- **Read your profile** - Access your skills, work experience, and education to personalize job searches
- **Provide apply links** - Each job result includes a direct link to the application page

## Getting an API key

1. Sign in to your Mokaru account at [mokaru.ai](https://mokaru.ai)
2. Go to **Settings > API Keys**
3. Create a new key with the scopes you need: `jobs:search`, `tracker:read`, `tracker:write`, `profile:read`
4. Copy the key (starts with `mk_`) and set it as `MOKARU_API_KEY` in your environment

## Example usage

```
> Find me remote React jobs in the US

Searching for "React" jobs, remote, in the US...
Found 47 results. Here are the top 5:

1. Senior React Engineer - Stripe (Remote, US) - $180k-$220k/yr
2. React Developer - Shopify (Remote) - $140k-$170k/yr
...

> Save the Stripe one to my tracker

Saved "Senior React Engineer" at Stripe to your application tracker.
Apply here: https://stripe.com/careers/1234

> I applied, mark it

Updated status to "applied".
```

## Scopes reference

| Scope           | Endpoints                              |
|-----------------|----------------------------------------|
| `jobs:search`   | Search job listings                    |
| `tracker:read`  | List tracked applications              |
| `tracker:write` | Create and update tracked applications |
| `profile:read`  | Read career profile                    |

## Learn more

Full API documentation: [mokaru.ai/docs/api](https://mokaru.ai/docs/api)
