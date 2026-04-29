---
name: cms-tbs-scene-create
description: 提供【TBS 训战场景创建】全流程执行能力。用户一旦表达“创建场景/生成对练场景/医药代表训练/销售训练/校验场景/确认落库”等执行意图，必须进入本 Skill 的分阶段脚本调用流程；仅当用户明确是纯咨询时，才允许先文字说明并二次确认是否执行。本 Skill 依赖 `cms-auth-skills` 获取 `access-token` 后才允许真实落库。
skillcode: cms-tbs-scene-create
github: https://github.com/xgjk/xg-skills/tree/main/cms-tbs-scene-create
dependencies:
  - cms-auth-skills
# bump 时须同步修改同目录下 version.json 的 version 字段
version: 0.6.33
tools_provided:
  - name: tbs-client
    category: exec
    risk_level: medium
    permission: write
    description: TBS Admin API 共享客户端，封装请求、主数据匹配与创建
    status: active
  - name: tbs-scene-session-init
    category: exec
    risk_level: low
    permission: write
    description: 初始化会话状态目录
    status: active
  - name: tbs-scene-payload-write
    category: exec
    risk_level: low
    permission: write
    description: 安全写入 latest-payload.json，避免手写 JSON 出错
    status: active
  - name: tbs-scene-preflight
    category: exec
    risk_level: low
    permission: read
    description: 只读检查会话状态，决定下一步
    status: active
  - name: tbs-scene-parse
    category: exec
    risk_level: low
    permission: read
    description: 解析用户输入、合并草稿、推进阶段
    status: active
  - name: tbs-scene-validate
    category: exec
    risk_level: low
    permission: read
    description: 校验场景草稿；FULL 用于最终确认，TBV 用于标题/背景补丁
    status: active
  - name: tbs-scene-knowledge-check
    category: exec
    risk_level: medium
    permission: write
    description: 查询/复用/创建产品知识，并写回 knowledgeReady
    status: active
  - name: tbs-scene-create-from-session
    category: exec
    risk_level: medium
    permission: write
    description: 从会话目录组装 create payload 并调用创建脚本
    status: active
  - name: tbs-scene-finalize-from-session
    category: exec
    risk_level: medium
    permission: write
    description: 用户最终确认后的总落库入口
    status: active
---

# cms-tbs-scene-create

## 核心定位

本 Skill 只做一件事：根据用户创建 TBS 训战场景的意图，读取对应 `references/*.md`，再执行 `scripts/*.py`。  
参数、边界、分支逻辑以 `references` 为准；`SKILL.md` 只保留入口级规则。

## 强制前置

真实落库前必须通过 `cms-auth-skills` 获取有效 `access-token`，并以 `--access-token` 注入最终落库入口。  
未鉴权时，可以 parse / validate / preflight，但不得调用真实 CMS/TBS 写接口。

## 标准执行流程

1. 识别用户是“执行创建”还是“纯咨询”。
2. 任何用户可见回复前，必须先读 `references/output-templates.md` 与 `references/review-checklist.md`，并按当前时点套用模板；模板是强制输出契约，不是参考文案。
3. 若用户首次只表达“创建场景/我要创建一个场景”，且未提供可解析基础信息：不得调用脚本，直接使用 `output-templates.md` 模板 0「标准版」原结构输出。
4. 若首轮输入为完整长文本并命中模板 0 的“长文本例外”：创建或复用 `sessionDir`，再进入 parse。
5. 每次执行脚本前，先读对应 `references/*.md`。
6. 用 `tbs-scene-payload-write.py` 写 payload；禁止手写/拼字符串 JSON。
7. 用 `tbs-scene-parse.py` 推进阶段；不要靠猜测判断阶段。
8. 当 parse 返回 `READY_FOR_SCENE_GENERATION` / `scenarioGenerated=false`：作为内部事务连续完成“场景内容生成 → 写回 draft → 再 parse → FULL validate”，除耗时提示外不得向用户播报内部状态。
9. 需要探路时先跑只读 `tbs-scene-preflight.py`，不要反复 parse/validate。
10. 模板 3 最终确认前执行 `tbs-scene-validate.py --scope full`。
11. 用户明确回复“确认”后，只调用 `tbs-scene-finalize-from-session.py`。

## 会话文件

同一场景全程复用同一个目录：

```text
workspace/.cms-log/state/cms-tbs-scene-create/{sessionId}/
├── latest-payload.json
├── latest-parse-result.json
├── latest-draft.json
├── latest-validate-result.json
├── latest-knowledge-check-result.json
└── latest-create-result.json
```

`latest-draft.json` 是唯一草稿真源。不要直接覆盖它，只能通过脚本写回。`tbs-scene-session-init.py` 默认会复用 120 秒内尚未写入业务文件的空 session（仅 `SESSION.txt`），用于抵抗审批/重试导致的多空目录；确需新会话时传 `--force-new`。

## 常用命令与必读文档

| 脚本 | 必读 reference | 用途 |
|---|---|---|
| `tbs-scene-session-init.py` | `references/tbs-scene-parse.md` | 初始化 session |
| `tbs-scene-payload-write.py` | `references/common-params.md` | 安全写 payload |
| `tbs-scene-preflight.py` | `references/tbs-scene-preflight.md` | 只读判断下一步 |
| `tbs-scene-parse.py` | `references/tbs-scene-parse.md` | 解析/合并/推进 |
| `tbs-scene-knowledge-check.py` | `references/tbs-scene-parse.md` | 产品知识查重/创建 |
| `tbs-scene-validate.py` | `references/tbs-scene-validate.md` | FULL/TBV 校验 |
| `tbs-scene-finalize-from-session.py` | `references/tbs-scene-create.md` | 用户确认后的总落库入口 |

补充：用户可见话术看 `references/output-templates.md`；场景正文生成看 `references/scenario-json-parse.md`；输出自检看 `references/review-checklist.md`；鉴权看 `references/auth.md`。

## Gate-5

用户最终确认后，OpenClaw/Agent 只调用：

```bash
python3 scripts/tbs-scene-finalize-from-session.py \
  --session-dir "<sessionDir>" \
  --user-confirmation 确认 \
  --access-token "<access-token>"
```

不要直接调用 `tbs-scene-create.py`。该脚本只允许被 session/finalize wrapper 内部调用。

## 路径选择

- **路径 A**：Gate-2 先完成 `knowledge-check`，之后生成场景、FULL validate、最终确认、finalize。
- **路径 B**：设置 `meta.deferKnowledgeCmsCheckUntilPreCreate=true`，把 CMS 知识查重/创建推迟到用户最终确认后，由 `finalize` 自动执行。

路径 B 写入 `knowledgeIds` 后会再跑一次 FULL validate；这是必要校验，不属于重复探路。

## 反向示例

- 未读 reference 就执行脚本。
- 用户可见回复自由发挥，未套用 `output-templates.md` 对应模板。
- 首轮“我要创建场景”时自行改写模板 0，或用自创的“完整描述/引导回答”结构替代模板 0。
- 直接手写 JSON 覆盖 `latest-draft.json`。
- 每轮用户消息都跑 `parse + validate`。
- 向用户展示 `scenarioGenerated=false`、`READY_FOR_SCENE_GENERATION`、`draft`、`parse`、`validate` 等内部状态。
- 在场景内容生成事务中间停下向用户解释内部判断，而不是连续执行到模板 3 或业务化失败提示。
- 用户未确认就进入 Gate-5。
- Agent 直接调用 `tbs-scene-create.py`。
- 凭 `scene.knowledgeIds` 非空就认为知识已就绪；必须看 `meta.knowledgeReady=true`。
- 在 knowledge-check 与第二次 FULL validate 之间再跑 parse。

## 错误处理与通用参数

通用错误格式、`--params-file`、JSON 安全写入与展示声明规则见 `references/common-params.md`。

---

## 目录结构

```text
cms-tbs-scene-create/
├── SKILL.md
├── version.json
├── scripts/
│   ├── tbs-client.py
│   ├── tbs-scene-session-init.py
│   ├── tbs-scene-payload-write.py
│   ├── tbs-scene-preflight.py
│   ├── tbs-scene-parse.py
│   ├── tbs-scene-knowledge-check.py
│   ├── tbs-scene-validate.py
│   ├── tbs-scene-create-from-session.py
│   └── tbs-scene-finalize-from-session.py
└── references/
    ├── auth.md
    ├── common-params.md
    ├── tbs-scene-parse.md
    ├── tbs-scene-preflight.md
    ├── tbs-scene-validate.md
    ├── tbs-scene-create.md
    ├── scenario-json-parse.md
    ├── output-templates.md
    └── review-checklist.md
```
