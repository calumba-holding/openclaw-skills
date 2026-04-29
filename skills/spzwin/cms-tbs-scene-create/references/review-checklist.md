# 运行时审查 Checklist

本文件是 Reviewer 模式的唯一真源。每次用户可见输出前、调用 validate 前、调用 create 前都按本文件自检。

## A. 禁止直出

以下内容不得出现在用户可见文案中；需要表达时转写为中文业务句。

- `baseInfoAcknowledged`
- `updatedConfirmationEchoed`
- `mustEchoUpdatedConfirmation`
- `validationReport`
- `blockingIssues`
- `warningIssues`
- `createAgentHints`
- `systemActionHint`
- `doctorOnlyContext`
- `coachOnlyContext`
- `READY_FOR_VALIDATE`
- `READY_FOR_SCENE_GENERATION`
- `scenarioGenerated`
- `scenarioGenerated=false`
- `draft`
- `parse`
- `validate`
- `sceneHash`
- `displayHash`
- `confirmedDisplayHash`
- `lastParseStage`
- `parse_stage_gate_failed`
- `validation_gate_failed`
- `display_gate_failed`
- `knowledge_gate_failed`
- 脚本报错原文
- 脚本名、stage 名、内部错误码或“正在跑/需要先让某脚本进入某阶段”等内部执行话术
- Gate 编号（如 Gate-0/Gate-1/…）或“进入某 Gate”字样
- access-token 明文或可逆片段

## B. 模板检查

- 用户可见输出前必须先判定模板编号：模板 0（首轮开场）、模板 1（收集确认）、模板 2（字段更新）、模板 3（落库前确认）、模板 4A/4B（创建结果）。
- 模板是强制输出契约，不是参考文案；除替换占位符、按结果增删占位行外，不得改写模板结构、标题、字段顺序或收口方式。
- 首轮用户只表达“创建场景/我要创建一个场景”且未提供可解析基础信息时，必须直接输出 `output-templates.md` 模板 0 标准版；禁止自由发挥或自创“完整描述/引导回答/建议”等结构。
- 收集阶段禁止自由发挥：若命中模板 0/1/2，应直接套用 `references/output-templates.md` 的对应模板正文
- 收集阶段：使用 `output-templates.md` 模板 1。
- 收集阶段（含长文本例外导致的模板 2 回显）：必须至少出现一次对“对象角色画像（自由复述）”与“代表成功经验/典型话术片段”的引导入口；若本轮未展示且用户未明确拒绝补充，则视为未通过本 Checklist。
- 若 `userOutputTemplate.supplementItems` 非空，用户可见回显必须展示为“补充素材”；不得只写入 `generationNotes` 或内部字段后对用户不可见。
- 产品知识阶段：`productKnowledgeNeeds` 必须展示为“产品知识主题”，`knowledge` 必须展示为“产品知识正文（可选）”。
- 不得播报“当前未提供正文/正文为空”等状态句（容易误导为必填/缺失资料）；如需提示，只用“可选补充正文要点（不影响推进）”。若知识检查已完成且已关联 `knowledgeIds`，可提示“已关联系统知识条目，无需额外正文”。
- 基础信息未确认时，不得展示具体产品知识主题清单；只能预告确认后生成主题。
- `declineProductKnowledge=true` 不得作为主题已确认依据；“暂无正文”不等于“无需产品知识主题”。
- 产品知识主题应按 `references/product-knowledge-topic-generate.md` 生成；脚本不得内置业务主题替代规范出题。
- 产品知识主题确认必须是轻确认：如无调整回复“确认”；允许删除、改名或新增；不得要求补正文后才推进。
- 用户确认产品知识主题后，必须执行 `tbs-scene-knowledge-check.py`；`knowledgeReady=false` 时不得进入场景内容生成。
- 性能去重（不改变门禁语义）：若草稿中已存在 `knowledgeReady=true` 且 `knowledgeIds` 完整，且 `meta.lastKnowledgeKey` 未变化，则不得重复触发知识检查网络请求（允许复用既有结果）。
- 知识检查阶段若品种不存在，应先自动创建品种并保存 `scene.drugId` / `meta.resolvedIds.drugId`，再查询或创建产品知识。
- `missingKnowledgeTopics` 非空时，必须提示用户“可补充每个缺失主题的正文要点后重新检查，或选择暂无正文继续”，且用户可见话术不得出现 `category/title/content/requiredFields` 等内部字段名。
- 字段有更新：使用 `output-templates.md` 模板 2。
- 落库前确认：使用 `output-templates.md` 模板 3，完整覆盖 `mustDisplayFields`（含 `productKnowledgeNeeds`、`actorProfile`），且只给“确认/取消”收口。
- 落库前确认必须展示 `actorProfileSummary` 或等价的对练对象角色摘要。
- 落库前确认不得展示 `doctorOnlyContext` / `coachOnlyContext` 逐段内容；内部上下文只作为校验输入。
- 若用户确认后发生任何用户可见字段变更，必须重新展示模板 3 并重新取得确认。
- create 成功：使用 `output-templates.md` 模板 4A。
- create 失败：使用 `output-templates.md` 模板 4B。

## C. 同轮约束

- 同轮最多 1 次 parse。
- 同轮最多向用户发 1 条最终消息。
- 若同轮出现多条 parse 结果，只渲染最新结果。
- `READY_FOR_SCENE_GENERATION` / `scenarioGenerated=false` 是内部生成事务状态，不是失败；必须连续执行场景内容生成、写回、再 parse、FULL validate，最终只输出模板 3 或业务化失败提示。
- 若内部生成事务耗时较长，仅允许输出一句业务化进度提示：`我正在整理场景内容并做创建前校验，请稍等。` 不得解释内部字段或脚本流程。

## C1. Parse 前 Payload 自检

调用 `tbs-scene-parse.py` 前：

- `productKnowledgeNeeds` 必须位于 `scene.productKnowledgeNeeds`；不得只放在 payload 顶层。
- 若 `baseInfoAcknowledged=true`，`scene` 必须仍包含基础 6 项：`businessDomainName`、`departmentName`、`drugName`、`location`、`doctorConcerns`、`repGoal`。
- 下一轮 payload 必须基于上一轮最新 draft 的 `scene` 增量合并；禁止用 `scene: {}` 或局部 `scene` 覆盖已确认字段。
- 知识阶段新增/修改产品知识主题、对象画像、代表话术或正文时，优先写入 `scene`；不要通过 `parsedFields` / `userUpdates` 覆盖已确认基础字段。
- `draftPath` 必须位于 `workspace/.cms-log/state/cms-tbs-scene-create/{sessionId}/latest-draft.json`；`--output` 结果也必须写入同一会话目录。禁止使用 `/tmp/*.json`、固定 `base-info-draft.json` 或其他非会话隔离路径作为跨轮状态。
- 若用户本轮提供对象角色画像、代表话术、成功经验、开场话术、推进建议或应对方式，必须先写入 `scene.actorProfileSupplement` / `scene.bestPracticeSupplement` 并重新调用 `tbs-scene-parse.py`；不得只保存在临时上下文或 `generationNotes`。

## D. 推进前自检

调用 validate 前：

- 当前 `stage` 必须是 `READY_FOR_VALIDATE`。
- 草稿必须已写盘或有等价可追踪 payload。
- 若用户本轮提供过画像/话术/成功经验/推进建议，但 parse 输出没有 `userOutputTemplate.supplementItems` 或用户可见输出没有“补充素材”，不得继续进入产品知识主题确认、知识检查或场景内容生成。
- 若包含 `productKnowledgeNeeds`，必须已经由用户确认、删除/改名/新增后确认；不得把 Agent 建议主题直接当作用户已确认主题。
- `productKnowledgeNeeds` 不得是“用户确认暂不补充产品知识主题”等占位文案。

调用 create 前，以下条件缺一不可：

- `userConfirmation = "确认"`。
- 草稿 `meta.lastParseStage=READY_FOR_VALIDATE`，确认已经完成场景内容生成并重新 parse。
- validate `passed=true`，且满足 FULL 或 TBV + `meta.lastFullValidationPassed=true` 组合门禁。
- `validationReport.sceneHash` 必须与当前 `scene` 的计算值一致；若缺失或不一致，必须重新 validate。
- `confirmedDisplayHash` 必须等于本轮 validate 输出的 `validationReport.displayHash`；若缺失或不一致，必须重新展示最终确认并重新取得确认。
- `displayContractSatisfied=true`，或 `displayedFields` 完整覆盖 `mustDisplayFields`。
- access-token 已注入且非占位符。
