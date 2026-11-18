import unittest
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step71_formal_promotion import (
    promote,validate,B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP,
    EXPECTED_STEP70_SHA,EXPECTED_STEP71_SHA
)
class Step71PromotionTests(unittest.TestCase):
    def test_read_only_is_default(self):
        self.assertEqual(promote.__defaults__,(True,))
        with patch("examples.three_loop_vp05_sector202_target_b_step71_formal_promotion.validate",
                   return_value={"status":"B_STEP71_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF"}) as v:
            self.assertIn("PREFLIGHT",promote()["status"])
            v.assert_called_once_with()
    def test_paths_distinct(self):
        paths=[B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
    def test_expected_sha(self):
        self.assertEqual(EXPECTED_STEP70_SHA,
          "b738b82b038d229850e043f63796fd01db4cb50a404ad3247ef1a5962ee07c04")
        self.assertEqual(EXPECTED_STEP71_SHA,
          "80d9eee0c153ddbef718bbccfc8b1d0087277d6a13ca51df1986f838436966f8")
if __name__=="__main__":
    unittest.main()
