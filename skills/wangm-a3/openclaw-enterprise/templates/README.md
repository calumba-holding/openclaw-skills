# OpenClaw Enterprise 使用指南

## 快速开始

```python
from scripts.chief_of_staff import ask_chief
import asyncio

# 向幕僚长提问
result = asyncio.run(ask_chief("帮我分析库存情况"))
print(result)
```

## 命令行使用

```bash
# 单次查询
python scripts/chief_of_staff.py "帮我分析库存"

# 运行工作流
python scripts/workflow_engine.py "采购审批流程"
```

## 可用工作流

1. 采购审批流程 - 从需求分析到成本核算
2. 订单履约流程 - 从订单到发货
3. 客户服务流程 - 客户问题处理

## Agent列表

- 采购与供应链：原料采购、仓储管理、物流调度
- 生产与研发：生产调度、质量检测
- 销售与市场：报价、订单履约、客户管理
- 财务与合规：成本核算、风险预警
- 通用运营：数据分析、报告生成、客服支持
