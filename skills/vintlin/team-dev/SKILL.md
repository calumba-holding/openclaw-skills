---
name: team-dev
description: Multi-agent development team orchestration. Use when managing coding agents (Codex, Claude Code, Gemini, Cursor) for automated software development: (1) Spawning agents for tasks, (2) Monitoring agent status, (3) Managing git worktrees, (4) Automated code review, (5) Handling notifications via Feishu.
---

# Team Dev

One-person dev team orchestration using Levi as the orchestrator.

## Quick Start

### 首次使用

```bash
# 运行设置检查
scripts/setup-check.sh
```

### Spawn an Agent

```bash
scripts/spawn-agent.sh \
  --agent codex \
  --repo my-repo \
  --branch fix/auth-error \
  --description "修复登录超时错误" \
  --prompt "在 src/auth.ts 中修复 token 过期后未刷新问题..."
```

### Check Agent Status

```bash
cat active-tasks.json
```

### Monitor Agents

```bash
scripts/check-agents.sh
```

---

## Supported Agents

| Agent | Use Case | Command |
|-------|----------|---------|
| **Codex** | 后端逻辑、复杂 bug、多文件重构 | `codex exec --dangerously-bypass-approvals-and-sandbox -C "/path" "prompt"` |
| **Claude Code** | 前端、git 操作、快速任务 | `claude --dangerously-skip-permissions -p "prompt"` |
| **Gemini** | UI 设计、生成规范 | `gemini -p "prompt"` 或 `gemini -y -p "prompt"` (YOLO 模式) |
| **Cursor** | 备用代理、IDE 集成 | `cursor agent -f -p --workspace "/path" "prompt"` |

---

## Scripts

### spawn-agent.sh

创建新任务并启动代理。

**参数：**
- `--agent` (必需): codex | claude | gemini | cursor
- `--repo` (必需): 仓库名
- `--branch` (必需): 分支名
- `--description` (必需): 任务描述
- `--prompt` (必需): 代理提示词

### check-agents.sh

监控所有运行中的代理。

**功能：**
- 检查 tmux 会话是否存活
- 检查 PR 是否已创建
- 失败自动重试 (最多3次)
- 写入通知到 `notifications.json` (由 OpenClaw 发送飞书通知)

### review-agent.sh

自动代码审查。

**参数：**
- `--repo` (必需): 仓库名
- `--branch` (必需): 分支名或 PR 号
- `--reviewers`: 审查者 (默认: codex,gemini)

### cleanup-worktrees.sh

清理已合并的 worktree。

### setup-check.sh

首次使用检查脚本，验证配置完整性。

---

## Task Registry

位置：`active-tasks.json` (skill 根目录)

---

## References

详细文档：

- **Prompt Templates**: [references/prompt-templates.md](references/prompt-templates.md)
- **初始化设置**: [references/initialization.md](references/initialization.md) - Cron 配置

---

## Interventions

### 发送消息到运行中的代理

```bash
tmux send-keys -t <session-name> "你的指令" Enter
```

### 停止代理

```bash
tmux kill-session -t <session-name>
```

---

## CLI Reference

### Codex
```bash
codex exec [OPTIONS] "prompt"
  --dangerously-bypass-approvals-and-sandbox
  -C, --cd <DIR>
```

### Claude Code
```bash
claude [OPTIONS] "prompt"
  --dangerously-skip-permissions
  -p, --print
```

### Gemini
```bash
gemini [OPTIONS] "prompt"
  -y, --yolo
```

### Cursor
```bash
cursor agent [OPTIONS] "prompt"
  -f, --force
  --workspace <path>
```

### tmux
```bash
tmux new-session -d -s <name> -c <dir> "command"
tmux send-keys -t <session> "text" Enter
tmux list-sessions
tmux kill-session -t <session>
```
