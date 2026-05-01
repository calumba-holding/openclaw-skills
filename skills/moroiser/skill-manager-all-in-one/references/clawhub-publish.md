# ClawHub Publish Guide | ClawHub 发布指南

## Two-step publishing workflow | 两步发布工作流

**无论改动多小、无论第几次修改，两步验证不可跳过。**

### 第一步（AI 内部执行，不输出给用户）

**A. Run full checklist | 完整清单核对**
Verify all items in the "Skill creation/modification checklist" section of SKILL.md:
逐项核对 SKILL.md 中"技能制作/修改清单"的全部项目。

**A0. Runtime expectations declaration | 运行依赖声明**

Before publishing skills that guide command execution or filesystem changes, explicitly declare:
发布会指导命令执行或文件系统修改的技能前，必须明确声明：

These declarations must appear in SKILL.md frontmatter `metadata` where possible, not only in prose. Use single-line JSON metadata because the OpenClaw skill parser expects single-line frontmatter values.
这些声明应尽量写入 SKILL.md frontmatter `metadata`，不能只写在正文。OpenClaw 技能解析器要求 frontmatter 值使用单行 JSON。

- Required binaries and verification commands, e.g. `clawhub --help`, `git --version`, `gh --version`.
  所需命令行工具及验证命令，例如 `clawhub --help`、`git --version`、`gh --version`。
- Credential/authentication expectations, e.g. ClawHub login session, Git/GitHub credentials; never ask users to paste long-lived secrets into chat.
  凭据/授权预期，例如 ClawHub 登录态、Git/GitHub 凭据；不得要求用户在聊天中粘贴长期密钥。
- Filesystem write scope: skill source in `~/.openclaw/workspace/skills/<slug>/`, outputs in `~/.openclaw/workspace/projects/<slug>/`, models in `~/.cache/huggingface/modules/<slug>/`.
  文件系统写入范围：技能源码在 `skills/<slug>/`，输出在 `projects/<slug>/`，模型在 `modules/<slug>/`。
- Exact commands must be shown to the user before publishing, deleting, moving, pushing, or otherwise mutating external/local state.
  发布、删除、移动、推送或其他写入操作前，必须向用户展示精确命令。

**B. Security verification | 安全性检查**

⚠️ **If the skill contains scripts (Python/Bash/etc.), manually inspect each script:**
如果技能包含脚本，必须手动检查每个脚本：

| 风险类型 | 检查要点 | 高危模式 |
|---------|---------|---------|
| **Shell 注入** | `os.system()`, `subprocess.call(..., shell=True)`, `eval()` 用于无过滤的用户输入 | `os.system(f"arecord ... {filepath}")` |
| **Python 代码注入** | `exec()`/`eval()` 构建自用户/远程输入；`python3 -c` 内字符串插值 | `f"python3 -c '...{user_input}...'"` |
| **路径注入** | 文件路径与无过滤的用户/远程输入直接拼接 | `subprocess.run(f"convert {filename}")` |
| **日志/输出泄露** | API Key、Token、凭证出现在日志、报错、返回值中 | 凭证明文出现在错误信息中 |
| **依赖不完整** | 代码 import 的包未出现在 `requirements.txt` / `package.json` 中 | 代码 import `av`，requirements.txt 没有 |

**C. File size check | 文件大小检查**
```bash
du -sh <skill-dir>
```
If the directory **exceeds 50MB**, the upload will fail.
- Report to user immediately.
- Move oversized files (e.g., model files) to a workspace backup location. Wait for explicit user confirmation.
- After upload succeeds, move files back. Wait for user confirmation again.
如果目录**超过 50MB**，上传会失败。立即报告用户，等待明确指示后再操作。

**D. Public wording and ClawHub Summary check | 对外表述与 ClawHub Summary 检查**

All user-facing bilingual wording should use **English first, Chinese second**. This applies to display names, the SKILL.md frontmatter `description` field that ClawHub exposes as registry `summary` / CLI `Summary:`, changelog entries, README key headings, core explanations, and examples.
所有面向用户的双语表述统一使用 **先英文、后中文**。适用范围包括展示名、SKILL.md frontmatter `description` 字段（发布到 ClawHub 后是 registry `summary` / CLI `Summary:`）、changelog、README 关键标题、核心说明和示例。

ClawHub preview cards may truncate long summaries. Before publishing, inspect the SKILL.md frontmatter `description` as product copy:
ClawHub 预览卡片可能截断长简介。发布前把 SKILL.md frontmatter 的 `description` 当作产品卡片文案检查：

- Keep the English part short enough that the Chinese part remains visible before truncation.
  英文部分要足够短，确保中文在截断前仍可见。
- Use `English sentence. 中文句子。` for `description`, not Chinese-first ordering.
  `description` 使用 `English sentence. 中文句子。`，不要中文在前。
- Avoid local debugging details, personal names, or one-off test content in the summary.
  简介中不要放本地调试细节、真实姓名或一次性测试内容。

**E. Draft changelog | 拟定 changelog**

⚠️ **Changelog 不写在 SKILL.md 里！** Changelog 是 ClawHub 网站上的发布说明，在 `clawhub publish` 时通过 `--changelog` 参数传入。SKILL.md 模板中不应包含"更新日志"章节（除非是永久保留的完整更新历史）。

- English first, Chinese after.
  英文在前,中文在后。
- Formal release-note tone only.
  仅使用正式发布说明语气。

**Changelog format | changelog 格式：**
Changelog 内容通过 `--changelog "..."` 参数传递给 `clawhub publish` 命令，显示在 ClawHub 网站的版本历史中。格式为英文在前、中文在后的数字序号列表。

Use plain numbered list (1. 2. 3.) with English first, Chinese after for each point.
使用纯数字序号分点，每点英文在前、中文在后。

**Changelog template | 模板：**
```
1. [English update]. [中文更新]。
2. [English update]. [中文更新]。
3. [English update]. [中文更新]。
```

**Recommended examples | 推荐示例：**
```
1. Initial release. 首次发布。
```
```
1. Add comprehensive pre-publish checklist and two-step publishing workflow. 新增发布前检查清单和两步发布流程。
2. Consolidate naming/writing standards and changelog rules into SKILL.md body. 整合命名写作规范与changelog规则至SKILL.md正文。
```

**Strictly avoid | 严格禁止：**
- personal corrections / 个人纠错
- format-only adjustments / 格式调整
- private debugging notes / 私人调试记录
- jokes, self-deprecation, apology-style wording / 玩笑、自嘲、道歉式表述

### 第二步（输出给用户，等待明确确认）

Report the following to user. **⚠️ Do NOT run `clawhub publish` until user explicitly confirms.**
**发布类操作（clawhub publish / git push / gh release create / 推广发帖等）必须经过两步验证，不可跳过。**

| Item | 内容 |
|---|---|
| Skill name + slug | 准确拼写 |
| ClawHub current published version | 来自 `clawhub inspect <slug>` |
| New version number | 在已发布版本上递增 |
| Changelog | 完整英中文双语内容 |
| Primary update summary | 一句话概括 |
| File size | 是否超 50MB |
| De-identification | 确认通过/需调整 |
| Scientificity | 确认通过/需调整 |
| AI readability | 确认通过/需调整 |
| Contextual coherence | 确认通过/需调整 |
| Stability | 确认通过/需调整 |
| **Code security** | 确认通过/需调整（Shell注入/Python代码注入/路径注入/依赖完整性） |
| Public wording order | Display name / SKILL.md `description` (ClawHub `Summary:`) / Changelog / README key content all use English first, Chinese second |
| ClawHub Summary | SKILL.md `description` is short; published `Summary:` is bilingual and Chinese is not truncated in preview |
| Full publish command | `clawhub publish ...` |

**Restart rule | 重启规则：**
Each user modification request → restart from Step 1.
每次用户提出修改，都必须从第一步重新开始。

## CLI commands | CLI 命令

Prefer `clawhub` from PATH. If it is missing, try the OpenClaw-managed tool path before declaring the command unavailable:
优先使用 PATH 中的 `clawhub`。若不存在，先尝试 OpenClaw 托管工具路径，再判断命令不可用：

```bash
CLAWHUB_BIN=$(command -v clawhub || true)
if [ -z "$CLAWHUB_BIN" ] && [ -x "$HOME/.openclaw/tools/node/npm/bin/clawhub" ]; then
  CLAWHUB_BIN="$HOME/.openclaw/tools/node/npm/bin/clawhub"
fi
[ -n "$CLAWHUB_BIN" ] || { echo "clawhub command not found"; exit 1; }
```

```bash
# 发布：双语展示名必须显式传 --name，不能依赖 _meta.json 或 SKILL.md 自动同步
"$CLAWHUB_BIN" publish <path> \
  --slug <slug> \
  --name "EN Title | 中文标题" \
  --version <version> \
  --changelog "<text>"

# 管理
"$CLAWHUB_BIN" delete <slug> --yes
"$CLAWHUB_BIN" hide <slug> --yes
"$CLAWHUB_BIN" unhide <slug> --yes
"$CLAWHUB_BIN" undelete <slug> --yes
"$CLAWHUB_BIN" sync
```

### Display name rule | 展示名规则

ClawHub page titles are controlled by the published display-name field. For bilingual names, always set it in two places:
ClawHub 页面标题由发布记录里的 display-name 控制。双语名必须两处一致：

1. `SKILL.md` YAML frontmatter: `name: EN Title | 中文标题`
2. Publish command: `--name "EN Title | 中文标题"`

Do **not** rely on `_meta.json.displayName` or `SKILL.md` alone when updating an existing skill. In practice, version updates may keep the old English-only title unless `--name` is passed explicitly.
更新已有技能时，不要只依赖 `_meta.json.displayName` 或 `SKILL.md name:`。实测如果发布命令未显式传 `--name`，页面顶部可能继续保留旧的纯英文展示名。

### ClawHub Summary rule | ClawHub Summary 规则

The local source field is SKILL.md frontmatter `description`. After publishing, ClawHub stores/exposes it as registry `summary`, and the CLI prints it as `Summary:`. The ClawHub preview area is short: a long English-first description can still hide the Chinese part behind truncation. For bilingual skills, keep the English sentence compact, then put the Chinese sentence immediately after it:
本地源字段是 SKILL.md frontmatter `description`。发布后，ClawHub 将其作为 registry `summary` 暴露，CLI 打印为 `Summary:`。ClawHub 预览区域很短：即使英文在前，只要英文太长，中文仍可能被截断。双语技能应让英文短句在前，中文紧随其后：

```yaml
description: "TTS helper. TTS 朗读助手；支持文本转语音，长文本自动分段。"
```

After publishing, verify both `Latest:` and `Summary:` with `inspect` or the web page.
发布后同时复验 `Latest:` 和 `Summary:`，不要只看版本号。

## Post-publish scan pending | 发布后安全扫描等待

Immediately after publishing, `inspect` may report that the skill is hidden while the security scan is pending. Treat this as a temporary state, not a publish failure. Wait briefly and inspect again until the latest version and summary are visible.
发布后立即 `inspect` 可能提示安全扫描中、技能暂时隐藏。这是临时状态，不是发布失败。短暂等待后再次 inspect，直到能看到最新版本和摘要。

## Version conflict | 版本冲突

If publish fails with `Version already exists`, bump the version and republish only after confirming with the user.
如果发布失败并提示 `Version already exists`，应先与用户确认，再升版本号重新发布。

## 查看安全扫描结果 | View Security Scan Results

发布后查看完整 Assessment 步骤：

1. 打开 ClawHub 技能页面（如 `https://clawhub.ai/skills/<slug>`）
2. 找到 **Security Scan** 区域
3. 找到 **OpenClaw Benign/Suspicious** 徽章旁边的 **Details ▾** 按钮
4. **点击 Details ▾ 展开** 才能看到完整的 Assessment 内容
5. Assessment 是 ClawHub 对技能的详细安全分析，包含 Purpose、Install Mechanism、Credentials 等项目的逐一评估

⚠️ **注意**：Summary 只是一句话概括，**必须展开 Details 才能看到完整 Assessment**。
