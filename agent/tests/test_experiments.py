from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 {relative_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


structured = load_module("tutorial_structured_output", "code/ch02/structured_output.py")
mini_agent = load_module("tutorial_mini_agent", "code/ch03/mini_agent.py")
dag = load_module("tutorial_dag_planner", "code/ch05/dag_planner.py")
memory = load_module("tutorial_memory_context", "code/ch06/memory_context.py")
rag = load_module("tutorial_rag_lab", "code/ch07/rag_lab.py")
checkpoint = load_module("tutorial_checkpoint_runner", "code/ch08/checkpoint_runner.py")
evaluation = load_module("tutorial_eval_metrics", "code/ch12/eval_metrics.py")
trace = load_module("tutorial_trace_metrics", "code/ch13/trace_metrics.py")
policy = load_module("tutorial_policy_gate", "code/ch14/policy_gate.py")


class StructuredOutputTests(unittest.TestCase):
    def test_valid_tool_call_and_final(self):
        action = structured.parse_action('{"type":"tool_call","name":"search","arguments":{"q":"agent"}}')
        self.assertEqual(action["name"], "search")
        final = structured.parse_action('{"type":"final","answer":"完成"}')
        self.assertEqual(final["answer"], "完成")

    def test_rejects_code_fence(self):
        with self.assertRaises(structured.ActionError) as caught:
            structured.parse_action('```json\n{"type":"final","answer":"14"}\n```')
        self.assertEqual(caught.exception.code, "invalid_json")

    def test_rejects_extra_and_missing_fields(self):
        for text in [
            '{"type":"final","answer":"14","approved":true}',
            '{"type":"tool_call","name":"search"}',
        ]:
            with self.subTest(text=text), self.assertRaises(structured.ActionError) as caught:
                structured.parse_action(text)
            self.assertEqual(caught.exception.code, "invalid_fields")

    def test_rejects_empty_unknown_and_non_object(self):
        cases = [("", "empty_input"), ("[]", "not_object"), ('{"type":"chat"}', "unknown_type")]
        for text, code in cases:
            with self.subTest(code=code), self.assertRaises(structured.ActionError) as caught:
                structured.parse_action(text)
            self.assertEqual(caught.exception.code, code)


class MiniAgentTests(unittest.TestCase):
    def setUp(self):
        self.tools = mini_agent.ToolRegistry()
        self.tools.register("calculator", mini_agent.safe_calculate)

    def test_tool_observation_returns_to_loop(self):
        model = mini_agent.ScriptedModel([
            {"type": "tool_call", "name": "calculator", "arguments": {"expression": "2+3*4"}},
            {"type": "final", "answer": "14"},
        ])
        result = mini_agent.run_agent(model, self.tools, "计算")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["steps"], 2)
        self.assertEqual(result["history"][0]["observation"]["content"], 14)

    def test_unknown_tool_is_controlled_observation(self):
        model = mini_agent.ScriptedModel([
            {"type": "tool_call", "name": "shell", "arguments": {}},
            {"type": "final", "answer": "无法调用"},
        ])
        result = mini_agent.run_agent(model, self.tools, "测试")
        observation = result["history"][0]["observation"]
        self.assertFalse(observation["ok"])
        self.assertEqual(observation["error_type"], "unknown_tool")
        self.assertEqual(result["status"], "completed")

    def test_max_steps_stops_repetition(self):
        model = mini_agent.ScriptedModel([
            {"type": "tool_call", "name": "calculator", "arguments": {"expression": "1+1"}}
        ])
        result = mini_agent.run_agent(model, self.tools, "不要停止", max_steps=2)
        self.assertEqual(result["status"], "max_steps_exceeded")
        self.assertEqual(result["steps"], 2)
        self.assertEqual(len(result["history"]), 2)

    def test_invalid_model_action_is_protocol_error(self):
        model = mini_agent.ScriptedModel([{"type": "text", "content": "你好"}])
        result = mini_agent.run_agent(model, self.tools, "测试")
        self.assertEqual(result["status"], "protocol_error")

    def test_calculator_rejects_code_and_bad_arguments(self):
        for expression in ["__import__('os')", "1/0", "", "True"]:
            with self.subTest(expression=expression), self.assertRaises(mini_agent.ToolError):
                mini_agent.safe_calculate(expression)

    def test_tool_signature_mismatch_is_structured(self):
        with self.assertRaises(mini_agent.ToolError) as caught:
            self.tools.execute("calculator", {"wrong": "2+2"})
        self.assertEqual(caught.exception.code, "invalid_arguments")


class DagPlannerTests(unittest.TestCase):
    def test_topological_batches(self):
        tasks = [dag.Task("a"), dag.Task("b"), dag.Task("c", ("a", "b")), dag.Task("d", ("c",))]
        self.assertEqual(dag.topological_batches(tasks), [["a", "b"], ["c"], ["d"]])

    def test_cycle_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "环"):
            dag.topological_batches([dag.Task("a", ("b",)), dag.Task("b", ("a",))])

    def test_unknown_self_and_duplicate_dependencies_are_rejected(self):
        cases = [
            [dag.Task("a", ("missing",))],
            [dag.Task("a", ("a",))],
            [dag.Task("a"), dag.Task("a")],
        ]
        for tasks in cases:
            with self.subTest(tasks=tasks), self.assertRaises(ValueError):
                dag.topological_batches(tasks)


class MemoryContextTests(unittest.TestCase):
    def setUp(self):
        self.store = memory.MemoryStore()
        self.store.put(memory.Memory("a", "user:A", "中文 回答 简洁", 1, priority=2))
        self.store.put(memory.Memory("b", "user:B", "中文 回答 详细", 1))
        self.store.put(memory.Memory("old", "user:A", "中文 旧回答", 1, expires_at=5))

    def test_scope_isolation(self):
        result = self.store.search("user:A", "中文", now=2)
        memory_ids = [item.memory_id for item in result]
        self.assertIn("a", memory_ids)
        self.assertNotIn("b", memory_ids)

    def test_expired_memory_is_not_returned(self):
        result = self.store.search("user:A", "中文", now=5)
        self.assertNotIn("old", [item.memory_id for item in result])

    def test_context_budget_prefers_priority(self):
        packed = memory.pack_context([
            memory.ContextSection("goal", "目标", 100),
            memory.ContextSection("history", "很长的历史", 1),
        ], max_chars=3)
        self.assertEqual(packed["included"], ["goal"])
        self.assertEqual(packed["omitted"], ["history"])
        self.assertLessEqual(packed["used_chars"], 3)

    def test_invalid_expiry_is_rejected(self):
        with self.assertRaises(ValueError):
            self.store.put(memory.Memory("bad", "user:A", "内容", 5, expires_at=5))


class RagTests(unittest.TestCase):
    def setUp(self):
        self.index = rag.TfIdfIndex({
            "refund": "退款 政策 三十天 申请",
            "ticket": "工单 状态 负责人",
        })

    def test_retrieval_ranks_relevant_document(self):
        hits = self.index.search("退款 申请")
        self.assertEqual(hits[0]["doc_id"], "refund")

    def test_fabricated_citation_is_rejected(self):
        hits = [{"doc_id": "refund"}]
        result = rag.validate_citations(["refund", "invented"], hits)
        self.assertFalse(result["all_exist_in_context"])
        self.assertEqual(result["invalid"], ["invented"])

    def test_recall_at_k(self):
        self.assertEqual(rag.recall_at_k(["a", "b", "c"], {"a", "c"}, 3), 1.0)
        self.assertEqual(rag.recall_at_k(["a", "b", "c"], {"a", "c"}, 1), 0.5)
        with self.assertRaises(ValueError):
            rag.recall_at_k([], set(), 1)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="test-checkpoint-", dir=ROOT)
        self.store = checkpoint.CheckpointStore(self.temporary.name)
        self.ledger = checkpoint.IdempotentLedger()

    def tearDown(self):
        self.temporary.cleanup()

    def test_resume_skips_completed_and_applies_one_effect(self):
        steps = ["prepare", "draft", "publish"]
        first = checkpoint.run_workflow(self.store, "run-1", steps, self.ledger, fail_before="publish")
        self.assertEqual(first["status"], "failed_before_step")
        second = checkpoint.run_workflow(self.store, "run-1", steps, self.ledger)
        self.assertEqual(second["status"], "completed")
        skipped = [event["step"] for event in second["events"] if event["event"] == "skipped_completed"]
        self.assertEqual(skipped, ["prepare", "draft"])
        self.assertEqual(len(self.ledger.effects), 1)

    def test_duplicate_operation_is_idempotent(self):
        payload = {"action": "write", "amount": 10}
        first = self.ledger.apply("op-1", payload)
        second = self.ledger.apply("op-1", dict(reversed(list(payload.items()))))
        self.assertEqual(first["status"], "applied")
        self.assertEqual(second["status"], "already_applied")
        self.assertEqual(len(self.ledger.effects), 1)

    def test_operation_id_cannot_be_reused_with_other_parameters(self):
        self.ledger.apply("op-1", {"amount": 10})
        with self.assertRaises(ValueError):
            self.ledger.apply("op-1", {"amount": 20})

    def test_checkpoint_is_persistent_and_path_is_constrained(self):
        state = self.store.load("run-2")
        state["completed"]["prepare"] = {"ok": True}
        self.store.save(state)
        self.assertEqual(self.store.load("run-2")["completed"], {"prepare": {"ok": True}})
        with self.assertRaises(ValueError):
            self.store.load("../escape")


class EvaluationTests(unittest.TestCase):
    def test_invalid_agent_failure_and_safety_are_distinct(self):
        result = evaluation.summarize_trials([
            {"status": "success"}, {"status": "success"},
            {"status": "agent_failure"}, {"status": "safety_violation"},
            {"status": "invalid"},
        ])
        self.assertEqual(result["valid"], 4)
        self.assertEqual(result["invalid"], 1)
        self.assertEqual(result["agent_failure"], 1)
        self.assertEqual(result["safety_violation"], 1)
        self.assertEqual(result["single_run_success_rate"], 0.5)

    def test_pass_at_k_and_pass_all_k(self):
        self.assertTrue(math.isclose(evaluation.pass_at_k(0.5, 3), 0.875))
        self.assertTrue(math.isclose(evaluation.pass_all_k(0.5, 3), 0.125))
        self.assertEqual(evaluation.pass_at_k(0, 3), 0)
        self.assertEqual(evaluation.pass_all_k(1, 3), 1)

    def test_no_valid_trials_has_no_rate(self):
        self.assertIsNone(evaluation.summarize_trials([{"status": "invalid"}])["single_run_success_rate"])

    def test_invalid_probability_k_and_status_are_rejected(self):
        for p, k in [(-0.1, 1), (1.1, 1), (0.5, 0), (True, 1), (0.5, True)]:
            with self.subTest(p=p, k=k), self.assertRaises(ValueError):
                evaluation.pass_at_k(p, k)
        with self.assertRaises(ValueError):
            evaluation.summarize_trials([{"status": "unknown"}])


class TraceMetricsTests(unittest.TestCase):
    @staticmethod
    def run(run_id, status="completed", outcome=True, violation=False, latency=100, cost=0.1):
        return {
            "run_id": run_id, "status": status, "outcome_passed": outcome,
            "policy_violation": violation, "latency_ms": latency,
            "model_calls": 1, "tool_errors": 0, "cost": cost,
        }

    def test_clean_success_latency_and_cost(self):
        runs = [
            self.run("a", latency=100, cost=0.1),
            self.run("b", latency=200, cost=0.2),
            self.run("c", status="failed", outcome=False, latency=300, cost=0.3),
            self.run("d", violation=True, latency=400, cost=0.4),
            self.run("e", status="invalid", outcome=False, latency=999, cost=0.5),
        ]
        result = trace.summarize_runs(runs)
        self.assertEqual(result["valid_runs"], 4)
        self.assertEqual(result["clean_successful_runs"], 2)
        self.assertEqual(result["success_rate"], 0.5)
        self.assertEqual(result["latency_ms_nearest_rank"], {"p50": 200, "p95": 400, "p99": 400})
        self.assertEqual(result["total_cost"], 1.5)
        self.assertEqual(result["cost_per_clean_success"], 0.75)
        self.assertEqual(result["policy_violations"], 1)

    def test_zero_clean_success_has_no_unit_cost(self):
        result = trace.summarize_runs([self.run("bad", violation=True, cost=2)])
        self.assertEqual(result["success_rate"], 0)
        self.assertIsNone(result["cost_per_clean_success"])

    def test_percentile_empty_and_invalid_values(self):
        self.assertIsNone(trace.percentile_nearest_rank([], 95))
        with self.assertRaises(ValueError):
            trace.percentile_nearest_rank([1], 0)
        with self.assertRaises(ValueError):
            trace.summarize_runs([self.run("negative", cost=-1)])


class PolicyGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = policy.PolicyGate()
        self.gate.register_tool("read_ticket", "read")
        self.gate.register_tool("refund", "high_risk_write")
        self.gate.grant("user:A", "read_ticket", "ticket:A")
        self.gate.grant("user:A", "refund", "order:A")
        self.refund = {"resource": "order:A", "amount": 20}

    def test_read_scope_and_unknown_tool(self):
        self.assertTrue(self.gate.decide("user:A", "read_ticket", {"resource": "ticket:A"})["allowed"])
        unknown = self.gate.decide("user:A", "shell", {"resource": "ticket:A"})
        self.assertEqual(unknown["reason"], "unknown_tool")

    def test_cross_tenant_resource_is_denied(self):
        result = self.gate.decide("user:A", "read_ticket", {"resource": "ticket:B"})
        self.assertEqual(result["reason"], "resource_scope_denied")

    def test_high_risk_write_requires_approval(self):
        self.assertEqual(self.gate.decide("user:A", "refund", self.refund)["reason"], "approval_required")
        self.gate.approve("user:A", "refund", self.refund)
        self.assertTrue(self.gate.decide("user:A", "refund", self.refund)["allowed"])

    def test_approval_is_bound_to_canonical_parameters(self):
        self.gate.approve("user:A", "refund", self.refund)
        reordered = {"amount": 20, "resource": "order:A"}
        self.assertTrue(self.gate.decide("user:A", "refund", reordered)["allowed"])
        tampered = self.gate.decide("user:A", "refund", {"resource": "order:A", "amount": 200})
        self.assertEqual(tampered["reason"], "approval_required")

    def test_model_claimed_approval_does_not_bypass_gate(self):
        forged = self.gate.decide("user:A", "refund", {**self.refund, "approved": True})
        self.assertFalse(forged["allowed"])
        self.assertEqual(forged["reason"], "approval_required")

    def test_approval_does_not_override_resource_scope(self):
        foreign = {"resource": "order:B", "amount": 20}
        self.gate.approve("user:A", "refund", foreign)
        self.assertEqual(self.gate.decide("user:A", "refund", foreign)["reason"], "resource_scope_denied")


if __name__ == "__main__":
    unittest.main()
