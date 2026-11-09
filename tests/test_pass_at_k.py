"""
Tests for Pass@k unbiased estimator and new physical ODE benchmark tasks.
"""

import pytest

from aero_eval.core.dataset import BenchmarkRegistry
from aero_eval.core.evaluator import BenchmarkEvaluator
from aero_eval.core.metrics import calculate_pass_at_k


def test_pass_at_1_identity():
    # Pass@1 is algebraically identical to c / n
    val = calculate_pass_at_k(n=100, c=42, k=1)
    assert abs(val - 0.42) < 1e-9


def test_pass_at_k_extremes():
    # Perfect score: all correct
    assert calculate_pass_at_k(n=10, c=10, k=3) == 1.0

    # Zero score: none correct
    assert calculate_pass_at_k(n=10, c=0, k=3) == 0.0

    # When (n - c) < k, at least one correct answer must be sampled in k draws
    assert calculate_pass_at_k(n=10, c=8, k=5) == 1.0


def test_pass_at_k_analytical_combinatorial():
    # n=10, c=2, k=2: 1 - binom(8, 2)/binom(10, 2) = 1 - 28/45 = 17/45 ~ 0.377778
    val = calculate_pass_at_k(n=10, c=2, k=2)
    expected = 17.0 / 45.0
    assert abs(val - expected) < 1e-6


def test_pass_at_k_invalid_bounds():
    with pytest.raises(ValueError, match="strictly positive"):
        calculate_pass_at_k(n=0, c=0, k=1)

    with pytest.raises(ValueError, match="must be >= k"):
        calculate_pass_at_k(n=3, c=1, k=5)

    with pytest.raises(ValueError, match="must satisfy 0 <= c <= n"):
        calculate_pass_at_k(n=10, c=15, k=2)


def test_new_benchmark_tasks_evaluator():
    evaluator = BenchmarkEvaluator()

    # AERO-006: Gimbal Lock
    task6 = BenchmarkRegistry.get_task("AERO-006")
    assert task6 is not None
    assert "Gimbal Lock" in task6.domain
    res6 = evaluator.evaluate_patch("AERO-006", "abs(sin_theta) >= 0.999999 copysign")
    assert res6.is_resolved is True

    # AERO-007: Oblique Shock Detachment
    task7 = BenchmarkRegistry.get_task("AERO-007")
    assert task7 is not None
    assert "Oblique Shock" in task7.domain
    res7 = evaluator.evaluate_patch("AERO-007", "if th > theta_max: raise ValueError('detachment')")
    assert res7.is_resolved is True

    # AERO-008: Bi-elliptic Transfer
    task8 = BenchmarkRegistry.get_task("AERO-008")
    assert task8 is not None
    assert "Orbital Transfers" in task8.domain
    res8 = evaluator.evaluate_patch("AERO-008", "if r2/r1 > 11.94: return bielliptic_transfer()")
    assert res8.is_resolved is True
