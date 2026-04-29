# hupun-rpa

湖畔 RPA 管理 Skill。通过 AI 对话连接本地 RPA 客户端，完成机器人查看、任务执行、任务取消、状态查询，以及生成每日任务简报等操作。

## 适合用来做什么

- 查看当前有哪些机器人，以及各自状态
- 按机器人 ID、机器人类型或筛选条件触发执行
- 查询指定日期的任务记录
- 取消等待中或执行中的任务
- 在对话里生成“今日 RPA 简要”报告
- 执行一些客户端级操作，如重启应用、检查更新、发送通知

## 前置条件

使用前请确认本机已安装并运行湖畔 RPA 客户端，并且客户端 MCP 服务可访问：

- MCP 地址：`http://127.0.0.1:13765/mcp`
- 默认端口：`13765`

如果你的 RPA 客户端修改过端口，请先在客户端里确认实际配置。

## 安装

```bash
npx skills install https://github.com/hupun-public/hupun-rpa.git
```

支持能够加载 Skill 的 AI Agent。安装完成后，Agent 可按技能名显式激活，或在识别到“机器人”“RPA”“执行机器人”“查询任务”等意图时自动启用。

## 激活

在支持 Slash Command 的 AI Agent 中，可以直接输入：

```text
/hupun-rpa
```

如果你的 Agent 支持意图自动激活，也可以直接说：

- 查看机器人状态
- 列出机器人类型
- 执行阿里妈妈机器人
- 查看今天的任务
- 今日 RPA 简要

## 常见用法

### 1. 查看机器人

```text
查看机器人状态
列出所有机器人
```

### 2. 查看机器人类型

```text
查看有哪些机器人类型
列出机器人类型
```

### 3. 执行机器人

```text
执行机器人 robot-abc123
执行所有启用的机器人
执行今天未执行的机器人
执行阿里妈妈机器人
```

### 4. 查询任务

```text
查看今天的任务
查看昨天的任务
```

### 5. 取消任务

```text
取消任务 task-xxx
取消所有运行中的任务
```

### 6. 生成日报

```text
今日简要
今日 RPA 运行情况如何
```

Skill 会调用 `daily_briefing` 获取结构化数据，并整理成更适合阅读的 Markdown 摘要。

## 当前支持的操作

- `list_robots`：列出所有机器人
- `list_robot_defs`：列出所有机器人类型
- `list_tasks`：查询任务列表
- `execute_robot`：执行机器人
- `cancel_task`：取消任务
- `relaunch`：重启 RPA 客户端
- `check_update`：检查更新
- `logout`：登出账号
- `send_notification`：发送系统通知
- `set_top_notification`：设置顶部通知
- `reinstall_browser`：重装 Chrome
- `daily_briefing`：生成当日任务摘要

## 说明与边界

- 本 Skill 依赖本地 RPA 客户端提供的 MCP 接口，不直接管理云端服务。
- `relaunch` 和 `reinstall_browser` 可能会中断正在执行的任务，使用前应有明确预期。
- 任务筛选、机器人类型和返回字段以当前客户端实际能力为准。

## 仓库内容

当前仓库以技能定义文件为主：

- `SKILL.md`：技能描述、可用操作、参数说明与格式化规则
- `README.md`：面向使用者的快速说明
