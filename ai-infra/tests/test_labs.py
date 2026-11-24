from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


roofline_module = load_module("roofline_lab", "code/ch03/roofline.py")
memory_module = load_module("memory_lab", "code/ch05/memory_estimator.py")
ring_module = load_module("ring_lab", "code/ch06/ring_allreduce.py")
inference_module = load_module("inference_lab", "code/ch09/inference_metrics.py")
batching_module = load_module("batching_lab", "code/ch10/batching_simulator.py")
Request = batching_module.Request


class RooflineTests(unittest.TestCase):
    def test_memory_bound_example(self):
        result = roofline_module.roofline(2e9, 100e6, 100e12, 1e12)
        self.assertAlmostEqual(result["arithmetic_intensity_flop_per_byte"], 20)
        self.assertAlmostEqual(result["ridge_point_flop_per_byte"], 100)
        self.assertAlmostEqual(result["attainable_flops_per_second"], 20e12)
        self.assertEqual(result["likely_bottleneck"], "memory")

    def test_compute_bound(self):
        result = roofline_module.roofline(1e12, 1e6, 100e12, 1e12)
        self.assertEqual(result["likely_bottleneck"], "compute")
        self.assertAlmostEqual(result["attainable_flops_per_second"], 100e12)

    def test_rejects_zero(self):
        with self.assertRaises(ValueError):
            roofline_module.roofline(0, 1, 1, 1)


class MemoryTests(unittest.TestCase):
    def test_common_sixteen_byte_assumption(self):
        result = memory_module.estimate_training_memory(1e9, 2, 2, 4, 8)
        self.assertAlmostEqual(result["static_gib"], 16e9 / 1024**3)

    def test_activation_and_workspace_are_added(self):
        result = memory_module.estimate_training_memory(1e9, 2, 2, 4, 8, 8, 2)
        self.assertAlmostEqual(result["estimated_total_gib"], result["static_gib"] + 10)


class RingTests(unittest.TestCase):
    def test_single_rank_has_no_communication(self):
        result = ring_module.ring_allreduce_model(1024, 1, 1e9, 1e-6)
        self.assertEqual(result["steps"], 0)
        self.assertEqual(result["per_rank_traffic_mib"], 0)
        self.assertEqual(result["modeled_seconds"], 0)

    def test_ring_traffic_formula(self):
        result = ring_module.ring_allreduce_model(8 * 1024**2, 8, 1e9, 0)
        self.assertAlmostEqual(result["per_rank_traffic_mib"], 14)


class InferenceTests(unittest.TestCase):
    def test_kv_cache_includes_k_and_v(self):
        result = inference_module.kv_cache_bytes(2, 2, 4, 3, 5, 2)
        self.assertEqual(result, 960)

    def test_percentile_uses_linear_interpolation(self):
        self.assertEqual(inference_module.percentile([1, 2, 3, 4], 50), 2.5)
        self.assertEqual(inference_module.percentile([1, 2, 3, 4], 100), 4)

    def test_failed_request_does_not_meet_slo(self):
        requests = inference_module.sample_requests()
        result = inference_module.summarize_requests(requests, 1000, 50, 10000)
        self.assertLess(result["goodput_fraction"], result["success_rate"])
        self.assertEqual(result["request_count"], 12)


class BatchingTests(unittest.TestCase):
    def setUp(self):
        self.requests = [Request("A", 0, 1), Request("B", 0, 3), Request("C", 0, 2)]

    def test_continuous_frees_slot_for_next_request(self):
        static = batching_module.static_batching(self.requests, 2)
        continuous = batching_module.continuous_batching(self.requests, 2)
        # 第一批需要 1 次 prefill + 3 次 decode，第二批需要 1 + 2 次。
        self.assertEqual(static["makespan_iterations"], 7)
        self.assertEqual(continuous["makespan_iterations"], 5)

    def test_no_request_starts_before_arrival(self):
        requests = [Request("later", 4, 1), Request("early", 0, 2)]
        for function in (batching_module.static_batching, batching_module.continuous_batching):
            result = function(requests, 2)
            for record in result["requests"]:
                self.assertGreaterEqual(record["start"], record["arrival"])

    def test_all_requests_finish_exactly_once(self):
        result = batching_module.continuous_batching(self.requests, 2)
        self.assertEqual(sorted(r["name"] for r in result["requests"]), ["A", "B", "C"])


if __name__ == "__main__":
    unittest.main()
