# Planning and State Update Protocol

This protocol makes the skill feel like a guided design process rather than a sequence of disconnected prompts.

## 0. Startup confirmation gate

For every newly triggered figure-design task, if there is no active state with `start_confirmed: true`, the first text-only reply must be `STARTUP_PLAN_ONLY`.

The assistant must first show the full workflow plan, describe each step, list helpful optional materials, recommend a default start route, and wait for user confirmation. It must not perform substantive figure analysis, paper interpretation, scheme selection, prompt construction, or image generation in this first gate response.

The startup gate should mark the current step as:

`当前处于：第 0/N 步 — 启动确认与流程预览`

Set in the footer:

- `start_confirmed: false`
- `awaiting_user_confirmation: true`
- `阶段：Startup Confirmation Gate`

After the user confirms, set `start_confirmed: true` and proceed to Round 0 / Intake.

## 1. Opening execution plan after confirmation

Once the user confirms start, begin the actual workflow with a compact execution plan. The plan should be visible to the user and should come before detailed figure analysis.

Required plan fields:

- `current_stage`: where the workflow is starting
- `goal_this_round`: what the current answer will produce
- `planned_steps`: 3–6 upcoming steps, such as intake → effect contract → opportunity map → candidate schemes → image brief → image generation
- `inference_policy`: what can be inferred from the draft and what would genuinely need user input
- `reference_image_check`: whether optional reference images would help now
- `default_route`: recommended path if the user wants to proceed directly

## 2. Adaptive plan updates

The plan is allowed to change. Update it when:

- the user adds new paper material or changes the target figure slot
- a figure effect contract is created or revised
- the user chooses or rejects a scheme
- reference images reveal useful visual principles
- generated candidates expose a layout, density, or metaphor problem
- the workflow moves to prompt generation, image generation, review, or final captioning

When the plan changes, include a short note: `计划调整：因为...，所以接下来...`

## 2A. Visible plan and current step in every text turn

Every text-only reply must show a compact plan block near the beginning of the answer. It is not enough to store the plan in the state footer. The user must be able to see both the plan and exactly where the current turn sits within it.

Required fields:

- `当前处于：第 X/Y 步 — <step name>`
- `本轮目标：...`
- `计划步骤：...` with completed/current/waiting markers
- `本轮是否调整计划：无 / 因为...，调整为...`

The footer must repeat the same step as `当前处于计划第 X/Y 步：...`.

The plan block may describe actions, but must not include copyable next-turn user prompts.

## 3. Mandatory state update after every text answer

Every text-only reply must end with `当前状态与产物` and `下一步你可以这样问`. This includes short acknowledgements, corrections, and turns that only modify a rule.

The state update must not be a blank template. It must record the newest state of the task:

- current stage
- current plan step, written as `当前处于计划第 X/Y 步：...`
- startup gate status: `start_confirmed` and `awaiting_user_confirmation`, when relevant
- current working plan
- plan adjustment, if any
- fixed decisions
- unresolved decisions
- recommended default
- reference image status
- artifacts created so far
- next recommended action

## 4. Compact footer pattern

Use this pattern at the end of every text-only answer:

```markdown
## 当前状态与产物
- 阶段：...
- 当前处于计划第 X/Y 步：...
- start_confirmed：true / false / 已完成启动门控
- awaiting_user_confirmation：true / false
- 当前执行计划：...
- 计划调整：无 / 因为...，已调整为...
- 已定：...
- 待定：...
- 默认推荐：...
- 参考图状态：未询问 / 已询问可选 / 已提供 / 已分析 / 暂不需要
- 产物：...
- 下一轮建议（动作，不写成用户提问句）：...
- 渲染规则提醒：ChatGPT web 使用原生图像生成的独立动作；OpenClaw/Codex/Trae/API 使用 OpenAI ChatGPT Images 2.0 或更新模型；禁止 SVG / Mermaid / TikZ / Graphviz / 代码绘图替代。

## 下一步你可以这样问
1. `请根据引导skill以及当前的状态，继续...`
2. `请根据引导skill以及当前的状态，继续...`
3. 不知道下一步时：`请根据引导skill以及当前的状态，继续告诉我下一步做什么。`
```

For a startup-gate response, prompt 1 should normally be a confirmation/start prompt.

## 5. What not to do

Do not:

- start paper analysis in the first trigger before the user confirms the workflow
- answer only with prose and no state footer
- hide the plan internally
- keep using an outdated plan after the user selects a different route
- ask for reference images as a blocker
- treat the state footer as optional when the answer is short

## v2.3 next-step prompt consistency

The final section `下一步你可以这样问` is the only place where copyable next-turn prompts may appear.

Rules:

- Do not place prompt suggestions in the opening plan, body, tables, default recommendation, or state bullets.
- In the body, write actions rather than user prompts: use “默认推荐动作：锁定布局骨架” instead of “你可以问我继续锁定布局骨架”.
- In the state footer, `下一轮建议` must be an action summary, not a copyable sentence.
- The first prompt in `下一步你可以这样问` should normally match the default recommendation.
- If the final prompt list offers alternatives, they must be mutually compatible and labeled by purpose.
- Run a last-pass consistency check: no earlier line should tell the user to ask something that contradicts the final list.

Do not:

- place suggested next-turn user prompts anywhere except the final `下一步你可以这样问` section
- let the final prompt list contradict the default recommendation or current plan

## v2.7 visual decision board state

When a visual decision board is proposed, generated, reviewed, skipped, or selected, update the state footer with:

- `视觉决策板状态`
- board type
- varied axis
- fixed elements
- candidate count
- selected candidate, if any
- default recommendation

This board state is separate from the final image-generation state.
