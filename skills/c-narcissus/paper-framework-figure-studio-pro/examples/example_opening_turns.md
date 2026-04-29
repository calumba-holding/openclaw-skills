# Example opening turns

## Example 1 — User already has a deep-reading report

**User**

Please use `paper-framework-figure-studio-pro`. I already have a Markdown deep-reading report for my paper draft. Read it, build the Figure Brief, and tell me whether to generate the first multi-style candidate board.

**Expected studio behavior**

- briefly confirm that a Markdown deep-reading report is the preferred upstream input
- say that this is enough to begin
- extract a Figure Brief
- summarize the likely first style-family decision
- ask whether to generate the first multi-style candidate board now
- end with a short Next Steps block

## Example 2 — User has only a model idea

**User**

Please use `paper-framework-figure-studio-pro`. I do not have a full draft. I only have a method summary, module list, and algorithm steps. Tell me whether that is enough to start.

**Expected studio behavior**

- recommend, but do not require, a Markdown deep-reading report as best practice
- explicitly say that module notes and algorithm steps are acceptable
- ask whether the user is ready to begin figure design now
- if yes, build the Figure Brief and propose the first candidate board

## Example 3 — Continue from saved state

**User**

Please continue with `paper-framework-figure-studio-pro` from the current saved state. Keep the winning layout, reduce clutter, and strengthen the baseline-vs-ours comparison.

**Expected studio behavior**

- recall the last accepted direction
- identify the current pending decision
- say what the next generation batch will vary
- ask whether to generate the refinement batch now

## Example 4 — Strict separation before a generation batch

**User**

Please continue with `paper-framework-figure-studio-pro` from the current state and prepare the next refinement batch.

**Expected studio behavior**

- summarize what will vary in the next batch
- keep the reply text-only
- explicitly ask whether to generate the next batch now
- wait for the user to confirm
- generate images only in the next separate image action/turn

## Example 5 — User asks for next-step help after images

**User**

接下来做什么

**Expected studio behavior**

- briefly restate the current saved state
- tell the user what the next recommended decision is
- give 2 to 5 concrete feedback axes they can comment on
- if relevant, offer a ready-to-send next prompt in one line


Rendering rule reminder used in every text-only reply:
- ChatGPT web: use native image generation under the strongest available thinking-assisted path; prefer Extended Thinking when available; do not ask the user to manually switch to Create image.
- OpenClaw / Codex / Trae / API hosts: use OpenAI ChatGPT Images 2.0 or newer.
- SVG, mermaid, tikz, graphviz, and other vector-code fallbacks are forbidden.
