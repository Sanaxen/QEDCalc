"""Offline regression tests for bounded exact Sector202 Step63."""
import unittest
from examples.three_loop_vp05_sector202_step63_guard import interpret

class Step63GuardTests(unittest.TestCase):
    def setUp(self):
        self.old = {"steps":62,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                    "pivot_path":[[i,139] for i in range(62)],
                    "exact_target_proven":False}
        self.new = {**self.old,"steps":63,
                    "pivot_path":[[i,139] for i in range(63)]}
    def test_success(self):
        self.assertEqual(interpret(0,self.old,self.new),
                         "STEP63_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")
    def test_stop(self):
        self.assertEqual(interpret(-1,self.old,self.old),
                         "STEP63_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
        capped = {**self.old,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF"}
        self.assertEqual(interpret(0,self.old,capped),
                         "STEP63_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
    def test_reject_unexpected_change(self):
        with self.assertRaises(RuntimeError):
            interpret(1,self.old,self.new)
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"pivot_path":[]})
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"exact_target_proven":True})

if __name__=="__main__":
    unittest.main()
