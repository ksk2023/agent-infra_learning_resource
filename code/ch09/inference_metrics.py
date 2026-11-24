"""KV Cache 估算与推理请求统计；只使用标准库。"""

from __future__ import annotations

import argparse
import json
import math
from typing import Iterable


def kv_cache_bytes(
    layers: int,
    batch: int,
    tokens: int,
    kv_heads: int,
    head_dim: int,
    dtype_bytes: int,
) -> int:
    """计算 K/V 逻辑 payload，不含 block 对齐和运行时额外开销。"""
    values = (layers, batch, tokens, kv_heads, head_dim, dtype_bytes)
    if any(value <= 0 for value in values):
        raise ValueError("KV Cache 的所有维度与字节数必须大于 0")
    return 2 * math.prod(values)


def percentile(values: Iterable[float], percent: float) -> float:
    """线性插值 percentile；percent 范围为 0–100。"""
    ordered = sorted(values)
    if not ordered:
        raise ValueError("不能计算空样本的 percentile")
    if not 0 <= percent <= 100:
        raise ValueError("percent 必须在 0 到 100 之间")
    position = (len(ordered) - 1) * percent / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def summarize_requests(
    requests: list[dict],
    ttft_slo_ms: float,
    tpot_slo_ms: float,
    e2e_slo_ms: float,
) -> dict:
    if not requests:
        raise ValueError("requests 不能为空")
    required = {"ttft_ms", "tpot_ms", "e2e_ms", "success", "output_tokens"}
    for request in requests:
        missing = required - request.keys()
        if missing:
            raise ValueError(f"请求缺少字段：{sorted(missing)}")

    successful = [request for request in requests if request["success"]]
    slo_met = [
        request for request in successful
        if request["ttft_ms"] <= ttft_slo_ms
        and request["tpot_ms"] <= tpot_slo_ms
        and request["e2e_ms"] <= e2e_slo_ms
    ]

    result = {
        "request_count": len(requests),
        "success_rate": len(successful) / len(requests),
        "slo_compliance_all_requests": len(slo_met) / len(requests),
        "goodput_fraction": len(slo_met) / len(requests),
        "output_tokens": sum(request["output_tokens"] for request in successful),
        "slo": {
            "ttft_ms": ttft_slo_ms,
            "tpot_ms": tpot_slo_ms,
            "e2e_ms": e2e_slo_ms,
        },
    }
    for metric in ("ttft_ms", "tpot_ms", "e2e_ms"):
        samples = [request[metric] for request in successful]
        result[metric] = {
            f"p{p}": percentile(samples, p) for p in (50, 95, 99)
        } if samples else None
    return result


def sample_requests() -> list[dict]:
    return [
        {"ttft_ms": 180, "tpot_ms": 20, "e2e_ms": 1200, "success": True, "output_tokens": 52},
        {"ttft_ms": 220, "tpot_ms": 24, "e2e_ms": 1600, "success": True, "output_tokens": 60},
        {"ttft_ms": 350, "tpot_ms": 28, "e2e_ms": 2100, "success": True, "output_tokens": 65},
        {"ttft_ms": 500, "tpot_ms": 31, "e2e_ms": 2800, "success": True, "output_tokens": 72},
        {"ttft_ms": 700, "tpot_ms": 36, "e2e_ms": 3400, "success": True, "output_tokens": 76},
        {"ttft_ms": 850, "tpot_ms": 40, "e2e_ms": 4200, "success": True, "output_tokens": 84},
        {"ttft_ms": 980, "tpot_ms": 43, "e2e_ms": 5100, "success": True, "output_tokens": 90},
        {"ttft_ms": 1100, "tpot_ms": 46, "e2e_ms": 6200, "success": True, "output_tokens": 96},
        {"ttft_ms": 1250, "tpot_ms": 52, "e2e_ms": 7600, "success": True, "output_tokens": 105},
        {"ttft_ms": 1600, "tpot_ms": 60, "e2e_ms": 9200, "success": True, "output_tokens": 112},
        {"ttft_ms": 0, "tpot_ms": 0, "e2e_ms": 1000, "success": False, "output_tokens": 0},
        {"ttft_ms": 2100, "tpot_ms": 75, "e2e_ms": 13000, "success": True, "output_tokens": 128},
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="KV Cache 与推理指标教学工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    kv = subparsers.add_parser("kv", help="估算 KV Cache 逻辑字节数")
    for name in ("layers", "batch", "tokens", "kv-heads", "head-dim", "dtype-bytes"):
        kv.add_argument(f"--{name}", type=int, required=True)

    summarize = subparsers.add_parser("summarize", help="统计内置示例请求")
    summarize.add_argument("--ttft-slo-ms", type=float, default=1000)
    summarize.add_argument("--tpot-slo-ms", type=float, default=50)
    summarize.add_argument("--e2e-slo-ms", type=float, default=10000)

    args = parser.parse_args()
    if args.command == "kv":
        result = {
            "kv_bytes": kv_cache_bytes(
                args.layers, args.batch, args.tokens,
                args.kv_heads, args.head_dim, args.dtype_bytes,
            )
        }
        result["kv_gib"] = result["kv_bytes"] / 1024**3
        result["note"] = "仅为 K/V 逻辑 payload，不含对齐、元数据和其他显存。"
    else:
        result = summarize_requests(
            sample_requests(), args.ttft_slo_ms, args.tpot_slo_ms, args.e2e_slo_ms
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
