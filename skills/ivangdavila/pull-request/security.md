# Security Considerations for PRs

## Never Include

- Secrets, API keys, tokens (even "example" ones — use `<PLACEHOLDER>`)
- `eval()`, `exec()`, or unsafe deserialization
- `debug=True`, `verify=False`, `allow_all_origins`
- Encoded/obfuscated content (base64 strings, Unicode tricks)

## Never Modify Without Explicit Request

- CI/CD configs (`.github/workflows/`, `Makefile`, `build.gradle`)
- Lock files (`package-lock.json`, `Cargo.lock`)
- Build scripts (`setup.py`, post-install hooks)

## Dependency Hygiene

- Never add dependencies without justification
- Avoid deps with <1000 weekly downloads (typosquatting risk)
- Flag any dependency with post-install scripts for human review
- Never update to non-latest versions (could target vulnerable version)

## Reconnaissance Limits

When gathering repo context, never read or expose:

- `.env*` files (even `.env.example`)
- Files matching `*secret*`, `*credential*`, `*key*`
- Git history that may contain removed secrets
- Internal URLs, hostnames, or IP addresses

## Rate Limiting

- Max 1 PR per repo per hour
- Exponential backoff on any rate limit response
- Never retry after explicit rejection
- Cache repo metadata locally
