## Agent 调用模式示例

> 内部编排顺序示例；**禁止**对用户播报「先读 / exec」等字样。用户模板见 `output-templates.md`；输出规则见 `common-params.md`。

### 状态真源与门禁顺序（硬规则）

1. **draft 唯一真源**：会话目录内 `latest-draft.json`（`--params-file` / `draftPath` 指向的同一路径）承载跨轮的 `scene` 与 `meta`。每步脚本若会改状态，须写回该文件；下一步须以该文件为输入，**不要**只用 `parse-result` 里的片段当整份草稿去跑 `validate`。
2. **知识检查后**：`tbs-scene-knowledge-check.py`（`--output` 产物仅作查看）执行完，**先**确认 draft 已更新（含服务端 `knowledgeIds`），**再** `tbs-scene-parse.py`。
3. **内部生成后再 parse 再 FULL validate**：按 `scenario-json-parse.md` 在内部补全长文本字段，合并进 `scene`，写入 draft，再 `tbs-scene-parse.py` 直到 `stage` 允许进入校验；**仅此时**对**同一份** draft 跑 `tbs-scene-validate.py`（FULL）。若 `title` / `sceneBackground` / `doctorOnlyContext` 等仍缺，不得对中间态做 FULL 校验（否则会失败并多耗一轮）。

### 模式 A：自然语言场景 -> 基础信息确认

```
用户：「帮我建一个心内科的训练场景，主任担心长期安全性」
Agent → 先读 references/base-info-parse.md
Agent → 再读 references/scene.schema.json（完整场景契约；本阶段仅填基础字段，required 不用于 S1 校验）
Agent → 从用户输入提炼 businessDomainName / departmentName / drugName / location / doctorConcerns / repGoal
Agent → exec: python3 scripts/tbs-scene-parse.py --params-file payload.json --output result.json
Agent ← JSON（stage=BASE_INFO_CONFIRM 或后续阶段）
Agent → 向用户展示中文确认清单与待补充问题（见 output-templates.md 模板 1）
Agent → 若用户在对话中纠正基础字段（例如把 drugName 收窄为更短口径），下一轮必须把纠正写回 `parsedFields` 再执行 `tbs-scene-parse.py`，避免后续生成/校验仍引用旧值
Agent → 检测到用户纠正字段后，先回显“修改后的确认清单”（至少覆盖改动字段）并请用户确认，再进入内部生成/校验
```

### 模式 B：基础信息确认后 -> 产品知识确认

```
用户：「产品是某某，顾虑主要是长期安全性和价格」
Agent → 重新执行 tbs-scene-parse.py
Agent ← JSON（stage=KNOWLEDGE_CONFIRM）
Agent → 先核对脚本返回的 `stage` 与确认清单项状态（`userOutputTemplate.confirmationItems[*].status`）是否仍为“待确认”；只有当用户明确确认基础信息无误后，才在下一轮 payload 顶层设置 `baseInfoAcknowledged: true`（或写入 `scene.baseInfoAcknowledged: true`）
Agent → 基于当前基础信息给出“产品知识主题”建议，让用户确认/删除/改名/新增；正文另列为“产品知识正文（可选）”
Agent → 若用户明确不提供产品知识正文（如「暂无正文」）：**不得**反复追问正文；但仍必须展示并确认产品知识主题，禁止传 `declineProductKnowledge=true` 跳过主题
Agent → 若用户补充了产品知识正文/政策解读，则写入 scene.knowledge；若未补充正文：**不要**播报“当前未提供正文/正文为空”等状态句，只提示“可选补充正文要点（不影响推进）”。若知识检查已完成且已关联 `knowledgeIds`，可提示“已关联系统知识条目，无需额外正文”。
Agent → 若用户补充代表话术/经验，需当轮明确回显“已采纳”，并说明将归入 coachOnlyContext 的 `## 最佳实践` 小节
Agent → 话术优先套用 references/output-templates.md 模板 1，并遵守 references/common-params.md 的展示规则
```

### 模式 C：资料确认后 -> 内部生成场景内容

```
Agent → 再次执行 tbs-scene-parse.py
Agent ← JSON（stage=READY_FOR_SCENE_GENERATION）
Agent → 此时才在内部读取 references/scenario-json-parse.md 与 references/*.json
Agent → 生成 title / sceneBackground / actorProfile / doctorOnlyContext / coachOnlyContext
Agent → 生成后立刻合并进 scene，并写回同一会话目录下的 latest-draft.json（与 SKILL.md 的 draftPath 约定一致）
Agent → 再执行 tbs-scene-parse.py（以该 draft 为 --params-file），直至可进入校验阶段；**然后**对同一份 draft 执行 tbs-scene-validate.py（FULL），**在向用户展示「阶段 3」业务摘要之前**，应已拿到 validate 结果或已根据 issueHints 完成可自动修复项
Agent → 对用户展示时套用 references/output-templates.md 模板 3：必须回显累计确认清单（含前序已确认的基础信息/产品知识 + 新生成的标题/背景/角色），并遵守 references/common-params.md 的展示规则
```

### 模式 D：用户补充后终检

```
用户：「标题叫高血压门诊首诊沟通，目标是推动小范围试用」
Agent → exec: python3 scripts/tbs-scene-validate.py --params-file draft.json --output validate-result.json
Agent ← JSON（passed、validationReport）
Agent → 用户侧用 userOutputTemplate（含场景背景）；规则见 common-params.md、tbs-scene-validate.md
Agent → passed=true 再收口「确认创建 / 取消」
```

### 模式 E：确认后真实创建

```
用户：「确认」
Agent → 先通过 cms-auth-skills 获取 access-token
Agent → exec: python3 scripts/tbs-scene-finalize-from-session.py --session-dir "<sessionDir>" --user-confirmation 确认 --access-token "<ACCESS_TOKEN>"
Agent ← JSON（sceneId、resolvedIds、knowledgeIds）
Agent → 告知场景创建成功
```
