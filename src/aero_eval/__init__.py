"""AeroEval: Aerospace and Computational Physics SWE-bench AI Benchmark Framework."""
from .core.dataset import BENCHMARK_TASKS, BenchmarkRegistry, BenchmarkTask
from .core.evaluator import BenchmarkEvaluator, EvaluationResult
from .core.metrics import BenchmarkSummary, calculate_metrics

__version__ = "0.1.0"
__all__ = [
    "BENCHMARK_TASKS",
    "BenchmarkRegistry",
    "BenchmarkTask",
    "BenchmarkEvaluator",
    "EvaluationResult",
    "BenchmarkSummary",
    "calculate_metrics",
]
