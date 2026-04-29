# State and Turn Contract

This contract is strict: every text-only answer must either execute the current confirmed step or, before confirmation, maintain the startup gate and update recoverable state.

## Mandatory Startup Confirmation Gate

At the first trigger of a new figure-design task, the assistant must provide a startup plan preview and wait for user confirmation before substantive execution.

The first response must be `STARTUP_PLAN_ONLY` and must include:

- visible `当前执行计划` block
- `当前处于：第 0/N 步 — 启动确认与流程预览`
- a complete list of workflow steps and plain-language descriptions
- optional materials the user can provide
- optional reference-image note
- default recommended route
- final-only prompt suggestions for confirming or modifying the start
- footer with `start_confirmed: false` and `awaiting_user_confirmation: true`

It must not yet analyze the paper, rank figure schemes, build prompts, or generate images.

## Mandatory Opening Plan After Confirmation

After the user confirms start, the assistant must begin with a concise skill-driven plan before detailed analysis. The plan must be derived from the workflow in `SKILL.md`, not from a generic conversation template.

The opening execution plan must include:

- current stage
- goal of the current reply
- next 3–6 planned steps
- what will be inferred vs. requested
- whether optional reference images would help now
- recommended default route for immediate progress

The plan may change. When it changes, record the reason as `计划调整` in the state footer.

## Mandatory Visible Plan Step

Every text-only response must show a visible `当前执行计划` block near the beginning of the answer. The block must list the active plan and explicitly mark the current step as `当前处于：第 X/Y 步 — <step name>`. This is required for startup gate turns, opening turns, continuation turns, review turns, and short rule-modification turns.

The state footer must repeat the same current step as `当前处于计划第 X/Y 步：...`.

The visible plan block may describe workflow actions but must not include copyable next-turn user prompts.

## Mandatory State Footer for Text Turns

Every text-only response must end with:

1. 当前状态与产物
2. 下一步你可以这样问

The footer exists because the skill may not persist in an agent/session. It must contain enough context for another assistant turn to continue. It must be updated after **every** text-only answer, including startup-gate replies, short answers, corrections, and replies that only modify the skill rules.

## Modality Rule

- Text turn: no image generation.
- Image turn: image generation only; no text.

If a user asks for both explanation and image in one message, first provide the text-only image brief and ask the user to use the next message to request image-only generation.

## Recovery Phrase

Always remind the user to include:

`请根据引导skill以及当前的状态，继续...`

Recommended fallback:

`请根据引导skill以及当前的状态，继续告诉我下一步做什么。`

---

# v2 Addendum

## Visual candidate reminder

Every text-only planning response should remind the user that visual choices are best made from multiple candidates. Prefer 3–5 candidates in early exploration and 2–4 in refinement.

## Rendering rule reminder

Every text-only response should repeat one compact rule:

ChatGPT web uses native image generation as a separate action; OpenClaw / Codex / Trae / API hosts use OpenAI ChatGPT Images 2.0 or newer; SVG, Mermaid, TikZ, Graphviz, HTML/CSS, matplotlib, and other code-rendered figure fallbacks are forbidden.

## Stronger state requirements

The state block must include:

- current plan step, written as `当前处于计划第 X/Y 步：...`
- startup gate status when relevant: `start_confirmed` and `awaiting_user_confirmation`
- current working plan and any plan adjustment
- figure effect contract
- selected scheme
- current visual decision
- candidate history
- next candidate batch design


## Recommended default choice

Every text-only planning reply must include one opinionated default path so the user can proceed immediately:

- `我建议优先选择：...`
- `默认推荐路线：...`
- `如果你想直接推进，我建议下一步做：...`

The recommendation should be justified by reader effect, paper claim, reviewer risk, visual clarity, or generation feasibility. It must be stored in the compact state as `recommended_default`.

## Optional reference image prompt

Ask for optional reference images when they would help with layout, style, density, or visual metaphor:

`如果你有1–3张参考图，可以发给我，我会分析它们的布局、信息层级、文字密度和视觉语言；如果没有，我也会继续按论文主张推进。`

Do not ask this in every single turn. Do not block progress when the user has no reference images. If images are provided, analyze transferable principles and avoid exact copying.


## Footer must be an update, not a placeholder

The footer should record what changed in the current turn. If the turn only updates a rule, record the rule update as an artifact or fixed decision. Do not copy an old state block unchanged.

## v2.3 next-step prompt placement rule

Copyable next-turn prompt suggestions must appear only in the final `下一步你可以这样问` section. Do not place them in the opening plan, analysis body, option tables, recommendation block, or state bullets.

The state footer may summarize the immediate next action, but it should not introduce additional user-prompt wording. The final prompt list must be checked against the current plan and default recommendation so the response does not contain conflicting next steps. Prompt 1 should normally match `recommended_default`.


## v2.4 plan-step visibility rule

Every text-only reply must visibly list the plan and the current step near the beginning, not only in the footer. The current step must be explicit, for example `当前处于：第 4/12 步 — 图机会地图`. The footer repeats the same step. If the plan changes, both the visible plan block and footer must reflect the change.

## v2.5 startup confirmation rule

The first trigger is a gate, not the first design step. It previews the plan and waits for confirmation. After confirmation, the skill works step-by-step from Intake onward.


## v2.6 style-state requirement

When visual style is discussed, the text reply and state footer must record whether style is `not_started`, `style_board_proposed`, `default_recommended`, or `locked`. If a default style is recommended, include the rationale and at least one risk control.

Do not let style recommendations contradict earlier reader-effect or layout decisions. If a user asks for a style that conflicts with the paper slot, explain the risk and offer a safer adaptation.
