"""演示记忆作用域、过期和上下文预算；不是生产向量数据库。"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re


@dataclass(frozen=True)
class Memory:
    memory_id: str
    scope: str
    content: str
    created_at: int
    expires_at: int | None = None
    priority: int = 0


class MemoryStore:
    def __init__(self) -> None:
        self._items: dict[str, Memory] = {}

    def put(self, memory: Memory) -> None:
        if not memory.memory_id or not memory.scope or not memory.content:
            raise ValueError("memory_id、scope、content 不能为空")
        if memory.expires_at is not None and memory.expires_at <= memory.created_at:
            raise ValueError("expires_at 必须晚于 created_at")
        self._items[memory.memory_id] = memory

    def search(self, scope: str, query: str, now: int, limit: int = 3) -> list[Memory]:
        if limit < 1:
            raise ValueError("limit 必须至少为 1")
        terms = set(re.findall(r"[\w\u4e00-\u9fff]+", query.lower()))
        candidates = []
        for item in self._items.values():
            if item.scope != scope or (item.expires_at is not None and item.expires_at <= now):
                continue
            item_terms = set(re.findall(r"[\w\u4e00-\u9fff]+", item.content.lower()))
            score = len(terms & item_terms)
            if score:
                candidates.append((score, item.priority, item.created_at, item))
        candidates.sort(key=lambda entry: (entry[0], entry[1], entry[2], entry[3].memory_id), reverse=True)
        return [entry[3] for entry in candidates[:limit]]


@dataclass(frozen=True)
class ContextSection:
    name: str
    content: str
    priority: int


def pack_context(sections: list[ContextSection], max_chars: int) -> dict:
    if max_chars < 1:
        raise ValueError("max_chars 必须大于 0")
    selected: list[ContextSection] = []
    used = 0
    omitted = []
    for section in sorted(sections, key=lambda item: item.priority, reverse=True):
        size = len(section.content)
        if used + size <= max_chars:
            selected.append(section)
            used += size
        else:
            omitted.append(section.name)
    return {
        "text": "\n".join(section.content for section in selected),
        "included": [section.name for section in selected],
        "omitted": omitted,
        "used_chars": used,
    }


def main() -> None:
    store = MemoryStore()
    store.put(Memory("m1", "user:A", "用户偏好简洁中文回答", created_at=1))
    store.put(Memory("m2", "user:B", "用户偏好英文回答", created_at=1))
    store.put(Memory("m3", "user:A", "旧项目偏好详细表格", created_at=1, expires_at=5))
    memories = store.search("user:A", "中文 回答", now=10)
    packed = pack_context([
        ContextSection("goal", "当前目标：回答用户问题", 100),
        ContextSection("memory", "\n".join(item.content for item in memories), 50),
        ContextSection("old_history", "不相关的旧对话" * 20, 1),
    ], max_chars=60)
    print(json.dumps({"memories": [item.memory_id for item in memories], "context": packed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
