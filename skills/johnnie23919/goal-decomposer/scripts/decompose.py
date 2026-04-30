#!/usr/bin/env python3
"""Goal Decomposer - 目标拆解器"""

import json
import sys
from typing import Dict, List

def decompose(goal: str, context: str = "") -> Dict:
    """拆解目标为任务树"""
    goal_type = classify_goal(goal)
    template = get_template(goal_type)
    tasks = fill_template(template, goal)
    
    return {
        "root_goal": goal,
        "goal_type": goal_type,
        "tasks": tasks,
        "execution_order": [t["id"] for t in tasks]
    }

def classify_goal(goal: str) -> str:
    """分类目标类型"""
    keywords = {
        "research": ["调研", "分析", "研究", "了解"],
        "create": ["开发", "创建", "生成", "制作", "写"],
        "manage": ["管理", "运营", "维护", "优化"]
    }
    goal_lower = goal.lower()
    for gtype, kws in keywords.items():
        if any(kw in goal_lower for kw in kws):
            return gtype
    return "general"

def get_template(goal_type: str) -> Dict:
    """获取拆解模板"""
    templates = {
        "research": {
            "structure": [
                {"title": "确定范围", "children": ["明确对象", "确定维度"]},
                {"title": "收集数据", "children": ["搜索信息", "整理数据"]},
                {"title": "分析总结", "children": ["提取关键", "输出结论"]}
            ]
        },
        "create": {
            "structure": [
                {"title": "明确需求", "children": ["功能定义", "约束确认"]},
                {"title": "设计方案", "children": ["原型设计", "评审确认"]},
                {"title": "执行实现", "children": ["编码制作", "测试验证"]}
            ]
        }
    }
    return templates.get(goal_type, templates["research"])

def fill_template(template: Dict, goal: str) -> List[Dict]:
    """填充模板"""
    tasks = []
    for i, item in enumerate(template["structure"], 1):
        task = {
            "id": f"T{i}",
            "title": item["title"],
            "priority": "P0" if i == 1 else "P1",
            "children": [
                {"id": f"T{i}.{j}", "title": c, "priority": "P1"}
                for j, c in enumerate(item["children"], 1)
            ]
        }
        tasks.append(task)
    return tasks

if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "测试目标"
    result = decompose(goal)
    print(json.dumps(result, ensure_ascii=False, indent=2))
