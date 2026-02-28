---
name: realmrouter-switch
description: Zero-friction RealmRouter model manager for OpenClaw. Chat-first workflow for setting API key, guided model picking, switching with precheck, rollback, connectivity testing, and short rr commands.
user-invocable: true
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - openclaw
      env:
        - REALMROUTER_API_KEY
    primaryEnv: REALMROUTER_API_KEY
    emoji: "🔁"
    install:
      - id: python3
        kind: brew
        formula: python
        label: Python 3
    os:
      - darwin
      - linux
      - win32
  version: 1.6.1
---

# RealmRouter Switch

> Chat-first model switching for OpenClaw.  
> 面向 OpenClaw 的对话式模型切换工具。

## ✅ P0/P1/P2 已增强（v1.6.1）

### P0
- 对话式“先列模型再选择”流程（支持编号选择）
- 模型别名映射（如 `opus`, `gpt53`, `qwen`, `r1`, `gemini`）
- key 在状态中仅掩码展示（避免明文泄露）

### P1
- **输入 key 时默认先鉴权（可用性验证）**
- **切换模型前默认鉴权该模型当前可用性**
- 失败可强制执行（`--force`）
- 新增一键回滚（`rollback`）
- 新增更短别名命令：`rr m`, `rr k`, `rr rb`

### P2
- 上架文案双语优化（便于商店转化）
- 推荐模型优先展示，降低选择成本

## Chat-first usage / 对话优先

直接说：
- “切换模型” → 我先发列表，你回复编号（如 `1`）或模型名
- “把 key 设为 xxx”
- “测试连通性”
- “回滚到上一个备份”

## Short commands / 短命令

```bash
rr pick                 # 列出编号模型
rr use 1                # 按编号切换（默认先验证模型可用性）
rr use gpt53            # 按别名切换
rr use gpt-5.3-codex    # 按模型名切换
rr k <KEY>              # 验证并更新 key
rr test                 # 连通性测试
rr show                 # 当前状态
rr rb                   # 回滚最近备份
```

如需安装 `rr`：

```bash
bash skills/realmrouter-switch/scripts/install_rr.sh
```

## Full script path / 完整脚本

`skills/realmrouter-switch/scripts/realm_manager.py`
