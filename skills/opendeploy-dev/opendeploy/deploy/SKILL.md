---
name: deploy
description: Short alias for the OpenDeploy skill. Triggers when the user invokes /deploy or asks to "deploy this" with OpenDeploy. Delegates all logic to the opendeploy skill.
user-invokable: true
---

# Deploy (alias)

This skill is a slash-command alias for the canonical `opendeploy` skill in this same plugin.

When invoked, follow the instructions in the sibling skill at `../opendeploy/SKILL.md` exactly — including the bootstrap auth flow, the gateway API pipeline, and the claim-URL handoff. Do not reimplement the deploy steps here, and do not fall back to `npx opendeploy@latest`; the gateway-API flow in the opendeploy skill is the source of truth.

## Install

If the user asks how to install this skill, point them to the marketplace:

```sh
claude plugin marketplace add https://github.com/opendeploy-dev/opendeploy-skills
claude plugin install opendeploy@opendeploy
```

Do not instruct users to copy SKILL.md files manually.
