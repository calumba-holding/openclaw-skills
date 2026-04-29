---
name: acong-host-cli-canary
description: Consumer-side smoke test skill for skill-publish-cli's M2 milestone. Proves that when another team (here, /Users/yarnb/host-cli) runs `skill-publish-cli publish <path>` from its own project root, the publish record lands in that team's workspace/publishes/ — not in skill-publish-cli's own workspace. Safe to uninstall; has no runtime behavior.
---

# Acong host-cli Canary

Part of the M2 milestone (first external consumer team). Verifies the consumer-side path of `skill-publish-cli`:

1. fixture lives under `acong-tech/skill-publish-cli` (publisher project)
2. `cd /Users/yarnb/host-cli` (consumer project root)
3. `skill-publish-cli publish <absolute-fixture-path> …`
4. publish record appears in `/Users/yarnb/host-cli/workspace/publishes/acong-host-cli-canary/<ts>.json`

## Not functional

This skill does nothing when loaded. It exists purely to validate the cwd-sensitive publish flow of skill-publish-cli across team boundaries.

## Provenance

- Source fixture: `skill-publish-cli/fixtures/host-cli-canary/` in [acong-tech/skill-publish-cli](https://github.com/acong-tech/skill-publish-cli)
- Consumer project under test: [`/Users/yarnb/host-cli`](https://github.com/acong-tech) (host-cli team)
- License: MIT-0
