---
name: Pull Request
description: Create quality PRs that get merged with pre-flight checks, scope detection, rate limits, and maintainer-friendly communication.
---

## First: Read the Repo

Before ANY PR, check:

- **CONTRIBUTING.md** — Issue required? CLA/DCO? Discussion first?
- **Recent merged PRs** — What does success look like?
- **AI policy** — Search for "AI", "bot", "automated" in docs
- **Project state** — Active? In freeze? Accepting contributions?

Adapt to THEIR workflow.

## Scope Boundaries — STOP If:

```
□ Change touches >5 files OR >200 lines
□ Change modifies public API
□ Change involves security, auth, crypto
□ Change is in governance, licensing, CoC
□ Issue has "needs discussion" or RFC label
```

→ **Escalate to human before proceeding.**

## Rate Limits

- Max 1 open PR per repo at a time
- Wait 24h between PRs to same repo
- If 2 PRs rejected consecutively → STOP, escalate to human

## Pre-PR Checklist

```
□ Repo accepts contributions (check notices)
□ Correct target branch
□ Tests pass locally (or disclose "could not run")
□ Linter passes with repo's config
□ No unrelated changes
□ Commits match project format
□ Branch rebased, no conflicts
```

## AI Disclosure

```markdown
## 🤖 AI-Assisted PR
- **Agent:** [Name/tool]
- **Testing:** [Full suite / Manual / Could not run locally]
- **Human review:** [Yes / No]
- **Prompts:** [Link or summary if available]
```

## PR Description Format

```markdown
## Summary
What and why.

## Changes
- Actual changes (not "updated files")

## Testing
How verified.

## Related
Fixes #123 (if applicable)
```

## After Opening

- Respond to review feedback within 48h
- If unable to continue: "I cannot address this; @human please take over"
- Never abandon a PR silently

## Red Flags to Avoid

- Scope creep (typo fix → refactor)
- Generic commits ("Fix bug")
- Patterns not in codebase
- No uncertainty on complex changes

## Hard Rules

- One logical change per PR
- Never modify CI/CD without explicit request
- Never include secrets (use `<PLACEHOLDER>`)
- Max ~400 lines (ideally <200)

## Security

For security-sensitive repos, see `security.md`.
