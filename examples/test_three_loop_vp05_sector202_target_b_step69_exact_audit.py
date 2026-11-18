import unittest
from examples.three_loop_vp05_sector202_target_b_step69_exact_audit import (
    field_equal,coefficient_identity,COEFF,IBP,SCRATCH,
    EXPECTED_STEP69_SHA,EXPECTED_STEP68_SHA,
    CHECKPOINT,SOURCE,CERT,
)
class Step69ExactAuditTests(unittest.TestCase):
    def test_independent_exact_rational_field(self):
        self.assertTrue(field_equal("1",[("z","1/(z+1)"),("1","1/(z+1)")]))
        self.assertFalse(field_equal("2",[("z","1/(z+1)"),("1","1/(z+1)")]))
    def test_correct_update_signs(self):
        self.assertTrue(coefficient_identity("remainder","z+2","2","1","z"))
        self.assertTrue(coefficient_identity("source","2","z+2","1","z"))
        self.assertFalse(coefficient_identity("source","2","z+3","1","z"))
    def test_pinned_baseline_and_scratch(self):
        self.assertEqual(EXPECTED_STEP68_SHA,"09368c634e482c40a8ae7dd9e7657c0d0667608f82f7d5b6537cc66067ac5ae8")
        self.assertEqual(EXPECTED_STEP69_SHA,"97307fc660bc7a5b9cb17e4c6057025c1488d023a6e5b7f87341343de8c57b2d")
        self.assertEqual(len({COEFF.resolve(),IBP.resolve(),SCRATCH.resolve()}),3)
    def test_source_provenance_imported_from_canonical_module(self):
        from examples.three_loop_vp05_sector202_target_exact_reduction import (
            CHECKPOINT as CP,SOURCE as SO,CERT as CE,
        )
        self.assertEqual((CHECKPOINT,SOURCE,CERT),(CP,SO,CE))
if __name__=="__main__":
    unittest.main()
