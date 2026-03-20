---
name: code-dev
displayName: 🔧 代码开发
description: |
  规范的 Git 开发流程：分支管理 → 开发 → PR → Review → 合并。
  支持新 feature 开发和 bug 修复，强制禁止直接推送到 main。
  触发于 "开发", "实现", "新功能", "修复", "提交 PR", "创建分支"。
author: LuciusCao
license: MIT
version: 1.2
tags:
  - git
  - workflow
  - development
  - pr
repository: https://github.com/LuciusCao/openclaw-skills/tree/main/code-dev
---

# Git Workflow Skill

安全的 Git 开发流程。

---

## ⚠️ 核心规则

- ❌ 禁止直接推送到 main 分支
- ❌ 禁止跳过 PR 流程
- ❌ 禁止在未理解代码库的情况下开发新功能
- ❌ 禁止在未找到 Bug 根因的情况下修复 Bug
- ✅ 必须从 develop 创建新分支
- ✅ 必须通过 PR 合并到 develop
- ✅ 使用 code-review 技能审查代码（如可用）

---

## 前置检查

执行前检查环境能力：

```javascript
// 检查 subagent 支持
const supportsSubagent = await checkSubagentSupport();

// 检查 code-review 技能
const hasCodeReview = await checkSkillAvailable("code-review");
if (!hasCodeReview) {
  console.log("⚠️ 未安装 code-review 技能，请手动审查代码");
}
```

---

## 执行流程

### 1. 任务分析
- 确定类型：feature / fix / docs / refactor
- 生成分支名：`feature/xxx`, `fix/xxx`
- 确认目标分支 = develop

### 2. 代码库理解（Feature 必需）

检查清单：
- □ 是否已有类似 helper/util？
- □ 会影响哪些现有功能？
- □ 需要修改哪些文件？
- □ 哪些代码不必要修改？

避免：重复实现、影响当前功能、修改不必要代码

### 3. Bug 根因调研（Fix 必需）

调研清单：
- □ Bug 的具体表现？
- □ 触发条件？
- □ 根因位置？
- □ 修复方案及影响范围？

禁止：未找到根因就修复、只修复表面症状

### 4. 分支创建

```bash
git checkout develop
git pull origin develop
git checkout -b {type}/{name}
```

### 5. 开发实施

必须包含：
- ✅ 代码实现（最小修改范围）
- ✅ 单元测试
- ✅ 文档更新
- ✅ 类型检查通过
- ✅ Lint 通过

### 6. 代码审查

如安装了 code-review 技能：
```javascript
sessions_spawn({
  runtime: "subagent",
  mode: "run",
  task: `使用 code-review 技能审查当前变更：
         - 分支: {branchName}
         - 对比: develop...HEAD`
});
```

如无 code-review 技能：提示用户手动审查

### 7. 提交 PR

```bash
git push origin {branchName}
gh pr create --base develop --head {branchName} \
  --title "{type}: {描述}" \
  --body "{PR 描述}"
```

---

## 分支命名

| 类型 | 格式 | 示例 |
|------|------|------|
| Feature | `feature/{name}` | `feature/auth` |
| Fix | `fix/{name}` | `fix/cors` |
| Docs | `docs/{name}` | `docs/api` |
| Refactor | `refactor/{name}` | `refactor/db` |

---

## 更多参考

- [详细工作流](references/WORKFLOW.md) - 完整开发流程
- [Subagent 模板](references/SUBAGENT_TEMPLATE.md) - 任务模板
- [Commit 规范](references/COMMIT.md) - Conventional Commits
