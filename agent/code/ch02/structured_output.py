"""严格解析教学用 Agent 动作；只验证协议，不执行任何工具。"""

from __future__ import annotations

import json
from typing import Any


class ActionError(ValueError):
    """带稳定错误代码的协议错误。"""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_action(text: str) -> dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        raise ActionError("empty_input", "动作输入不能为空")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise ActionError("invalid_json", "输入必须是完整 JSON") from error

    if not isinstance(value, dict):
        raise ActionError("not_object", "动作顶层必须是 object")

    action_type = value.get("type")
    if action_type == "tool_call":
        expected = {"type", "name", "arguments"}
        if set(value) != expected:
            raise ActionError("invalid_fields", "tool_call 字段必须恰好为 type/name/arguments")
        if not isinstance(value["name"], str) or not value["name"].strip():
            raise ActionError("invalid_name", "工具名必须是非空字符串")
        if not isinstance(value["arguments"], dict):
            raise ActionError("invalid_arguments", "arguments 必须是 object")
        return value

    if action_type == "final":
        if set(value) != {"type", "answer"}:
            raise ActionError("invalid_fields", "final 字段必须恰好为 type/answer")
        if not isinstance(value["answer"], str) or not value["answer"].strip():
            raise ActionError("invalid_answer", "answer 必须是非空字符串")
        return value

    raise ActionError("unknown_type", "type 只支持 tool_call 或 final")


def main() -> None:
    samples = [
        '{"type":"tool_call","name":"calculator","arguments":{"expression":"2+3*4"}}',
        '{"type":"final","answer":"14"}',
        '```json\n{"type":"final","answer":"14"}\n```',
        '{"type":"tool_call","name":"calculator"}',
    ]
    results = []
    for sample in samples:
        try:
            results.append({"ok": True, "action": parse_action(sample)})
        except ActionError as error:
            results.append({"ok": False, "error_type": error.code, "error": str(error)})
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
