# cms-tbs-scene-create 与需求对齐：修改与验收清单  
> **实现**：Skill **v0.6.0** 已覆盖下列 §二 主路径；§三 仍建议人工走查。

---

## 一、需求 ↔ 现状速查

| 需求要点 | 当前 Skill 典型现状 | 修改落点 |
|-----------|---------------------|----------|
| 阶段1/2 确认后**锁定**，仅标题/背景可 PATCH | `parse` 合并补丁未按阶段过滤；`tbs-scene-parse.md` 仍允许改已确认项表述 | `tbs-scene-parse.py` + `tbs-scene-parse.md` |
| PATCH 后 **TBV**（只校 title / sceneBackground） | 仅 `tbs-scene-validate.py` 全量校验 | `validate` 增 scope 或新脚本 + 返回 `tbvReport` |
| RV 确认落库**不跑全量 S4**，仍须凭证 | `create.py` 强制 `validationReport.passed` | `create.py` + 草稿 `meta` 记录全量通过 / TBV 通过组合规则 |
| **对齐则省 S3**：背景 vs 顾虑+目标 + 成稿齐 | 无 | 编排层或 `parse`/独立小步 + PRE **变更摘要** 字段 |
| PRE **变更摘要**（是否重跑、要点） | `userOutputTemplate` 未约定该块 | `parse` 输出结构 + `tbs-scene-parse.md` + Agent 话术约束（`SKILL.md`） |
| 人侧摘要、草稿全量 | 主要靠 Agent，脚本未截断 | 可选：`parse` 增加摘要字段；至少文档写清 |
| 咨询不进创建链 | 脚本无 | `SKILL.md` / Agent 规则（非脚本） |

---

## 二、修改清单（实现）

### 2.1 必改文件

| # | 文件 | 要做什么 |
|---|------|----------|
| 1 | `scripts/tbs-scene-parse.py` | 按 `stage`/确认标志**过滤补丁**；拒绝改锁字段时返回明确错误/ `rejectedFields`；必要时输出 **变更摘要** / **对齐结论** / **是否建议免 S3** 等结构化字段（字段名与 `tbs-scene-parse.md` 对齐后实现） |
| 2 | `references/tbs-scene-parse.md` | 删除/改写与「锁定」冲突的「已确认字段仍可改…」类表述；写入 **PRE/TBV/RV/PATCH**、**编辑权限**、**对齐省 S3**、**变更摘要** 与入参/出参约定 |
| 3 | `scripts/tbs-scene-validate.py`（或新增脚本并在 README 登记） | **TBV**：仅 `title` + `sceneBackground`（及与实现绑定的 `background` 若一致）规则子集；输出与全量 `validationReport` 可区分 |
| 4 | `references/tbs-scene-validate.md` | 描述全量 S4 vs TBV 的调用时机、返回结构、`create` 衔接 |
| 5 | `scripts/tbs-scene-create.py` | **放行规则**：首落库 = 全量 `passed`；PATCH 路径 = `meta`/报告 满足「曾全量通过 + TBV 通过」或文档最终定稿规则；**落库前** `sceneBackground`→`repBriefing` 同步策略与 TBV 一致 |
| 6 | `references/tbs-scene-create.md` | 与 `create.py` 门禁、`userConfirmation`、凭证一致 |
| 7 | `SKILL.md` | 串联规则第 3～4 条：`parse`→（S3）→`validate`（全量 / TBV）→`create`；禁止仅靠 Agent 绕过脚本门禁 |
| 8 | `SKILL.md` 头 / `version.json` | 版本号与 `maintenance.md` 同步 bump |
| 9 | `references/README.md` | 已索引本清单 |
| 10 | `references/maintenance.md` | 补充本次联动文件（若有结构例外） |

### 2.2 条件修改

| 条件 | 文件 / 动作 |
|------|-------------|
| `GENERATED_CONFIRM_FIELDS` 仍含 `actorProfile` 与需求「仅标题/背景」冲突 | `tbs-scene-parse.py` + `tbs-scene-parse.md`：用户侧确认项与可 PATCH 字段对齐 |
| 对齐省 S3 放在模型侧 | `scenario-json-parse.md` / 上游调用约定：入参带「跳过生成」标志时的输出约定 |
| 自动化测试 | `scripts/` 同目录或 CI 增加最小 payload 用例：锁字段拒收、TBV 过/不过、create 放行 |

### 2.3 全局检索（防漏改）

在 `cms-tbs-scene-create` 目录执行（或 IDE 全局搜）：

```
validationReport.passed
READY_FOR_VALIDATE
userConfirmation
parsedFields|userUpdates
GENERATED_CONFIRM_FIELDS|BASE_CONFIRM_FIELDS
已确认|确认清单
```

逐条对照是否仍符合 **0.7.2** 文档表述。

---

## 三、验收清单（测试 / 走查）

### 3.1 门禁与分支

| # | 场景 | 期望 |
|---|------|------|
| A1 | 阶段2 已确认后，`parsedFields` 带 `doctorConcerns` | **拒收**或忽略并提示；不写脏草稿 |
| A2 | 同阶段仅带 `title` / `sceneBackground`（及约定别名） | **接受**；进入 TBV 路径 |
| A3 | 首进 PRE 前未跑全量 S4 或 `passed!=true` | `create` **拒绝** |
| A4 | 首链全量 S4 已过 → PATCH → TBV 过 → RV 确认 | `create` **可成功**（不强制再全量 S4，与文档一致） |
| A5 | TBV 不过 | 回 RV / 提示修正；**不可**带错标题背景落库 |
| A6 | `userConfirmation=取消` | 不写库、退出码/提示与文档一致 |

### 3.2 对齐省 S3（若已实现）

| # | 场景 | 期望 |
|---|------|------|
| B1 | 背景与顾虑/目标判定**一致**且内部稿齐 | **不调用** S3（或等价跳过）；仍 TBV→PRE |
| B2 | 判定**不一致**或背景缺短 | **调用** S3→S4→… |
| B3 | PRE 展示 | 含 **变更摘要**（是否重跑 + 至少一行要点） |

### 3.3 体验与安全

| # | 场景 | 期望 |
|---|------|------|
| C1 | 用户可见回复 | 无 JSON、无 token、无内部字段名（与 `SKILL.md` 一致） |
| C2 | 长书面材料 | 人侧摘要策略可执行（脚本或 Agent 至少一侧落实） |
| C3 | 鉴权 | 无有效 token 不调写库接口 |

---

## 四、发布前核对

- [ ] `version.json` 与 `SKILL.md` `version` 一致  
- [ ] `references/README.md` 索引已更新  
- [ ] 本清单 **二、三** 全部可勾选或通过说明「不适用」  
- [ ] 与需求文档版本号在提交说明或 `maintenance.md` 中注明对应关系  

---

*清单随需求文档升级而更新；冲突时以需求文档为准。*
