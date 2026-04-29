<!-- Gate-1 · BASE_INFO_CONFIRM ──────────────────────────────
  允许  ① 模板1 回显已识别字段+待补充项+clarifyQuestions
        ② 每轮最多2问、最多2轮
        ③ 接收补充后重新 parse
  禁止  调用 validate/create；自行生成 title/sceneBackground/doctorOnlyContext
        扩展确认清单字段；用户未明确确认前设置 baseInfoAcknowledged=true
  推进  6字段齐备 AND 用户明确确认 → 双写 baseInfoAcknowledged=true

  Gate-2 · KNOWLEDGE_CONFIRM ─────────────────────────────
  允许  ① 同时展示基础信息6项+产品知识确认项
        ② 展示主题分桶（existingTopics/suggestedMissingTopics）
        ③ 同轮最多1次 parse
        ④ 用户说"暂无正文"→ 仅记录正文为空
  禁止  只展示知识主题不展示基础信息6项；同轮 parse 超1次
        调用 validate/create；把"暂无正文"当作"无需主题"；向用户索要 title/sceneBackground
  推进  用户确认主题并传 productKnowledgeNeedsConfirmed=true → READY_FOR_SCENE_GENERATION
──────────────────────────────────────────────────────── -->

### 1. 解析场景 — `tbs-scene-parse.py`

**意图**：作为多阶段编排脚本，按“基础信息确认 → 产品知识/资料确认 → 场景内容生成 → 校验”的顺序，输出当前阶段需要用户确认/补充的内容。  
**本脚本不做自然语言全量语义生成**：自然语言长文本或用户零散补充内容，应该先通过 `references/base-info-parse.md` 提取基础信息骨架；本脚本只接收已有 `scene` / `parsedFields`，判断当前处于哪个阶段，并给出下一步动作。
**硬性顺序**：长文本 → `base-info-parse.md` 抽取 `parsedFields` → `tbs-scene-parse.py --output ...`。不得把长文本直接当作最终 `scene` 传入，也不得把脚本完整 JSON 贴给用户。

## 0) 30 秒上手（先看这个）

- 最短命令：`python3 scripts/tbs-scene-parse.py --params-file payload.json --output result.json`
- 最关键输入：`scene`、`userText`、`baseInfoAcknowledged`、`productKnowledgeNeedsConfirmed`、`existingProductKnowledgeTopics`
- 最关键输出：`stage`、`sceneHash`、`missingFields`、`userOutputTemplate.confirmationItems`、`userOutputTemplate.clarifyQuestions`、`userOutputTemplate.supplementItems`、`knowledgeTopicBuckets`
- 推进规则：只按本轮 `stage` 决定下一步，不做调用方硬编码跳转。

```bash
python3 scripts/tbs-scene-parse.py --params-file payload.json --output result.json

# 可选：中间轮次加速（满足条件时快进到 READY_FOR_VALIDATE，且不写草稿）
python3 scripts/tbs-scene-parse.py --params-file payload.json --mode fast_forward --no-write-draft --output result.json
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `--params-file` / `--input` | ✅ | 输入 JSON 文件 |
| `--mode` | ❌ | `default`（默认）或 `fast_forward`；当基础信息已确认且 `scene` 已满足创建前必需字段时，可直接输出 `READY_FOR_VALIDATE`，减少重复 parse 轮次 |
| `--no-write-draft` | ❌ | 若传入则不写回 `draftPath`（返回中含 `draftWriteSkipped=true`），用于中间轮次降低文件 IO |

**输入 JSON 关键字段**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `userText` | ❌ | 用户自然语言输入 |
| `scene` | ❌ | 已有场景草稿 |
| `scene.knowledge` | ❌ | 用户补充的产品知识正文（可选）；创建前按“先查后建”解析为 `knowledgeIds` |
| `parsedFields` | ❌ | 上游结构化补丁，覆盖同名字段（基础信息阶段可用；知识阶段优先写入 `scene`） |
| `userUpdates` / `userConfirmedFields` / `userProvidedFields` | ❌ | 用户本轮补充/纠正字段（与 `parsedFields` 等价，会按同名字段覆盖进 `scene`；知识阶段仅在必要时使用） |
| `draftPath` | ❌ | 草稿文件路径，便于后续 validate/create 复用 |
| `baseInfoAcknowledged` | ❌ | 仅当用户已明确确认基础信息无误时置为 `true`；用于区分“已识别”与“已确认”（也可写入 `scene.baseInfoAcknowledged` 或 `meta.baseInfoAcknowledged`） |
| `declineProductKnowledge` | ❌ | 历史兼容字段，仅表示用户不补充产品知识正文；不得用于跳过 `productKnowledgeNeeds` 主题确认 |
| `scene.actorProfileSupplement` | ❌ | 用户补充的对象角色画像摘要（自由复述）；只用于“补充素材”回显和后续生成，不进入 `missingFields` |
| `scene.bestPracticeSupplement` | ❌ | 用户补充的代表成功经验、开场话术、推进建议或应对方式；只用于“补充素材”回显和后续 `coachOnlyContext ## 最佳实践`，不进入 `missingFields` |
| `actorProfileSupplement` / `bestPracticeSupplement` | ❌ | 顶层历史兼容输入；脚本会迁移到 `scene.actorProfileSupplement` / `scene.bestPracticeSupplement` 并输出 `payloadShapeWarnings`，调用方不得依赖该兜底 |
| `existingProductKnowledgeTopics` / `meta.existingProductKnowledgeTopics` | ❌ | 调用方可选传入“该产品已存在知识主题列表”（接口查询结果）；用于在 `KNOWLEDGE_CONFIRM` 输出“已存在主题/建议补充主题”分组 |
| `updatedConfirmationEchoed` | ❌ | 调用方标记“本轮更新后的确认清单已回显给用户”；也可写入 `meta.updatedConfirmationEchoed=true` |
| `productKnowledgeNeedsConfirmed` | ❌ | 仅当用户已确认、删除/改名/新增并确认产品知识主题后置为 `true`；也可写入 `scene.productKnowledgeNeedsConfirmed` 或 `meta.productKnowledgeNeedsConfirmed` |
| `meta` | ❌ | 可选元信息；其中 `meta.baseInfoAcknowledged=true` 与顶层字段等价 |

**会话级状态目录（强制）**：

- 每个创建会话必须分配稳定 `{sessionId}`，并将所有中间 JSON 保存到：`workspace/.cms-log/state/cms-tbs-scene-create/{sessionId}/`。
- `tbs-scene-session-init.py` 默认复用 120 秒内的空 session（仅 `SESSION.txt`），防止审批/重试生成多个空目录；确需强制新建时传 `--force-new`。
- 推荐固定文件名：
  - `latest-payload.json`
  - `latest-parse-result.json`
  - `latest-draft.json`
  - `latest-validate-result.json`
  - `latest-create-result.json`
- `draftPath` 必须使用同一会话目录下的 `latest-draft.json`，例如：`workspace/.cms-log/state/cms-tbs-scene-create/{sessionId}/latest-draft.json`。
- `/tmp/*.json` 仅允许一次性调试；不得作为正式流程中的 `draftPath`，也不得跨轮读取 `/tmp` 状态推进阶段。
- 下一轮 payload 必须基于同一 `{sessionId}` 下 `latest-draft.json` 中的 `scene` 增量合并，再写入 `latest-payload.json` 并调用脚本。
- **禁止覆盖草稿真源（强制）**：调用方/编排层不得用 “Write 文件” 的方式直接覆盖 `draftPath` 指向的草稿文件（例如 `latest-draft.json`）。草稿只能由本 Skill 脚本写回（`tbs-scene-parse.py` / `tbs-scene-knowledge-check.py` / `tbs-scene-validate.py` / `tbs-scene-create.py`）；调用方只能写本轮输入 `latest-payload.json`，再执行脚本让其合并并写回草稿。否则容易把草稿写成“残缺/非标准形状”，导致阶段回退与门禁错判。
- **工作目录（cwd）必须稳定（强制）**：所有示例命令均默认在本 Skill 根目录（`cms-tbs-scene-create/`）执行，即 `python3 scripts/xxx.py` 的 `scripts/` 指向本 Skill 的 `scripts/`。若调用方无法控制 cwd，必须改用明确的相对路径（例如在 `workspace/tbs-scene-assistant` 下执行：`python3 ../skills/cms-tbs-scene-create/scripts/tbs-scene-parse.py ...`），禁止在错误 cwd 下直接执行 `python3 scripts/xxx.py`（会导致脚本路径跑偏、报 No such file）。

**Payload 形状硬约束（防字段冲突）**：
- `productKnowledgeNeeds` 必须写入 `scene.productKnowledgeNeeds`；禁止只写顶层 `productKnowledgeNeeds`。脚本会兼容迁移顶层旧写法并输出内部告警，但调用方不得依赖该兜底。
- `actorProfileSupplement` / `bestPracticeSupplement` 必须写入 `scene.*`；脚本会兼容迁移顶层旧写法并输出内部告警，但调用方不得依赖该兜底。
- `baseInfoAcknowledged=true` 后，后续 payload 必须以最新草稿中的 `scene` 为基线增量合并；禁止提交 `scene: {}` 或只提交局部 `scene` 覆盖已确认字段。
- 若使用 `draftPath`，必须使用上方会话级状态目录，并在下一轮沿用同一会话的最新草稿；禁止多个会话共用固定 `base-info-draft.json`、`/tmp/scene_draft*.json` 或其他非会话隔离路径作为长期草稿。
- 知识阶段新增/修改主题、正文、画像、话术等信息时，优先写入 `scene`，不要再通过 `parsedFields` / `userUpdates` 覆盖已确认基础字段。
- 用户本轮提供对象角色画像、代表话术、成功经验或推进建议时，必须先写入 `scene.actorProfileSupplement` / `scene.bestPracticeSupplement`（与最新草稿 `scene` 合并）并重新调用本脚本；禁止直接跳到产品知识主题生成或场景内容生成。

错误形状（禁止）：

```json
{
  "scene": {
    "businessDomainName": "临床推广",
    "departmentName": "风湿免疫科",
    "drugName": "美泰彤",
    "location": "风湿免疫科诊室",
    "doctorConcerns": ["项目合规性"],
    "repGoal": "推动主任观念转变",
    "baseInfoAcknowledged": true
  },
  "productKnowledgeNeeds": ["项目背景与合规性", "扫码补贴流程"]
}
```

正确形状（推荐）：

```json
{
  "scene": {
    "businessDomainName": "临床推广",
    "departmentName": "风湿免疫科",
    "drugName": "美泰彤",
    "location": "风湿免疫科诊室",
    "doctorConcerns": ["项目合规性"],
    "repGoal": "推动主任观念转变",
    "baseInfoAcknowledged": true,
    "productKnowledgeNeeds": ["项目背景与合规性", "扫码补贴流程"]
  },
  "draftPath": ".cms-log/state/cms-tbs-scene-create/{sessionId}/latest-draft.json"
}
```

约束补充（强制）：
- `baseInfoAcknowledged=true` 仅能由“用户明确确认基础信息无误”触发；产品知识补充行为本身不构成该确认信号。
- 基础 6 项齐备但 `baseInfoAcknowledged` 未确认时，只能预告“确认后会根据这些信息建议产品知识主题”；不得生成或要求用户确认 `productKnowledgeNeeds`。
- `productKnowledgeNeedsConfirmed=true` 仅能由“用户明确确认产品知识主题”触发；Agent 按规范生成的建议主题不构成确认信号。
- 用户明确“暂无正文/先不补正文”时，不需要反复追问正文；但仍必须展示并确认 `productKnowledgeNeeds`。
- `declineProductKnowledge=true` 是历史兼容字段，不再构成主题确认，也不会让脚本写入“用户确认暂不补充产品知识主题”。

**补丁锁定（脚本）**：`baseInfoAcknowledged` 后不得再补丁改业务六字段；进入 `READY_FOR_SCENE_GENERATION` / `READY_FOR_VALIDATE` 后，补丁**仅** `title`、`sceneBackground`、`background`。否则 `patch_fields_locked` + `rejectedFields`；`hint` 会明确：此阶段被拒字段须改写到请求 JSON 顶层的 `scene` 对象（与已有草稿合并）后再调用本脚本，**勿**再经 `parsedFields` / `userUpdates` / `userConfirmedFields` / `userProvidedFields` 覆盖（含 `productKnowledgeNeeds`、`doctorOnlyContext`、`knowledge` 等）。`actorProfile` 只走内部写入与门禁，不进用户补丁与阶段 3 清单。

**PRE 摘要**：`parseMeta` 与 `userOutputTemplate.changeSummaryLines`（对齐结论、是否建议跳过 S3）。对用户只口述中文，不展示 JSON。`skipScenarioGenerationSuggested=true` **不**免除 TBV 与 PRE。

**流程步骤**：
1. 读取 `scene` 和补丁输入（基础信息阶段可用补丁键；知识阶段优先以 `scene` 提交）。
2. 判断基础信息 6 字段是否齐备：`businessDomainName`、`departmentName`、`drugName`、`location`、`doctorConcerns`、`repGoal`。
3. 基础信息齐备后，仍需用户明确确认（`baseInfoAcknowledged=true`）才可推进到后续阶段。
4. 基于已确认基础信息分析并写入 `productKnowledgeNeeds`（建议主题/关键词）。
5. 产品知识阶段执行细则统一以“阶段 2：产品知识确认字段（用户侧）→ 说明（硬约束）”为准，本处不重复定义。
6. 基础信息与知识阶段满足推进条件后，内部执行 `references/scenario-json-parse.md` 生成 `title`、`sceneBackground`、`actorProfile`、`doctorOnlyContext`、`coachOnlyContext`。
7. 场景内容生成完成后输出 `READY_FOR_VALIDATE` 与 `sceneHash`，再进入 `tbs-scene-validate.py`；若提供 `draftPath`，写回草稿。

**编排**：`success=false` 先处理 `error`；`success=true` 再看 `stage` + `missingFields` + `clarifyQuestions`。`READY_FOR_SCENE_GENERATION` / `scenarioGenerated=false` 仅表示“下一步应内部生成场景内容”，不是失败；必须连续执行：生成 `title` / `sceneBackground` / `actorProfile` / `doctorOnlyContext` / `coachOnlyContext` → 写回 draft → 再 parse → FULL validate。中间不得向用户展示 `stage`、`scenarioGenerated`、`draft`、`parse`、`validate` 等内部状态；耗时较长时只允许业务化提示“我正在整理场景内容并做创建前校验，请稍等。”。`READY_FOR_VALIDATE` 执行校验。`draftPath` 建议贯穿 parse/validate/create；create 前必须使用 validate 针对当前 `sceneHash` 生成的结果。

性能建议（不改变门禁语义）：
- 中间轮次可用 `--mode fast_forward --no-write-draft`，在满足门禁条件时直接进入 `READY_FOR_VALIDATE`，并跳过草稿写盘；
- 最终进入 validate/create 前，仍建议保留一次落盘（去掉 `--no-write-draft`）以便追踪与复现。

**`stage` 常见取值（以脚本实际返回为准）**：

- `BASE_INFO_CONFIRM`：先确认基础信息
- `KNOWLEDGE_CONFIRM`：再确认产品知识与资料
- `READY_FOR_SCENE_GENERATION`：已可进入场景内容生成
- `READY_FOR_VALIDATE`：已可执行场景校验

说明：调用方不应硬编码阶段推进逻辑，应以脚本本轮返回的 `stage` 为准决定下一步。

## 1) 调用方单轮执行约束（强制）

1. 同轮最多执行一次 parse；非必要不得同轮重复解析。
2. 同轮用户侧最多输出 1 条最终消息；若同轮出现多条结果，仅渲染最新结果。
3. 渲染前必须执行内部字段拦截（如 `baseInfoAcknowledged`、`updatedConfirmationEchoed` 等不得直出）。
4. `KNOWLEDGE_CONFIRM` 阶段仅在 `baseInfoAcknowledged=true` 后查询“已存在主题”。
5. 用户明确“暂无正文”后，不得反复追问正文；但必须继续展示并确认产品知识主题。
6. 每轮结束应落盘最新草稿；下一轮仅基于最新草稿增量更新。
7. 组装下一轮 payload 前必须先读取最新草稿 `scene` 并做合并；若 payload 中 `baseInfoAcknowledged=true`，则基础 6 项必须仍在 `scene` 中。
8. `productKnowledgeNeeds` 层级、草稿合并与 `draftPath` 规则见上方“Payload 形状硬约束”。
9. 用户补充对象画像/代表话术/推进建议后，必须先写回 `scene.actorProfileSupplement` / `scene.bestPracticeSupplement` 并重新 parse，使 `userOutputTemplate.supplementItems` 可见；不得只把内容作为临时上下文继续下一步。

**用户可见**：通用见 `common-params.md`。  
**parse 补充**：
1. 以脚本返回阶段为准组织回显，展示 `clarifyQuestions` 与待确认项。
2. 未 `baseInfoAcknowledged` 前，不把基础信息当最终定案。
3. 若 `userOutputTemplate.supplementItems` 非空，必须作为“补充素材”展示；该字段仅用于回显，不进入 `missingFields`，不阻塞 Gate。调用方可直接使用 `userOutputTemplate.supplementRenderBlock` 渲染该区块；若 `userOutputTemplate.mustDisplaySupplementItems=true` 或 `outputBlockingRequirements` 非空，用户可见输出未展示“补充素材”不得继续推进。
4. 锁字段拒收（`patch_fields_locked`）要业务化解释，并引导调用方基于最新草稿 `scene` 重新合并后提交。

> 阶段对照：阶段1 ↔ `BASE_INFO_CONFIRM`；阶段2 ↔ `KNOWLEDGE_CONFIRM`；阶段3（内部生成）↔ `READY_FOR_SCENE_GENERATION`；阶段4 ↔ `READY_FOR_VALIDATE`。

**阶段 1（`BASE_INFO_CONFIRM`）：基础信息确认字段**：
- `businessDomainName`
- `departmentName`
- `drugName`
- `location`
- `doctorConcerns`
- `repGoal`

**阶段 2（`KNOWLEDGE_CONFIRM`）：产品知识确认字段（用户侧）**：
- `productKnowledgeNeeds`：产品知识主题，系统先建议，用户确认/删除/改名/新增。
- `knowledge`：产品知识正文（可选），用户额外提供的正文、政策、证据或资料。

说明（硬约束）：
- [强制] `productKnowledgeNeeds` 表示 Agent 按 `references/product-knowledge-topic-generate.md` 基于基础信息分析得到的建议知识主题/关键词，用于用户确认“本场景需要覆盖哪些产品知识”。
- [强制] 用户侧必须把 `productKnowledgeNeeds` 显示为“产品知识主题”；不得把“当前未提供正文”写到该字段下。
- [强制] 用户侧必须把 `knowledge` 显示为“产品知识正文（可选）”。
  - 若用户未补充正文：**不要**播报“当前未提供正文/正文为空”等状态句；只需提示“可选补充正文要点（不影响推进）”。
  - 若知识检查已完成且 `knowledgeReady=true`/已有关联 `knowledgeIds`：可提示“已关联系统知识条目，无需额外正文”，避免误导为缺失资料。
- [强制] `KNOWLEDGE_CONFIRM` 仅做产品知识确认，不向用户索要 `title`、`sceneBackground`（后续内部生成）。
- [强制] 生成时机：仅当 `baseInfoAcknowledged=true` 且 `productKnowledgeNeeds` 为空时，Agent 先读取 `references/product-knowledge-topic-generate.md`，生成 2-4 条建议主题并写入下一轮 parse payload（不要求用户先补知识正文）。
- [强制] 未确认基础信息前，即使基础 6 项已齐备，脚本也应停留在 `BASE_INFO_CONFIRM`；不得生成建议主题，只提示“确认基础信息后会生成产品知识主题供确认”。
- [强制] 主题确认门禁：Agent 生成或用户修改 `productKnowledgeNeeds` 后，脚本必须停留在 `KNOWLEDGE_CONFIRM`；只有用户明确确认主题，并在下一轮 payload 写入 `productKnowledgeNeedsConfirmed=true`，才可进入 `READY_FOR_SCENE_GENERATION`。
- [强制] 知识检查门禁：用户确认主题后，必须先执行 `scripts/tbs-scene-knowledge-check.py`；该脚本按 `drugName` 解析 `drugId`，品种不存在时先创建并写回 `scene.drugId` / `meta.resolvedIds.drugId`，再按 `productKnowledgeNeeds` 查询已有产品知识。
- [强制] 知识检查结果：已有知识直接复用 `knowledgeIds`；缺失主题写入 `missingKnowledgeTopics`，并提示用户“可补充每个缺失主题的正文要点，或选择暂无正文继续”；未达到 `knowledgeReady=true` 前不得进入 `READY_FOR_SCENE_GENERATION`。用户可见话术不得暴露 `category/title/content/requiredFields` 等内部字段名。
- [强制] 轻确认口径：展示建议主题后，只要求用户确认、删除、改名或新增；不得要求用户补产品知识正文后才推进。
- [强制] 推荐收口：`如无调整，请回复「确认」；也可以删除、改名或新增主题。`
- [强制] 查询触发：仅在 `baseInfoAcknowledged=true` 后、首次进入 `KNOWLEDGE_CONFIRM` 时查询一次；仅当 `drugName` 变化或用户明确要求“刷新主题”时重查，其余轮次复用缓存。
- [强制] 回显口径：仅展示 `已存在主题` 与 `建议补充主题`（2-4 条）；脚本不得内置业务主题替 Agent 出题。
- [强制] 分组输出：`result.knowledgeTopicBuckets`（以及 `userOutputTemplate.knowledgeTopicBuckets`）包含 `existingTopics`、`suggestedMissingTopics`、`existingTopicsSource`，供调用方直接渲染“已存在/待补充”。
- [强制] 交互收口：产品知识阶段最多追问 2 轮、每轮最多 2 问；用户明确“暂无正文”时不得反复追问正文，但仍需确认主题后才能推进。
- [建议] 正文补充：用户可选补充 `scene.knowledge`（例如：按“主题 + 正文要点”提供即可；如确有“资料类型/类别”也需用中文业务表达）。若知识检查发现主题缺失，则缺失主题正文是进入内容生成前的补充项。
- 用户可以：
  - 仅确认/调整这些主题关键词；
  - 额外补充产品知识正文、政策内容等材料；
  - 也可以暂时不补充正文，只保留需求关键词继续流程。
- 用户删除、改名或新增主题后，调用方必须回显基础信息 6 项 + 最新 `productKnowledgeNeeds` 全量清单，再请求确认。
- 若用户补充了“代表话术/经验”，默认归入 `coachOnlyContext` 的 `## 最佳实践`。
- 若用户补充了可落库的产品知识正文，建议写入可选字段 `scene.knowledge`（数组），供创建前执行“先查后建”的知识解析流程。

### 产品知识阶段常见问题与排查（重点）

1. 反复停留在 `KNOWLEDGE_CONFIRM`：
   - 常见原因：用户已口头确认基础信息，但调用方未在下一轮 payload 顶层与 `scene` 内双写 `baseInfoAcknowledged=true`。
2. 一直提示“建议补充主题”，看不到“已存在主题”：
   - 常见原因：调用方未传 `existingProductKnowledgeTopics`（或 `meta.existingProductKnowledgeTopics`），脚本无法做“已存在/待补充”分桶。
3. 用户说“暂无正文”后仍被反复追问正文：
   - 常见原因：调用方把 `knowledge` 正文当成必填；正文可为空，主题不可跳过。
4. 主题每轮都变化、用户感知不稳定：
   - 常见原因：同轮重复 parse 或 `drugName` 被改动触发重算；应遵守“同轮最多一次 parse，非必要不刷新主题”。
5. 明明传了产品知识主题，仍提示缺失 / `scene` 被清空：
   - 常见原因：payload 形状不符合上方“Payload 形状硬约束”，尤其是主题写到顶层、未基于最新草稿合并、多个会话复用固定 draft。
6. 用户提供了画像/话术，但确认页未回显“补充素材”：
   - 常见原因：调用方没有把用户补充写入 `scene.actorProfileSupplement` / `scene.bestPracticeSupplement` 并重新 parse，而是直接进入产品知识主题生成。

**阶段 3（`READY_FOR_SCENE_GENERATION`）：内容生成后对用户展示的完整确认清单（累计）**：
- `businessDomainName`
- `departmentName`
- `drugName`
- `location`
- `doctorConcerns`
- `repGoal`
- `productKnowledgeNeeds`
- `title`
- `sceneBackground`

说明：以上为阶段 3 固定清单字段（**不含完整** `actorProfile` 对象：该字段由内部生成并参与 `validate/create` 门禁；落库前确认可展示对练对象角色摘要）。默认不得临时新增展示项。若需新增字段，必须先同步更新本文件模板与相关联动文档。

**不进入用户确认清单的内部生成字段**：
- `doctorOnlyContext`
- `coachOnlyContext`

这些字段继续参与后续 `validate` 与创建门禁，但默认由模型/系统内部生成与校验，不向用户逐段确认正文。

---

## 标准 payload 示例（仅保留核心形状）

### 示例 1：基础信息确认阶段

```json
{
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
    "repGoal": "帮助医生快速了解产品特点并回应价格顾虑",
    "generationNotes": "drugName 为推断结果，待用户确认。"
  }
}
```

### 示例 2：已确认基础信息后提交产品知识（推荐）

```json
{
  "scene": {
    "businessDomainName": "临床推广",
    "departmentName": "儿科",
    "drugName": "维图可",
    "location": "儿童医院住院部办公室",
    "doctorConcerns": [
      "处方频率低的原因",
      "如何提高处方量"
    ],
    "repGoal": "了解用药障碍并提供解决方案，增加处方量",
    "baseInfoAcknowledged": true,
    "productKnowledgeNeeds": [
      "适应症定位",
      "用法用量",
      "临床证据要点"
    ]
  },
  "draftPath": ".cms-log/state/cms-tbs-scene-create/{sessionId}/latest-draft.json"
}
```

要点：
- 当 `baseInfoAcknowledged=true` 后，基础 6 字段放在 `scene` 中作为已确认上下文，不要再通过补丁键重复覆盖。
- `productKnowledgeNeeds` 必须写入 `scene.productKnowledgeNeeds`。
- 下一轮 payload 应基于最新 draft 的 `scene` 增量合并。

### 示例 3：错误形状（禁止）

```json
{
  "baseInfoAcknowledged": true,
  "parsedFields": {
    "businessDomainName": "临床推广",
    "departmentName": "儿科",
    "drugName": "维图可",
    "location": "儿童医院住院部办公室",
    "doctorConcerns": ["处方频率低的原因"],
    "repGoal": "增加处方量",
    "productKnowledgeNeeds": ["适应症定位"]
  }
}
```

说明：
- 该形状会把已锁定基础字段当作补丁提交，常见结果是 `patch_fields_locked`。
- 若把 `productKnowledgeNeeds` 写在 payload 顶层，也属于错误形状；规范写法见上方“Payload 形状硬约束”和示例 2。

## 面向用户展示模板

固定模板不在本文件重复定义。  
调用方一律直接引用：
- `references/output-templates.md`：四时点模板正文
- `references/common-params.md`：展示优先级与输出约束

本文件仅保留 parse 阶段判定与字段语义，不再维护用户话术模板文本，避免双真源漂移。
