# Session State Schema v2.7

Every text-only reply should preserve a compact state. v2.7 keeps the startup confirmation gate, explicit visual-style taxonomy state, and adds visual-first decision board state for early category/layout/style/metaphor/density choices. v2.5 adds a startup confirmation gate: the first skill-trigger response previews the plan and waits for confirmation before substantive figure design.

```yaml
state_version: v2.7
mode_this_turn: TEXT_ONLY | IMAGE_ONLY
start_gate:
  start_confirmed: false | true
  awaiting_user_confirmation: false | true
  startup_plan_shown: false | true
  confirmation_summary:
working_plan:
  plan_id:
  visible_plan_block_required: true
  plan_status: startup_gate | opening | active | adjusted | completed
  current_stage:
  current_step_index:
  total_steps:
  current_step_name:
  goal_this_round:
  planned_steps:
  completed_steps:
  plan_adjustments:
  next_step:
stage: Startup Confirmation Gate | Intake | Effect Contract | Opportunity Map | Candidate Schemes | Selected Scheme | Visual Decision | Image Brief Ready | Image Generated | Review | Revision | Final Text Package
reference_images:
  status: not_asked | requested_optional | provided | analyzed | not_needed
  count:
  transferable_principles:
  avoid_copying:
recommended_default:
  current_recommendation:
  reasons:
  alternative_when:
paper_summary:
  topic:
  main_claim:
  problem_gap:
  core_mechanism:
  contribution_delta:
figure_effect_contract:
  figure_slot:
  target_reader:
  10_second_takeaway:
  60_second_takeaway:
  reader_question:
  misconception_to_prevent:
  figure_thesis:
  anchor_case_or_evidence:
figure_decisions:
  figure_family:
  selected_scheme:
  panel_count:
  reading_path:
  layout_skeleton:
  visual_rhetoric:
  style_family:
  style_candidates_considered:
  default_style_recommendation:
  style_rationale:
  style_risks:
  aspect_ratio:
  label_policy:
  color_semantics:
  density:
visual_decision_boards:
  visual_decision_mode: text_only | exploratory_image_board | final_image_batch
  visual_board_recommended: false | true
  visual_board_type: figure_direction | layout | style | metaphor | density | refinement | final_candidate
  visual_board_axis_varied:
  visual_board_candidate_count:
  visual_board_status: not_started | proposed | confirmed | generated | reviewed | skipped
  visual_board_fixed_elements:
  selected_visual_candidate:
  default_visual_recommendation:
visual_candidate_history:
  - batch_id:
    candidate_count:
    varied_axis:
    fixed_elements:
    user_selection:
    rejected_reason:
artifacts:
  - name:
    type:
    status:
open_questions:
  - ...
next_recommended_actions:
  - ...
```

## Mandatory footer

Every text-only response must end with an updated footer. The state cannot be copied forward unchanged unless nothing changed; even then, the current working plan and next action must be restated. Every text-only response must include a visible `当前执行计划` block near the beginning and must end with:

```markdown
## 当前状态与产物
- 阶段：...
- 当前处于计划第 X/Y 步：...
- start_confirmed：true / false / 已完成启动门控
- awaiting_user_confirmation：true / false
- 当前执行计划：...
- 计划调整：无 / ...
- 已定：...
- 待定：...
- 默认推荐：...
- 参考图状态：未提供 / 已请求 / 已分析 / 暂不需要
- 视觉风格状态：未开始 / 已比较 / 已推荐 / 已锁定；默认推荐风格：...
- 视觉决策板状态：未开始 / 建议生成 / 已生成 / 已评审 / 已跳过；类型：...；变化轴：...
- 产物：...
- 下一轮建议（动作，不写成用户提问句）：...
- 渲染规则提醒：ChatGPT web 使用原生图像生成的独立动作；OpenClaw/Codex/Trae/API 使用 OpenAI ChatGPT Images 2.0 或更新模型；禁止 SVG / Mermaid / TikZ / Graphviz / 代码绘图替代。

## 下一步你可以这样问
1. `请根据引导skill以及当前的状态，继续...`
2. `请根据引导skill以及当前的状态，继续...`
3. 不知道下一步时：`请根据引导skill以及当前的状态，继续告诉我下一步做什么。`
```

For the startup gate, the first final prompt should normally ask to confirm start and continue to 第1步.

## v2.3 next-step prompt consistency

- `next_recommended_actions` stores action summaries only.
- Copyable user prompts must be printed only in the final `下一步你可以这样问` section.
- The first final prompt should normally match `recommended_default`.
- The state footer's `下一轮建议` should be phrased as an action, not as a user question.

## v2.4 plan-step visibility

- Every text-only answer must show a visible `当前执行计划` block near the beginning.
- The visible block must include `当前处于：第 X/Y 步 — <step name>`.
- The footer must repeat the same current step as `当前处于计划第 X/Y 步：...`.
- The visible plan block, footer, default recommendation, and final prompt list must be consistent.
- The visible plan block must not contain copyable next-turn prompt suggestions; those remain only in `下一步你可以这样问`.

## v2.5 startup confirmation gate

- First skill-trigger reply uses `stage: Startup Confirmation Gate`.
- First skill-trigger reply sets `start_confirmed: false` and `awaiting_user_confirmation: true`.
- No substantive figure analysis happens until the user confirms.
- After confirmation, set `start_confirmed: true` and move to Intake.


## v2.6 visual style taxonomy

- When visual style is a decision, compare a compact set of relevant style families rather than giving only a vague style adjective.
- Supported mainstream choices include editorial flat, formal architecture schematic, mechanism snapshot, premium scientific illustration, isometric / soft 3D, low-poly abstract 3D, cartoon / comic-lite, storyboard, tile / card / mosaic, paper-cut collage, blueprint, dashboard metaphor, mini-evidence infographic, and minimal line-art.
- The assistant must recommend one `默认推荐风格` and record style rationale and risks in state.
- For high-variance styles such as 3D, cartoon, photorealistic, and tile/mosaic boards, record risk controls in `style_risks`.

## v2.7 visual-first decision boards

- When category, layout, style, metaphor, or density is primarily a visual decision, the assistant may recommend or proceed to an exploratory `IMAGE_ONLY` board before the final figure-generation round.
- Boards are tracked separately from final image batches using `visual_decision_boards`.
- Board types include `figure_direction`, `layout`, `style`, `metaphor`, `density`, `refinement`, and `final_candidate`.
- A board should normally vary one dominant axis while fixing paper thesis, anchor case, and core labels.
- After a board is reviewed, record the selected candidate and default recommendation.
