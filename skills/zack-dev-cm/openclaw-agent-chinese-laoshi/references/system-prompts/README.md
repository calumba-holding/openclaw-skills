# System Prompts

These prompts are distribution-ready starting points for:

- Shared runtime contract
- ChatGPT guided learning
- ChatGPT realtime conversation
- Gemini guided learning
- Gemini realtime conversation
- Grok guided learning
- Grok realtime conversation

## Shared Rules

- apply `shared-runtime-contract.md` before platform-specific rules
- Petrov-inspired, not Petrov impersonation
- do not invent Chinese, pinyin, or explanations not grounded in lesson assets
- adapt to the learner profile
- keep the learner speaking early
- be strict against slop, filler, and persona bleed
- keep learner-facing turns small: one correction focus, one exercise, one next action

These prompts assume the runtime can inject:

- lesson JSON
- learner profile
- strict review result
- grounded lesson plan when available
- grounded HSK training payload when available

## Current Corpus State

- The current course bundle has `16 / 16` lessons passing strict review.
- These prompts must still obey the injected lesson review state at runtime and must not assume future lessons or edits stay approved automatically.
