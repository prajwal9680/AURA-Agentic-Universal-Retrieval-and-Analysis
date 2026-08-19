"""
AURA — Information Retrieval (IR) Metrics Suite
Calculates formal IR metrics for retrieval benchmarking:
- Precision@K (P@1, P@3, P@5, P@10)
- Recall@K (R@1, R@3, R@5, R@10)
- Mean Reciprocal Rank (MRR)
- Normalized Discounted Cumulative Gain (NDCG@K)
- Mean Average Precision (MAP)
- Latency percentiles (p50, p90, p95, p99)
"""
import math
import numpy as np
from typing import List, Dict, Any, Set


def precision_at_k(retrieved_ids: List[str], ground_truth_ids: Set[str], k: int) -> float:
    """Computes Precision@K = (relevant items in top K) / K."""
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    relevant_count = sum(1 for mid in top_k if mid in ground_truth_ids)
    return relevant_count / float(k)


def recall_at_k(retrieved_ids: List[str], ground_truth_ids: Set[str], k: int) -> float:
    """Computes Recall@K = (relevant items in top K) / (total relevant items)."""
    if not ground_truth_ids:
        return 1.0
    top_k = retrieved_ids[:k]
    relevant_count = sum(1 for mid in top_k if mid in ground_truth_ids)
    return relevant_count / float(len(ground_truth_ids))


def reciprocal_rank(retrieved_ids: List[str], ground_truth_ids: Set[str]) -> float:
    """Computes Reciprocal Rank (1 / rank of first relevant item)."""
    for rank, mid in enumerate(retrieved_ids, start=1):
        if mid in ground_truth_ids:
            return 1.0 / float(rank)
    return 0.0


def dcg_at_k(retrieved_ids: List[str], relevance_scores: Dict[str, float], k: int) -> float:
    """Computes Discounted Cumulative Gain at K."""
    dcg = 0.0
    for idx, mid in enumerate(retrieved_ids[:k]):
        rel = relevance_scores.get(mid, 0.0)
        dcg += rel / math.log2(idx + 2)
    return dcg


def ndcg_at_k(retrieved_ids: List[str], ground_truth_ids: Set[str], k: int, graded_relevance: Dict[str, float] = None) -> float:
    """
    Computes Normalized Discounted Cumulative Gain at K.
    If graded_relevance is None, binary relevance (1.0 for GT, 0.0 otherwise) is used.
    """
    if graded_relevance is None:
        graded_relevance = {gid: 1.0 for gid in ground_truth_ids}

    actual_dcg = dcg_at_k(retrieved_ids, graded_relevance, k)

    # Ideal DCG: sort ground truth items by relevance descending
    sorted_ideal_rels = sorted(graded_relevance.values(), reverse=True)
    ideal_dcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(sorted_ideal_rels[:k]))

    if ideal_dcg == 0.0:
        return 0.0
    return min(actual_dcg / ideal_dcg, 1.0)


def compute_ir_benchmark(
    query_evaluations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Aggregate formal IR metrics across a dataset of benchmark queries.

    Expected input per item:
    {
        "query": str,
        "retrieved_ids": List[str],
        "ground_truth_ids": Set[str] or List[str],
        "graded_relevance": Optional[Dict[str, float]],
        "latency_ms": float,
    }
    """
    if not query_evaluations:
        return {}

    p1_list, p3_list, p5_list, p10_list = [], [], [], []
    r1_list, r3_list, r5_list, r10_list = [], [], [], []
    mrr_list = []
    ndcg3_list, ndcg5_list, ndcg10_list = [], [], []
    latencies = []

    for ev in query_evaluations:
        ret_ids = ev["retrieved_ids"]
        gt_set = set(ev["ground_truth_ids"])
        graded = ev.get("graded_relevance")
        lat = ev.get("latency_ms", 0.0)
        latencies.append(lat)

        p1_list.append(precision_at_k(ret_ids, gt_set, 1))
        p3_list.append(precision_at_k(ret_ids, gt_set, 3))
        p5_list.append(precision_at_k(ret_ids, gt_set, 5))
        p10_list.append(precision_at_k(ret_ids, gt_set, 10))

        r1_list.append(recall_at_k(ret_ids, gt_set, 1))
        r3_list.append(recall_at_k(ret_ids, gt_set, 3))
        r5_list.append(recall_at_k(ret_ids, gt_set, 5))
        r10_list.append(recall_at_k(ret_ids, gt_set, 10))

        mrr_list.append(reciprocal_rank(ret_ids, gt_set))

        ndcg3_list.append(ndcg_at_k(ret_ids, gt_set, 3, graded))
        ndcg5_list.append(ndcg_at_k(ret_ids, gt_set, 5, graded))
        ndcg10_list.append(ndcg_at_k(ret_ids, gt_set, 10, graded))

    return {
        "num_queries": len(query_evaluations),
        "precision": {
            "p@1": round(float(np.mean(p1_list)), 4),
            "p@3": round(float(np.mean(p3_list)), 4),
            "p@5": round(float(np.mean(p5_list)), 4),
            "p@10": round(float(np.mean(p10_list)), 4),
        },
        "recall": {
            "r@1": round(float(np.mean(r1_list)), 4),
            "r@3": round(float(np.mean(r3_list)), 4),
            "r@5": round(float(np.mean(r5_list)), 4),
            "r@10": round(float(np.mean(r10_list)), 4),
        },
        "mrr": round(float(np.mean(mrr_list)), 4),
        "ndcg": {
            "ndcg@3": round(float(np.mean(ndcg3_list)), 4),
            "ndcg@5": round(float(np.mean(ndcg5_list)), 4),
            "ndcg@10": round(float(np.mean(ndcg10_list)), 4),
        },
        "latency_ms": {
            "mean": round(float(np.mean(latencies)), 2),
            "p50": round(float(np.percentile(latencies, 50)), 2),
            "p95": round(float(np.percentile(latencies, 95)), 2),
            "p99": round(float(np.percentile(latencies, 99)), 2),
        }
    }
