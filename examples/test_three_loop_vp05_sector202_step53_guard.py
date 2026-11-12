"""Offline synthetic tests for guarded Step53 continuation."""
import unittest
from examples.three_loop_vp05_sector202_step53_guard import interpret


class Step53Tests(unittest.TestCase):
    def setUp(self):
        self.old = {"steps":52,"pivot_path":[[i,139] for i in range(52)],
                    "exact_target_proven":False}
        self.new = {"steps":53,"pivot_path":[[i,139] for i in range(53)],
                    "exact_target_proven":False}

    def test_completed_step(self):
        self.assertEqual(interpret(0,self.old,self.new),
                         "STEP53_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")

    def test_unchanged_and_cap_stop(self):
        self.assertEqual(interpret(-1,self.old,self.old),
                         "STEP53_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
        capped={**self.old,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF"}
        self.assertEqual(interpret(0,self.old,capped),
                         "STEP53_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")

    def test_reject_error_or_inconsistent_checkpoint(self):
        with self.assertRaises(RuntimeError):
            interpret(1,self.old,self.new)
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"pivot_path":[]})
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"exact_target_proven":True})


if __name__ == "__main__":
    unittest.main()
