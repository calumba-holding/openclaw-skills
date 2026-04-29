# Rendering-path reminder

Before any generation batch, add a one-line reminder that framework figures must be rendered with OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation, never SVG. In ChatGPT web, keep the user in chat and do not ask them to manually switch to Create image first; in IDE/API hosts, ask for an OpenAI API key if one is missing.

# Prompt Library for Framework Figures

Use these prompts as **building blocks**. Always customize them with the current conversation state.

---

## Prompt Assembly Header

Start prompts with a concrete scientific framing block like this:

> Create a publication-quality A4 [portrait/landscape] framework figure for a top computer science paper. The paper idea is: "[TITLE]". The figure must let a reviewer understand the full method at a glance. The figure should be self-contained, highly legible, publication-ready, and suitable for a top-tier conference or journal.

Then add:

- the core claim
- the required panel sequence
- the selected style family
- the visual vocabulary
- the typography requirements
- the comparison requirements
- the output constraints

---

## Candidate-board rule

When the user is choosing between schemes, prompts must explicitly create **multiple visually distinct candidates** for the same scientific content.

A good board prompt must state:

- what stays fixed across all candidates
- what specific axes vary across A / B / C / D
- that the result should be suitable for user selection by looking at the images

Useful batch instruction pattern:

> Generate [N] candidate framework figures for the same paper. Keep the scientific content fixed. Vary only the following visible axes: [STYLE / LAYOUT / DENSITY / VISUAL LANGUAGE / SNAPSHOT INTENSITY]. Make each candidate clearly distinguishable so the user can choose from the images.

---

## Family 1 — Academic Conservative

> Create a publication-quality A4 [portrait/landscape] scientific framework diagram in a classic top-tier machine learning paper style. Use crisp vector graphics, a white background, light panel borders, restrained color coding, clean arrows, and concise labels. Use blue for shared structure, orange for personal structure, and green for decentralized collaboration. Build a clear [left-to-right / top-down] reading path. Include these panels: (1) problem setting, (2) dual-channel pseudo-labeling, (3) gating, (4) shared-personal bi-timescale learning, (5) selective aggregation, (6) consensus-only vs beyond-consensus comparison, (7) compact outcomes. Add at most one or two equations and keep all text sharp and readable.

Best when:
- the user wants safety and formal clarity
- the target audience is technically experienced

---

## Family 2 — Modern Modular Tiles

> Create a publication-quality A4 [portrait/landscape] framework figure in a modern modular magnetic-tile style. Use elegant rounded rectangles, a premium editorial dashboard feel, consistent card spacing, subtle depth, clean typography, capsule labels, and a strong information hierarchy. Organize the figure as modular tiles that a reviewer can scan quickly: title tile, problem-setting tile, shared pseudo-label tile, personal pseudo-label tile, gating tile, shared-branch tile, personal-branch tile, selective-aggregation tile, comparison tile, and outcomes tile. Keep the visual system modern and neat, like a 2025 ML paper figure.

Best when:
- the user wants modernity without becoming too illustrative
- the reviewer should be able to scan quickly

---

## Family 3 — Mechanism + Result Snapshots

> Create a publication-quality A4 [portrait/landscape] framework figure in a mechanism-plus-result-snapshot style. Each stage should show both the mechanism and a tiny local effect or state after that stage. Use mini scatterplots, micro heatmaps, tiny decision-boundary sketches, or compact before/after inserts only where they clarify the method. The figure should clearly show: the decentralized problem setup, shared pseudo-label generation, personal pseudo-label generation, sample-wise gating, bi-timescale learning, and selective aggregation. Include concise ribbons such as "result after this step" where helpful. Keep the style elegant, not busy.

Best when:
- the user wants mechanism explainability
- the method is abstract and benefits from tiny state-change examples

---

## Family 4 — Editorial Flat Illustration

> Create a publication-quality A4 [portrait/landscape] framework figure in a modern editorial flat-illustration style common in recent high-quality ML papers. Use rounded shapes, refined icons, tasteful color blocks, crisp typography, and slight personality without becoming childish. If appropriate, use small client avatars or stylized client icons. Keep all scientific semantics precise. The figure should visually communicate that the method shares what is common while preserving what is personal. Use clear mini plots for local decision boundaries and a polished comparison between consensus-only and beyond-consensus behavior.

Best when:
- the user wants a memorable main figure
- the paper also benefits from project-page or talk reuse

---

## Family 5 — Premium Scientific Illustration

> Create a publication-quality A4 [portrait/landscape] framework figure in a high-end scientific illustration style with subtle gradients, soft dimensionality, refined capsules and nodes, thin precise arrows, and sophisticated editorial polish. It should feel premium and memorable while remaining journal-appropriate. Emphasize the shared vs personal structure split, the gating mechanism, the bi-timescale learning, and selective aggregation. Use beautifully rendered network nodes, tidy mini plots, and elegant callout bubbles.

Best when:
- the user wants a flagship visual
- the figure may also be used for posters, slides, or project pages

---

## Required content block for this paper direction

For the current paper idea, the prompt should usually specify these blocks explicitly:

1. Problem setting
   - decentralized client graph
   - no central server
   - few labeled and many unlabeled samples
   - heterogeneous client-specific structures
   - note that not all differences are noise

2. Dual-channel pseudo-labeling
   - shared pseudo-label from neighbors
   - personal pseudo-label from local model

3. Sample-wise gate
   - show \( g_i(x) \in [0,1] \)
   - include the fusion equation

4. Shared-personal bi-timescale learning
   - shared branch \(\theta_i^{sh}\)
   - personal branch \(\theta_i^{per}\)
   - fast collaborative update vs slow local adaptation

5. Selective aggregation
   - only shared branch aggregated
   - weight logic includes quality, similarity, personalization risk

6. Beyond-consensus comparison
   - consensus-only overwrites personal structure
   - our method preserves client-specific structure while still collaborating

7. Outcomes
   - better average accuracy
   - stronger worst-client performance
   - higher personalization retention

---

## Standard equation snippets

Use only a few equations inside the figure. Good candidates:

- \( \hat{y}_i(x) = g_i(x)\hat{y}_i^{sh}(x) + (1-g_i(x))\hat{y}_i^{per}(x) \)
- \( 	heta_i^{sh,t+1} = \sum_j w_{ij}^{sh,t}\,	ilde{	heta}_j^{sh,t} \)
- weight hint: quality + similarity - personalization risk

---

## Style-family board prompt pattern

> Create [N] distinct candidate framework figures for the same paper idea. Keep the scientific modules fixed. Candidate A should emphasize [AXIS 1]. Candidate B should emphasize [AXIS 2]. Candidate C should emphasize [AXIS 3]. Candidate D should emphasize [AXIS 4]. Make the candidates visually different enough for image-based selection. Do not change the scientific claim.

Example varying axes:
- classic conservative vs modular tiles vs mechanism snapshots vs flat illustration
- more formal vs more modern vs more explanation-heavy vs more visually memorable

---

## Structural-skeleton board prompt pattern

> Create [N] candidate framework figures for the same paper and same style family, but vary only the composition skeleton. Candidate A: left-to-right pipeline. Candidate B: top-down narrative stack. Candidate C: central mechanism with surrounding callouts. Candidate D: modular tile grid. Keep typography family, color semantics, and scientific content fixed. Make layout differences obvious enough for image-based selection.

---

## Density / reviewer-bias board prompt pattern

> Create [N] candidate framework figures with identical scientific content and same overall style direction, but vary the visual density and reviewer orientation. Candidate A: technical/formal medium density. Candidate B: cross-domain easier-to-understand medium density. Candidate C: visually modern but still rigorous medium density. Candidate D: high-density expert version. Keep the content fixed and make the density differences obvious in the images.

---

## Internal visual-language board prompt pattern

> Create [N] candidate framework figures that keep the chosen layout stable but vary the internal visual language. Candidate A: abstract nodes, no avatars, minimal mini-plots. Candidate B: small avatars or client icons with mini scatterplots. Candidate C: result snapshots and richer callouts. Candidate D: fewer labels but one stronger equation panel. Keep the paper content fixed and make the differences visible for image-based selection.

---

## First integrated exploration-batch prompt pattern

> Create [N] candidate framework figures for the same paper idea. Keep the scientific content fixed. Vary only the selected exploration axes from the current state: [AXES]. All candidates must be publication-ready, A4-balanced, and legible. The candidates must be different enough that a user can choose among them by looking at the images.

---

## Refinement-batch prompt pattern

> Refine the selected direction while keeping its core composition. Preserve [KEEP LIST]. Change only the following aspects: [CHANGE LIST]. Improve label hierarchy, reduce clutter, and make the main claim more immediately legible. Keep the same paper content and A4 publication balance. Produce [N] refinement variants that differ only in controlled visible ways so the user can choose from the images.

---

## Final-polish prompt pattern

> Create a final polished framework figure based on the chosen direction. Keep the composition stable. Tighten spacing, sharpen text, unify icon style, improve panel hierarchy, and ensure the figure looks ready for a top conference or journal submission. Do not introduce new modules. Make the final comparison panel crisp and reviewer-friendly.


## Text-only reply footer rule

After every text-only planning reply, add a short navigation footer that tells the user:

- what the next action is
- whether the next action is a separate image-generation step
- what feedback to give after the images appear
- what the assistant will do after the user chooses

Suggested footer pattern:

> **Next step:** The next action is to generate [BOARD TYPE] as a separate image batch.
> **After the images appear, please choose by image** and comment on: [AXIS 1], [AXIS 2], [AXIS 3].
> **Then I will:** [NEXT NARROWER STEP].


## First-contact text scaffold

Use this on the first planning turn before any image generation:

1. Recommend a Markdown deep-reading report as the preferred input.
2. Mention the paper-deep-reading skill URL: `https://clawhub.ai/c-narcissus/paper-deep-reading`.
3. Clarify that this is recommended, not required.
4. Say that method sketches, module descriptions, algorithm notes, and early design ideas are also acceptable.
5. Ask whether the user is ready to start figure design now.
6. Preview that after reading the input, the first generation round will usually be a multi-style candidate board.
7. End with a Next Steps block and a resume reminder.
