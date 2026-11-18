import unittest
from examples.three_loop_vp05_sector202_target_b_step70_exact_audit import (
    field_equal,coefficient_identity,COEFF,IBP,SCRATCH,
    EXPECTED_STEP70_SHA,EXPECTED_STEP69_SHA,
    CHECKPOINT,SOURCE,CERT,formal_next_lead,
)
class Step70ExactAuditTests(unittest.TestCase):
    def test_exact_rational_identity(self):
        self.assertTrue(field_equal("1",[("z","1/(z+1)"),("1","1/(z+1)")]))
        self.assertFalse(field_equal("2",[("z","1/(z+1)"),("1","1/(z+1)")]))
    def test_update_direction(self):
        self.assertTrue(coefficient_identity("remainder","z+2","2","1","z"))
        self.assertTrue(coefficient_identity("source","2","z+2","1","z"))
        self.assertFalse(coefficient_identity("source","2","z+3","1","z"))
    def test_sha_pins_and_phase_paths(self):
        self.assertEqual(EXPECTED_STEP70_SHA,"b738b82b038d229850e043f63796fd01db4cb50a404ad3247ef1a5962ee07c04")
        self.assertEqual(EXPECTED_STEP69_SHA,"97307fc660bc7a5b9cb17e4c6057025c1488d023a6e5b7f87341343de8c57b2d")
        self.assertEqual(len({COEFF.resolve(),IBP.resolve(),SCRATCH.resolve()}),3)
    def test_formal_next_lead_is_derived(self):
        baseline={"remaining":[[[7,139],"1"],[[8,139],"1"]],"metrics":{"lead":[7,139]}}
        self.assertEqual(formal_next_lead(baseline),[7,139])
    def test_source_provenance_imports_canonical(self):
        from examples.three_loop_vp05_sector202_target_exact_reduction import (
            CHECKPOINT as CP,SOURCE as SO,CERT as CE,
        )
        self.assertEqual((CHECKPOINT,SOURCE,CERT),(CP,SO,CE))
if __name__=="__main__":
    unittest.main()
