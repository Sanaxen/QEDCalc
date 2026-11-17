import unittest
from examples.three_loop_vp05_sector202_target_b_step67_exact_audit import (
    field_equal,coefficient_identity,COEFF,IBP,SCRATCH,
)
class Step67ExactAuditTests(unittest.TestCase):
    def test_exact_field_original_identity(self):
        self.assertTrue(field_equal("1",[("1/(z+1)","z"),("1/(z+1)","1")]))
        self.assertFalse(field_equal("2",[("1/(z+1)","z"),("1/(z+1)","1")]))
    def test_coefficient_remainder_and_source_signs(self):
        self.assertTrue(coefficient_identity("remainder","z+2","2","1","z"))
        self.assertTrue(coefficient_identity("source","2","z+2","1","z"))
        self.assertFalse(coefficient_identity("remainder","z+2","3","1","z"))
    def test_distinct_audit_outputs(self):
        self.assertEqual(len({COEFF.resolve(),IBP.resolve(),SCRATCH.resolve()}),3)
if __name__=="__main__":
    unittest.main()
