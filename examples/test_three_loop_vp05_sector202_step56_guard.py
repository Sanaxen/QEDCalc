"""Isolated transition tests for exact Target A Step56 guard."""
import unittest
from examples.three_loop_vp05_sector202_step56_guard import interpret


class Step56GuardTests(unittest.TestCase):
    def setUp(self):
        self.old = {"steps":55, "status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                    "pivot_path":[[i,139] for i in range(55)],
                    "exact_target_proven":False}
        self.new = {**self.old, "steps":56,
                    "pivot_path":[[i,139] for i in range(56)]}

    def test_success(self):
        self.assertEqual(interpret(0,self.old,self.new),
                         "STEP56_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")

    def test_cap_or_time_stop(self):
        self.assertEqual(interpret(-1,self.old,self.old),
                         "STEP56_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
        cap = {**self.old, "status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF"}
        self.assertEqual(interpret(0,self.old,cap),
                         "STEP56_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")

    def test_no_unexpected_change(self):
        with self.assertRaises(RuntimeError):
            interpret(1,self.old,self.new)
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"pivot_path":[]})
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"exact_target_proven":True})


if __name__ == "__main__":
    unittest.main()
