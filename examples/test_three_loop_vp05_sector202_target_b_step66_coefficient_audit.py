import unittest
from examples.three_loop_vp05_sector202_target_b_step66_coefficient_audit import verify_coefficient
class Step66CoefficientAuditTest(unittest.TestCase):
    def test_removal_and_source_update(self):
        self.assertTrue(verify_coefficient("remainder",(1,139),"z","0","1","z"))
        self.assertTrue(verify_coefficient("source",1,"0","z/2","1/2","z"))
    def test_detect_changed_saved_value(self):
        with self.assertRaises(AssertionError):
            verify_coefficient("remainder",(1,139),"z","1","1","z")
if __name__=="__main__":
    unittest.main()
