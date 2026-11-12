"""Offline guards for VP05 sector202 exact Step55."""
import unittest
from examples.three_loop_vp05_sector202_step55_guard import interpret


class Step55GuardTests(unittest.TestCase):
    def setUp(self):
        self.old = {"steps":54, "status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                    "pivot_path":[[i,139] for i in range(54)],
                    "exact_target_proven":False}
        self.new = {**self.old,"steps":55,
                    "pivot_path":[[i,139] for i in range(55)]}

    def test_step55_success(self):
        self.assertEqual(interpret(0,self.old,self.new),
                         "STEP55_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")

    def test_stop_before_step55(self):
        self.assertEqual(interpret(-1,self.old,self.old),
                         "STEP55_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
        capped = {**self.old,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF"}
        self.assertEqual(interpret(0,self.old,capped),
                         "STEP55_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")

    def test_reject_inconsistent_state(self):
        with self.assertRaises(RuntimeError):
            interpret(1,self.old,self.new)
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"pivot_path":[]})
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"exact_target_proven":True})


if __name__=="__main__":
    unittest.main()
