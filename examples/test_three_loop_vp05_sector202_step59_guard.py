"""Regression tests for VP05 sector202 Target A Step59 guard."""
import unittest
from examples.three_loop_vp05_sector202_step59_guard import interpret

class Step59GuardTests(unittest.TestCase):
    def setUp(self):
        self.old={"steps":58,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                  "pivot_path":[[i,139] for i in range(58)],
                  "exact_target_proven":False}
        self.new={**self.old,"steps":59,
                  "pivot_path":[[i,139] for i in range(59)]}

    def test_success(self):
        self.assertEqual(interpret(0,self.old,self.new),
                         "STEP59_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")

    def test_not_committed(self):
        self.assertEqual(interpret(-1,self.old,self.old),
                         "STEP59_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
        self.assertEqual(
            interpret(0,self.old,{**self.old,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF"}),
            "STEP59_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")

    def test_invalid_transition(self):
        with self.assertRaises(RuntimeError):
            interpret(1,self.old,self.new)
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"pivot_path":[]})
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"exact_target_proven":True})

if __name__=="__main__":
    unittest.main()
