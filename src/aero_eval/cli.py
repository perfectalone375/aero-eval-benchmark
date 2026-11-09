"""Command-line interface for aero-eval-benchmark (aeroeval)."""

from __future__ import annotations

import argparse
import json
import sys

from .core.dataset import BenchmarkRegistry
from .core.evaluator import BenchmarkEvaluator
from .core.metrics import calculate_metrics


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        prog="aeroeval",
        description="AeroEval: Aerospace SWE-bench Style Benchmark & AI Evaluation Runner",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    subparsers.add_parser("list", help="List all registered benchmark task instances")

    # info
    inf = subparsers.add_parser("info", help="Display details for a specific task")
    inf.add_argument("instance_id", type=str, help="Instance ID (e.g., AERO-001)")

    # eval
    ev = subparsers.add_parser("eval", help="Evaluate a candidate patch or gold reference")
    ev.add_argument("instance_id", type=str, help="Instance ID")
    ev.add_argument("--patch-file", type=str, help="Path to patch file")
    ev.add_argument("--use-gold", action="store_true", help="Evaluate reference gold patch")
    ev.add_argument("--json", action="store_true", help="Output JSON format")

    # run-all
    ra = subparsers.add_parser("run-all", help="Evaluate all tasks using gold reference patches")
    ra.add_argument("--json", action="store_true", help="Output JSON leaderboard summary")

    args = parser.parse_args()

    if args.command == "list":
        tasks = BenchmarkRegistry.list_all()
        print("=" * 80)
        print(f"  AeroEval Benchmark Registry: {len(tasks)} Curated Engineering Challenges")
        print("-" * 80)
        print(f"  {'ID':<10} | {'Difficulty':<10} | {'Repository':<24} | {'Domain'}")
        print("-" * 80)
        for t in tasks:
            print(f"  {t.instance_id:<10} | {t.difficulty:<10} | {t.repository:<24} | {t.domain}")
        print("=" * 80)

    elif args.command == "info":
        task = BenchmarkRegistry.get_task(args.instance_id)
        if not task:
            print(f"Error: Task {args.instance_id} not found.")
            sys.exit(1)
        print("=" * 80)
        print(f"  Task Instance: {task.instance_id} [{task.difficulty}]")
        print(f"  Target Repository: {task.repository}")
        print(f"  Domain: {task.domain}")
        print("-" * 80)
        print(f"  Problem Statement:\n  {task.problem_statement}\n")
        print(f"  Hints:\n  {task.hints}\n")
        print(f"  Fail-To-Pass Tests: {task.fail_to_pass_tests}")
        print(f"  Pass-To-Pass Tests: {task.pass_to_pass_tests}")
        print("=" * 80)

    elif args.command == "eval":
        task = BenchmarkRegistry.get_task(args.instance_id)
        if not task:
            print(f"Error: Task {args.instance_id} not found.")
            sys.exit(1)

        patch_content = ""
        if args.use_gold:
            patch_content = task.reference_patch
        elif args.patch_file:
            with open(args.patch_file, encoding="utf-8") as f:
                patch_content = f.read()
        else:
            print("Error: Specify --patch-file or --use-gold")
            sys.exit(1)

        evaluator = BenchmarkEvaluator()
        res = evaluator.evaluate_patch(args.instance_id, patch_content)

        if args.json:
            print(json.dumps(res.to_dict(), indent=2))
        else:
            print("=" * 60)
            status_badge = "RESOLVED [PASS]" if res.is_resolved else "FAILED [FAIL]"
            print(f"  Evaluation Result: {res.instance_id} -> {status_badge}")
            print(f"  Fail-To-Pass:      {res.fail_to_pass_passed}/{res.fail_to_pass_total}")
            print(f"  Pass-To-Pass:      {res.pass_to_pass_passed}/{res.pass_to_pass_total}")
            print(f"  Latency:           {res.execution_time_ms:.2f} ms")
            print(f"  Notes:             {res.message}")
            print("=" * 60)

    elif args.command == "run-all":
        tasks = BenchmarkRegistry.list_all()
        evaluator = BenchmarkEvaluator()
        results = [evaluator.evaluate_patch(t.instance_id, t.reference_patch) for t in tasks]
        metrics = calculate_metrics(results)

        if args.json:
            out = {
                "summary": metrics.to_dict(),
                "results": [r.to_dict() for r in results],
            }
            print(json.dumps(out, indent=2))
        else:
            print("=" * 70)
            print("  AeroEval Full Suite Gold Baseline Benchmark Run")
            print("-" * 70)
            print(f"  Total Scenarios:         {metrics.total_tasks}")
            print(f"  Resolved Scenarios:      {metrics.resolved_tasks}")
            print(f"  Resolution Rate:         {metrics.resolution_rate_percent:.1f}%")
            print(f"  Mean Evaluation Latency: {metrics.mean_latency_ms:.2f} ms")
            print("=" * 70)


if __name__ == "__main__":
    main()
