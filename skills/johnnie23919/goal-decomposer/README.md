# Goal Decomposer

> 将自然语言目标拆解为可执行的任务树

## 特性

- ✅ **MECE原则**：任务互斥完全穷尽，不遗漏不重复
- ✅ **智能依赖识别**：自动识别任务间前置关系
- ✅ **优先级排序**：P0/P1/P2分级，聚焦关键路径
- ✅ **多场景适配**：产品规划、创业计划、学习计划等

## 安装

```bash
openclaw skill install goal-decomposer
```

## 快速开始

### 基础用法

```python
from skills.goal_decomposer import decompose

result = decompose("做一个AI写作工具")
print(result.task_tree)
```

### 带约束条件

```python
result = decompose(
    goal="开一家咖啡店",
    constraints=[
        "预算30万以内",
        "3个月内开业",
        "选址在商务区"
    ]
)
```

## 使用示例

### 示例1：产品规划
输入："做一个AI写作工具"

输出：
```
目标：开发AI写作工具
├─ T1: 市场调研 [P0]
│  ├─ 1.1 竞品分析（Notion AI, Jasper）
│  └─ 1.2 用户痛点收集
├─ T2: 产品设计 [P0]
│  ├─ 2.1 功能清单定义
│  └─ 2.2 交互原型设计
└─ T3: 技术实现 [P0]
   ├─ 3.1 架构选型
   └─ 3.2 MVP开发
```

### 示例2：创业计划
输入："开一家咖啡店"

输出：包含选址、装修、设备、团队、营销等8大模块的完整计划树

详见 [examples/example2_startup.md](examples/example2_startup.md)

### 示例3：学习计划
输入："准备研究生考试（计算机专业）"

输出：按科目、时间、阶段拆解的学习计划，含时间分配建议

详见 [examples/example3_study.md](examples/example3_study.md)

## 输出格式

```json
{
  "goal": "原始目标",
  "tasks": [
    {
      "id": "T1",
      "title": "任务标题",
      "priority": "P0",
      "estimate": "1周",
      "dependencies": [],
      "subtasks": [
        {
          "id": "T1.1",
          "title": "子任务标题",
          "executable": true
        }
      ]
    }
  ],
  "critical_path": ["T1", "T2", "T3"],
  "total_estimate": "6-8周"
}
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goal | string | ✅ | 自然语言目标描述 |
| context | string | ❌ | 背景信息 |
| constraints | array | ❌ | 约束条件列表 |
| max_depth | number | ❌ | 最大拆解深度（默认3） |
| include_estimate | boolean | ❌ | 是否包含时间估算（默认true） |

## 定价

- **免费试用**：3次拆解
- **首月优惠**：$15
- **正常价格**：$29/月
- **企业授权**：联系定价

## 竞品对比

| 技能 | 价格 | MECE | 依赖识别 | 迭代细化 |
|------|------|------|----------|----------|
| task-decomposer | $10 | ❌ | ❌ | ❌ |
| project-planner | $49 | ✅ | ✅ | ❌ |
| **goal-decomposer** | **$15** | **✅** | **✅** | **✅** |

## 技术原理

1. **目标解析**：NLP提取核心意图
2. **知识检索**：匹配行业最佳实践模板
3. **MECE验证**：确保任务完整性
4. **依赖推断**：基于前置关系构建DAG
5. **优先级排序**：关键路径算法

## 限制与边界

- 最大拆解深度：3层（避免过度拆解）
- 单次任务上限：50个子任务
- 支持语言：中文、英文
- 不支持场景：纯创意任务（如"写一部小说"）

## 更新日志

### v1.0.0 (2026-04-25)
- 首次发布
- 支持基础拆解功能
- 包含3个典型场景示例

## 支持

- Issue反馈：https://github.com/openclaw/skill-goal-decomposer/issues
- 使用文档：[SKILL.md](SKILL.md)
- 示例库：[examples/](examples/)

## License

MIT License

---

**作者**：筱龙虾 🦞  
**创造时间**：2026-04-25  
**最后更新**：2026-04-26
