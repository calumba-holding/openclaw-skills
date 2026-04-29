# references 索引

本目录只放脚本参数、门禁和输出约束。串联入口看 `SKILL.md`。

## 文件清单

| 文件 | 用途 |
|---|---|
| `auth.md` | token 获取与注入 |
| `common-params.md` | 通用参数、错误格式、JSON 安全写入 |
| `base-info-parse.md` | 基础信息抽取 |
| `tbs-scene-parse.md` | 分阶段 parse 与 draft 写回 |
| `product-knowledge-topic-generate.md` | 产品知识主题建议 |
| `scenario-json-parse.md` | 场景正文生成 |
| `tbs-scene-preflight.md` | 只读判断下一步 |
| `tbs-scene-validate.md` | FULL/TBV 校验 |
| `tbs-scene-create.md` | 最终确认后落库 |
| `output-templates.md` | 用户可见模板 |
| `review-checklist.md` | 输出与推进自检 |
| `agent-patterns.md` | 典型编排示例 |
| `maintenance.md` | 维护清单 |
| `doc-consistency.md` | 发布前一致性检查 |

## 使用顺序

1. 先读 `SKILL.md`。
2. 按目标脚本读取对应 reference。
3. 需要判断下一步时，先用 `tbs-scene-preflight.py`，不要反复 parse/validate 试探。
4. 用户最终确认后，统一调用 `tbs-scene-finalize-from-session.py`。
