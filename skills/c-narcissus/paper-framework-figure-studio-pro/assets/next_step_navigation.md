# Next-Step Navigation Patterns

This file defines how every text-only reply should guide the user into the next one or two steps.

## Principle

A good framework-figure studio conversation never leaves the user guessing. After each text reply, the assistant should explicitly say:

- what will happen next
- whether the next move is a separate image-generation step
- what the user should evaluate in the generated candidates
- what the assistant will do after the user chooses

## Default footer template

Use a concise block like this at the end of every text-planning reply:

**Next step**
- The next action is: [describe the separate image-generation step or text decision].
- After the images appear, please choose by image and comment on: [2 to 5 concrete evaluation axes].
- Then I will: [describe the next narrower step].
- If you are not sure how to continue after the images appear, you can simply type **"接下来做什么"** and I will tell you the recommended next prompt or decision.
- **Rendering rule reminder:** In ChatGPT web, the next image step must use the assistant's native image generation under the strongest available thinking-assisted path (prefer Extended Thinking when available) and you should **not** manually switch to Create image; in OpenClaw / Codex / Trae / API hosts, the next image step must use **OpenAI ChatGPT Images 2.0** or newer; **SVG and other vector-code fallbacks are forbidden**.

## Good evaluation axes after images appear

Depending on the round, ask the user to comment on some of the following:

- overall style family fit
- layout / composition
- visual hierarchy
- density / clutter
- reviewer-friendliness
- mechanism clarity
- baseline-vs-ours comparison strength
- icon vocabulary / avatar usage
- mini scatterplots or result snapshots
- equation visibility and readability
- journal-like vs conference-like tone

## Round-specific footer suggestions

### After intake / Figure Brief
- The next action is to generate a style-family candidate board as a separate image batch.
- After the images appear, please choose by image and comment on whether you prefer more conservative, modular, mechanism-explanation, flat-illustration, or premium-polish directions.
- Then I will narrow the winning style into structural skeleton candidates.

### After style-family selection
- The next action is to generate structural-skeleton candidates as a separate image batch.
- After the images appear, please choose by image and comment on whether you prefer a left-to-right pipeline, top-down narrative, central-core-with-callouts, or tile-grid composition.
- Then I will prepare a density / reviewer-bias comparison if needed.

### After structural selection
- The next action is to generate density / reviewer-bias variants as a separate image batch.
- After the images appear, please choose by image and comment on technicality, readability, and whether the figure should target expert reviewers or broader readers.
- Then I will refine the internal visual language.

### After density / bias selection
- The next action is to generate internal visual-language variants as a separate image batch.
- After the images appear, please choose by image and comment on avatars, mini-plots, result snapshots, equation count, and comparison-panel strength.
- Then I will prepare the first integrated exploration batch.

### After exploration batch selection
- The next action is to generate a narrower refinement batch as a separate image batch.
- After the images appear, please choose by image and comment on what must stay fixed and what still needs improvement.
- Then I will lock the final direction and ask whether you want figure text support.

### After final-direction lock
- The next action is a text-only step: I can draft the caption, legend, and panel explanation text.
- Please tell me whether you want caption only, legend only, panel callouts, or all three.
- Then I will produce the publication-facing figure text package.


## Resume reminder line

At the end of every text-only planning reply, add one short continuity reminder such as:

- **For the next turn:** please explicitly ask `paper-framework-figure-studio-pro` to continue from the current saved state when you send the next change request.

## First-contact navigation pattern

Use a first-turn ending such as:

- **Next step:** If you are ready, send your Markdown deep-reading report or your current method description, and I will extract the Figure Brief.
- **After I read it:** the first image round will usually be a multi-style candidate board for you to choose from.
- **Then I will:** record the initial state and prepare the first visual decision round.
- **For the next turn:** please explicitly ask `paper-framework-figure-studio-pro` to continue from the current saved state.

## Mandatory help reminder

Every text-only planning reply should end with a short help reminder such as:

- **If you are not sure what to ask after the images are generated, just type `接下来做什么`, and I will guide you to the next step.**
- **If you are unsure how to continue, simply reply `接下来做什么` and I will suggest the next prompt.**


## Mandatory per-reply rendering reminder

Every text-only reply must visibly repeat a short rendering reminder. Do not assume the user still remembers it from earlier turns.

Recommended one-line reminder:

- **Rendering rule reminder:** ChatGPT web should use native image generation under the strongest available thinking-assisted path (prefer Extended Thinking when available) without asking you to manually switch to Create image; OpenClaw / Codex / Trae / API hosts must use OpenAI ChatGPT Images 2.0 or newer; SVG fallbacks are forbidden.
