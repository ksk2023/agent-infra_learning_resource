"""模拟模型驱动的最小 Agent Loop；不包含真实模型能力或网络调用。"""

from __future__ import annotations

import ast
import json
import operator
from typing import Any, Callable, Protocol


class ToolError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def safe_calculate(expression: str) -> int | float:
    """用 AST 白名单计算四则运算，绝不使用 eval。"""
    if not isinstance(expression, str) or not expression.strip() or len(expression) > 100:
        raise ToolError("invalid_arguments", "expression 必须是 1–100 字符的表达式")

    binary = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}
    unary = {ast.UAdd: operator.pos, ast.USub: operator.neg}

    def visit(node: ast.AST) -> int | float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in binary:
            return binary[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in unary:
            return unary[type(node.op)](visit(node.operand))
        raise ToolError("unsupported_expression", "只允许数字、括号与四则运算")

    try:
        return visit(ast.parse(expression, mode="eval"))
    except ToolError:
        raise
    except (SyntaxError, ZeroDivisionError, OverflowError) as error:
        raise ToolError("calculation_error", "表达式无法计算") from error


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, function: Callable[..., Any]) -> None:
        if not name or name in self._tools:
            raise ValueError("工具名必须非空且唯一")
        self._tools[name] = function

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        if name not in self._tools:
            raise ToolError("unknown_tool", f"未注册工具：{name}")
        try:
            return self._tools[name](**arguments)
        except TypeError as error:
            raise ToolError("invalid_arguments", "工具参数与函数签名不匹配") from error


class Model(Protocol):
    def decide(self, context: list[dict[str, Any]]) -> dict[str, Any]: ...


class ScriptedModel:
    """按顺序返回预定动作，用于可重复测试。"""

    def __init__(self, outputs: list[dict[str, Any]]) -> None:
        if not outputs:
            raise ValueError("outputs 不能为空")
        self.outputs = outputs
        self.index = 0

    def decide(self, context: list[dict[str, Any]]) -> dict[str, Any]:
        del context
        output = self.outputs[min(self.index, len(self.outputs) - 1)]
        self.index += 1
        return output


def run_agent(model: Model, tools: ToolRegistry, goal: str, max_steps: int = 6) -> dict[str, Any]:
    if max_steps < 1:
        raise ValueError("max_steps 必须至少为 1")
    context: list[dict[str, Any]] = [{"type": "goal", "content": goal}]
    history: list[dict[str, Any]] = []

    for step in range(1, max_steps + 1):
        action = model.decide(context)
        if not isinstance(action, dict) or action.get("type") not in {"tool_call", "final"}:
            return {"status": "protocol_error", "steps": step, "history": history}

        if action["type"] == "final":
            answer = action.get("answer")
            if not isinstance(answer, str) or not answer.strip():
                return {"status": "protocol_error", "steps": step, "history": history}
            history.append({"step": step, "action": action})
            return {"status": "completed", "answer": answer, "steps": step, "history": history}

        name = action.get("name")
        arguments = action.get("arguments")
        call_id = f"call-{step}"
        record: dict[str, Any] = {"step": step, "action": action, "call_id": call_id}
        if not isinstance(name, str) or not isinstance(arguments, dict):
            return {"status": "protocol_error", "steps": step, "history": history + [record]}
        try:
            value = tools.execute(name, arguments)
            observation = {"call_id": call_id, "ok": True, "content": value}
        except ToolError as error:
            observation = {"call_id": call_id, "ok": False, "error_type": error.code, "content": str(error)}
        except Exception as error:  # 教学 Runner：把普通工具异常变成受控观察。
            observation = {"call_id": call_id, "ok": False, "error_type": "tool_exception", "content": type(error).__name__}
        record["observation"] = observation
        history.append(record)
        context.extend([{"type": "action", "content": action}, {"type": "observation", "content": observation}])

    return {"status": "max_steps_exceeded", "steps": max_steps, "history": history}


def main() -> None:
    tools = ToolRegistry()
    tools.register("calculator", safe_calculate)
    model = ScriptedModel([
        {"type": "tool_call", "name": "calculator", "arguments": {"expression": "2 + 3 * 4"}},
        {"type": "final", "answer": "计算结果是 14"},
    ])
    result = run_agent(model, tools, "计算 2 + 3 * 4")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
