from aero_eval.core.evaluator import BenchmarkEvaluator
from aero_eval.core.metrics import calculate_metrics
from aero_eval.mcp.server import TOOLS, handle_call_tool


def test_calculate_metrics():
    evaluator = BenchmarkEvaluator()
    r1 = evaluator.evaluate_patch("AERO-001", "tanh bridge")
    r2 = evaluator.evaluate_patch("AERO-002", "")
    summary = calculate_metrics([r1, r2])
    assert summary.total_tasks == 2
    assert summary.resolved_tasks == 1
    assert summary.resolution_rate_percent == 50.0


def test_mcp_tools():
    assert len(TOOLS) == 3
    tasks_res = handle_call_tool("aeroeval_list_tasks", {})
    assert tasks_res["count"] >= 5

    spec_res = handle_call_tool("aeroeval_get_task_spec", {"instance_id": "AERO-001"})
    assert spec_res["instance_id"] == "AERO-001"

    eval_res = handle_call_tool(
        "aeroeval_evaluate_patch",
        {"instance_id": "AERO-001", "patch": "tanh transonic saturation"},
    )
    assert eval_res["resolved"] is True
