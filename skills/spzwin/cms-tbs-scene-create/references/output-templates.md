# 输出模板真源

本文件只保存用户可见模板与模板占位符。输出规则、字段拦截与门禁见 `common-params.md` 与 `review-checklist.md`。

### 四时点统一模板正文（强制）

以下模板用于用户可见输出，调用方必须按时点直接套用，避免自由发挥导致口径漂移。

强制套用规则：
1. 模板是输出契约，不是参考文案；除替换占位符、按结果增删占位行外，不得改写模板结构、标题、字段顺序或收口方式。
2. 首轮用户只表达“创建场景/我要创建一个场景”且未提供可解析基础信息时，必须输出模板 0 标准版；不得自创“完整描述/引导回答/建议”等替代结构。
3. 若使用分步引导版，必须满足本文件写明的触发条件；默认不用分步引导版。
4. 每次用户可见输出前必须按 `references/review-checklist.md` 完成模板编号检查。

#### 产品知识显示规则（强制）

1. `productKnowledgeNeeds` 用户侧名称固定为“产品知识主题”，表示系统建议、用户确认/删改/新增后的主题清单。
2. `knowledge` 用户侧名称固定为“产品知识正文（可选）”，表示用户额外提供的正文、政策、证据或资料。
3. `BASE_INFO_CONFIRM`：不显示 `knowledge`，仅可提示“后续会根据基础信息建议产品知识主题”。
4. `KNOWLEDGE_CONFIRM`：必须显示 `productKnowledgeNeeds`。若本轮仅做“主题确认”（尤其主题刚更新的回显），且用户未提供 `knowledge` 正文，则**不展示**“正文为空”的占位行；只需提示“可选补充正文（不影响推进）”，避免用户误解为必填/需确认。
5. `READY_FOR_SCENE_GENERATION`：必须保留 `productKnowledgeNeeds`；`knowledge` 无正文时可省略；如需提示，只用“可选补充正文（不影响推进）”的业务化表达，不要用“当前未提供正文…”这类状态播报。
6. `READY_FOR_VALIDATE` / 落库前确认：默认展示 `mustDisplayFields`；若本轮用户刚修改过主题或正文，需补充显示最新 `productKnowledgeNeeds` / `knowledge`。
7. 正文条目显示格式统一使用：`主题 / 正文要点 / 状态`（状态仅 `已提供`、`未提供`）。可选补充“资料类型/类别”等信息时必须用中文业务表达，禁止暴露内部字段名（如 `category/title/content/requiredFields`）。

占位符兜底文案（统一）：
1. `{knowledgeItemsOrNotProvidedHint}`：
   - 有条目时：按 `主题/正文要点/状态` 逐条展开；
   - 无条目时：**收集阶段可省略该行**；若必须提示，仅写“可选补充正文（不影响推进）”。
2. `{knowledgeItemsIfRecentlyUpdatedElseOmit}`：
   - 本轮修改过知识条目时：按 `主题/正文要点/状态` 逐条展开；
   - 未修改时固定写：`本轮知识条目无新增修改，沿用已确认内容。`

#### 模板 0：首轮开场（基础信息收集）

当用户首次表达“要创建场景”，且尚未形成可回显的结构化确认清单时，先使用以下开场模板之一。

首轮快响约束（强制）：
1. 首轮执行策略：默认先做收集引导；但命中第 4 条“长文本例外”时，首轮直接执行一次 parse。
2. 仅当用户补充了可解析基础信息，或明确要求“继续执行解析”时，才进入脚本链路。
3. 若执行链路受审批阻塞（approval-pending），先回到收集引导，不在用户侧暴露内部审批细节（此状态由 Agent 宿主平台控制，脚本不返回该 stage；遇到时静默回退到「模板 0」开场引导）。
3.1 首轮或初始化阶段不得向用户展示任何内部追踪信息（例如 `sessionId` / 会话目录路径 / `draftPath`）；这些仅用于内部落盘与排障。
4. 长文本例外触发条件：首轮输入建议 >=80 字，且含“医生关注/未处方原因/目标/希望达成”等语义；命中后按第 1 条直接执行一次 parse，并按 `confirmationItems/phaseSections` 回显。
5. 若首轮已解析出 `doctorConcerns` 或 `repGoal`，用户侧不得再把该字段标记为“待补充”；应改为“已识别，请确认/可补充修正”。

标准版（默认）：

```text
开始创建场景。你可以选一种方式发给我：

- 业务领域选哪一类：临床推广 / 院外零售 / 学术合作 / 通用能力？
- 这次主要面对哪个科室/哪类医生？
- 要沟通的产品是什么？
- 场景发生在哪（门诊/病房/院外等）？
- 医生最关注或最担心的问题是什么？（建议 1-2 条）
- 这次代表希望达成什么目标？
- 是否有时间窗口、业务节点或其他背景？

💡 强烈建议顺手补一条：**当时你是怎么和医生沟通成功的？**
可以是：一段 3-6 轮的对话片段（你说/医生说），或你用的关键话术/应对方式，以及医生的反应。
复述大意就好，越接近原话越能让生成的场景贴近真实沟通。

💡 可选补充（不影响继续，但能让对练对象更贴近真实）：请用 2-3 句话描述这位医生（比如：角色/职称、沟通风格、最在意什么、最可能抛出的质疑）。

你可以先简单写，信息不完整也没关系。我会自动提取并回显确认清单，再补问关键缺口。
```

分步引导版（可由系统主动提供）：

```text
可以，我来一步步引导你补齐关键信息。先回答这两点即可：
- 业务领域选哪一类：临床推广 / 院外零售 / 学术合作 / 通用能力？
- 这次主要沟通对象是哪个科室/哪类医生？

我会根据你的回答继续追问关键缺口，每轮最多问 2 个问题。
```

分步引导模板触发建议（避免“用户不会说触发词”）：
1. 首轮开场默认提供两种方式：`完整描述` / `引导问题`。
2. 引导问题可按 5W 方法组织，但用户侧不显示 Who/What/Where/Why/When 字样。
3. 当用户出现“我不知道怎么填/你来引导我/随便问我几个问题”等表达时，自动切换到分步引导版。
4. 当自动解析后关键缺口较多（建议 >=2）时，可主动改用分步引导版补缺，不等待用户明确提出引导方式。
5. 若用户已给出完整长文本，优先走自动解析 + 缺口确认，不强制切到分步逐问。

#### 模板 1：收集阶段（BASE_INFO_CONFIRM / KNOWLEDGE_CONFIRM）

内部生成耗时提示（仅当 `READY_FOR_SCENE_GENERATION` 后连续内部生成耗时较长时允许使用；不得展示内部字段名）：

```text
我正在整理场景内容并做创建前校验，请稍等。
```

```text
我先按当前阶段回显关键信息，请确认：

- 当前阶段：{stageLabel}
- 需确认字段：
  - {field_1_label}：{field_1_value}
  - {field_2_label}：{field_2_value}
  - {field_3_label}：{field_3_value}
  （按当前阶段字段继续展开）
- 产品知识正文（可选）：
  - {knowledgeItemsOrNotProvidedHint}
  - 若你希望把场景做得更贴近真实临床沟通，可补充每个主题对应的“正文要点/数据口径/注意事项”（几条要点即可）。
  - 若本轮未补充正文，也不影响你先确认主题继续推进；后续如知识检查提示缺失，再补即可。
  （若未提供正文且本轮仅做主题确认，可省略本段；不展示“正文为空”的状态占位）
- 补充素材（如已提供）：
  - 对象角色画像：{actorProfileSupplementOrOmit}
  - 代表成功经验/典型话术：{bestPracticeSupplementOrOmit}
- 待补充项：{missingLabels}
- 需要你确认的问题：
  - {clarifyQuestion_1}
  - {clarifyQuestion_2}
- 💡 可选补充（不影响继续，但能让场景更像真实沟通）：
  - 你当时最关键的一句话/应对方式是什么？医生怎么回？你如何把对话推进下去的？
- 💡 可选补充（对象角色画像，自由复述，2-3 句话即可）：
  - 这位医生大概是什么类型？他最在意什么、沟通风格怎样、最可能提出什么质疑？

请直接补充或纠正，我会按你的更新继续下一步。
```


#### 模板占位符字段来源（强制）

| 占位符 | 来源字段路径 | 无值时 |
|--------|-------------|--------|
| `{stageLabel}` | `stage`（映射：`BASE_INFO_CONFIRM`→"基础信息确认"；`KNOWLEDGE_CONFIRM`→"产品知识确认"） | 不展示 |
| `{field_N_label}` | `userOutputTemplate.confirmationItems[N].label` | 跳过该行 |
| `{field_N_value}` | `userOutputTemplate.confirmationItems[N].value` | 写"待补充" |
| `{missingLabels}` | `missingFields`（映射为中文字段名，逗号分隔） | 写"（无）" |
| `{clarifyQuestion_N}` | `userOutputTemplate.clarifyQuestions[N]` | 跳过该行 |
| `{updatedFieldLabels}` | `userOutputTemplate.updatedFieldLabels`（数组，逗号拼接） | 不展示模板 2 |
| `{mustDisplayField_N_label/value}` | `userOutputTemplate.mustDisplayConfirmationItems[N].label/value` | 不可省略 |
| `{knowledgeItemsOrNotProvidedHint}` | 见上方"占位符兜底文案" | 固定兜底文案 |
| `{knowledgeItemsIfRecentlyUpdatedElseOmit}` | 见上方"占位符兜底文案" | 固定兜底文案 |
| `{actorProfileSupplementOrOmit}` | 用户提供的对象角色画像摘要；来源可为 `scene.actorProfile`、`generationNotes` 中的画像线索或调用方从用户原文提炼的 1-2 句摘要 | 未提供则整行不展示 |
| `{bestPracticeSupplementOrOmit}` | 用户提供的代表成功经验/典型话术摘要；来源可为用户原文中的开场话术、推进建议、应对方式，后续落入 `coachOnlyContext` 的 `## 最佳实践` | 未提供则整行不展示 |
| `{supplementRenderBlock}` | `userOutputTemplate.supplementRenderBlock`；由脚本按 `supplementItems` 预渲染的“补充素材”区块 | 无值时整块不展示 |
| `{errorReason}` | `error`（业务化转写，不直出英文码） | "未知原因" |
| `{nextAction_N}` / `{nextActionText}` | `userOutputTemplate.nextActions[N]`（若无则用固定兜底） | 省略该行 |

收集阶段补充约束（强制）：
1. 默认先回显“已识别字段 + 待补充项”，再提问题；不要要求用户整单重填。
2. 每轮最多提出 2 个澄清问题；优先问最影响下一步的关键缺口。
3. 连续追问建议不超过 2 轮；达到上限仍缺失时，改为“关键缺口单问 + 其余待确认挂起”。
4. 当用户明确要求“请你引导我填”时，可改用分步问法，但最终仍仅回填既有结构化字段。
5. 上限触发后的收口建议：先按当前可确认信息继续，并明确列出“待确认项可随时补充更新”。
5.1. 在“每轮最多 2 问”约束下，除基础 6 项缺口外，优先在下列两类里任选其一追问（另一个保持为“可选补充”入口即可）：A) 成功沟通经验/典型话术片段；B) 对象角色画像。选择规则：若用户已提供对话片段/关键话术→优先追画像；若仅给背景无沟通细节→优先追话术片段。
5.2. 当用户提供对象角色画像、代表话术、成功经验、推进建议等增强信息时，后续回显必须在“补充素材”区展示摘要；不得只写入 `generationNotes` 后对用户不可见。该区块不进入 `missingFields`，不阻塞 Gate 推进。
5.3. 若对象角色画像与代表成功经验/典型话术均未提供，则“补充素材（如已提供）”整块不展示，避免空区块干扰用户。
5.4. 若脚本返回 `userOutputTemplate.mustDisplaySupplementItems=true`，调用方必须展示 `userOutputTemplate.supplementRenderBlock` 或等价逐条回显 `supplementItems`；若 `outputBlockingRequirements` 非空，未满足前不得进入产品知识主题确认、知识检查或场景内容生成。
6. `KNOWLEDGE_CONFIRM` 阶段仅确认产品知识主题/正文，不向用户索要 `title`、`sceneBackground`。
7. 产品知识主题是必确认项：用户回复“暂无正文”仅表示 `knowledge` 为空，不得跳过 `productKnowledgeNeeds` 主题确认。
8. 异步审批完成回执（如 “An async command ... completed”）按系统事件处理，不作为新的用户业务输入。
9. `KNOWLEDGE_CONFIRM` 阶段必须同时展示：基础信息 6 项 + 产品知识确认项；禁止只展示产品知识主题问题。
10. 基础 6 项齐备但用户未明确确认时，仍属于 `BASE_INFO_CONFIRM`；只能预告“确认后会根据这些信息建议产品知识主题”，不得生成或要求确认 `productKnowledgeNeeds`。
11. `productKnowledgeNeeds` 必须作为“系统建议的产品知识主题”展示，不能让用户从零填写主题。
12. 产品知识主题必须按 `references/product-knowledge-topic-generate.md` 生成；代码不得内置业务主题替 Agent 出题。
13. 产品知识主题采用轻确认：展示建议主题后，只给“确认 / 删除 / 改名 / 新增”收口；不得要求用户补正文后才继续。
14. 推荐收口话术：`如无调整，请回复「确认」；也可以删除、改名或新增主题。`
15. 用户修改主题后，必须完整回显基础信息 6 项 + 最新产品知识主题，再请求轻确认。
16. 用户确认主题后，下一轮 parse payload 必须写入 `productKnowledgeNeedsConfirmed=true`（也可写入 `scene.productKnowledgeNeedsConfirmed=true` 或 `meta.productKnowledgeNeedsConfirmed=true`）。
17. `declineProductKnowledge=true` 不得用于跳过主题确认；历史 payload 中出现该字段时，只能理解为“不补充正文”。
18. `KNOWLEDGE_CONFIRM` 阶段同轮最多一次 parse；若仅补充展示文案，不得重复调用 parse。
19. 用户明确确认基础信息后，后续 parse payload 必须双写：顶层 `baseInfoAcknowledged=true` 且 `scene.baseInfoAcknowledged=true`（除非用户明确要求回退）。
20. 每轮内部自检（不对用户展示）：记录 `turnId`、`payload.baseInfoAcknowledged`、`payload.scene.baseInfoAcknowledged`、`payload.productKnowledgeNeedsConfirmed`、`result.stage`，用于排查竞态与信号丢失。

医生画像增强（可选，不阻塞）：
1. 触发时机：基础信息已基本齐备，且用户希望“更贴近真实医生”或当前信息对医生对象区分度不足。
2. 追问范围：每轮最多 2 问，优先问“沟通风格 + 核心关注”或“角色定位 + 主要异议点”。
3. 用户可见提问模板（示例）：
   - 为了让场景更贴近真实对象，我再确认两点：
   - 这位医生更偏哪种沟通风格（理性看数据/时间紧张/谨慎保守）？
   - 你预判他最可能提出的质疑是什么？
4. 若用户不补充，需明确“可先按当前信息继续，后续可随时补充医生特征”。

#### 模板 2：修改回显（mustEchoUpdatedConfirmation / updatedFieldLabels）

```text
你本轮已更新以下内容：{updatedFieldLabels}。
我已按最新内容更新确认清单，请你核对：

- {field_1_label}：{field_1_value}
- {field_2_label}：{field_2_value}
- {field_3_label}：{field_3_value}
（完整展示本轮应回显字段）
- 产品知识正文（可选）：
  - 若你希望把场景做得更贴近真实临床沟通，可补充每个主题对应的“正文要点/数据口径/注意事项”（几条要点即可）。
  - 若本轮未补充正文，也不影响你先确认主题继续推进；后续如知识检查提示缺失，再补即可。
- 补充素材（如已提供）：
  - 对象角色画像：{actorProfileSupplementOrOmit}
  - 代表成功经验/典型话术：{bestPracticeSupplementOrOmit}
- 💡 可选补充（不影响继续，但能让场景更像真实沟通）：
  - 你当时最关键的一句话/应对方式是什么？医生怎么回？你如何把对话推进下去的？
- 💡 可选补充（对象角色画像，自由复述，2-3 句话即可）：
  - 这位医生大概是什么类型？他最在意什么、沟通风格怎样、最可能提出什么质疑？

以上修改是否准确？确认后我继续下一步。
```

#### 模板 3：落库前确认（validate 通过，准备 create）

```text
创建前请你做最后确认：

- 最终确认清单：
  - {mustDisplayField_1_label}：{mustDisplayField_1_value}
  - {mustDisplayField_2_label}：{mustDisplayField_2_value}
  - {mustDisplayField_3_label}：{mustDisplayField_3_value}
  （按 mustDisplayFields 完整展示）
- 产品知识主题：
  - {productKnowledgeNeedsItems}
- 对练对象角色：
  - {actorProfileSummary}
- 补充素材（如已提供）：
  - 对象角色画像：{actorProfileSupplementOrOmit}
  - 代表成功经验/典型话术：{bestPracticeSupplementOrOmit}
- 产品知识正文（可选）：
  - {knowledgeItemsIfRecentlyUpdatedElseOmit}

如无误，请回复「确认」或「取消」。
```

内部绑定（禁止对用户展示）：渲染模板 3 时记录本轮 `validationReport.displayHash`；用户确认后调用 create 必须传 `confirmedDisplayHash=validationReport.displayHash`。若确认后任何用户可见字段变化，必须重新渲染模板 3 并重新取得确认。

#### 模板 4A：落库结果（create 成功）

```text
创建成功 🎉

- 场景名称：{title}
- 场景背景：{sceneBackground}
- 关键信息：
  - 业务领域：{businessDomainName}
  - 科室：{departmentName}
  - 产品：{drugName}
  - 知识条目数量：{knowledgeCount}

{nextActionText}
```

#### 模板 4B：落库结果（create 失败）

```text
创建失败，原因：{errorReason}

- 建议下一步：
  - {nextAction_1}
  - {nextAction_2}
```

约束：
1. 模板中的字段值必须来自脚本输出，不得自行改写含义。
2. 当 `mustShowSceneBackgroundFullText=true` 时，`sceneBackground` 必须使用 `sceneBackgroundFullText` 原文。
3. create 成功/失败必须分别使用模板 4A / 4B，不得混用字段。
4. `productKnowledgeNeeds` 与 `knowledge` 是否展示，严格按“产品知识显示规则（强制）”执行。
