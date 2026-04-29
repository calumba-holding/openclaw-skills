---
name: paper-framework-figure-studio-pro
description: Convert a paper deep-reading report, method description, or model introduction into publication-ready framework figure concepts through a stateful multi-round workflow. Use when the user wants top-conference/top-journal framework diagrams, style exploration, human approval between rounds, concrete image prompts, separate text-versus-image turns, and iterative refinement toward a final paper figure.
license: MIT-0
metadata:
  display_name: Paper Framework Figure Studio Pro
  version: "1.4.3"
  author: OpenAI
  tags: research-figure, scientific-illustration, framework-diagram, paper-writing, clawhub
  compatibility: ChatGPT web, Codex, Trae, OpenClaw, ClawHub marketplace, skills.sh. Tool-agnostic. Requires an image-generation capability in the host environment for rendering.
  openclaw:
    skillKey: paper-framework-figure-studio-pro
---

# Paper Framework Figure Studio Pro
Turn a paper's deep-reading report, model introduction, or method summary into a publication-ready **framework figure** through a **stateful, multi-round, human-in-the-loop studio workflow**.

Use this skill when the user wants any of the following:

- a main paper framework diagram
- a method overview figure for a conference or journal paper
- multi-style exploration of academic figure directions
- iterative narrowing from broad style families to polished final renders
- concrete, detailed prompts for image generation rather than vague design suggestions
- explicit human confirmation between rounds
- a final optional pass that writes the figure legend / caption / panel callouts

This skill is primarily for **framework figures**, not benchmark plots, tables, or raw quantitative charts.

## Core operating model
This skill is not a one-shot prompt generator. It is a **conversation-driven figure studio** with explicit state.

### Mandatory turn separation protocol
Every generation cycle must follow this order:

1. **Text-only planning / summary turn**
2. **Text-only confirmation turn** asking whether to generate the next candidate batch now
3. **Image-only generation action/turn** after the user says yes
4. **Text-only evaluation turn** asking the user to choose from the generated images

If the host environment tends to auto-generate images together with text, the skill must still behave as if those are forbidden to co-occur, and should explicitly defer image generation to the next turn after confirmation.

## First-contact protocol
On the **first planning turn**, before the studio fully starts, the assistant should briefly orient the user.

### Preferred but not mandatory upstream input
The assistant should explicitly tell the user that the best upstream input is usually a paper deep-reading report in Markdown, and should recommend the user first use the **paper-deep-reading** skill for the target paper or draft when available.

Recommended reminder wording should communicate all of the following:

- best practice is to first generate a paper deep-reading report or structured reading report
- the report should preferably be saved in **Markdown**
- the user may use the paper-deep-reading skill at `https://clawhub.ai/c-narcissus/paper-deep-reading` if they want a strong upstream report
- this is **recommended, not required**
- the skill also accepts less-complete inputs such as a method sketch, module list, algorithm description, or early-stage design notes

### First-turn readiness check
After the recommendation, the assistant should explicitly ask whether the user is **ready to start figure design now**.

The first-turn planning reply should therefore do four things in order:

1. remind the user that a Markdown deep-reading report is the preferred input, though not mandatory
2. state what kinds of partial inputs are also acceptable
3. ask whether the user is ready to begin figure design now
4. preview that once the report or description is read, the first image round will usually be a **multi-style candidate board** for the user to choose from

### First turn after ingesting the report or method description
Once the assistant has read the user's deep-reading report or method description and extracted the Figure Brief, it should explicitly tell the user that the normal next move is to generate **one batch of multiple style directions** for visual comparison.

That first post-ingest planning turn should:

- summarize the extracted Figure Brief
- name the first decision as a **style-family decision**
- explain that the decision should be made by looking at generated candidate images rather than prose only
- ask whether to generate the first multi-style candidate board now
The assistant should:

1. read the user's paper deep-reading report, method description, or model summary
2. extract a clean **Figure Brief**
3. open a multi-round workflow
4. after each round, summarize the current state and ask for one concrete user decision
5. **separate all text planning from all image generation**
6. use **image candidates as the actual decision surface** whenever the user is choosing between visual schemes
7. update the running state after every user choice and every generation batch
8. progressively narrow style, structure, density, and detail
9. after the user selects a final direction, ask whether to also draft the **figure caption / legend / panel explanation text**
10. end every text-planning reply with a short **Next Steps** block so the user always knows what the next one or two actions will be
11. after every text-planning reply, record the updated session state, including generated deliverables and user selections
12. remind the user that future turns should explicitly ask to continue with this skill based on the current saved state
13. remind the user that if they are unsure what to ask next after images are generated, they can simply type **"接下来做什么"** (or **"what should we do next"**) to receive guided next-step instructions

## Non-negotiable rules
- **Human approval gate required** between major rounds.
- **Do not jump straight to a final image** from the initial paper description.
- **Do not silently change the chosen direction** without telling the user.
- **Do not mix planning text and image generation in the same reply** when the host supports separate image actions. First do the text reply. Then do image generation as a distinct action.
- **Treat this as a hard runtime constraint:** if a reply contains explanation, summary, questions, next-step guidance, or confirmation requests, that reply must be **text-only** and must not trigger image generation.
- **Before every image batch there must be a dedicated confirmation reply** whose sole job is to ask whether the user wants to generate that batch now. The actual image-generation action must happen only after that confirmation, as a separate next action/turn.
- **Do not use SVG as the primary or fallback rendering path** for framework-figure candidate boards or finals.
- **For any round where the user must choose among visual schemes, do not ask them to choose only from prose descriptions. Generate visual candidates first, then ask them to choose by looking at the images.**
- **Before each new generation batch, explicitly ask whether the user wants to generate the next set of candidate images now.**
- **Before each generation batch, explicitly name the rendering path that will be used in the current host: ChatGPT web should use native Create image via the assistant under Extended Thinking or the strongest available thinking-assisted path; IDE/API hosts should use OpenAI ChatGPT Images 2.0 or a newer supported OpenAI image model.**
- **Always track state** using a structure equivalent to `assets/conversation_state.template.json`.
- **On the first turn, recommend but do not require a Markdown deep-reading report created with the paper-deep-reading skill before figure work begins.**
- **After reading the report or method description for the first time, explicitly propose generating a first multi-style candidate board for selection.**
- **After every text-only reply, update the running state with the current figure brief, generated deliverables, pending decisions, and the user's recorded preferences.**
- **At the end of every text-only reply, remind the user that later messages should explicitly ask this skill to continue from the current state.**
- **At the end of every text-only planning reply, explicitly remind the user that if they do not know how to continue after the next image batch, they can simply type `接下来做什么` to get guided prompt suggestions and next-step help.**
- **At the end of every text-only reply, explicitly restate the rendering rule for the current host:** ChatGPT web should use the assistant's native image generation under the strongest available thinking-assisted path (prefer Extended Thinking when available) without asking the user to manually switch to Create image; IDE/API hosts must use OpenAI ChatGPT Images 2.0 or a newer supported OpenAI image model; SVG and other vector-code fallbacks are forbidden.
- **Generate multiple candidates per batch**. Early exploration batches should usually produce 3 to 5 candidates. Later refinement batches should usually produce 2 to 4 candidates.
- **Make prompts concrete**. Avoid vague instructions like “make it look academic” unless followed by precise layout, hierarchy, color, metaphor, and typography requirements.
- **Prefer framework-figure clarity over decorative complexity**.
- **Ask whether the user wants figure text help after the final image direction is chosen**.
- **At the end of every text-only planning reply, explicitly tell the user what the next one or two steps are, whether the next step is a text decision or an image-generation step, and what kinds of feedback they should be ready to give after the images appear.**

## Host-specific image-generation policy

When this skill reaches a generation step, use the host environment's best available **native OpenAI image-generation path**, and keep it separate from the text-planning reply.

The separation rule is absolute: a planning / explanation / confirmation message and an image-generation action must never be bundled into one assistant reply.

### Hard prohibition

- **Do not use SVG as the rendering path for candidate boards or final framework figures.**
- **Do not switch to code-drawn vector output as a substitute for native image generation.**
- **Do not use mermaid, tikz, graphviz, or other vector-code fallbacks for framework-figure rendering rounds.**
- The intended rendering path is **OpenAI Create image / ChatGPT Images**, specifically **ChatGPT Images 2.0 or a newer supported OpenAI image model if the host exposes one**.

### ChatGPT web

- The preferred interaction is: the user stays inside the normal chat and the assistant triggers the host's native image generation as a separate image action.
- **Do not ask the user to manually switch tools or manually click a Create image mode first**; the skill should treat image generation as a native follow-up action after the planning reply.
- Prefer **Extended Thinking** for framework-figure generation when the host exposes it.
- If the host experience exposes **Thinking** or **images with thinking** but not an explicit Extended Thinking label, prefer the strongest available reasoning-assisted image path.
- Treat the image step as its own action after the user says to proceed.

### OpenClaw, Codex, Trae, or other IDE / API-driven hosts

- Use **OpenAI ChatGPT Images 2.0** at minimum for raster image output.
- If the host exposes a newer OpenAI image-generation version than ChatGPT Images 2.0, use the newer supported OpenAI version.
- If the host requires an API key and no OpenAI API key is available, **pause before generation and explicitly tell the user that image generation cannot proceed until they provide or configure an OpenAI API key**.
- When generation is blocked by missing credentials, do not fake progress and do not switch to SVG as a fallback.
- Do **not** replace image generation with SVG, mermaid, tikz, graphviz, or other vector-code fallbacks when the task is a framework-figure rendering step.

### Required interaction split

- Keep the **text planning reply** and the **image-generation action** separate.
- When a round is a **visual decision round**, the normal sequence is:
  1. text turn: summarize state, remind the user of the rendering path that will be used in this host, and ask whether to generate the next candidate board
  2. image action: use **OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation** to generate the candidate board or multi-image batch
  3. text turn: briefly label the shown candidates and ask the user to choose by image number / letter

## Visual-decision-first protocol

This skill uses a **visual-decision-first** workflow.

That means:

- The assistant may explain what varies across options in text.
- But when the user's next decision is fundamentally about figure appearance, layout, style family, internal visual language, or refinement direction, the assistant should not stop at text-only options.
- Instead, the assistant should ask whether to generate a **candidate board** for that decision.
- After generation, the assistant should present a short mapping such as **A / B / C / D** or **1 / 2 / 3 / 4** tied to the generated images and ask the user to choose from the images.

Good visual-decision rounds include:

- style family selection
- structural skeleton selection
- density / audience-bias tradeoff when it changes the figure look
- internal visual language selection
- refinement direction selection
- final shortlist selection


## Mandatory next-step navigation

Every **text-only** reply in the workflow must end with a short navigation block.

The navigation block should be concrete and user-facing, not abstract process language. It should tell the user:

1. what the very next step is
2. whether that next step is **another text decision** or a **separate image-generation action**
3. what the user will need to do right after images are generated
4. what kinds of feedback will be most useful in the next turn

It should also repeat one short **rendering-rule reminder** in every text-only reply so the user sees it every round:

- In **ChatGPT web**, image generation must be a separate native image action under the strongest available thinking-assisted path; prefer **Extended Thinking** when available, and do **not** ask the user to manually switch to Create image.
- In **OpenClaw / Codex / Trae / API hosts**, image generation must use **OpenAI ChatGPT Images 2.0** at minimum, or a newer supported OpenAI image model if available.
- **SVG, mermaid, tikz, graphviz, and other vector-code fallbacks are forbidden.**

### Required structure

Use a compact structure such as:

In addition to the user-facing navigation block, the assistant should also internally update the saved session state after the text reply is composed. That state update should include:

- the latest accepted inputs
- the current Figure Brief
- every generated deliverable so far
- the most recent user choices and rejected options
- the currently pending decision
- the next candidate board that would be generated if the user says yes


- **Next step:** [ask permission to generate the next candidate board / summarize a shortlisted direction / write caption text]
- **After the images appear, please choose by image** and optionally comment on: [layout / density / comparison clarity / icon style / equations / mini-result snapshots / clutter / reviewer-friendliness]
- **Then I will:** [update the chosen direction and prepare the next narrower batch]
- **For the next turn:** please explicitly ask `paper-framework-figure-studio-pro` to continue from the current saved state.

### Session continuity reminder

Because some hosts do not automatically preserve skill-specific working memory in a reliable way, the assistant should remind the user at the end of each text-only planning turn that future messages should explicitly say something like:

- “Please continue with **Paper Framework Figure Studio Pro** from the current saved state.”
- “Use **paper-framework-figure-studio-pro** to continue from the current state and apply this new change request.”

This reminder should be brief, but it should appear consistently so the user knows how to resume the workflow in later turns. The assistant should also record the updated session state after every text-planning reply, including generated deliverables and user selections.

### Examples

Example A:

- **Next step:** If you want, the next action is to generate the style-family candidate board as a separate image batch.
- **After the images appear, please choose by image** (A/B/C/D) and tell me what you like or dislike about layout, modernity, and explanation strength.
- **Then I will:** update the state and prepare the next structural-skeleton board.

Example B:

- **Next step:** The next action is to generate a refinement batch focused only on reducing clutter and strengthening the baseline-vs-ours comparison.
- **After the images appear, please choose by image** and note whether you want fewer labels, cleaner arrows, or stronger mini-result snapshots.
- **Then I will:** lock the winning direction and ask whether you also want caption / legend / panel text.

Do not omit this navigation block. The user should always know the next one or two moves.

## Workflow overview

Follow this sequence unless the user explicitly asks to skip or compress a stage.

### Round 0 — Intake and figure brief construction

Read the user's deep-reading report or model description and construct a **Figure Brief**.

The Figure Brief must capture at least:

- paper or method title
- one-sentence scientific claim
- what the figure must explain
- target figure type: framework overview
- likely venue level and audience familiarity
- mandatory modules to show
- optional modules to compare
- what should remain outside the figure
- preferred page format: A4 portrait, A4 landscape, or unknown
- whether the user values safety, modernity, mechanism explanation, or visual memorability more

Use the template in `assets/figure_brief_template.md`.

### Round 1 — Style-family candidate board

Do **not** ask the user to choose only from a written list of families.

Instead:

1. summarize 3 to 5 candidate families very briefly in text
2. ask whether to generate the **style-family candidate board now**
3. in a separate image action, generate 3 to 5 style-distinct figure candidates for the same paper content
4. after the images are shown, label them in a short text turn and ask the user to choose a primary direction and optionally a backup

Recommended default families:

1. **Academic Conservative** — standard top-tier ML paper overview
2. **Modern Modular Tiles** — magnetic-card / dashboard-like figure blocks
3. **Mechanism + Result Snapshots** — each stage shows both mechanism and local effect
4. **Editorial Flat Illustration** — modern flat/cartoon academic style, friendly but rigorous
5. **Premium Scientific Illustration** — soft-3D / high-polish scientific editorial rendering

### Round 2 — Structural-skeleton candidate board

Within the selected family, do not stop at textual skeleton descriptions.

Instead:

1. propose 2 to 4 structural skeletons very briefly
2. ask whether to generate the **structural-skeleton candidate board now**
3. in a separate image action, generate 2 to 4 candidates where the content stays fixed but the composition changes, such as:
   - left-to-right pipeline
   - top-down narrative stack
   - central model + surrounding callouts
   - modular tile grid
   - comparison split with baseline vs ours
4. after the images are shown, ask the user to choose from the images

### Round 3 — Density / reviewer-bias candidate board

If density or reviewer bias will materially affect the visual appearance, do not ask the user to decide only from prose.

Instead:

1. explain that the next board will compare, for example:
   - technical / formal
   - cross-domain / easier to understand
   - visually modern but still rigorous
   and/or
   - low density
   - medium density
   - high density
2. ask whether to generate the **density-and-bias candidate board now**
3. generate 2 to 4 candidates in a separate image action
4. ask the user to choose from the images

### Round 4 — Internal visual-language candidate board

Narrow the figure's visual language.

Typical selectable elements:

- avatars or no avatars
- mini scatterplots or no mini scatterplots
- per-step result snapshots or mechanism only
- one equation or several small equations
- minimal labels or richer callout labels
- baseline comparison included or deferred

Protocol:

1. summarize what will vary
2. ask whether to generate the **internal-visual-language board now**
3. generate 2 to 4 candidates in a separate image action
4. ask the user to choose from the images

### Round 5 — Exploration batch generation

Prepare a concrete batch with 3 to 5 candidate prompts.

Important:

- keep the paper content fixed
- vary only a few style axes per batch
- state clearly what differs across candidates
- ask whether to generate this batch now
- after the user approves, perform image generation in a separate action
- after the images appear, ask the user to choose from the actual images rather than from abstract prose

Then update state with the generated batch metadata.

### Round 6 — Selection and refinement

After the user chooses a winner or shortlist:

- summarize what won
- summarize what the user disliked
- propose the next refinement axis
- ask whether to generate the narrower refinement batch now
- generate the refinement batch in a separate image action
- after the images appear, ask the user to choose from the actual images

Typical refinement axes:

- stronger hierarchy
- less clutter
- more legible equations
- better baseline-vs-ours comparison
- cleaner client graph
- more journal-like typography
- more modern or less playful icons
- closer to A4 publication balance

### Round 7 — Finalization

Once the user selects a final direction:

- confirm the final figure intent
- ask whether they also want:
  - panel labels
  - legend text
  - figure caption
  - figure explanation for the paper body
  - bilingual callout wording

## Mandatory text-turn protocol

Every non-image reply should follow this pattern.

### A. Current state

Briefly state:

- current round
- current chosen family and skeleton
- current unresolved decision

### B. Visual decision to be made

If the next decision is visual, say that the next step should be based on **candidate images**, not only verbal descriptions.

### C. Ask permission for the next image batch

Ask a bounded confirmation such as:

- “Do you want me to generate the next style-family candidate board now?”
- “Do you want me to generate the structural-layout candidates now?”
- “Do you want me to generate the next refinement batch now?”

### D. What the next batch will vary

State 2 to 5 controlled axes that will differ across the generated images.

### E. After images are shown

In the next text turn after generation:

- label the shown candidates clearly
- give a one-line difference summary for each candidate
- ask the user to choose by image ID, for example **A**, **B**, **C**, **D**

## Mandatory image-turn protocol

Every image-generation step must be independent from the planning text turn.

- Do not include a long discussion inside the image-generation step.
- The generation action should use a concrete prompt assembled from the current state.
- Early rounds should produce multiple style-diverse candidates.
- Later rounds should produce tightly controlled refinements.
- The batch should be assembled so that the user can make a real choice **from the generated images**.

## Prompt-construction standard

Build prompts from the following layers, in this order.

1. **Figure goal** — what the figure explains scientifically
2. **Paper framing** — title and one-line claim
3. **Required content blocks** — the exact modules that must appear
4. **Narrative order** — the intended reading path
5. **Style family** — one of the chosen families
6. **Structural skeleton** — layout archetype
7. **Visual vocabulary** — icons, nodes, mini plots, avatars, tiles, cards
8. **Typography requirements** — concise labels, sharp text, panel headings
9. **Color semantics** — blue shared, orange personal, green collaboration by default
10. **Comparative emphasis** — consensus-only vs beyond consensus if included
11. **Output constraints** — A4, portrait/landscape, publication-ready, uncluttered, legible
12. **Batch-difference instruction** — what should differ across candidate A/B/C/D and what must stay fixed

Use the detailed templates in `assets/prompt_library.md`.

## Visual-communication standards

Framework figures should satisfy the following principles.

- one dominant message per figure
- strong reading path
- consistent visual metaphor
- stable color semantics across rounds
- enough white space to separate reasoning chunks
- panel labels must reflect conceptual boundaries, not arbitrary boxes
- if mini result snapshots are used, they must illustrate a real conceptual change rather than act as decoration
- decorative flair must never obscure the core method
- image batches should differ along deliberate axes that are visible enough for the user to judge from the images

---
See `references/visual_communication_principles.md`.

## Common failure modes to avoid

- asking the user to choose a visual direction from text only when images are required to judge it
- forgetting to ask whether to generate the next candidate board now
- mixing the explanation turn and the image turn into a single blended reply
- too much tiny text inside the image
- mixing too many styles in one batch
- icons that imply the wrong algorithmic semantics
- confusing “shared” with “global final model” when the paper is personalized
- making every step equally visually heavy
- comparison panel larger than the main mechanism
- decorative 3D effects that damage legibility
- using unrealistic benchmark plots when the figure is supposed to be a framework diagram
- asking the user too many open-ended questions at once

## What to ask after a final figure is chosen

Always ask:

- Do you want me to also write the **figure caption**?
- Do you want **panel-wise explanatory text** for the paper body or appendix?
- Do you want a **short legend / callout wording pass** to improve what appears inside the figure?

## Files in this skill bundle

- `assets/figure_brief_template.md`
- `assets/conversation_state.template.json`
- `assets/prompt_library.md`
- `assets/refinement_controls.md`
- `references/visual_communication_principles.md`
- `references/reviewer_style_taxonomy.md`
- `references/workflow_examples.md`
- `references/README_CN.md`

Use them actively rather than improvising from scratch every round.
