"""Pure synthetic guard tests, independent of production QED data."""
import unittest
from examples.three_loop_vp05_sector202_step52_guard import interpret


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.old = {"steps": 51, "pivot_path": [[i, 139] for i in range(51)]}
        self.new = {"steps": 52, "pivot_path": [[i, 139] for i in range(52)]}

    def test_successful_step(self):
        self.assertEqual(interpret(0, self.old, self.new),
                         "STEP52_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")

    def test_bounded_stop(self):
        self.assertEqual(interpret(-1, self.old, self.old),
                         "STEP52_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")

    def test_does_not_silently_approve_inconsistent_update(self):
        with self.assertRaises(RuntimeError):
            interpret(1, self.old, self.new)
        with self.assertRaises(RuntimeError):
            interpret(0, self.old, {"steps": 52, "pivot_path": []})


if __name__ == "__main__":
    unittest.main()
