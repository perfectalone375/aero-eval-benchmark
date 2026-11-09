"""Benchmark metrics calculation: Pass@1, Resolution Rate, and Latency Analysis."""

from __future__ import annotations

from dataclasses import dataclass

from .evaluator import EvaluationResult


@dataclass
class BenchmarkSummary:
    total_tasks: int
    resolved_tasks: int
    failed_tasks: int
    resolution_rate_percent: float
    mean_latency_ms: float

    def to_dict(self) -> dict:
        return {
            "total_tasks": self.total_tasks,
            "resolved_tasks": self.resolved_tasks,
            "failed_tasks": self.failed_tasks,
            "resolution_rate_percent": round(self.resolution_rate_percent, 2),
            "mean_latency_ms": round(self.mean_latency_ms, 2),
        }


def calculate_metrics(results: list[EvaluationResult]) -> BenchmarkSummary:
    """Calculate aggregated benchmark score metrics."""
    if not results:
        return BenchmarkSummary(0, 0, 0, 0.0, 0.0)

    total = len(results)
    resolved = sum(1 for r in results if r.is_resolved)
    failed = total - resolved
    rate = (resolved / total) * 100.0
    mean_lat = sum(r.execution_time_ms for r in results) / total

    return BenchmarkSummary(
        total_tasks=total,
        resolved_tasks=resolved,
        failed_tasks=failed,
        resolution_rate_percent=rate,
        mean_latency_ms=mean_lat,
    )


def calculate_pass_at_k(n: int, c: int, k: int) -> float:
    """
    Unbiased estimator of Pass@k evaluation metric from HumanEval (Chen et al., 2021).
    Pass@k = 1 - [ binom(n - c, k) / binom(n, k) ]

    Parameters
    ----------
    n : int
        Total number of candidate model outputs sampled per task (n >= k).
    c : int
        Number of correct / passing candidate solutions (0 <= c <= n).
    k : int
        Evaluation threshold sample budget (e.g., 1, 3, 5).
    """
    if n <= 0 or k <= 0:
        raise ValueError("n and k must be strictly positive integers.")
    if n < k:
        raise ValueError(f"Sample count n={n} must be >= k={k}.")
    if c < 0 or c > n:
        raise ValueError(f"Correct count c={c} must satisfy 0 <= c <= n={n}.")

    if n - c < k:
        return 1.0

    prod = 1.0
    for i in range(1, k + 1):
        prod *= (n - c - i + 1) / (n - i + 1)

    return float(1.0 - prod)
