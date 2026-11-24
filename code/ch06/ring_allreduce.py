"""Ring AllReduce 教学模型，不是 NCCL benchmark。"""

from __future__ import annotations

import argparse
import json

MIB = 1024**2


def ring_allreduce_model(
    size_bytes: float,
    ranks: int,
    bandwidth_bytes_per_second: float,
    latency_seconds: float,
) -> dict:
    """使用 reduce-scatter + allgather 的经典 ring 量级模型。"""
    if size_bytes <= 0:
        raise ValueError("size_bytes 必须大于 0")
    if ranks < 1:
        raise ValueError("ranks 必须至少为 1")
    if bandwidth_bytes_per_second <= 0:
        raise ValueError("bandwidth 必须大于 0")
    if latency_seconds < 0:
        raise ValueError("latency 不能小于 0")

    steps = 2 * (ranks - 1)
    per_rank_bytes = 0.0 if ranks == 1 else 2 * (ranks - 1) / ranks * size_bytes
    modeled_seconds = steps * latency_seconds + per_rank_bytes / bandwidth_bytes_per_second
    return {
        "ranks": ranks,
        "steps": steps,
        "per_rank_traffic_mib": per_rank_bytes / MIB,
        "modeled_seconds": modeled_seconds,
        "note": "理想 ring 模型；忽略拓扑、协议、拥塞、算法切换与计算通信重叠。",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ring AllReduce 教学估算")
    parser.add_argument("--size-mib", type=float, required=True)
    parser.add_argument("--ranks", type=int, required=True)
    parser.add_argument("--bandwidth-gbps", type=float, required=True, help="有效带宽，十进制 GB/s")
    parser.add_argument("--latency-us", type=float, required=True, help="每步延迟，微秒")
    args = parser.parse_args()
    result = ring_allreduce_model(
        args.size_mib * MIB,
        args.ranks,
        args.bandwidth_gbps * 1e9,
        args.latency_us * 1e-6,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
