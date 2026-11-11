"""Synthetic offline exact rational identities; no production inputs required."""
import unittest
from examples.three_loop_vp05_sector202_step51_exact_coefficient_audit import (
    identity_difference, check_progress,
)


class ExactStep51CoefficientTests(unittest.TestCase):
    def test_exact_arithmetic(self):
        self.assertEqual(identity_difference(
            "(z+3)-(z+1)*(z+2)", "z+3", "z+1", "z+2", -1), 0)
        self.assertEqual(identity_difference(
            "d-1+(z+1)/2", "d-1", "z+1", "1/2", 1), 0)
        self.assertNotEqual(identity_difference(
            "d", "d-1", "z+1", "1/2", 1), 0)

    def test_progress_guard(self):
        config = {"operation_count": 288}
        valid = {"version": 1, "config": config,
                 "status": "EXACT_STEP51_COEFFICIENT_PREFIX_NOT_TARGET_PROOF",
                 "exact_target_proven": False, "verified_count": 100}
        check_progress(valid, config)
        for bad in (-1, 289, 1.1, True):
            with self.assertRaises(RuntimeError):
                check_progress({**valid, "verified_count": bad}, config)
        with self.assertRaises(RuntimeError):
            check_progress({**valid, "config": {}}, config)
        with self.assertRaises(RuntimeError):
            check_progress({**valid, "exact_target_proven": True}, config)


if __name__ == "__main__":
    unittest.main()
