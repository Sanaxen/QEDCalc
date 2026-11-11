"""Offline synthetic regression tests for Step51 exact compaction."""
import unittest
from examples.three_loop_vp05_sector202_step51_compaction import compact_exact


class CompactionTests(unittest.TestCase):
    def test_factor_and_exact_identity(self):
        raw = "(z**2-1)/(z-1)"
        self.assertEqual(compact_exact(raw, cap=8), "z + 1")

    def test_reject_unreachable_cap(self):
        self.assertIsNone(compact_exact("(z**2-1)/(z-1)", cap=1))


if __name__ == "__main__":
    unittest.main()
