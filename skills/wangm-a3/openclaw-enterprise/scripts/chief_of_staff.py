#!/usr/bin/env python3
"""OpenClaw Enterprise - 幕僚长调度器"""

import os
import json
import asyncio
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class AgentTask:
    task_id: str
    agent_name: str
    instruction: str
    context: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Optional[Dict] = None

@dataclass
class AgentDefinition:
    name: str
    category: str
    keywords: List[str]
    description: str
    capabilities: List[str]

class ChiefOfStaff:
    """幕僚长 - 负责理解用户意图、调度Agent、聚合结果"""
    
    def __init__(self, api_key: str = None, provider: str = "openai"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.provider = provider
        self.agents: Dict[str, AgentDefinition] = {}
        self.task_history: List[AgentTask] = []
        self._load_agents()
    
    def _load_agents(self):
        """加载所有Agent定义"""
        agents_config = [
            ("原料采购Agent", "procurement", ["原料", "供应商", "行情", "比价", "采购"], "负责供应商匹配、行情分析、采购下单", ["供应商比价", "行情分析"]),
            ("仓储管理Agent", "procurement", ["库存", "库位", "仓储", "备货"], "负责库存预警、库位优化", ["实时库存监控", "安全库存计算"]),
            ("物流调度Agent", "procurement", ["物流", "车队", "运输", "发货"], "负责车队匹配、路线优化", ["车队调度", "路线规划"]),
            ("生产调度Agent", "production", ["排产", "工单", "交期", "产能"], "负责排产、工单管理", ["智能排产", "工单管理"]),
            ("质量检测Agent", "production", ["质量", "检测", "合格率", "质检"], "负责质量检测", ["质量检测", "合格率统计"]),
            ("报价Agent", "sales", ["报价", "价格", "定价", "询价"], "负责快速报价", ["快速报价", "成本计算"]),
            ("订单履约Agent", "sales", ["订单", "发货", "履约", "跟踪"], "负责订单跟踪", ["订单跟踪", "异常预警"]),
            ("客户管理Agent", "sales", ["客户", "跟进", "复购", "CRM"], "负责客户管理", ["客户分级", "复购分析"]),
            ("成本核算Agent", "finance", ["成本", "毛利", "利润", "核算"], "负责成本核算", ["成本核算", "毛利分析"]),
            ("风险预警Agent", "finance", ["风控", "预警", "信用", "风险"], "负责风险预警", ["信用评估", "风险预警"]),
            ("数据分析Agent", "operations", ["数据", "报表", "月报", "分析"], "负责数据分析", ["数据汇总", "报表生成"]),
            ("报告生成Agent", "operations", ["报告", "会议", "文档", "纪要"], "负责报告生成", ["文档生成", "会议纪要"]),
            ("客服支持Agent", "operations", ["售后", "投诉", "客服", "支持"], "负责客服支持", ["问题解答", "投诉处理"]),
        ]
        
        for name, cat, kw, desc, caps in agents_config:
            self.agents[name] = AgentDefinition(name=name, category=cat, keywords=kw, description=desc, capabilities=caps)
    
    def route_task(self, user_input: str) -> List[str]:
        """路由任务到合适的Agent"""
        matched = []
        for name, agent in self.agents.items():
            for kw in agent.keywords:
                if kw in user_input and name not in matched:
                    matched.append(name)
                    break
        return matched if matched else ["数据分析Agent"]
    
    async def dispatch_to_agent(self, agent_name: str, task: AgentTask) -> Dict:
        """分发任务到Agent"""
        agent = self.agents.get(agent_name)
        if not agent:
            return {"error": f"Agent {agent_name} not found"}
        
        # 模拟执行（真实环境需要API Key）
        return {
            "agent": agent_name,
            "category": agent.category,
            "task": task.instruction,
            "status": "completed",
            "message": f"{agent_name}已处理任务",
            "capabilities": agent.capabilities
        }
    
    async def process_request(self, user_input: str) -> Dict:
        """处理用户请求"""
        matched = self.route_task(user_input)
        
        tasks = [AgentTask(
            task_id=f"task_{i}_{datetime.now().strftime('%H%M%S')}",
            agent_name=agent,
            instruction=user_input
        ) for i, agent in enumerate(matched[:3])]
        
        results = await asyncio.gather(*[
            self.dispatch_to_agent(agent, task)
            for agent, task in [(t.agent_name, t) for t in tasks]
        ])
        
        return {
            "chief_of_staff": "ChiefOfStaff",
            "user_input": user_input,
            "matched_agents": matched,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

async def ask_chief(user_input: str) -> Dict:
    chief = ChiefOfStaff()
    return await chief.process_request(user_input)

if __name__ == "__main__":
    import sys
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "帮我分析库存"
    result = asyncio.run(ask_chief(user_input))
    print(json.dumps(result, ensure_ascii=False, indent=2))
