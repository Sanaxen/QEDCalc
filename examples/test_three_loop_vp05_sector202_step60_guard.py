"""Offline tests for Step60 guard transitions."""
import unittest
from examples.three_loop_vp05_sector202_step60_guard import interpret


class Step60Tests(unittest.TestCase):
    def setUp(self):
        self.old = {"steps":59,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                    "pivot_path":[[i,139] for i in range(59)],
                    "exact_target_proven":False}
        self.new = {**self.old,"steps":60,
                    "pivot_path":[[i,139] for i in range(60)]}

    def test_success(self):
        self.assertEqual(interpret(0,self.old,self.new),
                         "STEP60_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")

    def test_cap_stop(self):
        self.assertEqual(interpret(-1,self.old,self.old),
                         "STEP60_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
        cap = {**self.old,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF"}
        self.assertEqual(interpret(0,self.old,cap),
                         "STEP60_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")

    def test_unexpected_mutation(self):
        with self.assertRaises(RuntimeError):
            interpret(1,self.old,self.new)
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"pivot_path":[]})
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"exact_target_proven":True})


if __name__=="__main__":
    unittest.main()
