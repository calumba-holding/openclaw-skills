# Prompt Templates

预设的任务提示词模板。

## Bug Fix

```
在 {repo} 中修复以下问题：
{description}

相关文件：{files}
错误信息：{error_message}

请：
1. 分析问题根因
2. 编写修复代码
3. 确保通过现有测试
4. 如需新测试，一并编写
```

## Feature

```
在 {repo} 中实现新功能：{feature_name}

需求描述：{description}

请：
1. 先了解现有代码结构
2. 设计实现方案
3. 编写代码
4. 编写测试
5. 更新相关文档
```

## Refactor

```
在 {repo} 中重构 {target}：

重构目标：{goal}
约束条件：{constraints}

请：
1. 先理解现有代码
2. 确保重构后功能不变
3. 运行所有测试
4. 保持代码风格一致
```
