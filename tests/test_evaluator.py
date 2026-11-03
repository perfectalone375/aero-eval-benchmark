from aero_eval.core.evaluator import BenchmarkEvaluator


def test_evaluate_gold_patch_resolves():
    evaluator = BenchmarkEvaluator()
    res = evaluator.evaluate_patch("AERO-001", "tanh transonic saturation bridge")
    assert res.is_resolved
    assert res.status == "RESOLVED"
    assert res.fail_to_pass_passed == res.fail_to_pass_total


def test_evaluate_empty_patch_fails():
    evaluator = BenchmarkEvaluator()
    res = evaluator.evaluate_patch("AERO-001", "")
    assert not res.is_resolved
    assert res.status == "FAILED"


def test_evaluate_invalid_task():
    evaluator = BenchmarkEvaluator()
    res = evaluator.evaluate_patch("UNKNOWN-TASK", "some patch")
    assert res.status == "ERROR"
