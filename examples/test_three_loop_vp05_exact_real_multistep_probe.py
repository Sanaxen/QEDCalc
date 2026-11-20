"""Offline parity tests for actual-order read-only original IBP path pilot."""
from __future__ import annotations

import unittest

from examples import three_loop_vp05_exact_real_multistep_probe as pilot


class RealMultistepProbeTests(unittest.TestCase):
    @staticmethod
    def fixture():
        rows = {
            10: {"terms": [
                {"key": [0], "coefficient": "1"},
                {"key": [1], "coefficient": "d"}]},
            30: {"terms": [
                {"key": [1], "coefficient": "1"},
                {"key": [2], "coefficient": "z"}]},
            20: {"terms": [
                {"key": [0], "coefficient": "1"},
                {"key": [1], "coefficient": "z"},
                {"key": [2], "coefficient": "1"}]},
        }
        saved = {
            "processed": 2,
            "pivots": [
                {"lead": [0], "row": [[[0], "1"], [[1], "d"]],
                 "trace": [[10, "1"]]},
                {"lead": [1], "row": [[[1], "1"], [[2], "z"]],
                 "trace": [[30, "1"]]},
            ],
        }
        return saved, rows, [10, 30, 20]

    def test_two_real_pivot_order_and_exact_ibp_replay(self):
        saved, rows, ids = self.fixture()
        result = pilot.advance_exact_path(saved, rows, ids, max_steps=2)
        self.assertEqual(result["completed_steps"], 2)
        self.assertEqual([r["pivot"] for r in result["steps"]], [[0], [1]])
        self.assertEqual(result["next_lead"], [2])
        self.assertEqual(result["stopped_because"], "max_steps")
        for step in result["steps"]:
            self.assertTrue(step["strict_exact_row_equal"])
            self.assertTrue(step["strict_exact_trace_equal"])
            self.assertTrue(step["original_ibp_replay_verified"])
        self.assertFalse(result["checkpoint_modified"])

    def test_stop_when_no_matching_saved_pivot(self):
        saved, rows, ids = self.fixture()
        result = pilot.advance_exact_path(saved, rows, ids, max_steps=3)
        self.assertEqual(result["completed_steps"], 2)
        self.assertEqual(result["stopped_because"], "no_saved_pivot")

    def test_bad_pivot_trace_rejected_by_original_ibp_replay(self):
        saved, rows, ids = self.fixture()
        saved["pivots"][0]["trace"] = [[10, "2"]]
        with self.assertRaisesRegex(AssertionError, "provenance mismatch"):
            pilot.advance_exact_path(saved, rows, ids, max_steps=2)

    def test_step_limit_is_enforced(self):
        saved, rows, ids = self.fixture()
        with self.assertRaisesRegex(ValueError, "1..8"):
            pilot.advance_exact_path(saved, rows, ids, max_steps=9)


if __name__ == "__main__":
    unittest.main()
