<!-- Gate-4 · READY_FOR_VALIDATE → 落库前确认 ────────────────
  步骤  Step1 执行 validate(scope=FULL)；passed=false → 转写blockingIssues为中文，禁止继续
        Step2 仅 passed=true 后：执行 SKILL.md §D 自检；未通过不得展示落库前确认
        Step3 模板3 完整展示 mustDisplayFields；只给"确认/取消"收口
        Step4 等待用户明确回复；"取消"→终止；"确认"→进Gate-5
  禁止  passed=false 时继续；未完整展示 mustDisplayFields 就收口；
        scope=TBV 通过直接 create（须同时满足 meta.lastFullValidationPassed）
  推进  用户明确回复"确认" → 进 Gate-5
──────────────────────────────────────────────────────── -->

### 2. 校验场景 — `tbs-scene-validate.py`

**意图**：校验场景草稿是否已经达到“可向用户发起最终确认”的条件。

```bash
python3 scripts/tbs-scene-validate.py --params-file draft.json --output validate-result.json
python3 scripts/tbs-scene-validate.py --params-file draft.json --scope tbv --output validate-tbv-result.json
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `--params-file` / `--input` | ✅ | 输入 JSON 文件 |
| `--scope` | ❌ | `full`（默认）或 `tbv`；也可在输入 JSON 顶层传 `validationScope`：`FULL` / `TBV` |

| `scope` | 含义 | `meta`（有 `draftPath` 时） |
|---------|------|---------------------------|
| `FULL`（默认） | 下列全量「创建前」规则 | `passed` → `lastFullValidationPassed`；写入 `lastValidatedSceneHash`；失败时清 `lastTbvPassed` |
| `TBV` | 仅 `title`、`sceneBackground` 叙述规则（**背景类 issue 一律阻断**） | `passed` → `lastTbvPassed`；写入 `lastValidatedSceneHash`；另有 `tbvReport` |

写草稿：**合并**原文件，只覆盖 `scene`、`validationReport`、`meta`（保留 `parseResult` 等）。

## 调用决策（避免误用）

| 场景变更 | 推荐 scope | 说明 |
|---|---|---|
| 仅改 `title` / `sceneBackground` | `TBV` | 轻量校验，适合补丁后快速回归 |
| 改了基础字段、`doctorOnlyContext`、`coachOnlyContext`、`actorProfile`、`productKnowledgeNeeds` | `FULL` | 必须跑全量门禁 |
| 准备发起 create 前最终检查 | `FULL`（或 `TBV + meta.lastFullValidationPassed=true`） | 仍需满足知识检查门禁（`knowledgeReady=true`）与 create 展示门禁（`displayContractSatisfied` 或完整 `displayedFields`） |

> 关键：`validationReport.passed=true` 仅表示“本次 scope 通过”。  
> - `scope=TBV` 时，**不等于可直接创建**。  
> - `validationReport.sceneHash` 必须与 create 时当前 `scene` 的 hash 一致；不一致必须重新 validate。
> - `validationReport.displayHash` 必须绑定本轮最终确认展示内容；用户确认后传给 create 的 `confirmedDisplayHash` 必须与它一致。
> - 可创建判定以 `tbs-scene-create.py` 的组合门禁为准。

**校验要求（`scope=FULL`）**：

- 必须具备：`title`
- 必须具备：`businessDomainName`
- 必须具备：`departmentName`
- 必须具备：`drugName`
- 必须具备：`location`
- 必须具备：`doctorConcerns`
- 必须具备：`repGoal`
- 必须具备：`sceneBackground`
- 必须具备：`productKnowledgeNeeds`
- `sceneBackground` 额外规则：长度 <= 180；不得包含【】或“待补充”；不得使用标签化前缀（如“场景背景：”）；`departmentName` 与 `location` 需作为子串出现；`drugName` 允许以括号前主名称作为锚点（与 `references/scenario-json-parse.md` 描述一致）；避免出现面向具体个人的代词（你/我/他/她/它/咱/咱们/我们/你们/他们/她们）。
- 必须具备：`doctorOnlyContext`
- 必须具备：`coachOnlyContext`（且须包含 5 节固定标题，按顺序：`## 期望代表行为`、`## 评分重点`、`## 终止条件`、`## 最佳实践`、`## 输出要求`；详见 `references/scenario-json-parse.md §coachOnlyContext 要求`）
> 说明：`doctorOnlyContext` 与 `coachOnlyContext` 仍然是创建前必过的内部门禁，但不属于用户逐段确认内容。

**说明**：不再要求证据状态/证据来源作为校验阻断条件。`doctorOnlyContext` 的 `## 核心顾虑` bullet ≥3 条时合并为至多 2 条并记入 `autoNormalized`；生成阶段仍应尽量一次合规。

**流程**：读 `scene` → 规范化 → 计算 `sceneHash` 与 `displayHash` → 按 `scope` 收集 issues → `validationReport`（含 `sceneHash`、`displayHash`、`blockingIssues` / `warningIssues`；**TBV 无 warning 分桶**）→ `passed=true` 可进用户确认/下一步。`success` 判定同 `common-params.md`。

**FULL 专用**：`sceneBackground` 的 `too_long` / `placeholder` / `label_style` / `pronoun` / `anchor_missing` 进 **warning**；其余 issue 进 **blocking**。**TBV** 下上述背景码也进 **blocking**。

**与 create**：仅 TBV 通过不能落库，须 `meta.lastFullValidationPassed`（见 `tbs-scene-create.md`）。

**自动修复**：`sceneBackground` 低风险规范化（符号/占位/前缀/锚点/长度）；写入 `validationReport.autoNormalized` 供追踪，**不改变** TBV/FULL 各自放行语义。

**用户可见话术（通用）**：`common-params.md`。  
**validate 特有**：转述 `confirmationItems` 时**须含场景背景完整正文**（若 `mustShowSceneBackgroundFullText=true`，优先使用 `sceneBackgroundFullText` 原文）；禁止写成“场景背景（摘要）/背景摘要/节选”，勿用「训练目标」替代；用 `issueHints` / `warningHints`（`passed=true` 时 warning 勿说成必改）。若返回 `mustDisplayFields` / `mustDisplayConfirmationItems`，须完整展示该清单并在创建前声明展示已完成。若用户本轮有修改，回显触发与内容范围统一遵守 `common-params.md`「修改回显协议（强制）」。

**Agent 专用输出（`scope=FULL`，stdout JSON）**：

| 字段路径 | 出现条件 | 用途 |
|----------|----------|------|
| `userOutputTemplate.doctorOnlyContextCanon` | 恒出现（FULL） | `requiredHeaderOrder`、`outputRequirementsLines`、`endingRulesLines`：生成或修复 `doctorOnlyContext` 时与校验脚本逐字对齐 |
| `userOutputTemplate.doctorOnlyContextDiagnostics` | `doctorOnlyContext` 未通过 | `reasonCodes` / `agentHints`：定位标题顺序、核心顾虑条数、两节固定模板是否逐字一致 |
| `userOutputTemplate.createAgentHints` | `passed=true` | 创建前须先完成 `tbs-scene-knowledge-check.py`，再满足 `displayContractSatisfied`（或 `displayedFields`）、`confirmedDisplayHash` 及用户确认口径 |
| `userOutputTemplate.preCreateBlockedReminder` | `passed=false` | 明确禁止在阻断未清除时调用 `tbs-scene-create`，并要求先对用户说明原因 |

## 校验失败后的动作（Agent）

1. 先按 `issueHints` / `doctorOnlyContextDiagnostics.agentHints` 给用户业务化说明“哪里不通过、怎么修”，不要只回 error code。
2. 若是 `doctorOnlyContext_invalid`：优先使用 `doctorOnlyContextCanon` 的固定段落逐字回填，再跑 `FULL`。
3. 仅改了标题/背景时可先 `TBV` 快速回归；涉及上下文/基础字段变动后，必须回到 `FULL`。
4. `passed=false` 时不得进入 create；需修复并重新校验通过后，再向用户收口“确认/取消”。

---

## 判定示例（内部）

### 可进入确认

```json
{
  "success": true,
  "validationReport": {
    "scope": "FULL",
    "passed": true,
    "blockingIssues": [],
    "warningIssues": [
      "scene.sceneBackground_pronoun"
    ]
  }
}
```

### 不可进入确认

```json
{
  "success": true,
  "validationReport": {
    "scope": "FULL",
    "passed": false,
    "blockingIssues": [
      "scene.title_missing"
    ],
    "warningIssues": []
  }
}
```
