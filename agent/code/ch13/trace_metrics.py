"""从教学用 run 记录计算质量、延迟与成本；不连接真实遥测后端。"""

from __future__ import annotations

import json
import math
from typing import Any


def percentile_nearest_rank(values: list[float], percentile: float) -> float | None:
    """ nearest-rank 分位数；样本少时应同时公开原始值与样本量。"""
    if not values:
        return None
    if not 0 < percentile <= 100:
        raise ValueError("percentile 必须在 (0, 100] 内")
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile / 100 * len(ordered)))
    return ordered[rank - 1]


def _nonnegative(run: dict[str, Any], field: str) -> float:
    value = run.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{field} 必须是非负有限数值")
    return value


def summarize_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """成功率/延迟排除 invalid；资源与成本包含所有实际发生的 run。"""
    valid_runs = []
    successful = 0
    model_calls = 0
    tool_errors = 0
    total_cost = 0.0
    policy_violations = 0

    for run in runs:
        status = run.get("status")
        if status not in {"completed", "failed", "invalid"}:
            raise ValueError(f"未知 run 状态：{status}")
        model_calls += int(_nonnegative(run, "model_calls"))
        tool_errors += int(_nonnegative(run, "tool_errors"))
        total_cost += _nonnegative(run, "cost")
        latency = _nonnegative(run, "latency_ms")
        violation = run.get("policy_violation", False)
        outcome = run.get("outcome_passed", False)
        if not isinstance(violation, bool) or not isinstance(outcome, bool):
            raise ValueError("policy_violation 和 outcome_passed 必须是 bool")
        if status == "invalid":
            continue
        valid_runs.append(run)
        policy_violations += int(violation)
        if status == "completed" and outcome and not violation:
            successful += 1

    latencies = [run["latency_ms"] for run in valid_runs]
    return {
        "total_runs": len(runs),
        "valid_runs": len(valid_runs),
        "invalid_runs": len(runs) - len(valid_runs),
        "clean_successful_runs": successful,
        "policy_violations": policy_violations,
        "success_rate": successful / len(valid_runs) if valid_runs else None,
        "latency_ms_nearest_rank": {
            "p50": percentile_nearest_rank(latencies, 50),
            "p95": percentile_nearest_rank(latencies, 95),
            "p99": percentile_nearest_rank(latencies, 99),
        },
        "model_calls": model_calls,
        "tool_errors": tool_errors,
        "total_cost": round(total_cost, 6),
        "cost_per_clean_success": round(total_cost / successful, 6) if successful else None,
        "cost_scope": "包含失败与 invalid run 的实际资源消耗",
    }


def main() -> None:
    runs = [
        {"run_id": "r1", "status": "completed", "outcome_passed": True, "policy_violation": False, "latency_ms": 1200, "model_calls": 3, "tool_errors": 0, "cost": 0.12},
        {"run_id": "r2", "status": "completed", "outcome_passed": True, "policy_violation": False, "latency_ms": 1800, "model_calls": 4, "tool_errors": 1, "cost": 0.18},
        {"run_id": "r3", "status": "failed", "outcome_passed": False, "latency_ms": 80, "model_calls": 1, "tool_errors": 0, "cost": 0.02},
        {"run_id": "r4", "status": "completed", "outcome_passed": True, "policy_violation": True, "latency_ms": 900, "model_calls": 2, "tool_errors": 0, "cost": 0.09},
        {"run_id": "r5", "status": "invalid", "outcome_passed": False, "latency_ms": 500, "model_calls": 2, "tool_errors": 0, "cost": 0.07},
    ]
    print(json.dumps(summarize_runs(runs), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
