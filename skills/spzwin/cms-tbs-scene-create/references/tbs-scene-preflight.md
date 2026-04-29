# tbs-scene-preflight

只读检查会话状态，避免 Agent 通过反复 `parse` / `validate` 探路。

```bash
python3 scripts/tbs-scene-preflight.py --session-dir <sessionDir>
```

## 特性

- 只读：不写 `latest-*`，不调用 TBS API。
- 输入：会话目录。
- 输出：JSON 到 stdout，包含 `status` 与 `nextAction`。

## 常见状态

| status | 含义 |
|---|---|
| `NEED_PARSE` | 草稿缺失、阶段未到 `READY_FOR_VALIDATE` |
| `NEED_KNOWLEDGE_CHECK` | 有知识主题但 `meta.knowledgeReady` 未通过，且未启用路径 B |
| `NEED_VALIDATE` | 缺少有效 FULL validate，或 hash 已不一致 |
| `READY_TO_CONFIRM` | 可展示模板 3，等待用户确认 |
| `READY_TO_FINALIZE` | 已启用路径 B，用户确认后调用 finalize |
| `ALREADY_CREATED` | 已有成功 `sceneId` |

## 约束

- 不能替代 `parse` / `validate` / `finalize`。
- 只能用于决定下一步，不能作为创建门禁。
