"""教学用 DAG 校验与按层拓扑排序；不执行真实任务。"""

from __future__ import annotations

from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Task:
    task_id: str
    dependencies: tuple[str, ...] = ()


def topological_batches(tasks: list[Task]) -> list[list[str]]:
    if not tasks:
        raise ValueError("任务列表不能为空")
    by_id: dict[str, Task] = {}
    for task in tasks:
        if not task.task_id.strip():
            raise ValueError("task_id 不能为空")
        if task.task_id in by_id:
            raise ValueError(f"重复 task_id：{task.task_id}")
        by_id[task.task_id] = task

    remaining = set(by_id)
    for task in tasks:
        unknown = set(task.dependencies) - set(by_id)
        if unknown:
            raise ValueError(f"{task.task_id} 存在未知依赖：{sorted(unknown)}")
        if task.task_id in task.dependencies:
            raise ValueError(f"{task.task_id} 不能依赖自己")

    batches: list[list[str]] = []
    completed: set[str] = set()
    while remaining:
        ready = sorted(
            task_id for task_id in remaining
            if set(by_id[task_id].dependencies).issubset(completed)
        )
        if not ready:
            raise ValueError(f"依赖图存在环：{sorted(remaining)}")
        batches.append(ready)
        completed.update(ready)
        remaining.difference_update(ready)
    return batches


def main() -> None:
    tasks = [
        Task("collect"),
        Task("outline"),
        Task("draft", ("collect", "outline")),
        Task("verify", ("draft",)),
        Task("publish", ("verify",)),
    ]
    print(json.dumps({"batches": topological_batches(tasks)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
