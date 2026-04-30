---
name: example-project
description: 示例项目 - 演示 skill 编排系统的使用
version: 1.0.0
---

# 示例项目设计编排指南

## 概述

这是一个示例项目，演示如何使用 skill 编排系统进行系统化开发。

## 工作流程

### 阶段 1: 需求分析

**使用的 Skills**:
- writing-plans

**任务**:
- 分析需求
- 编写用户故事
- 定义功能列表

**输出**:
- requirements.md
- user-stories.md
- features.md

### 阶段 2: 设计

**使用的 Skills**:
- huashu-design-integration

**任务**:
- 创建原型
- 设计评审
- 导出设计规范

**输出**:
- design/prototypes/
- docs/design-spec.md

### 阶段 3: 计划

**使用的 Skills**:
- writing-plans

**任务**:
- 编写实现计划
- 定义技术方案
- 制定测试策略

**输出**:
- IMPLEMENTATION.md
- docs/technical-design.md
- docs/test-plan.md

### 阶段 4: 开发

**使用的 Skills**:
- test-driven-development
- subagent-driven-development

**任务**:
- 编写测试
- 实现功能
- 代码审查

**输出**:
- src/
- tests/
- docs/code-review.md

### 阶段 5: 文档

**使用的 Skills**:
- obsidian

**任务**:
- 生成文档
- 保存到知识库
- 建立链接

**输出**:
- docs/
- wiki/

## 上下文传递

context:
  writing-plans:
    output: [requirements.md, IMPLEMENTATION.md]
    pass_to: test-driven-development
  
  test-driven-development:
    input: IMPLEMENTATION.md
    output: [tests/, src/]
    pass_to: github-code-review
  
  github-code-review:
    input: [tests/, src/]
    output: docs/code-review.md
    pass_to: obsidian

## 质量验证

validation:
  writing-plans:
    required_sections: [overview, implementation, testing]
    format: markdown
    max_length: 10000
  
  test-driven-development:
    test_coverage: 80
    test_style: pytest
  
  github-code-review:
    check_severity: high
    auto_fix: false

## 状态管理

state:
  checkpoints:
    - name: requirements_complete
      after: writing-plans
    - name: tests_complete
      after: test-driven-development
    - name: code_reviewed
      after: github-code-review
  
  auto_save: true
  save_interval: 300
