"""Offline transition regression tests for VP05 sector202 Target A Step62."""
import unittest
from examples.three_loop_vp05_sector202_step62_guard import interpret


class Step62GuardTests(unittest.TestCase):
    def setUp(self):
        self.old = {"steps":61, "status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                    "pivot_path":[[i,139] for i in range(61)],
                    "exact_target_proven":False}
        self.new = {**self.old, "steps":62,
                    "pivot_path":[[i,139] for i in range(62)]}

    def test_success(self):
        self.assertEqual(interpret(0,self.old,self.new),
                         "STEP62_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")

    def test_cap_stop(self):
        self.assertEqual(interpret(-1,self.old,self.old),
                         "STEP62_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
        cap = {**self.old,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF"}
        self.assertEqual(interpret(0,self.old,cap),
                         "STEP62_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")

    def test_invalid_checkpoint(self):
        with self.assertRaises(RuntimeError):
            interpret(1,self.old,self.new)
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"pivot_path":[]})
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"exact_target_proven":True})


if __name__=="__main__":
    unittest.main()
