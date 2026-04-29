# tbs-scene-create

用户最终确认后的真实落库说明。**OpenClaw/Agent 默认只调用 `tbs-scene-finalize-from-session.py`**；`tbs-scene-create.py` 仅供 wrapper 内部调用。

## 推荐入口

```bash
python3 scripts/tbs-scene-finalize-from-session.py \
  --session-dir <sessionDir> \
  --user-confirmation 确认 \
  --access-token <ACCESS_TOKEN>
```

## finalize 做什么

1. 读取 `latest-draft.json` 与 `latest-validate-result.json`。
2. 若启用路径 B（`meta.deferKnowledgeCmsCheckUntilPreCreate=true`），先执行 knowledge-check。
3. 若知识未齐，停止并输出 `missingKnowledgeTopics`，不调用创建接口。
4. knowledge-check 写入 `knowledgeIds` 后，自动 FULL validate。
5. 若最终展示 hash 变化，停止并要求重新展示确认。
6. 调用 `tbs-scene-create-from-session.py` 组装 payload 并创建场景。

## 创建门禁

必须同时满足：

- 用户确认：`userConfirmation=确认`
- `meta.lastParseStage=READY_FOR_VALIDATE`
- FULL validate 通过，或 TBV 通过且已有 `meta.lastFullValidationPassed=true`
- `validationReport.sceneHash` 与当前 `scene` 一致
- `confirmedDisplayHash` 与当前展示内容一致
- 若有 `productKnowledgeNeeds`，必须 `meta.knowledgeChecked=true` 且 `meta.knowledgeReady=true`
- `access-token` 有效且非占位符

## 禁止

- Agent 直接调用 `tbs-scene-create.py`
- 手写 create payload
- 用户未确认就落库
- knowledge-check 与第二次 FULL validate 之间再跑 parse
- 凭 `scene.knowledgeIds` 非空判断知识已就绪；必须看 `meta.knowledgeReady=true`

## 结果

成功返回：

- `success=true`
- `sceneId`
- `resolvedIds`
- `personaIds`
- `knowledgeIds`

失败返回统一 JSON，常见错误：

- `knowledge_not_ready`
- `display_hash_changed_after_knowledge_check`
- `parse_stage_gate_failed`
- `validation_gate_failed`
- `knowledge_gate_failed`
- `display_gate_failed`
