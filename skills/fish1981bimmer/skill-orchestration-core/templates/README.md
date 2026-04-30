# Skill 编排核心

轻量级的 skill 编排系统，专注于上下文管理、流程编排和质量保证。

## 快速开始

### 1. 创建项目

```bash
# 创建项目目录
mkdir my-project
cd my-project

# 复制示例 DESIGN.md
cp ~/.hermes/skills/devops/skill-orchestration-core/templates/example-project/DESIGN.md .
```

### 2. 修改 DESIGN.md

根据你的项目需求修改 DESIGN.md 文件。

### 3. 执行流程

```bash
# 使用上下文管理器
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js show

# 使用流程编排器
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js parse DESIGN.md

# 使用输出验证器
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/output-validator.js load-design DESIGN.md
```

## 核心功能

### 1. 上下文管理

管理 skill 之间的上下文传递和共享。

```javascript
const ContextManager = require('./scripts/context-manager.js');

const context = new ContextManager('/path/to/project');

// 保存数据
context.set('plan', planContent);

// 获取数据
const plan = context.get('plan');

// 传递给下一个 skill
context.passTo('test-driven-development');

// 保存到文件
context.save();
```

### 2. 流程编排

基于 DESIGN.md 的流程编排。

```javascript
const WorkflowOrchestrator = require('./scripts/workflow-orchestrator.js');

const orchestrator = new WorkflowOrchestrator('/path/to/DESIGN.md');

// 执行流程
await orchestrator.execute();

// 暂停
orchestrator.pause();

// 恢复
await orchestrator.resume();

// 获取状态
const status = orchestrator.getStatus();
```

### 3. 质量保证

自动验证 skill 输出质量。

```javascript
const OutputValidator = require('./scripts/output-validator.js');

const validator = new OutputValidator();

// 添加验证规则
validator.addRule('writing-plans', {
  requiredSections: ['overview', 'implementation', 'testing'],
  format: 'markdown',
  maxLength: 10000
});

// 验证输出
const result = await validator.validate('writing-plans', output);

if (!result.valid) {
  console.error('验证失败:', result.errors);
}
```

## 项目结构

```
project/
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

## 使用示例

### 示例 1: 简单项目

```bash
# 创建项目
mkdir simple-project
cd simple-project

# 创建 DESIGN.md
cat > DESIGN.md << 'EOF'
---
name: simple-project
description: 简单项目示例
version: 1.0.0
---

# 项目设计编排指南

## 工作流程

### 阶段 1: 计划

**使用的 Skills**:
- writing-plans

**任务**:
- 编写实现计划

**输出**:
- IMPLEMENTATION.md
EOF

# 解析 DESIGN.md
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/workflow-orchestrator.js parse DESIGN.md
```

### 示例 2: 上下文管理

```bash
# 初始化上下文
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js save

# 设置数据
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js set plan '{"title":"My Plan"}'

# 获取数据
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js get plan

# 查看上下文
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/context-manager.js show
```

### 示例 3: 质量验证

```bash
# 从 DESIGN.md 加载验证规则
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/output-validator.js load-design DESIGN.md

# 验证输出
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/output-validator.js validate writing-plans "$(cat IMPLEMENTATION.md)"

# 获取验证报告
node ~/.hermes/skills/devops/skill-orchestration-core/scripts/output-validator.js report
```

## 最佳实践

### 1. 上下文管理

- 只传递必要的数据
- 使用有意义的键名
- 定期清理不需要的数据

### 2. 流程编排

- 明确每个阶段的输入输出
- 合理设置检查点
- 使用自动保存

### 3. 质量验证

- 设置合理的验证规则
- 不要过于严格
- 利用自动修复功能

## 常见问题

### Q: 上下文太大怎么办？

A: 使用上下文压缩：

```javascript
context.config.contextCompression = true;
context.config.maxContextSize = 50000;
```

### Q: 如何处理长时间运行的项目？

A: 使用检查点：

```yaml
state:
  checkpoints:
    - name: requirements_complete
      after: writing-plans
  auto_save: true
  save_interval: 300
```

### Q: 如何验证输出质量？

A: 使用质量验证：

```javascript
const validator = new OutputValidator();
const result = await validator.validate('writing-plans', output);

if (!result.valid) {
  console.error('验证失败:', result.errors);
}
```

## 贡献

欢迎贡献改进建议和最佳实践！

## 许可证

MIT
