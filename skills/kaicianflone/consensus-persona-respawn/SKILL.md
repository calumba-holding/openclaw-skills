---
name: consensus-persona-respawn
description: Ledger-informed persona lifecycle management. Replaces low-performing personas with successor personas derived from mistake patterns in board decision history, preserving adaptive governance over long-running automation. Reputation updates are computed by consensus-persona-engine.
homepage: https://github.com/kaicianflone/consensus-persona-respawn
source: https://github.com/kaicianflone/consensus-persona-respawn
metadata:
  {"openclaw": {"requires": {"bins": ["node", "tsx"]}}}
---

# consensus-persona-respawn

`consensus-persona-respawn` is the adaptive maintenance loop for persona governance.

## What this skill does

- identifies dead/weak personas by trigger or reputation threshold
- mines historical decision artifacts for mistake patterns
- generates successor persona profiles informed by those failures
- writes `persona_respawn` and updated `persona_set` artifacts
- keeps governance panel quality from stagnating

## Why this matters

A static evaluator panel drifts over time. This skill provides lifecycle renewal so consensus quality improves instead of degrading.

## Ecosystem role

Consumes persona-engine outputs for long-term adaptation and ties directly into board-ledger evidence.

## Best use cases

- long-running agent teams
- recurring decision domains with repeated failure classes
- autonomous systems requiring evaluator maintenance


## Runtime, credentials, and network behavior

- runtime binaries: `node`, `tsx`
- network calls: none in the guard decision path itself
- conditional network behavior: if a run needs persona generation and your persona-generator backend uses an external LLM, that backend may perform outbound API calls
- credentials: none required by default
- optional credentials: external LLM-backed persona generation may require provider API keys (e.g., `OPENAI_API_KEY`) depending on your deployed persona-generator backend
- filesystem writes: board/state artifacts under the configured consensus state path

## Dependency trust model

- `consensus-guard-core` and `consensus-persona-generator` are first-party consensus packages
- versions are semver-pinned in `package.json` for reproducible installs
- this skill does not request host-wide privileges and does not mutate other skills

## Quick start

```bash
node --import tsx run.js --input ./examples/input.json
```

## Tool-call integration

This skill is wired to the consensus-interact contract boundary (via shared consensus-guard-core wrappers where applicable):
- readBoardPolicy
- getLatestPersonaSet / getPersonaSet
- writeArtifact / writeDecision
- idempotent decision lookup

This keeps board orchestration standardized across skills.

## Invoke Contract

This skill exposes a canonical entrypoint:

- `invoke(input, opts?) -> Promise<OutputJson | ErrorJson>`

`invoke()` executes persona replacement based on lineage and failure patterns. Reputation deltas are expected from consensus-persona-engine outputs.
