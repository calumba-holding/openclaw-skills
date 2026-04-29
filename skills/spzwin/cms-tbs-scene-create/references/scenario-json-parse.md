# 已确认骨架 → `scene` 内容生成 JSON

本文件用于编排调用方在对话内调用模型时的系统提示词规范。目标是：在**基础信息**与**产品知识/资料状态**已经确认后，再由模型内部补齐 `scene` 的剩余内容字段，避免一开始就全量生成整份场景草稿。

> **⛔ 硬性前置条件**：本文件**只能**在 `tbs-scene-parse.py` 返回 `stage=READY_FOR_SCENE_GENERATION` **之后**使用。若 Agent 未先执行 parse 脚本并确认 stage，则**禁止**读取本文件并生成内容。违反此规则将导致跳过用户分阶段确认，产出不合规的全量场景草稿。
> **产品知识边界**：本文件只消费已确认的 `productKnowledgeNeeds`，不得生成、改名、补充或替用户确认产品知识主题。

对用户可见话术遵守 `common-params.md`（本文件不重复）。

---

## 0) 使用时机（重要）

- **不要**把本文件作为自然语言场景的第一步。
- 第一阶段应先由 `tbs-scene-parse.py` 收集并确认以下基础信息：
  - `businessDomainName`
  - `departmentName`
  - `drugName`
  - `location`
  - `doctorConcerns`
  - `repGoal`
- 第二阶段再确认：
  - `productKnowledgeNeeds`
- 第二阶段中，`productKnowledgeNeeds` 的来源应是：基于已确认的业务领域、科室、品种、地点、医生顾虑、代表目标，**先分析出当前训练场景应覆盖的产品知识主题/关键词**，再交由用户确认、调整或补充。
- 第二阶段用户侧必须拆开展示：“产品知识主题”对应 `productKnowledgeNeeds`；“产品知识正文（可选）”对应 `knowledge`。
  - 若用户未补充 `knowledge` 正文：**不要**播报“正文为空/当前未提供正文”这类状态句；只需提示“可选补充正文要点（不影响推进）”。
  - 若已完成知识检查并已关联 `knowledgeIds`（`knowledgeReady=true`）：可业务化提示“已关联系统知识条目，无需额外正文”，避免误导用户以为缺资料。
- 产品知识主题确认采用轻确认：系统展示 2-4 条建议主题，用户可直接回复“确认”，也可删除、改名或新增；确认后才进入本文件。
- 用户对产品知识的补充是**可选**的：
  - 可以只确认 `productKnowledgeNeeds` 关键词；
  - 也可以额外补充知识正文，写入 `scene.knowledge` 供后续创建前解析；
  - 如果用户暂时不补充正文，不应阻断后续场景生成。
- 用户补充“代表话术/经验”时，默认归入 `coachOnlyContext` 的 `## 最佳实践`（必要时同步微调 `repGoal`）。
- **仅当以上信息已稳定后**，才在内部使用本文件补齐场景内容字段：
  - 核心生成字段：`sceneBackground`、`doctorOnlyContext`、`coachOnlyContext`
  - 最小补齐字段：`title`、`actorProfile`（仅在缺失时补齐，已有则保留）

---

## 1) 提取总原则（scene 单对象）

- 只输出一个 UTF-8 JSON 对象，字段键名必须与 Schema 完全一致。
- 输出对象即 `scene` 语义字段，不再使用旧结构键名。
- 对已确认字段遵循“**能复用就复用，非必要不改写**”原则，避免覆盖用户已确认的基础信息。
- 字段补齐采用固定顺序，保证稳定性：
  1. 已确认主数据字段：`businessDomainName`、`departmentName`、`drugName`、`location`
  2. 已确认训练目标字段：`doctorConcerns`、`repGoal`
  3. 产品知识字段：`productKnowledgeNeeds`（已确认输入，只复用）
  4. 用户可选补充的知识正文：`knowledge`
  5. 待生成内容字段：`sceneBackground`、`doctorOnlyContext`、`coachOnlyContext`
  6. 缺失时最小补齐字段：`title`、`actorProfile`
- 不确定信息允许保守推断，但必须写入 `generationNotes` 标注待确认。
- 禁止编造输入中未出现的具体数据、制度条文、研究结论、系统名。

---

## 2) 共用系统提示词（System）

```text
你是企业训战「对话场景」设计专家。你必须只输出一个 UTF-8 JSON 对象，符合用户消息中给出的 JSON Schema：键名与层级完全一致，字符串值为简体中文，可直接用于后台配置。

规则：
1. 已确认字段优先保留：businessDomainName、departmentName、drugName、location、doctorConcerns、repGoal、productKnowledgeNeeds。
   - 除非输入里出现了更明确、且不与用户确认内容冲突的新事实，否则不要改写这些字段。
   - `doctorConcerns` 在收集阶段建议控制为 1-2 条；本阶段仅复用，不扩写为更多条目。
2. 必填主数据字段：title、businessDomainName、departmentName、drugName、location、doctorConcerns、repGoal。
   - businessDomainName 仅允许：临床推广 / 院外零售 / 学术合作 / 通用能力。
   - businessDomainName 视为上阶段已确认结果，本阶段只保留，不重新确认。
   - drugName 与训战活动配置的品种/产品或训练主题口径一致；若输入未给出，允许合理推断并在 generationNotes 标注待确认。

3. 必填正文字段：sceneBackground、doctorOnlyContext、coachOnlyContext。
  - sceneBackground 需写成一段自然叙述，优先采用「场景对象与关系 + 核心冲突/顾虑 + 本次沟通目标」结构，避免空泛背景描述。
   - sceneBackground 必须满足：长度 <= 180；不得包含【】或“待补充”；不得出现“场景背景：/人物关系：/训练目的：/开场建议：/AI角色对象的顾虑：”等标签化写法。
   - sceneBackground 必须覆盖以下语义要素：场景发生时机/地点、双方角色关系、关键顾虑点、代表本次希望达成的训练目标（如达成共识/推动准入/优化用药方案）。
   - 锚点匹配规则（与 `tbs-scene-validate.py` 对齐）：`departmentName` 与 `location` 需作为子串出现在 `sceneBackground` 中；`drugName` 允许以**括号前主名称**作为锚点（例如 `drugName` 为“美泰彤（甲氨蝶呤针剂）”时，正文出现“美泰彤”即可）。
   - sceneBackground 中不得出现具体姓氏/姓名（如“王某某”“李某某”）；可使用“主任/医生/医师/药剂科主任”等职业称谓，但避免“某主任+具体姓氏”的组合写法。
   - sceneBackground 中避免使用第一、第二人称代词（如“你/我/你们/我们/咱/咱们”），优先使用角色称谓与第三人称客观叙述。
   - doctorOnlyContext 与 coachOnlyContext 均为纯字符串，允许在字符串内使用 Markdown 小节组织内容。

4. doctorOnlyContext（对练对象侧）要求：
   - 不绑定固定行业身份，按场景写清对练对象称谓（如上级/下属/同事/客户/合作方/医师等）。
   - 需体现：角色立场、具体担忧、对话行为、可追问方向。
   - doctorOnlyContext 必须且按顺序包含以下 6 节标题：
     ## 已知背景
     ## 核心顾虑
     ## 今日状态
     ## 终止条件
     ## 输出要求
     ## 对话结束规则（强制）
   - `## 核心顾虑` 必须是 1-2 条 bullet（最多 2 条）。**计数规则**：该小节内凡以 `-` 开头的行均计为一条 bullet；超过 2 条时 `tbs-scene-validate.py` 会在校验前自动合并为 2 条，但仍应在模型侧避免滥发列表，以免语义被挤进单条过长叙述。
   - **输出 JSON 前强制自检**：若你写出了 3 条及以上「`-` 核心顾虑」，必须先合并为 2 条再输出；不要依赖后处理。
   - `## 输出要求` 与 `## 对话结束规则（强制）` 两节内容必须逐字使用本文件“对话结束规则参考模板”中的固定条目，不得改写、增删、换序。
   - `## 终止条件` 可按场景定制，但必须可判定、与输入事实一致。
   - 此字段属于模型内部生成与系统校验内容，不要求向用户逐段确认正文。

5. coachOnlyContext（教练侧）要求：
   - 必须包含以下 5 节标题：
     ## 期望代表行为
     ## 评分重点
     ## 终止条件
     ## 最佳实践
     ## 输出要求
   - 内容需可观察、可评估；避免出现 `[对话结束]` 等“对练对象输出专用标记”的字面量（以免被误读为需要输出的内容）。如需表达“不要输出结束标记”，建议写为“不要输出对话结束标记/结束提示”。
   - 此字段属于模型内部生成与系统校验内容，不要求向用户逐段确认正文。

6. actorProfile：
   - 必须提供，且至少含 name。
   - 推荐补充 roleType、title、description、personaConfig。
   - 若无需人设细节，可仅保留最小结构（例如：`{"name":"..."}`）。

7. 产品知识：
   - productKnowledgeNeeds 是上游已确认输入，本阶段只复用，不生成、不改名、不扩展。
   - 若用户提供了可落库的产品知识正文，可写入可选字段 `knowledge`；每条知识建议至少包含 `category`、`title`、`content`（`category` 由用户提供，如“整体介绍”），可选补 `evidenceSource`、`evidenceStatus`。这些条目不要求在本提示词阶段创建 ID，只需保留到创建前链路。
8. 代表话术/经验吸收规则：
   - 若用户提供了代表实战经验、常用话术或应对技巧，默认写入 `coachOnlyContext` 的 `## 最佳实践` 小节。
   - 不要把“代表应对策略”并入 `doctorConcerns`。

9. generationNotes：
   - 仅记录不确定点、待确认点、推断依据，不写与输入矛盾的“确定事实”。

10. 禁止在 JSON 外输出任何字符（不要 markdown 围栏）。
11. 字段名必须与 schema 完全一致。
```

---

## 3) 统一用户提示词（在基础信息与资料已确认后使用）

```text
【已确认的业务背景】
{{user_input}}

【可选补充信息】
- 产品知识材料（可空）：{{product_knowledge}}
- 学员在训战中扮演的角色：{{trainee_role}}
- 期望对话形态：{{dialogue_type}}
- 品种/产品或训练主题（已知则填）：{{product_name}}
- 部门/组织单元偏好：{{department_hint}}
- 是否需要详细对话结束规则（是/否）：{{need_end_rules}}（为「是」时，须在 doctorOnlyContext 内用独立小节写全结束规则）

【任务】
1. 以上输入已经过用户确认，请在不违背已确认事实的前提下，**只补齐本阶段负责的场景内容字段**，不要把本阶段改写成重新确认基础信息或资料状态。
2. 本阶段核心生成：`sceneBackground`、`doctorOnlyContext`、`coachOnlyContext`。
3. `title`、`actorProfile` 仅在缺失时做最小补齐；若输入中已存在，则直接保留，不作为本阶段重点改写对象。
4. `businessDomainName`、`departmentName`、`drugName`、`location`、`doctorConcerns`、`repGoal`、`productKnowledgeNeeds` 若已提供，则直接复用，不重新确认、不擅自改写。
5. 若输入中已给出 `knowledge`，请直接保留并透传；若用户只确认了知识主题、未给完整正文，不要生成知识正文草案，只保留已确认主题。
6. 结束硬约束仅写入 `doctorOnlyContext`，不新增独立 JSON 字段；`need_end_rules` 仅用于调整场景语气，不影响固定结构输出。

【输出】
仅输出 JSON 对象，结构严格符合 System 中描述的 Schema。
```

---

## 4) 占位符说明

| 占位符 | 含义 | 未提供时 |
|--------|------|----------|
| `{{user_input}}` | 用户任意输入（可是一句话、脚本片段、业务背景、需求描述） | 必填 |
| `{{product_knowledge}}` | 产品知识全文或节选（可选） | 可为空 |
| `{{trainee_role}}` | 学员扮演角色 | 由模型推断 |
| `{{dialogue_type}}` | 如上下级辅导、跨部门、绩效面谈 | 由模型推断 |
| `{{product_name}}` | 品种/产品或训练主题标识 | 推断 + generationNotes |
| `{{department_hint}}` | 部门/组织单元偏好 | 可忽略 |
| `{{need_end_rules}}` | 是否要求把结束硬约束写进 doctorOnlyContext | 默认否；为是时必须完整撰写 |

---

## 5) 生成后自检（程序或人工）

- [ ] 可解析为合法 JSON，且不含 JSON 外字符
- [ ] `sceneBackground` 长度 <= 180，且覆盖 departmentName、drugName、location 三个锚点信息（其中 `drugName` 允许以括号前主名称命中）；为一段自然叙述，不含“人物关系：/训练目的：”等标签化前缀
- [ ] `businessDomainName` 取值属于：`临床推广` / `院外零售` / `学术合作` / `通用能力`
- [ ] `coachOnlyContext` 包含五节固定标题（可选：避免出现对练对象输出专用标记字面量，以免被误读）
- [ ] `doctorOnlyContext` 包含六节固定标题；`## 核心顾虑` 为 1-2 条以 `-` 开头的 bullet（输出前自检，勿超过 2 条）；`## 输出要求` 与 `## 对话结束规则（强制）` 逐字匹配模板固定条目

---

## 6) `doctorOnlyContext` 固定模板（与 `tbs-scene-validate.py` 逐行一致）

整段 `doctorOnlyContext` 必须是 Markdown 字符串，且 **6 个二级标题按以下顺序出现**（标题字面值须完全一致，勿改标点或空格）：

1. `## 已知背景`
2. `## 核心顾虑`（正文为 **1～2** 条以 `-` 开头的要点行）
3. `## 今日状态`
4. `## 终止条件`（可按场景自定义若干条 `-` 要点，**不参与**逐字比对）
5. `## 输出要求`（下文「固定 A」：**逐行**拷贝，不得改写/增删/换序）
6. `## 对话结束规则（强制）`（下文「固定 B」：**逐行**拷贝，且须放在全文最后一个小节）

> 生成后调用 `tbs-scene-validate.py` 时，成功/失败响应里的 `userOutputTemplate.doctorOnlyContextCanon` 会再次给出 `outputRequirementsLines` 与 `endingRulesLines`；**以脚本输出为准**，本文件与之冲突时以脚本为准。

### 固定 A — `## 输出要求` 正文（逐行原样）

```text
- 输出长度控制：每次回复控制在30-50字左右，保持真实医生沟通的自然简洁；每轮最多聚焦1个核心点。
- 单问原则：每轮最多提出1个核心问题（问号≤1）。如果想到第二个问题，必须留到下一轮再问。
- 语言要求：以中文自然对话为主；允许必要的医学缩写/单位/符号，但不得滥用英文；严禁出现与医学沟通无关的英文单词。
- 纯文本要求（强制）：只输出纯文本对话，不要使用任何加粗/斜体/标题/代码符号等格式化写法。
- 提问后必须等待代表回答：提问后必须收住，不得在同一轮连续追问，更不得在提问后追加结束标记。
- 避免臆造数据（强制）：不得凭空编造背景之外的具体数值/比例/研究结论；不确定就说明需回去核对资料。
```

### 固定 B — `## 对话结束规则（强制）` 正文（逐行原样）

```text
- 只有对练对象角色可结束：仅在本轮末尾追加 [对话结束]，且必须放在全文最后。
- 允许结束：已触发终止条件，或系统明确要求本轮结束（最后一轮/轮次已满）。
- 互斥（执行检查）：若本轮出现问号或疑问词，则必须删除 [对话结束]。
- 互斥（执行检查）：若本轮要输出 [对话结束]，则全文不得出现任何问号或疑问词，且不得出现提问意图。
- 结束语边界：结束语必须是纯陈述句，不得提问，也不得安排任何后续动作或要求。
```

### `## 终止条件` 示例（可改写；勿与固定 A/B 合并成一节）

以下为结构示例，**不**要求与脚本逐字一致，但须可判定、与输入事实一致：

```markdown
## 终止条件
- 出现无依据的绝对化承诺，或夸大效果、隐瞒重大限制与风险。
- 回避本场景已点明的关键问题（需替换为与本场景一致的条目）。
- 编造数据/证据，或引用来源不清、前后矛盾。
- 单向灌输、拒绝回应对方异议，导致沟通目标失真。
```

---

## 7) 用户消息中须附带的 JSON Schema

调用方应在同一次用户消息或紧随其后的消息中附上完整 JSON Schema，确保键名与层级严格一致。

| 用途 | 文件 |
|------|------|
| 模型单次输出与场景草稿契约（两阶段共用） | `references/scene.schema.json` |
