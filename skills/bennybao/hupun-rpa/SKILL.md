---
name: hupun-rpa
description: 湖畔 RPA 机器人管理。通过 MCP 协议连接本地 RPA 客户端，控制机器人执行、取消任务、查看状态等操作。当用户提到"机器人"、"RPA"、"执行机器人"、"查询任务"等时自动激活。
argument-hint: <操作指令> 或 "状态"/"帮助"
thinking_mode: none
---

# 湖畔 RPA 管理技能

本技能通过 MCP 协议与本地 RPA 客户端通信，提供机器人管理、任务控制等功能。

## 连接信息

- MCP 服务地址：`http://127.0.0.1:13765/mcp`
- 默认端口：13765（可在 RPA 设置中修改）

## 可用操作

### 1. list_robots - 列出所有机器人

列出当前系统中所有机器人及其状态。

**参数**：无

**返回**：机器人列表，包含 ID、定义ID、启用状态、冻结状态、最近任务信息

---

### 2. list_robot_defs - 列出所有机器人类型

列出所有支持的机器人类型基本信息。

**参数**：无

**返回**：机器人类型列表，包含 ID、名称、描述、图标、账号类型、平台标识

**账号类型 (accountType)**：
- `ali` - 阿里系（淘宝、天猫）
- `pdd` - 拼多多

**平台标识 (platformKey)**：
- `0` - 淘宝
- `28` - 拼多多
- `1000` - 天猫

**使用示例**：说"查看有哪些机器人类型"或"列出机器人类型"

---

### 3. list_tasks - 查询任务列表

查询指定日期的任务执行记录。

**参数**：
- `date`（可选）：日期，格式 `YYYY-MM-DD`，不传则查询当天

---

### 4. execute_robot - 执行机器人

触发机器人执行，支持多种指定方式。

**参数**：
- `robotId`：机器人ID，支持以下格式：
  - **字符串**：单个机器人ID，如 `"robot-abc123"`
  - **数组**：多个ID，如 `["robot-abc", "robot-def"]`
  - **过滤条件对象**：根据条件筛选
    - `lastExecuteStatus`：最后执行状态
    - `lastExecuteTime`：最后执行时间，可设为 `"today"`
    - `robotType`：机器人类型ID
    - `enabled`：是否启用

**示例**：
```
触发所有启用的机器人：enabled: true
触发今天未执行过的机器人：lastExecuteTime: "today"
触发特定类型的机器人：robotType: "ali Mama"
```

---

### 5. cancel_task - 取消任务

取消正在等待或运行中的任务。

**参数**：
- `taskId`：任务ID，支持字符串、数组或过滤条件
  - 过滤条件：`robotType` - 按机器人类型筛选

---

### 6. relaunch - 重启应用

重启 RPA 客户端应用。正在执行的任务会被取消。

**参数**：无

---

### 7. check_update - 检查更新

检查应用是否有新版本。

**参数**：无

---

### 8. logout - 登出账号

登出当前登录的账号。

**参数**：无

---

### 9. send_notification - 发送通知

通过 RPA 客户端发送系统通知。

**参数**：
- `title`（必填）：通知标题
- `content`（可选）：通知内容

---

### 10. set_top_notification - 设置顶部通知

在 RPA 客户端顶部显示通知栏消息。

**参数**：
- `message`（必填）：通知消息，传空字符串可清除
- `duration`（可选）：显示时长（秒），不传则持续显示

---

### 11. reinstall_browser - 重装 Chrome

重新下载安装 Chrome 浏览器。正在执行的任务会被取消。

**参数**：无

### 12. daily_briefing - 今日简要

生成当日 RPA 任务执行情况摘要。返回 JSON 格式数据，本 Skill 负责格式化为 Markdown 展示。

**参数**：无

**返回 JSON 格式**：
```json
{
  "date": "2026-04-24",
  "stats": {
    "succeed": 8,
    "failed": 2,
    "running": 1
  },
  "details": {
    "succeed": [{ "name": "阿里妈妈账单", "count": 3 }],
    "failed": [{ "name": "拼多多账单", "count": 1, "reason": "Cookie失效" }],
    "running": [{ "name": "淘宝订单同步", "startTime": "15:30" }]
  },
  "comparison": {
    "totalChange": 2,
    "successRateChange": 5
  },
  "mainFailureReason": { "reason": "Cookie失效", "percent": 50 }
}
```

**字段说明**：
- `stats` - 执行统计（成功/失败/运行中数量）
- `details` - 按机器人类型分组的执行详情
- `comparison` - 环比昨日（仅当机器人类型数 >=10 且昨日任务数 >=10 时存在）
- `mainFailureReason` - 主要失败类型及占比（仅当有失败任务时存在）

## JSON 转 Markdown 格式规则

当用户问"今日简要"时，调用 `daily_briefing` 获取 JSON 数据，格式化为 Markdown：

```markdown
# 📊 今日 RPA 简要 (${date})

## 📈 执行统计
| 状态 | 数量 |
|------|------|
| ✅ 成功 | ${stats.succeed} |
| ❌ 失败 | ${stats.failed} |
| 🔄 运行中 | ${stats.running} |

## 🤖 执行详情

### ✅ 成功
${details.succeed.map(x => `- ${x.name} x${x.count}`).join('\n')}

### ❌ 失败
${details.failed.map(x => `- ${x.name} x${x.count} → ${x.reason}`).join('\n')}

## 📉 环比昨日
| 对比 | 变化 |
|------|------|
| 总任务 | ${totalChange >= 0 ? '+' : ''}${totalChange} (${todayTotal}→${yesterdayTotal}) |
| 成功率 | ${successRateChange >= 0 ? '+' : ''}${successRateChange}% |

> ⚠️ 主要失败类型：${mainFailureReason.reason} (${mainFailureReason.percent}%)
```

**失败归类规则**：
| 归类 | 关键词 |
|------|--------|
| Cookie失效 | Cookie、登录失效、登录失败 |
| 网络超时 | 超时、timeout、网络错误、请求失败 |
| 页面异常 | 页面加载、元素未找到、DOM |
| 脚本错误 | execute、script、脚本错误 |
| 系统错误 | 系统错误、内存不足、磁盘空间 |
| 用户取消 | 取消、cancelled |

---

## 使用示例

### 查询所有机器人状态

直接说"查看机器人状态"或"列出所有机器人"

### 查看支持的机器人类型

说"查看有哪些机器人类型"或"列出机器人类型"

### 执行特定机器人

说"执行机器人 xxx"或"触发机器人 robot-abc123"

### 按条件执行

- "执行所有启用的机器人" → `execute_robot` with `{ enabled: true }`
- "执行今天未执行的机器人" → `execute_robot` with `{ lastExecuteTime: "today" }`
- "执行阿里妈妈机器人" → `execute_robot` with `{ robotType: "ali Mama" }`

### 查询任务

- "查看今天的任务" → `list_tasks`（无参数）
- "查看昨天的任务" → `list_tasks` with `{ date: "2026-04-23" }`

### 取消任务

- "取消任务 xxx" → `cancel_task` with `{ taskId: "xxx" }`
- "取消所有运行中的任务" → `cancel_task` with `{ taskId: { robotType: "xxx" } }`

### 应用控制

- "重启 RPA" → `relaunch`
- "检查更新" → `check_update`
- "退出登录" → `logout`

### 通知功能

- "发送通知测试" → `send_notification` with `{ title: "测试通知", content: "这是一条测试消息" }`
- "显示顶部提示" → `set_top_notification` with `{ message: "你好", duration: 5 }`

---

## 注意事项

1. **执行机器人前**：建议先查看机器人状态，确认机器人已启用且未在执行中
2. **取消任务**：只能取消等待中或运行中的任务，已完成的任务无法取消
3. **批量操作**：支持同时对多个机器人/任务进行操作
4. **连接失败**：如果 MCP 连接失败，请检查 RPA 客户端是否正在运行
