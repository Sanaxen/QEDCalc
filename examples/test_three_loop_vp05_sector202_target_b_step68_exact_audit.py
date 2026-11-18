import unittest
from examples.three_loop_vp05_sector202_target_b_step68_exact_audit import (
    field_equal,coefficient_identity,COEFF,IBP,SCRATCH,
    EXPECTED_STEP68_SHA,EXPECTED_STEP67_SHA,
)
class Step68ExactAuditTests(unittest.TestCase):
    def test_exact_field_original_identity(self):
        self.assertTrue(field_equal("1",[("1/(z+1)","z"),("1/(z+1)","1")]))
        self.assertFalse(field_equal("2",[("1/(z+1)","z"),("1/(z+1)","1")]))
    def test_coefficient_signs(self):
        self.assertTrue(coefficient_identity("remainder","z+2","2","1","z"))
        self.assertTrue(coefficient_identity("source","2","z+2","1","z"))
        self.assertFalse(coefficient_identity("remainder","z+2","3","1","z"))
        self.assertFalse(coefficient_identity("source","2","z+3","1","z"))
    def test_independent_paths_and_hashes(self):
        self.assertEqual(len({COEFF.resolve(),IBP.resolve(),SCRATCH.resolve()}),3)
        self.assertEqual(EXPECTED_STEP67_SHA,"bd5e5dbd92c8636332b006371006891c2bbd1e9870c2f5d5fb353b935a790ba2")
        self.assertEqual(EXPECTED_STEP68_SHA,"09368c634e482c40a8ae7dd9e7657c0d0667608f82f7d5b6537cc66067ac5ae8")
if __name__=="__main__":
    unittest.main()
