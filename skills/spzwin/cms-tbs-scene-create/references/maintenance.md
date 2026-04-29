## 维护说明

需求对齐以当前 `references/*.md` 与 `scripts/*.py` 的一致性为准。

版本要点：
- **v0.6.1**：补丁锁、TBV、`meta`+create 门禁、回显协议、create 自校验。
- **v0.6.3**：`patch_fields_locked` 分层 hint、`doctorOnlyContext` 诊断、`createAgentHints` / `preCreateBlockedReminder`。
- **v0.6.4**：补齐 Intent 边界与鉴权预检；移除历史 `tbs_rules.py`。
- **v0.6.5**：`scripts/` 恢复扁平布局。
- **v0.6.6**：移除 `prompts/`；Schema 统一迁入 `references/`。
- **v0.6.7**：新增 `--mode fast_forward` 与 `--no-write-draft`。
- **v0.6.8**：强化 validate 的 FULL/TBV 调用决策。
- **v0.6.9**：收敛 `common-params.md` 的模板触发与字段优先级。
- **v0.6.10**：按 Gate 重构 `SKILL.md`；拆出 `output-templates.md` 与 `review-checklist.md`。
- **v0.6.11**：入口脚本新增 `--output` 契约，完整 JSON 写文件，stdout/stderr 仅输出摘要。
- **v0.6.12**：产品知识主题改为系统建议后用户确认；新增 `productKnowledgeNeedsConfirmed` 推进门禁。
- **v0.6.13**：拆分产品知识主题与产品知识正文展示口径，禁止把正文缺失提示放到主题字段下。
- **v0.6.14**：`declineProductKnowledge` 不再绕过主题确认；产品知识主题不可跳过，正文可暂无。
- **v0.6.15**：基础 6 项齐备但未确认时仍停留 `BASE_INFO_CONFIRM`，只预告后续生成主题。
- 修改 `SKILL.md` 中的 `version` 时，须同步更新 `version.json`
- 新增脚本时，必须同步更新：
  - `SKILL.md`
  - 对应 `references/*.md`
  - 目录结构说明
- JSON Schema 文件并入 `references/` 管理：`references/scene.schema.json`（两阶段共用，已移除冗余的 `scenario-json-parse.model.schema.json`）。
- 修改 `references/scenario-json-parse.md` 中的字段约束时，必须同步检查：
  - `references/scene.schema.json`
  - `scripts/tbs-scene-validate.py`
  - 发布前须 diff `references/scenario-json-parse.md` 固定节 A/B 正文与 `scripts/tbs-scene-validate.py` 中 Canon 文本是否完全一致
- 若变更真实创建接口字段，必须同时核对 `规范和接口/TBS_ADMIN_API_REFERENCE.md`
- 若变更编排判定口径（`success`/`error`/`stage`/`validationReport`/`userConfirmation` 等），必须同步更新：
  - `SKILL.md`
  - `references/common-params.md`
  - `references/tbs-scene-parse.md`
  - `references/tbs-scene-validate.md`
  - `references/tbs-scene-create.md`
- 若变更**用户可见输出**（拦截词、失败转写、收口等）：以 `references/common-params.md` 为真源，并核对 `SKILL.md`、`tbs-scene-parse.md`、`tbs-scene-validate.md`、`agent-patterns.md`、`scenario-json-parse.md` 中的交叉引用是否仍成立。
- 若变更**用户可见模板**：以 `references/output-templates.md` 为真源，并核对 `common-params.md`、`review-checklist.md`、`agent-patterns.md` 的引用。
- 若变更**运行时自检**：以 `references/review-checklist.md` 为真源，并核对 `SKILL.md` 的 Gate 入口条件。
- 若变更 `tbs-scene-parse.py` 的字段标签、阶段提示、追问文案或轻量关键词规则：优先修改 `references/parse-runtime-config.json`，避免在脚本中新增硬编码。

## 结构例外说明（本 Skill 约定）

- 本 Skill 不保留 `prompts/` 目录；Schema 与说明文档统一放在 `references/`。
- **`scripts/` 目录扁平化**（对齐 `cms-cwork-workflow`）：入口脚本 `tbs-scene-*.py` 与共享库 `tbs-client.py`、`tbs-md-sanitize.py` 同级；不设 `lib/` 子目录。
