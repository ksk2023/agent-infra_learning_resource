"""模型之外的策略门：资源授权与绑定参数哈希的高风险审批。"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any


@dataclass(frozen=True)
class ToolPolicy:
    risk: str


class PolicyGate:
    """教学策略门，不是完整 IAM；身份必须来自可信会话而非模型文本。"""

    def __init__(self) -> None:
        self._tools: dict[str, ToolPolicy] = {}
        self._scopes: dict[str, dict[str, set[str]]] = {}
        self._approvals: set[tuple[str, str, str]] = set()

    def register_tool(self, name: str, risk: str = "read") -> None:
        if not name or name in self._tools or risk not in {"read", "high_risk_write"}:
            raise ValueError("工具必须唯一且风险级别有效")
        self._tools[name] = ToolPolicy(risk)

    def grant(self, actor: str, tool_name: str, resource: str) -> None:
        if tool_name not in self._tools or not actor or not resource:
            raise ValueError("授权需要已注册工具、主体和资源")
        self._scopes.setdefault(actor, {}).setdefault(tool_name, set()).add(resource)

    @staticmethod
    def action_hash(tool_name: str, arguments: dict[str, Any]) -> str:
        try:
            canonical = json.dumps(
                {"tool": tool_name, "arguments": arguments},
                ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
            )
        except (TypeError, ValueError) as error:
            raise ValueError("工具参数必须是有限 JSON 值") from error
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def approve(self, actor: str, tool_name: str, arguments: dict[str, Any]) -> str:
        if tool_name not in self._tools or not isinstance(arguments, dict):
            raise ValueError("审批对象必须是已注册工具和参数 object")
        digest = self.action_hash(tool_name, arguments)
        self._approvals.add((actor, tool_name, digest))
        return digest

    def decide(self, actor: str, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """任何 arguments['approved'] 字段都不会被当作审批依据。"""
        if not isinstance(arguments, dict):
            return {"allowed": False, "reason": "invalid_arguments"}
        if tool_name not in self._tools:
            return {"allowed": False, "reason": "unknown_tool"}
        resource = arguments.get("resource")
        if not isinstance(resource, str) or not resource:
            return {"allowed": False, "reason": "invalid_resource"}
        if resource not in self._scopes.get(actor, {}).get(tool_name, set()):
            return {"allowed": False, "reason": "resource_scope_denied"}

        digest = self.action_hash(tool_name, arguments)
        if self._tools[tool_name].risk == "high_risk_write":
            if (actor, tool_name, digest) not in self._approvals:
                return {"allowed": False, "reason": "approval_required", "action_hash": digest}
        return {"allowed": True, "reason": "allowed", "action_hash": digest}


def main() -> None:
    gate = PolicyGate()
    gate.register_tool("read_ticket", "read")
    gate.register_tool("issue_refund", "high_risk_write")
    gate.grant("user:A", "read_ticket", "ticket:A-1")
    gate.grant("user:A", "issue_refund", "order:A-1")

    read = gate.decide("user:A", "read_ticket", {"resource": "ticket:A-1"})
    refund = {"resource": "order:A-1", "amount": 20, "currency": "CNY"}
    before = gate.decide("user:A", "issue_refund", refund)
    approval_hash = gate.approve("user:A", "issue_refund", refund)
    after = gate.decide("user:A", "issue_refund", refund)
    tampered = gate.decide("user:A", "issue_refund", {**refund, "amount": 200})
    forged = gate.decide("user:A", "issue_refund", {"resource": "order:A-1", "amount": 20, "currency": "CNY", "approved": True})
    unknown = gate.decide("user:A", "shell", {"resource": "order:A-1"})
    cross_tenant = gate.decide("user:A", "read_ticket", {"resource": "ticket:B-9"})

    print(json.dumps({
        "read": read, "before_approval": before, "approval_hash": approval_hash,
        "after_approval": after, "tampered_parameters": tampered,
        "forged_approval_field": forged, "unknown_tool": unknown,
        "cross_tenant": cross_tenant,
        "note": "所有动作仅做策略判定，未执行真实退款或数据访问。",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
