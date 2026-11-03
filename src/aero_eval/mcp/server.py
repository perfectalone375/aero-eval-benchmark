"""Model Context Protocol (MCP) Server for AeroEval Benchmark Runner."""
from __future__ import annotations

import json
import sys
from typing import Any

from ..core.dataset import BenchmarkRegistry
from ..core.evaluator import BenchmarkEvaluator

TOOLS = [
    {
        "name": "aeroeval_list_tasks",
        "description": "List all aerospace and computational physics SWE-bench task instances.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "aeroeval_get_task_spec",
        "description": "Get detailed problem statement, hints, and test requirements for a benchmark task.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance_id": {"type": "string", "description": "Instance ID, e.g. 'AERO-001'"},
            },
            "required": ["instance_id"],
        },
    },
    {
        "name": "aeroeval_evaluate_patch",
        "description": "Run isolated evaluation of a candidate unified diff patch against a benchmark task.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance_id": {"type": "string", "description": "Instance ID, e.g. 'AERO-001'"},
                "patch": {"type": "string", "description": "Unified diff patch string"},
            },
            "required": ["instance_id", "patch"],
        },
    },
]

evaluator_instance = BenchmarkEvaluator()


def handle_call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "aeroeval_list_tasks":
        tasks = BenchmarkRegistry.list_all()
        return {
            "count": len(tasks),
            "tasks": [
                {
                    "instance_id": t.instance_id,
                    "difficulty": t.difficulty,
                    "repository": t.repository,
                    "domain": t.domain,
                }
                for t in tasks
            ],
        }
    elif name == "aeroeval_get_task_spec":
        task = BenchmarkRegistry.get_task(args["instance_id"])
        if not task:
            raise ValueError(f"Task {args['instance_id']} not found.")
        return task.to_dict()
    elif name == "aeroeval_evaluate_patch":
        inst_id = args["instance_id"]
        patch = args["patch"]
        res = evaluator_instance.evaluate_patch(inst_id, patch)
        return res.to_dict()
    else:
        raise ValueError(f"Unknown tool: {name}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")

            if method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                result = handle_call_tool(name, args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
                }
            elif method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "aero-eval-mcp", "version": "0.1.0"},
                        "capabilities": {"tools": {}},
                    },
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method {method} not found"}}
            print(json.dumps(resp), flush=True)
        except Exception as err:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(err)}}
            print(json.dumps(err_resp), flush=True)


if __name__ == "__main__":
    main()
