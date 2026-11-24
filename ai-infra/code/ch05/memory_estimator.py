"""训练显存的透明估算模型；不包含框架和硬件的所有实际开销。"""

from __future__ import annotations

import argparse
import json

GIB = 1024**3


def estimate_training_memory(
    params: float,
    weight_bytes: float,
    gradient_bytes: float,
    master_weight_bytes: float,
    optimizer_state_bytes: float,
    activation_gib: float = 0,
    workspace_gib: float = 0,
) -> dict:
    """按每参数字节数估算静态状态，再加上激活和 workspace。"""
    per_param = {
        "weight_bytes": weight_bytes,
        "gradient_bytes": gradient_bytes,
        "master_weight_bytes": master_weight_bytes,
        "optimizer_state_bytes": optimizer_state_bytes,
    }
    if params <= 0:
        raise ValueError("params 必须大于 0")
    for name, value in per_param.items():
        if value < 0:
            raise ValueError(f"{name} 不能小于 0")
    if activation_gib < 0 or workspace_gib < 0:
        raise ValueError("activation_gib 和 workspace_gib 不能小于 0")

    states_gib = {
        name.removesuffix("_bytes"): params * value / GIB
        for name, value in per_param.items()
    }
    static_gib = sum(states_gib.values())
    total_gib = static_gib + activation_gib + workspace_gib
    return {
        "parameters": params,
        "states_gib": states_gib,
        "static_gib": static_gib,
        "activation_gib": activation_gib,
        "workspace_gib": workspace_gib,
        "estimated_total_gib": total_gib,
        "note": "不含通信 buffer、allocator 碎片和其他 runtime 开销；分片需另行建模。",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="估算训练显存")
    parser.add_argument("--params", type=float, required=True, help="参数量，可写 7e9")
    parser.add_argument("--weight-bytes", type=float, default=2)
    parser.add_argument("--gradient-bytes", type=float, default=2)
    parser.add_argument("--master-weight-bytes", type=float, default=4)
    parser.add_argument("--optimizer-state-bytes", type=float, default=8, help="一阶与二阶状态合计")
    parser.add_argument("--activation-gib", type=float, default=0)
    parser.add_argument("--workspace-gib", type=float, default=0)
    args = parser.parse_args()
    result = estimate_training_memory(
        args.params,
        args.weight_bytes,
        args.gradient_bytes,
        args.master_weight_bytes,
        args.optimizer_state_bytes,
        args.activation_gib,
        args.workspace_gib,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
