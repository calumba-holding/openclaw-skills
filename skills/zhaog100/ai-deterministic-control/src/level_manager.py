# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
LevelManager — 确定性等级管理器
L0(完全随机) → L1(轻度) → L2(中度) → L3(高度) → L4(极度)
"""

from typing import Dict, List, Optional


# Level definitions: temp, top_p, use_seed, use_template, strategy
LEVEL_CONFIGS: Dict[str, Dict] = {
    "L0": {
        "name": "完全随机",
        "temperature": 1.0,
        "top_p": 1.0,
        "use_seed": False,
        "use_template": False,
        "strategy": "none",
        "description": "无任何确定性控制，完全自由输出",
    },
    "L1": {
        "name": "轻度",
        "temperature": 0.7,
        "top_p": 0.95,
        "use_seed": False,
        "use_template": False,
        "strategy": "single",
        "description": "仅降低温度，适合需要一定创意但要求一致的场景",
    },
    "L2": {
        "name": "中度",
        "temperature": 0.3,
        "top_p": 0.9,
        "use_seed": True,
        "use_template": False,
        "strategy": "seed",
        "description": "固定种子+低温度，适合代码生成等任务",
    },
    "L3": {
        "name": "高度",
        "temperature": 0.1,
        "top_p": 0.8,
        "use_seed": True,
        "use_template": True,
        "strategy": "seed+prompt",
        "description": "种子+模板+低温度，适合配置生成等精确任务",
    },
    "L4": {
        "name": "极度",
        "temperature": 0.0,
        "top_p": 0.5,
        "use_seed": True,
        "use_template": True,
        "strategy": "seed+prompt+vote",
        "description": "最高确定性：种子+模板+多数投票，适合翻译等严格任务",
    },
}

# Task type → recommended level mapping
TASK_LEVEL_HINTS: Dict[str, str] = {
    "code": "L2",
    "代码": "L2",
    "config": "L3",
    "配置": "L3",
    "translation": "L4",
    "翻译": "L4",
    "creative": "L1",
    "创意": "L1",
    "写作": "L1",
    "analysis": "L2",
    "分析": "L2",
    "conversation": "L1",
    "对话": "L1",
    "chat": "L1",
}


def get_level_config(level: str) -> Dict:
    """获取指定等级的完整参数组合

    Args:
        level: 等级标识 (L0-L4)
    Returns:
        完整参数配置 dict
    """
    level = level.upper()
    if level not in LEVEL_CONFIGS:
        raise ValueError(f"未知等级 '{level}'，有效值: {list(LEVEL_CONFIGS.keys())}")
    config = LEVEL_CONFIGS[level].copy()
    config["level"] = level
    return config


def auto_detect_level(task_description: str) -> str:
    """根据任务描述自动推荐等级

    Args:
        task_description: 任务描述文本
    Returns:
        推荐等级 (L0-L4)
    """
    desc_lower = task_description.lower()

    # 关键词匹配，取最高匹配等级
    best_level = "L1"  # 默认轻度
    for keyword, hint_level in TASK_LEVEL_HINTS.items():
        if keyword in desc_lower:
            # 取数值最大的
            if int(hint_level[1]) > int(best_level[1]):
                best_level = hint_level

    return best_level


def list_levels() -> List[Dict]:
    """列出所有等级及其配置概要"""
    result = []
    for k in sorted(LEVEL_CONFIGS.keys()):
        cfg = LEVEL_CONFIGS[k]
        result.append({
            "level": k,
            "name": cfg["name"],
            "temperature": cfg["temperature"],
            "top_p": cfg["top_p"],
            "strategy": cfg["strategy"],
            "description": cfg["description"],
        })
    return result
