---
name: Skill Manager All In One | 一站式技能管理器
description: Manage OpenClaw skills end-to-end. 一站式管理 OpenClaw 技能的创建、修改、发布、更新、升版与审计。
metadata: {"openclaw":{"requires":{"bins":["git","gh"]},"runtime":{"requiredBinaries":["clawhub","git","gh"],"credentialExpectations":["ClawHub CLI login/session for publish/delete/hide/unhide/sync","Git/GitHub CLI authentication for GitHub workflows"],"filesystemWrites":["~/.openclaw/workspace/skills/<slug>/","~/.openclaw/workspace/projects/<slug>/","~/.cache/huggingface/modules/<slug>/"],"externalWrites":["clawhub publish/delete/hide/unhide/sync","git push","gh release create"],"confirmation":"Show exact commands and wait for explicit user confirmation before publish, delete, push, move, overwrite, or other writes."}}}
---

# Skill Manager All In One | 一站式技能管理器

## Runtime Expectations | 运行依赖与权限声明

This skill may guide an agent to inspect, create, edit, move, publish, or audit OpenClaw skill files. It is not a passive documentation-only skill.
本技能可能指导 agent 检查、创建、编辑、移动、发布或审计 OpenClaw 技能文件；它不是只读文档型技能。

### Required binaries | 所需命令行工具

Declare and verify these before any publish or external write:
发布或外部写入前，必须声明并验证以下工具：

These requirements must be declared in SKILL.md frontmatter `metadata` as well as in the body text. ClawHub/security scanners read metadata, not only prose.
这些要求必须同时写入 SKILL.md frontmatter `metadata` 和正文说明。ClawHub/安全扫描器会读取 metadata，不只读取正文。

| Tool | Used for | Verify command |
|------|----------|----------------|
| `clawhub` | ClawHub skill inspect/publish/delete/hide/unhide/sync | `clawhub --help` or `~/.openclaw/tools/node/npm/bin/clawhub --help` |
| `git` | Git status/commit/log/revert workflows | `git --version` |
| `gh` | GitHub release/PR workflows, only when target platform is GitHub | `gh --version` |

### Credentials and authentication | 凭据与授权

- ClawHub publishing requires an authenticated ClawHub session/token.
  ClawHub 发布需要已登录的 ClawHub 会话/token。
- GitHub publishing requires Git/GitHub authentication and may use `gh` credentials.
  GitHub 发布需要 Git/GitHub 授权，可能使用 `gh` 凭据。
- Do **not** ask the user to paste long-lived secrets into chat. Prefer existing CLI login/session state.
  不要要求用户在聊天中粘贴长期密钥；优先使用已有 CLI 登录态。
- Before running credential-using commands, print the exact command and wait for explicit user confirmation.
  执行会使用凭据的命令前，必须打印精确命令并等待用户明确确认。

### Filesystem scope and write risks | 文件系统范围与写入风险

This skill may operate on:
本技能可能操作：

- `~/.openclaw/workspace/skills/<slug>/` — skill source files only.
  仅放技能源文件。
- `~/.openclaw/workspace/projects/<slug>/` — runtime files, outputs, reports, and project data.
  放运行文件、输出、报告和项目数据。
- `~/.cache/huggingface/modules/<slug>/` — model files.
  放模型文件。

Never move, delete, overwrite, publish, push, or otherwise mutate files without first showing the planned paths and commands and receiving explicit confirmation.
移动、删除、覆盖、发布、推送或其他写入操作前，必须先展示计划路径和命令，并获得明确确认。

### Dry-run first | 优先 dry-run / local-test

For high-impact changes, start in `local-test` mode: inspect files, produce a planned command list, and stop before mutation or publication.
高影响变更先进入 `local-test`：只检查文件、生成拟执行命令列表，在真正写入或发布前停止。

## 模式 | Mode

> 读取本 SKILL.md 后，先确认当前任务属于哪种模式，再跳转对应章节执行。

| 模式 | 说明 |
|------|------|
| **create** | 从零创建新技能 |
| **modify** | 修改已发布技能（升版/功能调整） |
| **audit** | 搜索/审计已有技能 |
| **local-test** | 仅本地测试，不发布 |

---

## 核心原则 | Core Rules

1. **Local first, network second** — 先检查本地已安装技能，再搜索网络。
2. **Be concrete** — 汇报时写清楚准确路径、准确命令、准确版本变化。
3. **One by one, confirm one by one** — 涉及多个文件/版本/技能时，必须逐个处理、逐个确认。禁止批量操作。
4. **Publish like a product** — 发布文本应像正式发布说明，而非聊天记录。
5. **For AI and humans** — 技能正文应兼顾 agent 与人类可读性。
6. **English first, Chinese second** — 对外展示文本统一先英文后中文；包括 `name`、SKILL.md frontmatter `description`（发布到 ClawHub 后显示为 registry `summary` / CLI `Summary:`）、Changelog、README 关键标题与核心段落。中文不能因英文过长而被预览截断。
7. **Learn from release evidence** — 发布流程规则来自真实发布证据；新增检查项前先确认它能防止具体失误，而不是堆砌流程。

---

## 技能制作流程 | Phase 1: Create / Modify

> 按顺序执行，边做边对照第 6 章「统一检查清单」的【通用质量基线】。

### 步骤 1：明确需求

确定以下四项，作为后续所有操作的依据：

- **目标平台**：ClawHub / GitHub / 其他
- **版本号**：首次发布为 `1.0.0`

> ⚠️ Display name 和 Skill slug 是 ClawHub 专属概念，若目标平台为 ClawHub，请在 Phase 2 步骤 1 确认。

### 步骤 2：创建目录结构

参考第 7 章「技能目录体系」，在正式技能目录创建技能文件夹。

```
~/.openclaw/workspace/skills/<slug>/
```

### 步骤 3：编写 SKILL.md

按本技能的主模板编写 SKILL.md（参考 Phase 1 步骤 1 确认的平台需求）。

### 步骤 4：边做边查——对照清单

每完成一个文件或代码块，立即对照第 6 章【通用质量基线】逐项打勾。

**目标平台已确定时，附加对应平台专项（ClawHub → CH01~CH09，GitHub → GH01~GH06）。**

> 如 Phase 1 已逐项打勾通用基线，Phase 2 只需复核 + 补充平台专项，不必重复全量检查。

---

## 技能发布验证流程 | Phase 2: Publish

> 必须完成 Phase 1 后才能执行本阶段。

### 步骤 1：确认基本信息 & 复查清单

**ClawHub 目标时，先确认以下两项：**
- **Display name**：`EN Title | CN Title` 双语格式（对应 CH01）
- **Skill slug**：小写字母 + 连字符，如 `speech-synthesizer`

**然后复查清单：**
- 对照第 6 章【通用质量基线】全部项（G01~G06）
- 根据目标平台，额外核对【平台专项】（ClawHub → CH01~CH09，GitHub → GH01~GH06）
- 逐项标注 ✅ / ⚠️，有问题的立即修复

### 步骤 2：⚠️ 两步验证（强制，必须执行）

**无论改动多小、无论第几次修改，两步验证不可跳过。**

#### 第一步（AI 内部执行，不输出给用户）
- 核对清单（G01~G06 + 对应平台专项）
- 检查文件大小（>50MB 需报告）
- ClawHub 目标时检查对外表述：`name`、SKILL.md frontmatter `description`（ClawHub registry `summary` / CLI `Summary:`）、Changelog、README 关键标题和核心说明均应先英文后中文
- 检查 ClawHub 摘要：`description` 应短而清楚；发布后用 `inspect` 查看 `Summary:`，确认中文在预览可见范围内
- 拟定 Changelog

#### 第二步（输出给用户，等待明确确认）
必须输出以下全部内容（用第 9 章汇报模板），**确认前不得执行任何发布类命令**：

Display name / Skill slug / 目标平台 / 当前版本 / 新版本号 / Changelog / 文件大小 / 核对清单 / 发布命令

**确认标志**：用户明确回复「好」「确认」「上传」「发吧」等。

**⚠️ 两步验证适用于所有发布类操作**：clawhub publish / git push / gh release create / 推广发帖 / 社交平台发帖等。

> 上两步验证前，先读对应 reference：ClawHub 上传/升版 → `references/clawhub-publish.md`；GitHub 上传 → `references/github-publish.md`。

### 步骤 3：执行发布

获得用户确认后，执行对应平台的发布命令。
> ClawHub 上传详见 `references/clawhub-publish.md`；GitHub 上传详见 `references/github-publish.md`。

**若用户拒绝发布**：回到 Phase 1 修改流程，递增修订版本号（如 1.2.1 → 1.2.2-dev），不得直接重复尝试发布相同内容。

---

## 发布后维护 | Phase 3: Maintain

参考 Phase 1 修改流程 + 版本号递增 → 回到 Phase 2 两步验证。

- **升版/更新**：ClawHub → `references/clawhub-publish.md`；GitHub → `references/github-publish.md`
- **宣传/推广**：读 `references/promotion.md`（Moltbook 格式、AI心理学、去标识化）
- **查看详情**：ClawHub → `clawhub inspect <slug>` + `references/clawhub-inspect.md`（Details ▾ 确认 Assessment）
- **GitHub**：`git log` 验证
- **回滚**：clawhub → `clawhub delete <slug> --yes`（软删除）；GitHub → `git revert`
- **隐藏/恢复/删除**：执行前报告 + 执行后验证

---

## 统一检查清单 | Checklist（制作与发布共享）

> Phase 1 边做边查，Phase 2 发布前复查。
> 制作时查【通用质量基线】，发布时查【通用 + 平台专项】。

### 通用质量基线（所有技能必查）

**上游参考技能保护**：不要直接修改上游/参考技能，尤其是 `skill-creator`。它会随 OpenClaw 或上游版本更新而变化；本技能只能把本地经验沉淀到 `skill-manager-all-in-one` 自己的 SKILL.md / references 中。若确实需要修改上游技能，必须先向用户说明原因、影响和恢复方案，等待明确授权。

| # | 检查项 | 说明 |
|---|---------|------|
| G01 | 去标识化 | 无个人信息、内部路径、私有凭证 |
| G02 | 安全性 | 无注入风险（Shell注入/Python注入/路径注入）、无过度权限、无数据外传 |
| G03 | 逻辑科学性 | 结构清晰、路径准确、模块化、**同名规范** |
| G04 | AI 可读性 | agent 可理解、上下文连贯、无歧义指令 |
| G05 | 易维护性 | 代码整洁、注释到位、变量命名清晰、模块化 |
| G06 | 依赖/凭据声明 | 外部 Python 包、命令行工具、API、模型、账号权限、凭据来源、文件系统写入范围必须明确声明；不得硬编码密钥。发布类技能需声明 `clawhub`/`git`/`gh` 等工具及验证命令。

### ClawHub 专项（附加于通用基线之后）

| # | 检查项 | 说明 |
|---|---------|------|
| CH01 | Display Name 双保险 | **ClawHub 页面展示名必须双保险**：`SKILL.md` frontmatter 的 `name:` 填 `EN Title | CN Title`，发布命令也必须显式传 `--name "EN Title | CN Title"`。实测仅改 `name:` / `_meta.displayName` 更新版本时，ClawHub 顶部展示名可能不会同步中文。例：`clawhub publish <path> --slug speech-synthesizer --name "TTS Speaker | TTS 朗读器" --version 1.0.1 ...` |
| CH02 | Skill slug | 技能唯一标识符，小写字母 + 连字符（例：`speech-synthesizer`）；在 `~/.openclaw/workspace/skills/<slug>/` 目录名和 `clawhub publish` 命令中使用 |
| CH03 | 坏符号链接 | 无失效符号链接 |
| CH04 | 运行时产物 | 无 `.pyc`、`.pyo`、`__pycache__`、`.log` 等运行时产物 |
| CH05 | 文件/模型分离 | 技能文件夹（`~/.openclaw/workspace/skills/<slug>/`）**严禁存放任何模型文件、运行产物、结果文件**。模型文件统一放 `~/.cache/huggingface/modules/<slug>/`；运行文件与结果文件统一放 `~/.openclaw/workspace/projects/<slug>/`。技能文件夹本身仅含技能代码（SKILL.md、脚本、配置文件等），大小应控制在 50MB 以内。发布前 `du -sh <skill-dir>` 超过 50MB 需立即处理。 |
| CH06 | Embedding 500 应急 | 当 SKILL.md 或引用的 reference 文件超过 500 行时，自动拆分或提供摘要版本 |
| CH07 | 目录隔离 | 确保技能文件夹内无 `.git/`、`.DS_Store`、`Thumbs.db` 等无关元数据 |
| CH08 | 版本号一致性 | `_meta.json` version、changelog 版本号、发布命令版本号三者必须一致 |
| CH09 | Changelog 格式 | 英文在前（面向用户描述功能变化，而非开发者心理活动）、双语数字列表 |
| CH10 | ClawHub Summary 双语可见 | 本地字段名是 SKILL.md frontmatter `description`；发布到 ClawHub 后是 registry `summary`，CLI `inspect` 显示为 `Summary:`。该摘要应遵循 English first, Chinese second，并控制英文长度，确保中文仍在卡片预览可见范围内。建议总长度一两句，英文部分优先短句。 |
| CH11 | 对外表述顺序统一 | 所有面向用户的双语表述统一先英文后中文：Display name、SKILL.md `description` / ClawHub `Summary:`、Changelog、README 关键标题、核心说明、示例说明。避免一处中文在前、一处英文在前造成发布页风格不一致。 |

### GitHub 专项（附加于通用基线之后）

> ⚠️ 必须先通过通用质量基线 G01~G06。

| # | 检查项 | 说明 |
|---|---------|------|
| GH01 | git status | 无未提交变更（`git status` 干净） |
| GH02 | 分支规范 | main/master 分支干净，commit 原子化 |
| GH03 | commit 规范 | commit message 简洁、描述性、一行概括 + 详细说明 |
| GH04 | Release Notes | 格式规范，与 changelog 内容一致 |
| GH05 | 文件完整性 | 无多余临时文件 |
| GH06 | License 检查 | 发布前确认包含合适开源许可证文件（如 MIT），或明确声明无许可证 |

---

## 技能目录体系 | Directory System

| 目录 | 路径 |
|------|------|
| 正式技能 | `~/.openclaw/workspace/skills/<slug>/` |
| 插件技能 | `~/.openclaw/extensions/` |
| 临时草稿 | `~/.openclaw/workspace/temp-skills/<slug>/` |
| 工作区资源 | `~/.openclaw/workspace/projects/<slug>/` |
| 模型缓存 | `~/.cache/huggingface/modules/<slug>/` |

### 各目录职责（强制分离）

> **技能文件夹 = 纯技能代码**。禁止放入任何模型、运行产物、结果文件。

| 目录 | 职责 | 禁止放入 |
|------|------|---------|
| `~/.openclaw/workspace/skills/<slug>/` | 技能代码（SKILL.md、脚本、配置） | 模型文件、运行结果、输出文件 |
| `~/.openclaw/workspace/projects/<slug>/` | 运行文件、结果输出、数据文件 | 技能源代码 |
| `~/.cache/huggingface/modules/<slug>/` | 所有模型文件（.pt/.onnx 等） | 非模型文件 |

**示例（speech-transcriber 技能）：**
```
~/.openclaw/workspace/skills/speech-transcriber/     # ✅ 技能代码（SKILL.md、scripts/、requirements.txt）
~/.openclaw/workspace/projects/speech-transcriber/   # ✅ 运行文件与结果（transcriptions/、recordings/、outputs/）
~/.cache/huggingface/modules/speech-transcriber/     # ✅ 模型文件（small/、medium/）
```

### 命名规范 | Naming Convention

**⚠️ 重要：项目目录和模型缓存必须与技能名（slug）保持一致。**

---


## 汇报模板 | Report Template

汇报时必须包含以下全部内容（ID + 文字说明）：

```yaml
display_name: "Skill Name | 中文名"
slug: "skill-name"
platform: "clawhub" | "github"
current_version: "1.0.0"
new_version: "1.0.1"
file_size: "48KB"
changelog:
  - "EN description. 中文描述。"

checklist:
  # 通用质量基线
  G01 去标识化: ✅     # 无个人信息、内部路径、私有凭证
  G02 安全性: ✅        # 无注入风险、无过度权限、无数据外传
  G03 逻辑科学性: ✅    # 结构清晰、路径准确、模块化、同名规范
  G04 AI可读性: ✅     # agent可理解、上下文连贯、无歧义指令
  G05 易维护性: ✅      # 代码整洁、注释到位、变量命名清晰
  G06 依赖声明: ✅      # 外部包/工具/密钥已声明，无硬编码

  # ClawHub 专项
  CH01 name字段: ✅    # Display Name：EN Title | CN Title格式；name:字段填此处
  CH02 slug: ✅        # 小写字母+连字符，如speech-synthesizer
  CH03 坏符号链接: ✅  # 无失效符号链接
  CH04 运行时产物: ✅   # 无.pyc/.pyo/__pycache__/.log
  CH05 文件/模型分离: ✅  # 技能文件夹无模型/结果；模型在modules/；结果在projects/
  CH06 Embedding500: ✅ # 文档过长时有降级方案
  CH07 目录隔离: ✅    # 无.git/.DS_Store等无关文件
  CH08 版本号一致: ✅  # _meta.json/changelog/命令三处一致
  CH09 Changelog: ✅   # 英文在前，面向用户，双语列表
  CH10 Summary: ✅  # SKILL.md description → ClawHub Summary；先英文后中文，且中文不会被卡片截断
  CH11 表述顺序: ✅  # Display name / SKILL.md description(ClawHub Summary) / Changelog / README关键内容均先英文后中文

  # 或（有问题时）
  G03 逻辑科学性: ⚠️    # 路径引用待修复
  CH05 文件/模型分离: ⚠️  # 技能文件夹无模型/结果；模型在modules/；结果在projects/
```

**汇报示例：**
```yaml
display_name: "PDF 解析器 | PDF Parser"
slug: "pdf-parser"
platform: "clawhub"
current_version: "1.2.0"
new_version: "1.2.1"
file_size: "12.3 MB"
changelog:
  - "Fixed: OCR timeout on large files. 修复：大文件 OCR 超时问题。"

checklist:
  G01 去标识化: ✅
  G02 安全性: ✅
  G03 逻辑科学性: ✅
  G04 AI可读性: ✅
  G05 易维护性: ✅
  G06 依赖声明: ✅
  CH01 name字段: ✅
  CH02 slug: ✅
  CH03 坏符号链接: ✅
  CH04 运行时产物: ✅
  CH05 文件≤50MB: ✅
  CH06 Embedding500: ✅
  CH07 目录隔离: ✅
  CH08 版本号一致: ✅
  CH09 Changelog: ✅
  CH10 Summary: ✅
  CH11 表述顺序: ✅

publish_command: "clawhub publish ~/.openclaw/workspace/skills/pdf-parser --version 1.2.1 --changelog '...'"
```

---

## 实用说明 | Practical Notes

### 执行提示

- 执行敏感操作前，用 `clawhub --help` 核对当前 CLI 行为
- `skill-creator` 是底层规则权威来源
