# 自然语言/补充输入 → 基础信息提取

本文件用于编排调用方在对话内调用模型时的系统提示词规范。目标是：无论用户一次性给出大段业务背景，还是按引导逐步补充字段，都先统一提取 `scene` 的**基础信息骨架**，供 `tbs-scene-parse.py` 进入“基础信息确认”阶段。

---

## 1) 使用时机

- 当用户输入是自然语言长文本、会议纪要、产品说明、业务需求描述时，应先使用本文件提取基础信息。
- 当用户按引导逐条补充字段时，也可把本轮新增信息合并到已有骨架后，继续使用本文件做增量抽取。
- 本文件**不负责**生成长正文，不生成：
  - `sceneBackground`
  - `doctorOnlyContext`
  - `coachOnlyContext`
- 本文件只负责提取以下基础字段：
  - `businessDomainName`
  - `departmentName`
  - `drugName`
  - `location`
  - `doctorConcerns`
  - `repGoal`
  - `generationNotes`（仅记录推断与待确认点）

---

## 2) 提取原则

- 只输出一个 UTF-8 JSON 对象，键名必须与 Schema 完全一致。
- 只抽取已明确表达或可保守推断的基础字段。
- 不确定就留空，不要为了“补齐”而臆造。
- 若有推断，必须写入 `generationNotes` 说明“为什么这样推断、哪些点需要用户确认”。
- `businessDomainName` 仅允许：`临床推广` / `院外零售` / `学术合作` / `通用能力`。
- `doctorConcerns` 可以是字符串，也可以是字符串数组；推荐优先输出数组。
- `doctorConcerns` 只放医生对产品、证据、安全性、费用、可及性、指南边界或推广方式的**具体顾虑/异议**；不得把职称、角色、性格、沟通风格直接写成顾虑。
- 若用户提到“主任/副主任/专家/观念保守/谨慎/强势/理性看数据/时间紧张”等画像线索，应写入 `generationNotes`，供后续生成 `actorProfile` 使用。
- 若用户这轮只补充了个别字段，其余字段应尽量保留已有输入值，不要清空。
- 本步骤产出的 JSON 仅用于内部编排：写入 `parsedFields` 并继续调用 `tbs-scene-parse.py`，不得直接展示给最终用户。
- 自然语言长文本禁止直接塞进 `tbs-scene-parse.py` 当成完整草稿；必须先经本文件抽取为 `parsedFields`，再调用 parse 判断 Gate。

## 2.1) 5W 采集策略（方法层）

- 引导与理解可使用 5W（Who / What / When / Where / Why），但 5W 仅用于分析，不得作为新增结构化字段输出。
- 字段映射建议：
  - Who -> `departmentName`（必要时结合 `businessDomainName` 判断业务语境）
  - What -> `drugName`、`doctorConcerns`、`repGoal`
  - When -> 若与训练目标强相关但无对应结构化字段，写入 `generationNotes` 待确认
  - Where -> `location`
  - Why -> `repGoal`；无法稳定映射时写入 `generationNotes`
- 若 5W 信息不全，不做臆造；仅提取可确认部分，其余在 `generationNotes` 标注缺口与待确认点。
- 当用户输入为碎片化补充时，优先合并已有骨架后再按 5W 查漏，不得回退或清空既有字段。

## 2.2) 收集决策规则（默认自动解析 + 5W 兜底）

- 默认先执行“自动解析”：无论用户输入一句话还是长文本，先尝试抽取 6 个基础字段（`businessDomainName`、`departmentName`、`drugName`、`location`、`doctorConcerns`、`repGoal`）。
- 触发 5W 引导的条件：
  - 用户明确表示“不知道该怎么填”或“请按 5W 引导”；
  - 当前轮抽取后仍存在 2 个及以上关键缺口，且无法保守推断。
- 追问策略采用“完整性门禁 + 追问成本上限”双阈值：
  - 完整性门禁：以 6 个基础字段是否齐备作为主判定标准；
  - 追问上限：建议最多 2 轮，每轮最多 2 个问题，避免反复盘问。
- 到达追问上限仍有缺口时执行降级：
  - 不再全量追问，仅保留 1 个最关键缺口问题；
  - 其余缺口写入 `generationNotes` 标注“待确认”，允许用户后续补充更新。
- 无论走自动解析还是 5W 引导，最终输出字段集合必须一致；不得因引导模式切换而变更 JSON 契约。

## 2.3) 用户可见输出

遵守 `common-params.md`。本节额外强调：不得对用户贴本步 JSON；骨架只写入 `parsedFields` 再调 `tbs-scene-parse.py`。

## 2.4) 医生画像增强信息（可选收集，不阻塞）

- 医生画像用于提升场景拟真度与异议命中率，默认作为“增强信息”，不替代基础 6 字段门禁。
- 收集时机建议：基础信息确认后、内容生成前；若用户已在长文本中给出画像线索，可直接抽取并复用。
- 最小收集集（建议优先这 4 项）：
  - 角色定位：科室 + 职称（如“心内科副主任”）
  - 沟通风格：理性数据型 / 时间紧张型 / 谨慎保守型（可多选）
  - 核心关注：疗效 / 安全性 / 价格与可及性 / 指南证据（建议 2-3 项）
  - 主要异议点：最可能出现的 1-2 条质疑
- 触发策略：
  - 用户提出“希望更贴近真实医生”或主动补充医生背景时，优先收集；
  - 自动解析后内容泛化风险高（缺少对象差异信息）时，可追加 1 轮定向追问。
- 成本约束：每轮最多 2 问；若用户不愿继续补充，按现有信息推进，并把未补齐画像线索写入 `generationNotes` 待确认。
- 契约约束：本文件输出字段仍保持基础字段子集 + `generationNotes`；医生画像细节不在此阶段扩展为新增结构化键。

## 2.5) 产品知识主题生成边界（与 parse 阶段衔接）

- 本文件不直接输出 `productKnowledgeNeeds`，其生成与兜底由 `references/tbs-scene-parse.md` 在 `KNOWLEDGE_CONFIRM` 阶段负责。
- 调用方在基础信息抽取完成后，应把结果写入 `parsedFields` 并进入 `tbs-scene-parse.py`；不要在本阶段扩展产品知识结构化字段。
- 若后续 `KNOWLEDGE_CONFIRM` 阶段出现 `productKnowledgeNeeds` 为空，应由 parse 链路基于基础 6 字段自动给出 2-4 条建议主题供用户确认（不在本文件处理）。

---

## 3) 共用系统提示词（System）

```text
你是企业训战「对话场景」设计助手。你必须只输出一个 UTF-8 JSON 对象，符合用户消息中给出的 JSON Schema：键名与层级完全一致，字符串值为简体中文。

你的任务不是生成完整场景，而是先从用户输入中提取基础信息骨架，供后续确认。

规则：
1. 只允许输出这些字段：businessDomainName、departmentName、drugName、location、doctorConcerns、repGoal、generationNotes。
   - 严禁新增任何额外键（如：关键决策者、利好背景、场景氛围、产品分类、适应症等）；此类信息若确有价值，只能写入 generationNotes 的文本说明，不得独立成字段。
2. businessDomainName 仅允许：临床推广 / 院外零售 / 学术合作 / 通用能力。
3. doctorConcerns 只记录医生的具体顾虑/异议，不记录医生职称、角色、性格或沟通风格；这些画像线索必须写入 generationNotes。
4. 对不确定信息允许保守推断，但必须在 generationNotes 标注“待确认”。
5. 若用户本轮只补充部分信息，保留已有基础字段，不要无故删除。
6. 先按 5W（Who/What/When/Where/Why）理解用户输入，再映射到允许字段；5W 不是输出字段。
7. 若 When/Why 等信息无法稳定映射到结构化字段，写入 generationNotes 并标注待确认。
8. 不要生成标题、场景背景、场景正文、上下文、产品知识正文。
9. 禁止在 JSON 外输出任何字符（不要 markdown 围栏）。
```

---

## 4) 统一用户提示词

```text
【用户输入】
{{user_input}}

【已有基础信息骨架（可空）】
{{base_scene}}

【任务】
1. 从用户输入中提取或更新以下字段：businessDomainName、departmentName、drugName、location、doctorConcerns、repGoal。
2. 若某字段输入中没有明确表达，且无法保守推断，则留空。
3. 若某字段来自推断而非明确表达，必须在 generationNotes 中写明。
4. 可先用 5W（Who/What/When/Where/Why）做语义归纳，再映射到允许字段；不得输出 5W 命名字段。
5. 若 5W 中有高价值信息暂无法映射（常见于 When/Why 细节），写入 generationNotes 并标注“待确认”。
6. 仅输出基础信息骨架，不生成完整场景内容；也不要把“关键决策者/主任关注点/利好背景/场景氛围”等扩展信息当结构化字段输出。
7. `doctorConcerns` 不得只包含“主任/副主任/专家/观念保守/谨慎/强势/理性看数据/时间紧张”等画像词；若有“反感推销/抵触推广”等可转化为异议的内容，只保留异议部分。

【输出】
仅输出 JSON 对象。
```

---

## 5) 生成后自检

- [ ] 可解析为合法 JSON，且不含 JSON 外字符
- [ ] 仅包含基础信息字段与 `generationNotes`
- [ ] `businessDomainName` 若非空，其值属于：`临床推广` / `院外零售` / `学术合作` / `通用能力`
- [ ] 未凭空生成标题、场景背景、上下文等长正文
- [ ] 对推断字段已在 `generationNotes` 说明
- [ ] 已按 5W 做查漏；无法映射的关键信息已写入 `generationNotes` 待确认
- [ ] `doctorConcerns` 未把职称、角色、性格或沟通风格当作顾虑；相关画像线索已转入 `generationNotes`

---

## 6) 用户消息中须附带的 JSON Schema

调用方应在同一次用户消息或紧随其后的消息中附上完整 JSON Schema，确保键名与层级严格一致。

| 用途 | 文件 |
|------|------|
| 基础信息提取模型输出 | `references/scene.schema.json`（完整场景契约；基础信息阶段仅填基础字段，`required` 不用于 S1 阶段校验） |

---

## 7) 标准交接示例

### 示例 A：长文本 -> 基础信息骨架

**模型输出示例**

```json
{
  "businessDomainName": "临床推广",
  "departmentName": "消化内科",
  "drugName": "美沙拉秦肠溶片",
  "location": "三级医院门诊",
  "doctorConcerns": [
    "产品优势",
    "集采与价格"
  ],
  "repGoal": "帮助医生快速了解产品特点并回应价格顾虑",
  "generationNotes": "drugName 根据上下文推断为美沙拉秦肠溶片，需用户确认品种名称是否准确。"
}
```

### 示例 A2：画像线索与医生顾虑分离

**用户输入**

```text
在三级医院分科门诊，医药代表针对观念保守、反感推销的主任。
```

**推荐输出**

```json
{
  "businessDomainName": "临床推广",
  "departmentName": "",
  "drugName": "",
  "location": "三级医院分科门诊",
  "doctorConcerns": [
    "反感推销，对代表推广有抵触"
  ],
  "repGoal": "降低医生对推销的抵触，建立专业信任",
  "generationNotes": "“主任”是角色线索，“观念保守”是沟通风格线索，不直接作为医生顾虑；后续生成 actorProfile 时使用。科室和产品名待补充。"
}
```

**禁止输出**

```json
{
  "doctorConcerns": [
    "观念保守",
    "主任"
  ]
}
```

### 示例 B：交给 `tbs-scene-parse.py` 的 payload

```json
{
  "userText": "用户原始长文本，可保留用于日志或后续参考",
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
    "generationNotes": "drugName 根据上下文推断为美沙拉秦肠溶片，需用户确认品种名称是否准确。"
  },
  "draftPath": ".cms-log/state/cms-tbs-scene-create/demo-draft.json"
}
```

### 示例 C：用户逐字段补充时的增量更新

```json
{
  "userText": "地点改成病房医生办公室，顾虑再加一个长期安全性",
  "scene": {
    "businessDomainName": "临床推广",
    "departmentName": "消化内科",
    "drugName": "美沙拉秦肠溶片",
    "location": "三级医院门诊",
    "doctorConcerns": [
      "产品优势",
      "集采与价格"
    ],
    "repGoal": "帮助医生快速了解产品特点并回应价格顾虑"
  }
}
```

> 约定：基础信息提取阶段输出的是“增量可合并骨架”，下一步统一交给 `tbs-scene-parse.py` 做阶段确认。
