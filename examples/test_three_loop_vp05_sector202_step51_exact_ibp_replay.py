"""Pure synthetic exact original-row replay tests."""
import unittest
from examples.three_loop_vp05_sector202_step51_exact_ibp_replay import (
    verify_column, key_index,
)


class ReplayTests(unittest.TestCase):
    def test_exact_zero_and_corruption(self):
        # initial = remainder + (z+1)*(2*e1-e2)
        initial = {(1, 1): "z+3"}
        rem = {(1, 1): "1-z", (2, 1): "-(z+1)"}
        trace = {10: "z+1", 11: "-1"}
        rows = {
            10: [{"key": [1, 1], "coefficient": "2"},
                 {"key": [2, 1], "coefficient": "1"}],
            11: [{"key": [1, 1], "coefficient": "0"}],
        }
        for key in key_index(initial, rem, rows):
            self.assertTrue(verify_column(key, initial, rem, trace, rows))
        self.assertFalse(verify_column((1, 1), initial,
                         {(1, 1): "z", (2, 1): "-(z+1)"}, trace, rows))


if __name__ == "__main__":
    unittest.main()
