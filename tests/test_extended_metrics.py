from aero_eval.core.dataset import BenchmarkRegistry
from aero_eval.core.evaluator import BenchmarkEvaluator
from aero_eval.core.metrics import calculate_metrics


def test_evaluator_all_tasks_have_hints():
    tasks = BenchmarkRegistry.list_all()
    for t in tasks:
        assert len(t.hints) > 10
        assert len(t.fail_to_pass_tests) > 0


def test_perfect_resolution_metrics():
    evaluator = BenchmarkEvaluator()
    tasks = BenchmarkRegistry.list_all()
    results = [evaluator.evaluate_patch(t.instance_id, t.reference_patch) for t in tasks]
    summary = calculate_metrics(results)
    assert summary.resolution_rate_percent == 100.0
    assert summary.resolved_tasks == len(tasks)
