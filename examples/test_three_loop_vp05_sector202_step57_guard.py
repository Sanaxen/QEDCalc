"""Isolated state transition tests for VP05 sector202 Target A Step57."""
import unittest
from examples.three_loop_vp05_sector202_step57_guard import interpret


class Step57GuardTests(unittest.TestCase):
    def setUp(self):
        self.old = {"steps": 56, "status": "EXACT_TARGET_PREFIX_NOT_PROOF",
                    "pivot_path": [[i,139] for i in range(56)],
                    "exact_target_proven": False}
        self.new = {**self.old, "steps": 57,
                    "pivot_path": [[i,139] for i in range(57)]}

    def test_committed_one_step(self):
        self.assertEqual(interpret(0,self.old,self.new),
                         "STEP57_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")

    def test_not_committed_on_timeout_or_cap(self):
        self.assertEqual(interpret(-1,self.old,self.old),
                         "STEP57_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
        capped = {**self.old, "status": "EXACT_TARGET_CAP_REACHED_NOT_PROOF"}
        self.assertEqual(interpret(0,self.old,capped),
                         "STEP57_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")

    def test_reject_invalid_state_transition(self):
        with self.assertRaises(RuntimeError):
            interpret(1,self.old,self.new)
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"pivot_path":[]})
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"exact_target_proven":True})


if __name__ == "__main__":
    unittest.main()
