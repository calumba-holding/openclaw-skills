# Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
ConsistencyChecker — 输出一致性检查器
"""

from dataclasses import dataclass, field
from typing import Optional, List, Callable, Dict
from enum import Enum

from algorithms import levenshtein_similarity, tfidf_cosine_similarity, composite_score
from config_manager import DeterministicConfig


class AlertLevel(Enum):
    OK = "ok"
    WARN = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    level: AlertLevel
    message: str
    threshold: float
    actual: float

    def to_dict(self):
        return {"level": self.level.value, "message": self.message,
                "threshold": self.threshold, "actual": self.actual}


@dataclass
class ConsistencyReport:
    samples: List[str]
    char_similarity: float
    semantic_similarity: float
    composite_score: float
    alert: Optional[Alert] = None

    def to_dict(self):
        d = {
            "samples": self.samples,
            "char_similarity": round(self.char_similarity, 4),
            "semantic_similarity": round(self.semantic_similarity, 4),
            "composite_score": round(self.composite_score, 4),
        }
        if self.alert:
            d["alert"] = self.alert.to_dict()
        return d


class ConsistencyChecker:
    TEXT_WEIGHT = 0.4
    STRUCT_WEIGHT = 0.3
    ENTROPY_WEIGHT = 0.3
    DEFAULT_SAMPLES = 5

    def __init__(self, config=None):
        self.config = config or DeterministicConfig()
        self._entropy_history: list = []

    def check(self, prompt, sampler_fn=None, n_samples=None,
              logprobs_list=None):
        """一致性检查主流程（v1.1: 支持熵一致性维度）

        Args:
            prompt: 测试 prompt
            sampler_fn: 采样函数
            n_samples: 采样次数
            logprobs_list: 可选，每次采样的 logprobs 列表
        """
        if n_samples is None:
            n_samples = self.DEFAULT_SAMPLES
        if sampler_fn is None:
            sampler_fn = self.default_sampler

        config_dict = self.config.to_dict()
        samples = []
        for _ in range(n_samples):
            try:
                s = sampler_fn(prompt, config_dict)
                samples.append(str(s))
            except Exception:
                samples.append("[error]")

        # 熵一致性计算
        entropy_score = 0.0
        if logprobs_list:
            from logprob_analyzer import entropy_from_logprobs
            entropies = []
            for lp in logprobs_list:
                if lp:
                    entropies.append(entropy_from_logprobs(lp))
            if entropies:
                # 熵一致性 = 1 - 归一化标准差（越一致分越高）
                import math
                mean_e = sum(entropies) / len(entropies)
                std_e = math.sqrt(sum((e - mean_e) ** 2 for e in entropies) / len(entropies))
                max_e = max(entropies) if max(entropies) > 0 else 1.0
                entropy_score = max(0.0, 1.0 - std_e / max_e)
                self._entropy_history.extend(entropies)

        if len(samples) < 2:
            return ConsistencyReport(
                samples=samples, char_similarity=0.0,
                semantic_similarity=0.0, composite_score=0.0,
                alert=Alert(AlertLevel.CRITICAL, "insufficient samples", 0.8, 0.0),
            )

        char_scores, sem_scores = [], []
        for i in range(len(samples)):
            for j in range(i + 1, len(samples)):
                cs = levenshtein_similarity(samples[i], samples[j])
                ss = tfidf_cosine_similarity(samples[i], samples[j])
                char_scores.append(cs)
                sem_scores.append(ss)

        avg_char = sum(char_scores) / len(char_scores)
        avg_sem = sum(sem_scores) / len(sem_scores)
        # v1.1 评分公式: 0.4×文本 + 0.3×结构 + 0.3×熵一致性
        comp = (self.TEXT_WEIGHT * avg_char +
                self.STRUCT_WEIGHT * avg_sem +
                self.ENTROPY_WEIGHT * entropy_score)
        alert = self._check_threshold(comp)
        return ConsistencyReport(
            samples=samples, char_similarity=avg_char,
            semantic_similarity=avg_sem, composite_score=comp, alert=alert,
        )

    def _check_threshold(self, score):
        if score >= 0.8:
            return None
        elif score >= 0.6:
            return Alert(AlertLevel.WARN, "moderate consistency", 0.8, score)
        else:
            return Alert(AlertLevel.CRITICAL, "low consistency", 0.6, score)

    @staticmethod
    def default_sampler(prompt, config):
        """
        默认采样函数：openclaw CLI → HTTP API → mock 降级
        """
        import subprocess
        try:
            result = subprocess.run(
                ["openclaw", "message", "--model", config.get("model", "glm-5-turbo"),
                 "--temperature", str(config.get("temperature", 0.3)),
                 "--no-stream", prompt],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
        return "[mock] {}".format(abs(hash(prompt)) % 10000)
