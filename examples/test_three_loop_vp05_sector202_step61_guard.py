"""Offline transition tests for exact Step61 guard."""
import unittest
from examples.three_loop_vp05_sector202_step61_guard import interpret


class Step61GuardTests(unittest.TestCase):
    def setUp(self):
        self.old = {"steps":60, "status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                    "pivot_path":[[i,139] for i in range(60)],
                    "exact_target_proven":False}
        self.new = {**self.old, "steps":61,
                    "pivot_path":[[i,139] for i in range(61)]}

    def test_success(self):
        self.assertEqual(interpret(0,self.old,self.new),
                         "STEP61_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")

    def test_cap_or_timeout(self):
        self.assertEqual(interpret(-1,self.old,self.old),
                         "STEP61_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
        capped = {**self.old,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF"}
        self.assertEqual(interpret(0,self.old,capped),
                         "STEP61_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")

    def test_reject_bad_transition(self):
        with self.assertRaises(RuntimeError):
            interpret(1,self.old,self.new)
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"pivot_path":[]})
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"exact_target_proven":True})


if __name__=="__main__":
    unittest.main()
