# GitLab 审查工作流参考

glab CLI 命令速查表及常用操作模式。

---

## glab CLI 速查表

### MR 操作

```bash
# 列出已打开的 MR
glab mr list --state=opened

# 切换到 MR 分支（自动创建本地分支）
glab mr checkout <MR_ID>

# 查看 MR diff
glab mr diff <MR_ID>

# 批准 MR
glab mr approve <MR_ID>

# 关闭 MR
glab mr close <MR_ID>

# 查看 MR 详情
glab mr view <MR_ID>
```

### 发布评论

```bash
# 发布普通评论（出现在 Overview 标签页）
glab mr note <MR_ID> --message "审查意见..."

# 多行评论（使用 heredoc）
glab mr note <MR_ID> --message "$(cat <<'EOF'
## 审查摘要

**结论：** request_changes

发现 2 个安全问题需修复。
EOF
)"
```

### API 直接调用

```bash
# 获取 MR 信息
glab api projects/:id/merge_requests/<MR_ID>

# 获取 diff_refs（发布行内评论时需要）
glab api projects/:id/merge_requests/<MR_ID> --jq '.diff_refs'

# 发布行内评论（Diff Note）
glab api projects/:id/merge_requests/<MR_ID>/discussions \
  --method POST \
  -f body="问题描述" \
  -f "position[position_type]=text" \
  -f "position[base_sha]=<BASE_SHA>" \
  -f "position[start_sha]=<START_SHA>" \
  -f "position[head_sha]=<HEAD_SHA>" \
  -f "position[new_path]=src/example.py" \
  -f "position[new_line]=42"
```

---

## 行内评论格式规范

使用 `scripts/gitlab_inline_commenter.py` 发布行内评论时，建议遵循以下格式：

```
[严重程度图标] **问题标题**

**问题：** 一句话描述问题所在。

**风险：** 说明可能造成的影响。

**建议：** 具体的修改方案或代码示例。
```

严重程度图标对应：
- 🔴 critical — 必须修复，阻塞合并
- 🟠 high — 强烈建议修复
- 🟡 medium — 建议修复
- 🟢 low — 可选优化
- ❓ 待确认 — 置信度不足，以提问形式发出

---

## 整体摘要评论模板

```bash
glab mr note <MR_ID> --message "$(cat <<'EOF'
## 代码审查摘要

**复杂度：** X/10  **质量评分：** XX/100
**变更文件：** N  **新增行：** +XXX  **删除行：** -XX

| 级别 | 数量 |
|------|------|
| 🔴 严重 | N |
| 🟠 高危 | N |
| 🟡 中等 | N |
| 🟢 低危 | N |

**结论：** approve / request_changes / block

> 由 GitLab MR Reviewer 自动生成
EOF
)"
```

---

## 飞书 Webhook 消息格式

飞书机器人支持富文本卡片，`feishu_notifier.py` 自动构造以下结构：

```json
{
  "msg_type": "interactive",
  "card": {
    "header": { "title": { "content": "MR #42 审查完成", "tag": "plain_text" } },
    "elements": [
      { "tag": "div", "text": { "content": "**结论：** request_changes\n**评分：** 62/100", "tag": "lark_md" } },
      { "tag": "action", "actions": [{ "tag": "button", "text": { "content": "查看 MR", "tag": "plain_text" }, "url": "https://gitlab.example.com/..." }] }
    ]
  }
}
```

---

## 常见问题排查

| 问题 | 排查步骤 |
|------|---------|
| 行内评论发布失败 | 检查 `diff_refs` 是否正确；确认 `new_line` 是 diff 中实际存在的行号 |
| `glab mr checkout` 后 diff 为空 | 运行 `git diff origin/main...HEAD --stat` 确认分支切换成功 |
| 飞书消息发送失败 | 用 curl 直接测试 Webhook URL；检查 IP 白名单设置 |
| 评论重复发布 | 检查是否多次运行了 `gitlab_inline_commenter.py`；使用 `--dry-run` 先预览 |
