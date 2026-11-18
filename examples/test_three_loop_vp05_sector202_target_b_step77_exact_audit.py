"""Regression tests for SHA-bound, read-only Step77 two-phase exact audits."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step77_exact_audit import (
    field_equal, coefficient_identity, COEFF, IBP, SCRATCH,
    EXPECTED_STEP77_SHA, EXPECTED_STEP76_SHA,
    CHECKPOINT, SOURCE, CERT, formal_next_lead,
)
class Step77ExactAuditTests(unittest.TestCase):
    def test_exact_fraction_field(self):
        self.assertTrue(field_equal("1",[("z","1/(z+1)"),("1","1/(z+1)")]))
        self.assertFalse(field_equal("2",[("z","1/(z+1)"),("1","1/(z+1)")]))
    def test_update_directions(self):
        self.assertTrue(coefficient_identity("remainder","z+2","2","1","z"))
        self.assertTrue(coefficient_identity("source","2","z+2","1","z"))
        self.assertFalse(coefficient_identity("source","2","z+3","1","z"))
    def test_saved_shas_and_unique_checkpoint_paths(self):
        self.assertEqual(EXPECTED_STEP77_SHA,
            "9df3d205bdee62f00533df12da0ee6918861f4d11ae31d91a474f3614d44622f")
        self.assertEqual(EXPECTED_STEP76_SHA,
            "33e29f0cd4e00522c27c748b0cbb45d58130db39788a2a26dfa66c71c0337222")
        self.assertEqual(len({COEFF.resolve(),IBP.resolve(),SCRATCH.resolve()}),3)
    def test_dynamic_formal_lead(self):
        baseline={"remaining":[[[7,139],"1"],[[8,139],"1"]],
                  "metrics":{"lead":[7,139]}}
        self.assertEqual(formal_next_lead(baseline),[7,139])
    def test_read_only_preflight_and_source_provenance(self):
        import inspect
        from examples.three_loop_vp05_sector202_target_b_step77_exact_audit import main
        code=inspect.getsource(main)
        self.assertIn("exists!=args.resume and not args.check_only",code)
        self.assertIn("checkpoint_exists",code)
        from examples.three_loop_vp05_sector202_target_exact_reduction import (
            CHECKPOINT as CP,SOURCE as SO,CERT as CE)
        self.assertEqual((CHECKPOINT,SOURCE,CERT),(CP,SO,CE))
if __name__=="__main__":
    unittest.main()
