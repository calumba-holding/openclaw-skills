# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
PromptTemplates — 确定性 Prompt 模板管理
"""

from typing import Dict, Optional

# Base template: injected into all task types
BASE_TEMPLATE = """\
请严格按照要求作答，不要添加额外内容或发散。
保持回答的确定性和一致性，避免模糊表述。
"""

# Task-specific templates
TEMPLATES: Dict[str, str] = {
    "code_generation": (
        BASE_TEMPLATE +
        "\n生成代码时：\n"
        "- 使用确定的实现方式，不提供替代方案\n"
        "- 代码格式一致，命名规范统一\n"
        "- 不添加注释解释除非明确要求\n"
    ),
    "config": (
        BASE_TEMPLATE +
        "\n生成配置时：\n"
        "- 严格按指定格式输出\n"
        "- 不添加注释或说明\n"
        "- 值类型精确匹配要求\n"
    ),
    "conversation": (
        BASE_TEMPLATE +
        "\n对话回复时：\n"
        "- 回答简洁直接\n"
        "- 不使用语气词或填充词\n"
        "- 保持一致的语气风格\n"
    ),
    "creative": (
        BASE_TEMPLATE +
        "\n创意写作时：\n"
        "- 遵循指定的风格和结构\n"
        "- 使用一致的叙事手法\n"
        "- 避免随意发挥\n"
    ),
    "analysis": (
        BASE_TEMPLATE +
        "\n分析任务时：\n"
        "- 基于提供的数据和事实\n"
        "- 分析步骤固定、逻辑清晰\n"
        "- 结论明确，不含模棱两可的表述\n"
    ),
    "translation": (
        BASE_TEMPLATE +
        "\n翻译任务时：\n"
        "- 忠实原文，不意译\n"
        "- 术语翻译保持一致\n"
        "- 不添加译注或解释\n"
    ),
}


def get_template(task_type: str, base_only: bool = False) -> str:
    """获取确定性 prompt 模板

    Args:
        task_type: 任务类型 key
        base_only: 是否只返回 base 模板
    Returns:
        完整 prompt 模板字符串
    """
    if base_only:
        return BASE_TEMPLATE
    return TEMPLATES.get(task_type, BASE_TEMPLATE)


def list_task_types() -> Dict[str, str]:
    """列出所有支持的任务类型"""
    return {k: v.split("\n")[1].strip() if "\n" in v else "通用"
            for k, v in TEMPLATES.items()}


def register_template(task_type: str, template: str) -> bool:
    """注册自定义模板

    Args:
        task_type: 任务类型 key
        template: 模板内容（不含 base）
    Returns:
        是否注册成功
    """
    if not task_type or not template.strip():
        return False
    TEMPLATES[task_type] = BASE_TEMPLATE + "\n" + template
    return True
