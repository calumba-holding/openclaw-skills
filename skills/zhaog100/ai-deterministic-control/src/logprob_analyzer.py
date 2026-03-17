# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
LogprobAnalyzer — 对数概率熵分析与异常检测
"""

import math
from typing import List, Optional, Dict


def entropy_from_logprobs(logprobs: List[float]) -> float:
    """计算 Shannon 熵 H = -Σ p(x) * log2(p(x))

    Args:
        logprobs: 对数概率列表（natural log, 即 ln(p)）
    Returns:
        Shannon 熵（bits）
    """
    if not logprobs:
        return 0.0
    # Normalize to valid probabilities
    raw = [math.exp(lp) for lp in logprobs]
    total_raw = sum(raw)
    if total_raw == 0:
        return 0.0
    probs = [r / total_raw for r in raw]
    log_probs = [math.log(p) for p in probs if p > 0]
    total = 0.0
    for p, lp2 in zip(probs, log_probs):
        if p > 0:
            total -= p * (lp2 / math.log(2))
    return total


def certainty_score(logprobs: List[float]) -> float:
    """确定性评分 0-100，熵越低分越高

    基于归一化熵：score = (1 - normalized_entropy) * 100
    假设最大熵为 log2(len(logprobs))
    """
    if not logprobs:
        return 0.0
    n = len(logprobs)
    max_entropy = math.log2(n) if n > 1 else 1.0
    h = entropy_from_logprobs(logprobs)
    return round((1.0 - h / max_entropy) * 100, 2)


def analyze_trend(history: List[float], window: int = 5) -> Dict:
    """分析熵值趋势

    Args:
        history: 历史熵值列表（按时间顺序）
        window: 趋势计算窗口大小
    Returns:
        {"direction": "rising"|"falling"|"stable",
         "slope": float, "avg": float, "latest": float}
    """
    if not history:
        return {"direction": "stable", "slope": 0.0, "avg": 0.0, "latest": 0.0}

    recent = history[-window:] if len(history) >= window else history
    if len(recent) < 2:
        return {"direction": "stable", "slope": 0.0,
                "avg": round(sum(recent) / len(recent), 4),
                "latest": recent[-1]}

    # 线性回归斜率
    n = len(recent)
    x_mean = (n - 1) / 2.0
    y_mean = sum(recent) / n
    numerator = sum((i - x_mean) * (recent[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0.0

    avg = round(y_mean, 4)
    latest = history[-1]

    if slope > 0.05:
        direction = "rising"
    elif slope < -0.05:
        direction = "falling"
    else:
        direction = "stable"

    return {"direction": direction, "slope": round(slope, 4), "avg": avg, "latest": latest}


def detect_anomaly(entropy: float, history: List[float],
                   threshold: float = 2.0) -> Dict:
    """基于 Z-score 的异常检测

    Args:
        entropy: 当前熵值
        history: 历史熵值
        threshold: Z-score 阈值（默认 2.0）
    Returns:
        {"is_anomaly": bool, "z_score": float, "mean": float, "std": float}
    """
    if len(history) < 3:
        return {"is_anomaly": False, "z_score": 0.0, "mean": 0.0, "std": 0.0}

    mean = sum(history) / len(history)
    variance = sum((h - mean) ** 2 for h in history) / len(history)
    std = math.sqrt(variance)

    if std == 0:
        return {"is_anomaly": False, "z_score": 0.0, "mean": round(mean, 4), "std": 0.0}

    z_score = (entropy - mean) / std
    return {
        "is_anomaly": abs(z_score) > threshold,
        "z_score": round(z_score, 4),
        "mean": round(mean, 4),
        "std": round(std, 4),
    }
