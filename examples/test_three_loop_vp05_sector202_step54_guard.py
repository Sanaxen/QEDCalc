"""Isolated tests for guarded Step54 checkpoint state transition."""
import unittest
from examples.three_loop_vp05_sector202_step54_guard import interpret


class Step54GuardTests(unittest.TestCase):
    def setUp(self):
        self.before = {"steps": 53, "status": "EXACT_TARGET_PREFIX_NOT_PROOF",
                       "pivot_path": [[i, 139] for i in range(53)],
                       "exact_target_proven": False}
        self.after = {**self.before, "steps": 54,
                      "pivot_path": [[i, 139] for i in range(54)]}

    def test_one_step_success(self):
        self.assertEqual(
            interpret(0, self.before, self.after),
            "STEP54_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")

    def test_timeout_or_cap_without_promotion(self):
        self.assertEqual(
            interpret(-1, self.before, self.before),
            "STEP54_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
        capped = {**self.before, "status": "EXACT_TARGET_CAP_REACHED_NOT_PROOF"}
        self.assertEqual(
            interpret(0, self.before, capped),
            "STEP54_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")

    def test_corruption_or_unexpected_proof_fails(self):
        with self.assertRaises(RuntimeError):
            interpret(1, self.before, self.after)
        with self.assertRaises(RuntimeError):
            interpret(0, self.before, {**self.after, "exact_target_proven": True})
        with self.assertRaises(RuntimeError):
            interpret(0, self.before, {**self.after, "pivot_path": []})


if __name__ == "__main__":
    unittest.main()
