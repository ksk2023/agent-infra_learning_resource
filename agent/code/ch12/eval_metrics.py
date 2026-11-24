"""离线评测指标：区分无效评分、Agent 失败、安全违规与干净成功。"""

from __future__ import annotations

import json
import math
from typing import Any


VALID_STATUSES = {"success", "agent_failure", "safety_violation", "invalid"}


def _validate_probability(p: float) -> None:
    if isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("p 必须是 0 到 1 之间的有限数值")


def _validate_k(k: int) -> None:
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k 必须是至少为 1 的整数")


def pass_at_k(p: float, k: int) -> float:
    """独立同分布简化模型下，k 次至少一次成功的概率。"""
    _validate_probability(p)
    _validate_k(k)
    return 1 - (1 - p) ** k


def pass_all_k(p: float, k: int) -> float:
    """独立同分布简化模型下，k 次全部成功的概率，即 pass^k。"""
    _validate_probability(p)
    _validate_k(k)
    return p ** k


def summarize_trials(trials: list[dict[str, Any]]) -> dict[str, Any]:
    """invalid 不进入成功率分母；安全违规属于有效试验，但不是干净成功。"""
    counts = {status: 0 for status in VALID_STATUSES}
    for trial in trials:
        status = trial.get("status")
        if status not in VALID_STATUSES:
            raise ValueError(f"未知试验状态：{status}")
        counts[status] += 1

    valid = len(trials) - counts["invalid"]
    clean_success = counts["success"]
    return {
        "total": len(trials),
        "valid": valid,
        "invalid": counts["invalid"],
        "clean_success": clean_success,
        "agent_failure": counts["agent_failure"],
        "safety_violation": counts["safety_violation"],
        "single_run_success_rate": clean_success / valid if valid else None,
        "success_numerator": clean_success,
        "success_denominator": valid,
    }


def main() -> None:
    trials = [
        {"task_id": "t1", "run": 1, "status": "success"},
        {"task_id": "t1", "run": 2, "status": "success"},
        {"task_id": "t1", "run": 3, "status": "agent_failure"},
        {"task_id": "t2", "run": 1, "status": "safety_violation"},
        {"task_id": "t3", "run": 1, "status": "invalid"},
    ]
    summary = summarize_trials(trials)
    p = summary["single_run_success_rate"]
    print(json.dumps({
        "summary": summary,
        "independent_probability_model": {
            "pass@3": pass_at_k(p, 3),
            "pass^3": pass_all_k(p, 3),
            "warning": "公式是独立性简化模型，不替代真实重复运行与置信区间。",
        },
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
