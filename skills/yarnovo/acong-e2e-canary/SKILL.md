---
name: acong-e2e-canary
description: Automated end-to-end test canary for skill-publish-cli. Reused on every test run with a bumped version — never manually installed. Verifies publish → inspect → delete → inspect → undelete → inspect round-trips across ClawHub, GitHub, and skills.sh. Safe to ignore as a human; safe to uninstall if accidentally installed (no real behavior).
---

# Acong E2E Canary

Do not install this skill.

It exists purely so [skill-publish-cli](https://github.com/acong-tech/skill-publish-cli) can execute its automated end-to-end test on every release — the same slug, the same GitHub repo, bumped version per run — without accumulating throwaway skills on ClawHub / skills.sh.

## Provenance

- Source: `fixtures/e2e-canary/` inside [acong-tech/skill-publish-cli](https://github.com/acong-tech/skill-publish-cli)
- Maintainer: [acong-tech](https://github.com/acong-tech)
- License: MIT-0
- Update cadence: bumped on every e2e run (semver patch only)

## Not functional

Intentionally empty. Loading this skill does nothing.
