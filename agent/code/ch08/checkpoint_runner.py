"""JSON 原子 checkpoint、故障恢复与模拟幂等副作用；不调用外部服务。"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any


class CheckpointStore:
    """每个 run 一个 JSON 文件，通过同目录临时文件和 os.replace 原子替换。"""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, run_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
            raise ValueError("run_id 只能包含字母、数字、下划线和连字符")
        return self.directory / f"{run_id}.json"

    def load(self, run_id: str) -> dict[str, Any]:
        path = self._path(run_id)
        if not path.exists():
            return {"run_id": run_id, "version": 1, "completed": {}}
        state = json.loads(path.read_text(encoding="utf-8"))
        if state.get("run_id") != run_id or state.get("version") != 1:
            raise ValueError("checkpoint 身份或版本不兼容")
        if not isinstance(state.get("completed"), dict):
            raise ValueError("checkpoint completed 必须是 object")
        return state

    def save(self, state: dict[str, Any]) -> None:
        path = self._path(state["run_id"])
        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.directory,
                prefix=path.name + ".", suffix=".tmp", delete=False,
            ) as temporary:
                temporary_name = temporary.name
                json.dump(state, temporary, ensure_ascii=False, indent=2, sort_keys=True)
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_name, path)
        finally:
            if temporary_name and os.path.exists(temporary_name):
                os.unlink(temporary_name)


class IdempotentLedger:
    """模拟服务端幂等约束：同一 operation_id 不能产生第二条副作用。"""

    def __init__(self) -> None:
        self._operations: dict[str, str] = {}
        self.effects: list[dict[str, Any]] = []

    @staticmethod
    def _canonical(payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def apply(self, operation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        canonical = self._canonical(payload)
        if operation_id in self._operations:
            if self._operations[operation_id] != canonical:
                raise ValueError("同一 operation_id 不能绑定不同参数")
            return {"status": "already_applied", "operation_id": operation_id}
        self._operations[operation_id] = canonical
        self.effects.append({"operation_id": operation_id, **payload})
        return {"status": "applied", "operation_id": operation_id}


def run_workflow(
    store: CheckpointStore,
    run_id: str,
    steps: list[str],
    ledger: IdempotentLedger,
    fail_before: str | None = None,
) -> dict[str, Any]:
    """从已确认 checkpoint 继续；fail_before 在指定步骤执行前注入故障。"""
    if not steps or len(set(steps)) != len(steps):
        raise ValueError("steps 必须非空且不能重复")
    state = store.load(run_id)
    already_completed = set(state["completed"])
    events: list[dict[str, Any]] = []

    for step in steps:
        if step in state["completed"]:
            events.append({"step": step, "event": "skipped_completed"})
            continue
        if step == fail_before:
            return {
                "run_id": run_id, "status": "failed_before_step", "failed_step": step,
                "completed": sorted(state["completed"]), "events": events,
            }

        if step == "publish":
            result = ledger.apply(
                f"{run_id}:publish",
                {"action": "publish", "destination": "demo-audience", "content": "approved-demo"},
            )
        else:
            result = {"status": "computed", "value": f"result-of-{step}"}
        state["completed"][step] = result
        store.save(state)
        events.append({"step": step, "event": "executed_and_checkpointed"})

    return {
        "run_id": run_id, "status": "completed", "resumed": bool(already_completed),
        "completed": sorted(state["completed"]), "events": events,
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="agent-checkpoint-", dir=Path.cwd()) as directory:
        store = CheckpointStore(directory)
        ledger = IdempotentLedger()
        first = run_workflow(store, "demo-run", ["prepare", "draft", "publish"], ledger, fail_before="publish")
        second = run_workflow(store, "demo-run", ["prepare", "draft", "publish"], ledger)
        duplicate = ledger.apply(
            "demo-run:publish",
            {"action": "publish", "destination": "demo-audience", "content": "approved-demo"},
        )
        print(json.dumps({
            "first": first, "resumed": second, "duplicate_retry": duplicate,
            "external_effect_count": len(ledger.effects),
            "note": "临时 checkpoint 已自动清理；真实系统还需崩溃一致性与外部状态对账。",
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
