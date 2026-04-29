# Plan Step Visibility Protocol

Every text-only reply must make the execution plan visible, not just store it in the footer. The user should always know which step of the plan is being executed now.

## 1. Required visible plan block

Every `TEXT_ONLY` reply must include a compact visible plan block near the beginning of the answer, before detailed analysis or recommendations. This applies to opening turns, continuation turns, review turns, and short corrective turns.

Use a concise block such as:

```markdown
## 当前执行计划
- 当前处于：第 X/Y 步 — <step name>
- 本轮目标：...
- 计划步骤：
  1. ... ✅ / 已完成
  2. ... ⏳ / 当前
  3. ... ⬜ / 待执行
  4. ... ⬜ / 待执行
- 本轮是否调整计划：无 / 因为...，调整为...
```

For very short rule-update answers, the block may be shorter, but it must still state `当前处于：第 X/Y 步`.

## 2. Current-step marking

The current step must be explicit. Do not only say “当前执行计划：继续推进”. Mark the exact step as one of:

- `第 1 步：输入与材料判断`
- `第 2 步：Figure Effect Contract`
- `第 3 步：论文逻辑压缩与瓶颈诊断`
- `第 4 步：图机会地图`
- `第 5 步：候选图方案生成`
- `第 6 步：方案锁定`
- `第 7 步：内容架构与 panel choreography`
- `第 8 步：视觉决策轮 / 参考图分析`
- `第 9 步：图像 brief / prompt 构建`
- `第 10 步：IMAGE_ONLY 图像生成`
- `第 11 步：图稿诊断与修订`
- `第 12 步：最终 caption / legend / 正文插入段`

The assistant may collapse or rename steps for a specific task, but it must still show the current step number and total number of steps.

## 3. Footer alignment

The state footer must repeat the current plan step in compact form:

```markdown
- 当前处于计划第 X/Y 步：...
- 当前执行计划：...
```

The visible plan block, state footer, default recommendation, and final `下一步你可以这样问` prompts must all agree.

## 4. Do not violate final-only prompt rule

The visible plan block may say what action will happen next, but it must not contain copyable user-prompt sentences. Copyable next-turn prompts still belong only in the final `下一步你可以这样问` section.


## 5. Startup gate step

In v2.5, the first skill-trigger response should use a special step before substantive execution:

`当前处于：第 0/N 步 — 启动确认与流程预览`

This step must still use the normal visible plan block, but it previews the workflow and asks for confirmation rather than analyzing the paper. After confirmation, the next current step should become `第 1/N 步 — 输入与材料判断`.
