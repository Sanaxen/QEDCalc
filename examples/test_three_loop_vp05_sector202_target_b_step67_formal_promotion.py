import unittest
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step67_formal_promotion import (
    promote,COEFF,IBP,SCRATCH,B_STATE,BACKUP,TEMP,
)
class Step67PromotionTests(unittest.TestCase):
    def test_default_is_read_only(self):
        with patch("examples.three_loop_vp05_sector202_target_b_step67_formal_promotion.validate",
                   return_value={"status":"B_STEP67_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF"}):
            self.assertIn("PREFLIGHT",promote()["status"])
    def test_unique_paths(self):
        paths=[COEFF,IBP,SCRATCH,B_STATE,BACKUP,TEMP]
        self.assertEqual(len({p.resolve() for p in paths}),len(paths))
    def test_explicit_promotion_only(self):
        self.assertEqual(promote.__defaults__,(True,))
if __name__=="__main__":
    unittest.main()
