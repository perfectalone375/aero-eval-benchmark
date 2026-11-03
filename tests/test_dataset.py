from aero_eval.core.dataset import BENCHMARK_TASKS, BenchmarkRegistry


def test_registry_has_tasks():
    assert len(BENCHMARK_TASKS) >= 5


def test_get_task_by_id():
    task = BenchmarkRegistry.get_task("AERO-001")
    assert task is not None
    assert task.instance_id == "AERO-001"
    assert "Prandtl-Glauert" in task.problem_statement


def test_get_nonexistent_task():
    assert BenchmarkRegistry.get_task("AERO-999") is None
