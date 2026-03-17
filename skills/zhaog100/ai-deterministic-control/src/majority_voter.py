# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
MajorityVoter — 多数投票一致性保障
"""

import concurrent.futures
from typing import List, Callable, Optional, Dict
from algorithms import levenshtein_similarity


def cluster_outputs(outputs: List[str], threshold: float = 0.85) -> List[List[str]]:
    """基于编辑距离的简单聚类（层次凝聚，单链接）

    Args:
        outputs: 输出文本列表
        threshold: 相似度阈值，高于此值归为同一簇
    Returns:
        聚类结果列表
    """
    if not outputs:
        return []
    clusters = [[o] for o in outputs]
    merged = True
    while merged:
        merged = False
        new_clusters = []
        used = set()
        for i in range(len(clusters)):
            if i in used:
                continue
            cluster = clusters[i][:]
            for j in range(i + 1, len(clusters)):
                if j in used:
                    continue
                # 比较两个簇中任意一对的相似度
                found = False
                for a in cluster:
                    for b in clusters[j]:
                        if levenshtein_similarity(a, b) >= threshold:
                            found = True
                            break
                    if found:
                        break
                if found:
                    cluster.extend(clusters[j])
                    used.add(j)
                    merged = True
            used.add(i)
            new_clusters.append(cluster)
        clusters = new_clusters
    return clusters


def majority_vote(outputs: List[str], similarity_threshold: float = 0.85) -> Dict:
    """多数投票：选最大簇的代表输出

    Args:
        outputs: 多次采样输出列表
        similarity_threshold: 聚类相似度阈值
    Returns:
        {"winner": str, "confidence": float, "cluster_sizes": list,
         "total": int, "agreement_ratio": float}
    """
    if not outputs:
        return {"winner": "", "confidence": 0.0, "cluster_sizes": [],
                "total": 0, "agreement_ratio": 0.0}
    clusters = cluster_outputs(outputs, similarity_threshold)
    clusters.sort(key=len, reverse=True)
    largest = clusters[0]
    winner = largest[0]  # 代表输出
    confidence = len(largest) / len(outputs)
    sizes = sorted([len(c) for c in clusters], reverse=True)
    return {
        "winner": winner,
        "confidence": round(confidence, 4),
        "cluster_sizes": sizes,
        "total": len(outputs),
        "agreement_ratio": round(confidence, 4),
    }


def vote_with_timeout(prompt_fn: Callable[[], str], n: int = 5,
                      timeout: float = 30) -> Dict:
    """带超时的并发采样投票

    Args:
        prompt_fn: 无参调用函数，返回一次采样结果
        n: 采样次数
        timeout: 单次超时秒数
    Returns:
        多数投票结果 + 失败信息
    """
    outputs = []
    errors = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        futures = {executor.submit(prompt_fn): i for i in range(n)}
        for future in concurrent.futures.as_completed(futures, timeout=timeout * n):
            try:
                result = future.result(timeout=timeout)
                outputs.append(str(result))
            except Exception:
                errors += 1

    vote_result = majority_vote(outputs)
    vote_result["errors"] = errors
    return vote_result
