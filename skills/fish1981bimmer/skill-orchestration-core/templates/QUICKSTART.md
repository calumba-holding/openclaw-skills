# Skill 编排核心 - 快速开始指南

欢迎使用 Skill 编排核心！这个指南将帮助你快速上手并开始使用。

## 5 分钟快速开始

### 步骤 1: 创建项目

```bash
# 创建项目目录
mkdir my-project
cd my-project

# 复制示例 DESIGN.md
cp ~/.hermes/skills/devops/skill-orchestration-core/templates/example-project/DESIGN.md .
```

### 步骤 2: 查看示例

```bash
# 查看示例 DESIGN.md
cat DESIGN.md
```

### 步骤 3: 解析流程

```bash
# 解析 DESIGN.md
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js parse DESIGN.md
```

### 步骤 4: 初始化上下文

```bash
# 初始化上下文
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js save
```

### 步骤 5: 加载验证规则

```bash
# 从 DESIGN.md 加载验证规则
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/output-validator.js load-design DESIGN.md
```

## 下一步

### 修改 DESIGN.md

根据你的项目需求修改 DESIGN.md 文件：

```yaml
---
name: my-project
description: 我的项目描述
version: 1.0.0
---

# 项目设计编排指南

## 工作流程

### 阶段 1: 需求分析

**使用的 Skills**:
- writing-plans

**任务**:
- 分析需求
- 编写用户故事

**输出**:
- requirements.md
- user-stories.md
```

### 使用上下文管理

```bash
# 设置数据
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js set requirements '{"title":"My Requirements"}'

# 获取数据
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js get requirements

# 查看上下文
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js show
```

### 使用流程编排

```bash
# 解析 DESIGN.md
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js parse DESIGN.md

# 查看状态
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js status DESIGN.md

# 查看进度
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js progress DESIGN.md
```

### 使用质量验证

```bash
# 验证输出
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/output-validator.js validate writing-plans "$(cat IMPLEMENTATION.md)"

# 获取验证报告
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/output-validator.js report
```

## 常用命令

### 上下文管理

```bash
# 查看上下文
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js show

# 保存上下文
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js save

# 加载上下文
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js load

# 清理上下文
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js clear

# 获取值
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js get <key>

# 设置值
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js set <key> <value>
```

### 流程编排

```bash
# 解析 DESIGN.md
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js parse DESIGN.md

# 查看状态
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js status DESIGN.md

# 查看进度
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js progress DESIGN.md

# 设置检查点
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js checkpoint DESIGN.md <name>

# 恢复检查点
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js restore DESIGN.md <name>

# 列出检查点
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js checkpoints DESIGN.md
```

### 质量验证

```bash
# 从 DESIGN.md 加载验证规则
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/output-validator.js load-design DESIGN.md

# 验证输出
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/output-validator.js validate <skill> <output>

# 获取验证报告
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/output-validator.js report
```

## 项目结构

```
my-project/
├── DESIGN.md                          # 设计编排指南
├── .orchestration/                   # 编排系统目录
│   ├── context.json                  # 上下文文件
│   ├── state.json                    # 状态文件
│   └── checkpoints/                  # 检查点
│       ├── checkpoint-001.json
│       └── checkpoint-002.json
├── requirements.md                   # 需求文档
├── IMPLEMENTATION.md                 # 实现计划
├── src/                              # 源代码
├── tests/                            # 测试
└── docs/                             # 文档
```

## 示例项目

### 简单项目

参见 `templates/example-project/` 目录中的示例项目。

### 复杂项目

参见 `templates/complex-project/` 目录中的复杂项目示例。

## 下一步学习

- 阅读 [README.md](templates/README.md) 了解更多详细信息
- 查看 [SKILL.md](../SKILL.md) 了解完整的 API 文档
- 查看 [examples/](../examples/) 目录中的更多示例

## 获取帮助

如果遇到问题：

1. 查看 [常见问题](../SKILL.md#常见问题)
2. 查看 [示例项目](../templates/example-project/)
3. 查看 [最佳实践](../SKILL.md#最佳实践)

## 贡献

欢迎贡献改进建议和最佳实践！

## 许可证

MIT
