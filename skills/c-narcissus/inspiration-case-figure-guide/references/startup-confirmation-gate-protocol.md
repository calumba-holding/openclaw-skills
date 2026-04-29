# Startup Confirmation Gate Protocol

This protocol prevents the skill from jumping into figure design before the user understands the workflow.

## 1. First-trigger behavior

When the skill is invoked for a new task and there is no active state with `start_confirmed: true`, the first text-only reply must be `STARTUP_PLAN_ONLY`.

The assistant must not yet perform substantive figure analysis, scheme ranking, prompt construction, or image generation. It may briefly acknowledge the available input, but it should not start reading or interpreting the paper in detail.

## 2. What the first reply must contain

The first reply must include:

1. a visible `当前执行计划` block with `当前处于：第 0/N 步 — 启动确认与流程预览`
2. a complete step-by-step workflow preview, with each step described in plain language
3. what the user can provide before starting: draft/PDF, abstract, method summary, existing sketch, reference figures, target slot, style preference, preferred or avoided visual families such as 3D, cartoon/comic-lite, tile/card/mosaic, editorial flat, formal architecture, constraints
4. how the skill will behave after confirmation: execute one step at a time, update state after every text turn, adapt the plan when necessary, keep copyable prompts only at the end
5. a recommended default route for users who want to proceed directly
6. optional reference-image note: reference images help but are not required
7. a state footer indicating `start_confirmed: false` and `awaiting_user_confirmation: true`
8. final `下一步你可以这样问` prompts, with the first prompt normally being a confirmation/start prompt

## 3. What counts as confirmation

After the startup gate, treat any of the following as confirmation:

- the user says 确认开始 / 开始 / 继续 / 直接开始 / 按默认路线开始 / 可以开始
- the user sends paper material with an instruction to proceed
- the user chooses a target figure slot or route and asks to continue
- the user uses a final suggested prompt that explicitly asks to start the workflow

Once confirmed, set `start_confirmed: true` and move to Round 0 / Intake.

## 4. If the user changes the plan before confirmation

If the user edits the workflow, target slot, candidate count, reference-image policy, visual style policy, or response style before confirmation, update the startup plan and remain in the confirmation gate until the user confirms.

## 5. If the user asks to skip confirmation

If the first user message already says they want to skip the startup gate or immediately execute, still give a very compact gate once unless the skill already has an active confirmed state. The gate may be short, but it must still ask for confirmation before substantive work.

## 6. First-trigger template

```markdown
## 当前执行计划
- 当前处于：第 0/9 步 — 启动确认与流程预览
- 本轮目标：先展示完整制图流程、每一步会做什么、需要/可选材料、默认推进路线；等用户确认后再进入第 1 步。
- 计划步骤：
  0. 启动确认与流程预览 ⏳ 当前
  1. 输入与材料判断 ⬜ 待确认后执行
  2. Figure Effect Contract ⬜ 待执行
  3. 论文逻辑压缩与瓶颈诊断 ⬜ 待执行
  4. 图机会地图与默认推荐 ⬜ 待执行
  5. 候选方案生成与锁定 ⬜ 待执行
  6. 图像 brief / prompt 构建 ⬜ 待执行
  7. IMAGE_ONLY 候选图生成 ⬜ 待执行
  8. 图稿诊断、修订与论文配套文字 ⬜ 待执行
- 本轮是否调整计划：无
```

Do not put copyable user prompts inside this plan block. Those belong only in the final `下一步你可以这样问` section.
