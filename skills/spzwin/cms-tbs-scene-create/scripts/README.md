# scripts 目录说明

本目录存放 `cms-tbs-scene-create` 的 Python 执行脚本与共享客户端，采用扁平布局（共享库与入口脚本同级）。

## 脚本清单

| 脚本 | 类型 | 作用 |
|------|------|------|
| `tbs-scene-preflight.py` | 只读入口 | 检查 session 状态并给出下一步，不写文件、不调 API |
| `tbs-scene-parse.py` | 编排入口 | 解析输入并推进分阶段确认流程 |
| `tbs-scene-knowledge-check.py` | 知识检查入口 | 在知识主题确认后检查/复用/创建产品知识，并写回 `knowledgeIds` / `knowledgeReady`（支持基于 `meta.lastKnowledgeKey` 的等价去重跳过重复网络检查） |
| `tbs-scene-validate.py` | 校验入口 | 对场景草稿执行创建前门禁校验 |
| `tbs-scene-finalize-from-session.py` | 创建总入口 | 用户确认后统一执行必要 knowledge-check / validate / create |
| `tbs-scene-create-from-session.py` | 内部辅助入口 | 以会话状态目录为真源，自动组装 create-payload 并调用 `tbs-scene-create.py` |
| `tbs-scene-create.py` | 内部创建脚本 | 仅供 wrapper 调用，不建议 Agent 直接调用 |
| `tbs-scene-session-init.py` | 编排辅助入口 | 生成一个新的会话级状态目录（`sess-YYYYMMDD-HHMMSS-xxxx`），用于替代容易混淆的 `$$` 目录名 |
| `tbs-client.py` | 共享库 | 封装 TBS Admin API 请求、主数据匹配/创建、知识去重逻辑 |
| `tbs-md-sanitize.py` | 共享库 | 对部分 Markdown 内容做预处理与清洗 |
| `check-doc-consistency.py` | 开发态自检 | 发布前校验文档口径一致性（不参与运行时链路） |

从技能根目录执行：`python3 scripts/tbs-scene-parse.py --params-file … --output result.json`。Agent 调用入口脚本时必须使用 `--output`，完整 JSON 写文件，stdout/stderr 仅保留一行摘要。

---

## 推荐：用会话目录做创建入口（减少 field-missing 报错）

在开始一次新的“场景创建会话”前，推荐先初始化一个稳定的 session 目录（避免使用字面量 `$$`）：

```bash
SESSION_DIR="$(python3 scripts/tbs-scene-session-init.py)"
echo "$SESSION_DIR"
```

真实落库（create）阶段使用 `tbs-scene-finalize-from-session.py`，它只需要会话目录与用户最终确认即可，内部会自动读取：

- `{sessionDir}/latest-draft.json`（权威 scene + meta）
- `{sessionDir}/latest-validate-result.json`（validationReport.displayHash 绑定最终确认）

必要时执行 knowledge-check / FULL validate，并生成 `{sessionDir}/create-payload.json` 后调用创建链路。

示例：

```bash
python3 scripts/tbs-scene-finalize-from-session.py \
  --session-dir "$SESSION_DIR" \
  --user-confirmation "确认" \
  --access-token "$ACCESS_TOKEN"
```

---

## `tbs-client.py` 说明

### 定位

`tbs-client.py` 是本 Skill 的共享客户端与领域工具库，不直接面向用户，也不是独立的业务入口脚本。  
它主要被 `tbs-scene-create.py` 导入调用。

### 主要职责

1. 封装 HTTP 请求与通用重试（`TBSClient.request_json`）。
2. 统一解析不同响应包裹格式（如 `data` / `result`）。
3. 解析主数据 ID，并执行“先查后建”（业务领域、科室、品种、画像、知识等）。
4. 汇总创建场景所需关联 ID：`resolve_ids_for_scene`。

### 边界与约束

- 不负责用户对话与话术输出；不单独获取鉴权（`access-token` 由 `cms-auth-skills` 注入）。

### 维护注意事项

- 若新增/变更主数据解析逻辑，需同步核对 `references/tbs-scene-create.md`、`references/maintenance.md`、`tbs-scene-create.py`。
