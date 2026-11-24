"""Roofline 估算器：只使用 Python 标准库。"""

from __future__ import annotations

import argparse
import json


def roofline(flops: float, bytes_moved: float, peak_flops: float, bandwidth: float) -> dict:
    """返回一致单位下的 Roofline 上界；时间单位为秒，带宽单位为字节/秒。"""
    values = {
        "flops": flops,
        "bytes_moved": bytes_moved,
        "peak_flops": peak_flops,
        "bandwidth": bandwidth,
    }
    for name, value in values.items():
        if value <= 0:
            raise ValueError(f"{name} 必须大于 0")

    intensity = flops / bytes_moved
    ridge_point = peak_flops / bandwidth
    attainable_flops = min(peak_flops, bandwidth * intensity)
    time_lower_bound = max(flops / peak_flops, bytes_moved / bandwidth)
    bottleneck = "memory" if intensity < ridge_point else "compute"

    return {
        "arithmetic_intensity_flop_per_byte": intensity,
        "ridge_point_flop_per_byte": ridge_point,
        "attainable_flops_per_second": attainable_flops,
        "time_lower_bound_seconds": time_lower_bound,
        "likely_bottleneck": bottleneck,
        "note": "理论下界，不包含 launch、同步、通信、排队和实现效率。",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="计算 Roofline 性能上界")
    parser.add_argument("--flops", type=float, required=True, help="算子 FLOPs")
    parser.add_argument("--bytes", type=float, required=True, dest="bytes_moved", help="访存字节数")
    parser.add_argument("--peak-flops", type=float, required=True, help="峰值 FLOP/s")
    parser.add_argument("--bandwidth", type=float, required=True, help="带宽，byte/s")
    args = parser.parse_args()
    result = roofline(args.flops, args.bytes_moved, args.peak_flops, args.bandwidth)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
