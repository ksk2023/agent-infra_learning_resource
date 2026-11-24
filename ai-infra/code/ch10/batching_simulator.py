"""以相同 iteration 成本比较 static 与 continuous batching 的教学模拟。"""

from __future__ import annotations

from dataclasses import dataclass
import json
from statistics import mean


@dataclass(frozen=True)
class Request:
    name: str
    arrival: int
    decode_steps: int

    def __post_init__(self) -> None:
        if self.arrival < 0 or self.decode_steps <= 0:
            raise ValueError("arrival 不能小于 0，decode_steps 必须大于 0")


def _result(records: list[dict], makespan: int, capacity: int, occupied_slots: int, policy: str) -> dict:
    return {
        "policy": policy,
        "makespan_iterations": makespan,
        "mean_request_latency_iterations": mean(r["finish"] - r["arrival"] for r in records),
        "occupied_slot_fraction": occupied_slots / (makespan * capacity),
        "requests": sorted(records, key=lambda record: record["name"]),
        "note": "每请求一次 prefill iteration；每轮 decode 成本相同，不代表真实 GPU 时间。",
    }


def static_batching(requests: list[Request], capacity: int) -> dict:
    """固定分组；组内完成后才启动下一组，短请求结束后槽位仍被占用。"""
    if capacity < 1:
        raise ValueError("capacity 必须至少为 1")
    if not requests:
        raise ValueError("requests 不能为空")

    ordered = sorted(requests, key=lambda request: (request.arrival, request.name))
    now = 0
    occupied_slots = 0
    records: list[dict] = []

    for offset in range(0, len(ordered), capacity):
        group = ordered[offset:offset + capacity]
        start = max([now] + [request.arrival for request in group])
        batch_steps = 1 + max(request.decode_steps for request in group)
        for request in group:
            records.append({
                "name": request.name,
                "arrival": request.arrival,
                "start": start,
                "finish": start + 1 + request.decode_steps,
            })
        occupied_slots += len(group) * batch_steps
        now = start + batch_steps
    return _result(records, now, capacity, occupied_slots, "static")


def continuous_batching(requests: list[Request], capacity: int) -> dict:
    """每轮处理活动请求；完成后的槽位在下一轮可被新请求补充。"""
    if capacity < 1:
        raise ValueError("capacity 必须至少为 1")
    if not requests:
        raise ValueError("requests 不能为空")

    pending = sorted(requests, key=lambda request: (request.arrival, request.name))
    next_index = 0
    active: list[dict] = []
    records: list[dict] = []
    now = 0
    occupied_slots = 0

    while next_index < len(pending) or active:
        while (
            next_index < len(pending)
            and pending[next_index].arrival <= now
            and len(active) < capacity
        ):
            request = pending[next_index]
            active.append({
                "request": request,
                "start": now,
                "remaining": 1 + request.decode_steps,
            })
            next_index += 1

        if not active:
            now = pending[next_index].arrival
            continue

        occupied_slots += len(active)
        still_active: list[dict] = []
        for item in active:
            item["remaining"] -= 1
            request = item["request"]
            if item["remaining"] == 0:
                records.append({
                    "name": request.name,
                    "arrival": request.arrival,
                    "start": item["start"],
                    "finish": now + 1,
                })
            else:
                still_active.append(item)
        active = still_active
        now += 1

    return _result(records, now, capacity, occupied_slots, "continuous")


def sample_requests() -> list[Request]:
    return [
        Request("A", 0, 2),
        Request("B", 0, 6),
        Request("C", 0, 3),
        Request("D", 0, 4),
        Request("E", 1, 2),
        Request("F", 2, 5),
        Request("G", 3, 1),
        Request("H", 4, 4),
    ]


def main() -> None:
    requests = sample_requests()
    capacity = 4
    result = {
        "static": static_batching(requests, capacity),
        "continuous": continuous_batching(requests, capacity),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
