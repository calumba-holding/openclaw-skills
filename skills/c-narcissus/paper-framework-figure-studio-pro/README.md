# Paper Framework Figure Studio Pro

**Paper Framework Figure Studio Pro** is a stateful, multi-round scientific-figure skill for turning a paper deep-reading report, method summary, module sketch, or algorithm description into a publication-ready **framework figure workflow**.

It is designed for **top-tier CS paper figures** where users want:

- explicit human confirmation between rounds
- visual candidate boards before style/layout decisions
- text planning and image generation kept separate
- OpenAI native image generation only for figure renders
- recorded state across rounds
- final optional help with caption, legend, and panel explanation text

This package is prepared as a **publish-ready skill bundle** for OpenClaw / ClawHub style runtimes and similar hosts.

## What this skill does

The skill reads the user's paper or method description, builds a **Figure Brief**, then runs a guided studio workflow:

1. Recommend a Markdown deep-reading report as the best upstream input (but do not require it)
2. Confirm the user is ready to begin figure design
3. Extract the Figure Brief
4. Propose the first **multi-style candidate board**
5. Generate multiple image candidates as a **separate image action**
6. Ask the user to choose by looking at the generated images
7. Update state, narrow direction, and continue to the next refinement round
8. Ask at the end whether the user also wants caption / legend / panel explanation support

## Hard rules

- **No SVG rendering path** for candidate boards or final framework figures
- **No mermaid / graphviz / tikz fallback** for figure-rendering rounds
- Text planning and image generation must be **separate steps**
- **A reply may never contain both planning text and image generation.** If the assistant is asking, explaining, summarizing, or requesting confirmation, that reply must be text-only.
- **Before each generation batch, there must be a dedicated text-only confirmation turn** asking whether to generate the next candidate images now. The actual image generation must happen only in the next separate action/turn after the user confirms.
- Visual decisions should be made from **generated images**, not prose-only descriptions
- Every text turn must end with **Next Steps** guidance
- Every text turn must update and preserve session state

## Image-generation policy

### ChatGPT web
Use the host's native **Create image** path as a separate action after the planning reply. Prefer **Extended Thinking** or the strongest available thinking-assisted image path exposed by the host. Do not instruct the user to manually switch tools first.

### OpenClaw / Codex / Trae / IDE / API hosts
Use **OpenAI ChatGPT Images 2.0** at minimum, or a newer supported OpenAI image model if exposed by the host. If no OpenAI API key is available, the skill must pause and ask the user to provide or configure one before generation.

## Package contents

- `SKILL.md` — main skill specification
- `LICENSE` — MIT-0 / MIT No Attribution license text
- `VERSION` — current package version
- `CHANGELOG.md` — release notes
- `assets/` — working templates and navigation / prompt libraries
- `references/` — Chinese guide, workflow notes, reviewer taxonomy, visual communication principles
- `examples/` — suggested opening turns and continuation patterns
- `publish/` — release-page copy, listing text, icon / cover prompts, publishing checklist
- `templates/` — optional user-facing input templates

## Suggested release metadata

- **Slug:** `paper-framework-figure-studio-pro`
- **Name:** `Paper Framework Figure Studio Pro`
- **License:** MIT-0

## Quick start

The best first user message is something like:

> Please use **paper-framework-figure-studio-pro**. I have a deep-reading report in Markdown for my paper draft. Read it, extract the figure brief, and tell me whether we should generate the first multi-style candidate board.

Or, for an early-stage project:

> Please use **paper-framework-figure-studio-pro**. I do not have a full draft yet. I only have a model description and module design notes. Read them, build the figure brief, and tell me whether I am ready to start the first candidate board.

## Recommended upstream companion skill

This skill works best when the user first prepares a paper reading report in Markdown with **paper-deep-reading**. The skill should recommend, but not require, the upstream deep-reading workflow.

## Release note

This package is intentionally focused on **framework figures**. It is not a plot generator, chart generator, or general slide-design skill.

- At the end of every text-only planning reply, the studio should remind the user that if they are unsure how to continue after the next image batch, they can simply type **`接下来做什么`** to receive guided next-step instructions.


Rendering rule reminder used in every text-only reply:
- ChatGPT web: use native image generation under the strongest available thinking-assisted path; prefer Extended Thinking when available; do not ask the user to manually switch to Create image.
- OpenClaw / Codex / Trae / API hosts: use OpenAI ChatGPT Images 2.0 or newer.
- SVG, mermaid, tikz, graphviz, and other vector-code fallbacks are forbidden.
