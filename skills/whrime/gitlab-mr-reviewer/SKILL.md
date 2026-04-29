---
name: "gitlab-mr-reviewer"
description: "当需要审核 GitLab 合并请求、检查 MR diff 风险、发布 GitLab 审查评论、执行 approve/request changes，或发送 MR 审查通知时使用。"
---

# GitLab MR Reviewer

GitLab MR 审查调度层技能。只定义触发条件、执行顺序、硬规则和失败回退；命令细节与长参考统一放到 `references/`。

## 适用场景

- 用户明确提到 GitLab MR 审查，例如：`审核 MR #42`、`检查合并请求 42`
- 需要对 MR 发布行内评论、总结评论、approve 或 request changes
- 需要在审查后发送飞书通知
- 需要对 MR 做静态分析或 AI 深审（在配置允许时）

## 不适用场景

- GitHub PR 审查（非 GitLab）
- 纯本地代码评审且用户明确不希望与 GitLab 交互
- 缺少最小配置且用户不希望先做初始化

## 执行前检查清单（Preflight）

执行前必须确认（配置优先从 `reviewer.config.json` 读取，其次才是环境变量）：

- 工具可用：`git`、`glab`、`python`
- 配置齐全：`gitlab.projectId`、`review.repoPath`、`gitlab.defaultBaseBranch`
- 主机格式一致：`gitlab.host` 统一使用主机名（例如 `gitlab.example.com`，不带协议）
- 已认证：`glab auth status` 可通过，或存在有效 `GITLAB_TOKEN`
- 当前任务目标明确：仅审查 / 审查并评论 / 审查并通知 / approve

缺少最小配置时，先停下并向用户追问，不得猜测 project id、host、repo path。

## 核心工作流

1. 同步仓库：进入 `REVIEW_REPO_PATH` 并执行 `git fetch --all --prune`
2. 切换 MR：优先 `glab mr checkout <MR_ID>`
3. 运行分析：执行 `scripts/mr_analyzer.py` 生成 JSON 结果
4. 生成结论：根据严重级别与置信度，得出 `approve` 或 `request_changes`
5. 发布评论：
   - 有有效文件与行号 -> `scripts/gitlab_inline_commenter.py`
   - 无法定位行号 -> 回退为 MR 总结评论
6. 需要通知时：执行 `scripts/feishu_notifier.py`

## 硬规则

- 永远先静态分析，再决定是否做 AI 深审
- 不泄露任何 secret（如 `GITLAB_TOKEN`、`FEISHU_WEBHOOK_URL`）
- `confidence < 0.6` 不下结论，改为提问式评论
- 单个问题只评论一次，避免重复刷屏
- 行号缺失或定位失败时，必须降级为 summary note
- 大 MR 优先审查高风险文件，不做无边界全量深审

## 失败回退顺序（必须按顺序）

1. `glab mr checkout` 失败 -> 检查 `glab version`、认证、host
2. 仍失败 -> 使用 `git fetch origin merge-requests/<MR_ID>/head:mr-<MR_ID>` + `git checkout`
3. `mr_analyzer.py` 显示无 diff -> 校验 base 分支与当前 HEAD
4. 行内评论发布失败 -> 回退到 MR 总结评论（Overview）
5. AI 上下文超限 -> 仅审查 `review_order` 前 N 个高风险文件
6. 证据不足 -> 停止断言并向作者提问

## 输出契约

- `mr_analyzer.py` 输出是后续评论/通知的事实来源
- 至少保证字段：`verdict`、`score`、`findings`、`severity_counts`
- `findings` 中 `file` 或 `line` 缺失时，不发送行内评论
- 审查结论只允许：`approve`、`request_changes`、`block`

## 最小示例

### 示例 1：审核 MR

输入：`审核 MR #42`

动作：preflight -> checkout -> analyzer -> 评论总结 -> 给出结论

### 示例 2：审核并通知

输入：`审核 MR #42 并通知飞书`

动作：示例 1 全流程 + `feishu_notifier.py`

### 示例 3：通过 MR

输入：`通过 MR #42`

动作：仅在无阻塞问题时执行 `glab mr approve 42`；否则改为 request changes 并解释原因

## 参考文档

- 运行配置：`reviewer.config.json`
- GitLab 命令与发布流程：`references/gitlab_review_workflow.md`
- 审查清单：`references/mr_review_checklist.md`
- AI 审查提示词：`references/review_prompts.md`
