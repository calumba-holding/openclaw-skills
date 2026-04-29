## 错误处理

所有脚本遵循统一错误约定：

- **成功**：JSON 到 stdout，含 `"success": true`
- **失败**：JSON 到 stderr，含 `"success": false` 和 `"error"` 字段，exit code ≠ 0
- **Agent 应同时检查 stdout 和 stderr**

### Agent 判定顺序（统一）

> 串联门禁总览见 `SKILL.md`「阶段状态机」；本节为 **success/字段判定** 与 **用户可见输出** 的通用真源。

1. 先判断 `success`：
   - `success=false`：当前链路中断，先处理 `error`
   - `success=true`：进入当前脚本的阶段字段判定
2. 再按脚本类型判断：
   - parse：看 `stage`、`missingFields`、`userOutputTemplate.clarifyQuestions`、`parseMeta`；补丁被拒时看 `error=patch_fields_locked` 与 `rejectedFields`
   - validate：看 `validationReport.scope`（`FULL`/`TBV`）、`validationReport.passed`、`blockingIssues`、`warningIssues`；TBV 时可看 `tbvReport`
   - create：看 `userConfirmation`、校验与草稿 `meta` 组合是否满足创建门禁（见 `references/tbs-scene-create.md`），以及 `sceneId` 等结果字段
3. 最后按 `userOutputTemplate` 组织用户可见中文话术，不直出内部 JSON。

### 统一示例（成功）

```json
{
  "success": true,
  "stage": "BASE_INFO_CONFIRM",
  "missingFields": [],
  "userOutputTemplate": {
    "clarifyQuestions": []
  }
}
```

### 统一示例（失败）

```json
{
  "success": false,
  "error": "创建前校验未通过：validationReport.passed=false，请先修复 blockingIssues"
}
```

## 用户可见输出（通用，各脚本不再重复展开）

通用硬约束（唯一）：
1. JSON 只给 Agent 读；对用户只输出中文业务句，优先使用各脚本 `userOutputTemplate`。
2. 仅使用脚本返回字段组织回显，不自行增删字段或改写字段含义。
3. **禁止**直出内部信息：英文字段名、内部状态、issue 码、鉴权原文与技术上下文报错。
4. `validationReport.passed=false` 时必须明确告知“当前不可确认创建 + 待修正项”，修复前不得假装可落库。
5. 基础信息收集采用“双阈值”：完整性门禁优先，同时限制追问成本，避免无限追问。
6. 用户补充"代表话术/最佳实践"时，当轮明确告知"已采纳"，并按 `bestPracticeTargetSection` 回显归入位置（`bestPracticeTargetSection` 由脚本在 `userOutputTemplate` 中返回，默认值为 `coachOnlyContext ## 最佳实践`）。
7. 同轮用户侧最多输出 1 条最终消息；若同轮内有多次解析结果，仅保留最新结果渲染，禁止连续发送“解析结果+补充解释”两条消息。

### 绝对禁止直出字段（强制）

以下内部字段或状态不得出现在用户可见文案中（包含原字段名、`key=value`、代码块）：

- `baseInfoAcknowledged`
- `updatedConfirmationEchoed`
- `mustEchoUpdatedConfirmation`
- `validationReport`
- `blockingIssues`
- `warningIssues`
- `createAgentHints`
- `systemActionHint`
- `sessionId`
- `sessionDir`
- `draftPath`

若需表达其业务含义，必须转写为中文业务语句（例如：“基础信息已确认，可继续下一步”），不得透出技术字段名。

### 四时点最小真源（强制）

只按以下 4 个时点组织用户可见内容，其他描述均以本表为准。

| 时点 | 触发条件 | 必须展示 | 下一步 |
|------|----------|----------|--------|
| 收集阶段 | `stage=BASE_INFO_CONFIRM` 或 `stage=KNOWLEDGE_CONFIRM` | 当前阶段字段原值（不摘要）；缺失项；`clarifyQuestions`（仅补充） | 用户补充/确认后重新 parse |
| 修改回显 | `mustEchoUpdatedConfirmation=true`（`updatedFieldLabels` 仅用于回显内容，不单独触发）；Agent 完成回显后在下轮 payload 写 `updatedConfirmationEchoed=true` 告知脚本已回显 | 更新字段说明 + 更新后确认清单（优先 `updatedConfirmationItems`，否则 `confirmationItems`） | 用户确认后进入 validate（或继续 parse） |
| 落库前确认 | validate 通过且准备 create（并满足 validate/create 组合门禁） | 最终清单（按 `mustDisplayFields`/`mustDisplayConfirmationItems` 完整展示）；仅给“确认/取消”收口 | 用户确认后调用 create |
| 落库结果 | create 返回成功/失败 | 成功：`sceneId` + 关键结果字段；失败：业务化原因 + 下一步动作 | 结束或按提示补充后重试 |

显示优先级与字段真源（唯一）：
1. 所有字段用原值回显，不做二次改写摘要。
2. 字段展示优先级按时点区分：
   - 修改回显：`sceneBackgroundFullText`（命中时）> `updatedConfirmationItems` > `confirmationItems`
   - 落库前确认：`sceneBackgroundFullText`（命中时）> `mustDisplayConfirmationItems` > `confirmationItems`
3. 当 `mustShowSceneBackgroundFullText=true` 时，`sceneBackgroundFullText` 必须原文展示，不得摘要改写。
4. 若存在 `userOutputTemplate.createAgentHints`，落库前确认阶段必须同步遵守其展示与收口要求。
5. `KNOWLEDGE_CONFIRM` 阶段展示优先级：`phaseSections` > `confirmationItems` > `clarifyQuestions`；禁止只展示 `clarifyQuestions`。
6. 当用户侧文案出现“基础信息确认 ✓/已确认”时，调用方必须确保本轮或下一轮 parse payload 携带 `baseInfoAcknowledged=true`；否则改为“基础信息待你确认”。
7. 结果选取规则：用户侧仅展示“本轮最新 parseResult”；若存在多条结果，按 `updatedAt`/轮次取最后一条，旧结果一律丢弃。
8. 一致性规则：若 `parseResult.baseInfoAcknowledged=true` 且 `stage=KNOWLEDGE_CONFIRM`，禁止再展示“请先确认基础信息”类话术。

创建前展示声明（强制）：
1. 用户最终确认后调用 `tbs-scene-finalize-from-session.py`；脚本内部创建前必须声明已完整展示 `mustDisplayFields`：
   - 方式 A：`displayContractSatisfied=true`
   - 方式 B：`displayedFields`（字段键名数组，必须覆盖 `mustDisplayFields`）
2. `mustDisplayFields` 默认最小集合：
   - `businessDomainName`、`departmentName`、`drugName`、`location`、`doctorConcerns`、`repGoal`、`productKnowledgeNeeds`、`title`、`sceneBackground`、`actorProfile`
3. 未声明或声明不完整时，create 链路返回 `display_gate_failed`，阻断创建。
4. 用户确认必须绑定本轮最终确认清单：`confirmedDisplayHash=validationReport.displayHash`；若确认后用户可见字段变化，必须重新展示最终确认并重新取得确认。

分阶段必显字段（统一）：
1. `BASE_INFO_CONFIRM`：`businessDomainName`、`departmentName`、`drugName`、`location`、`doctorConcerns`、`repGoal`
2. `KNOWLEDGE_CONFIRM`：阶段 1 全部字段 + `productKnowledgeNeeds`；主题由系统先建议，用户确认/删除/改名/新增后才可推进
3. `READY_FOR_SCENE_GENERATION`：阶段 2 全部字段（含 `productKnowledgeNeeds`）；`title`、`sceneBackground` 此时待内部生成，展示为「生成中」占位，不作为此阶段必显项
4. `READY_FOR_VALIDATE`：`businessDomainName`、`departmentName`、`drugName`、`location`、`doctorConcerns`、`repGoal`、`productKnowledgeNeeds`、`title`、`sceneBackground`、`actorProfile`

产品知识检查门禁（强制）：
1. 用户确认 `productKnowledgeNeeds` 后，路径 A 立即执行 `scripts/tbs-scene-knowledge-check.py`；路径 B 设置 `meta.deferKnowledgeCmsCheckUntilPreCreate=true`，由 `tbs-scene-finalize-from-session.py` 在最终确认后执行。
2. 检查顺序：按 `drugName` 解析 `drugId`；若品种不存在则先创建品种并写回 `scene.drugId` / `meta.resolvedIds.drugId`；若匹配多条则停下要求人工确认。
3. 拿到 `drugId` 后，按确认主题查询已有产品知识 → 已存在则复用 `knowledgeIds`。
4. 不存在且用户已提供同名 `knowledge` 正文时，脚本先查重，仍不存在才创建产品知识。
5. 不存在且无正文时，停留在 `KNOWLEDGE_CONFIRM`，回显 `missingKnowledgeTopics`，提示用户“可补充每个主题的正文要点，或选择暂无正文继续”（**不得**在用户可见文案中出现 `category/title/content/requiredFields` 等内部字段名）。
6. 路径 A 只有 `knowledgeReady=true` 后才可进入 `READY_FOR_SCENE_GENERATION`；路径 B 可先生成场景，但最终落库前必须由 finalize 补齐 knowledge-check。
7. 性能与去重（不改变门禁语义）：若草稿中已存在 `knowledgeReady=true`、`knowledgeIds` 完整，且 `meta.lastKnowledgeKey` 与本轮输入计算结果一致，则允许跳过重复网络检查，直接复用既有 `knowledgeIds`（避免反复请求导致慢）。

产品知识展示口径：
- `productKnowledgeNeeds` 只显示为“产品知识主题”。
- `knowledge` 只显示为“产品知识正文（可选）”。
- 若未提供 `knowledge` 正文，且当前轮次仅做“主题确认”（尤其主题刚更新的回显），用户可见输出应**省略**“正文为空”的状态播报；只需提示“可选补充正文（不影响推进）”。无论如何不得把“正文为空”写到“产品知识主题”下。
- “暂无正文”不等于“无需产品知识主题”；`productKnowledgeNeeds` 必须展示并经用户确认后才可推进。
- 基础信息齐备但未确认时仍按 `BASE_INFO_CONFIRM` 展示，不展示产品知识主题清单；只提示“确认基础信息后会生成产品知识主题供确认”。
- 产品知识主题应按 `references/product-knowledge-topic-generate.md` 生成；脚本不得用内置业务主题替 Agent 出题。
- 产品知识主题确认采用轻确认：如无调整回复“确认”；可删除、改名或新增；不得要求用户补正文后才推进。

### 输出模板真源

用户可见模板统一维护在 `references/output-templates.md`。本文件只保留输出规则、字段拦截、展示优先级与通用参数。

模板使用对照：

| 当前时点 | 必用模板 |
|---------|---------|
| 收集阶段 | `output-templates.md` 模板 1 |
| 字段有更新 | `output-templates.md` 模板 2 |
| 落库前确认 | `output-templates.md` 模板 3 |
| create 成功 | `output-templates.md` 模板 4A |
| create 失败 | `output-templates.md` 模板 4B |

## 通用参数

所有脚本均支持以下通用参数：

| 参数 | 说明 |
|------|------|
| `--params-file <path>` | 从 UTF-8 JSON 读参数，解决长文本和中文转义问题。 |
| `--input <path>` | 与 `--params-file` 等价，兼容旧调用。 |
| `--output <path>` | 将完整 JSON 写入文件；stdout/stderr 只输出一行摘要，避免内部 JSON 外显。Agent 运行脚本时必须使用。 |

### 用法示例（`--params-file` 参数层）

```json
{
  "userText": "帮我创建一个心内科沟通场景",
  "scene": {},
  "parsedFields": {},
  "draftPath": ".cms-log/state/cms-tbs-scene-create/demo-draft.json"
}
```

```bash
python3 scripts/tbs-scene-parse.py --params-file payload.json --output result.json
```

> 文件参数与命令行参数可混用，命令行参数优先级更高。文件必须为 UTF-8 编码。

### 推荐链路示例（自然语言长文本）

1. 先按 `references/base-info-parse.md` 提取基础信息骨架。
2. 将基础信息结果放入 `parsedFields`，执行 `tbs-scene-parse.py`。
3. 根据 `tbs-scene-parse.py` 返回的 `stage` 继续做用户确认或内部生成。

推荐 payload 形状：

```json
{
  "userText": "用户原始输入",
  "scene": {},
  "parsedFields": {
    "businessDomainName": "临床推广",
    "departmentName": "消化内科",
    "drugName": "美沙拉秦肠溶片",
    "location": "三级医院门诊",
    "doctorConcerns": [
      "产品优势",
      "集采与价格"
    ],
    "repGoal": "帮助医生快速了解产品特点并回应价格顾虑"
  },
  "draftPath": ".cms-log/state/cms-tbs-scene-create/demo-draft.json"
}
```
