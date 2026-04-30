---
name: openclaw-collaboration
description: Hermes 与本地 OpenClaw 协同工作方案 — 共享记忆、API互调、任务分工
version: 1.0
created: 2026-04-19
---

# Hermes + OpenClaw 协同工作

## 环境信息

- OpenClaw: /usr/local/bin/openclaw (v2026.4.15)
- 配置: ~/.openclaw/openclaw.json
- Workspace: ~/.openclaw/workspace/
- Gateway: 端口 18789 (loopback), token 认证
- 可用模型: minimax-m2.5(主), z-ai/glm5, gemma-3-27b-it
- NVIDIA API: integrate.api.nvidia.com/v1

## 三种协同方式

### 1. 共享记忆

Hermes 直接读写 OpenClaw workspace 目录下的记忆文件。
- Hermes 写入时在条目末尾加 [Hermes] 标记
- 避免同时写同一文件: Hermes 写 projects/ 和 decisions/, OpenClaw 写每日日志

### 2. API 互调

```bash
# 给 OpenClaw 派任务
openclaw agent --agent main --message "任务描述" --json --timeout 60
# 指定 agent
openclaw agent --agent glm5 --message "任务" --json --timeout 60
# 投递回复到频道
openclaw agent --agent main --message "任务" --deliver --reply-channel feishu
# 本地模式
openclaw agent --local --agent main --message "任务" --json --timeout 30
```

注意: agent 命令可能因模型超时卡住, 优先用 minimax-m2.5, 设合理 timeout

### 3. 任务分工

- 达梦数据库/SQL → Hermes (有专项 skill)
- 飞书消息处理 → OpenClaw (原生集成)
- 快速问答 → Hermes (响应更快)
- 深度推理 → OpenClaw (可调 thinking level)
- 代码编写/文件整理 → 两者均可

## 配置修复踩坑

1. 拼写错误: includeDefaultMemor → includeDefaultMemory
2. 非法 key: memory.flush 不是合法配置项(旧版遗留), 需删除
3. 修复: 直接编辑 json 文件, 或 openclaw doctor --fix(可能卡住)

### NVIDIA API 模型 ID 格式

- OpenClaw 配置用: nvidia/z-ai/glm5 (带 provider 前缀)
- NVIDIA API 实际: z-ai/glm5 (无 provider 前缀)
- 调 API 时用无前缀版本

### GLM5 超时问题

- GLM5 在 NVIDIA API 上频繁超时(idle watchdog 触发)
- 表现: agent 命令无响应, err.log 报 timeout from=nvidia/z-ai/glm5
- 这是之前卡顿的根因
- 解决: 优先用 minimax-m2.5 作为主模型

## Gateway 运维

- 检查在线: 访问 localhost:18789/health
- 查进程: ps aux | grep openclaw-gateway
- 查错误日志: tail ~/.openclaw/logs/gateway.err.log
- 重启: kill 旧进程后 openclaw gateway --port 18789

## 待完善

- [ ] WebSocket 长连接实时通信
- [ ] Python 封装脚本简化 agent 调用
- [ ] 文件锁或写入协调避免冲突
