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
