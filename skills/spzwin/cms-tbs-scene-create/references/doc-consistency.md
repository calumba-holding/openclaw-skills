# doc-consistency 模块说明

该模块用于发布前执行**文档一致性自检**，只检查 `.md` 文档规则，不参与运行时链路（parse/validate/create）。

## 触发场景

- 修改了 `SKILL.md` 或 `references/*.md` 的流程门禁、模板口径、字段定义。
- 发布前想快速确认没有口径回退或术语漂移。

## 输入

- 无业务输入参数。
- 直接扫描 skill 根目录下：
  - `SKILL.md`
  - `references/*.md`

## 动作

- `check-doc-consistency.py`
  - 校验禁用术语（如废弃阶段简称）
  - 校验关键口径（如医生关注点条数）
  - 校验阶段规则与模板单一真源约束

## 输出

- 通过：`OK: doc consistency checks passed.`
- 失败：逐条输出 `文件:行号:错误说明`，并返回非零退出码。
