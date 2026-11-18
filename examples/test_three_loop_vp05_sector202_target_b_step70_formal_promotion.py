import unittest
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step70_formal_promotion import (
    promote,validate,B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP,
    EXPECTED_STEP69_SHA,EXPECTED_STEP70_SHA
)
class Step70PromotionTests(unittest.TestCase):
    def test_read_only_is_default(self):
        self.assertEqual(promote.__defaults__,(True,))
        with patch("examples.three_loop_vp05_sector202_target_b_step70_formal_promotion.validate",
                   return_value={"status":"B_STEP70_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF"}) as v:
            self.assertIn("PREFLIGHT",promote()["status"])
            v.assert_called_once_with()
    def test_paths_distinct(self):
        paths=[B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
    def test_expected_sha(self):
        self.assertEqual(EXPECTED_STEP69_SHA,
          "97307fc660bc7a5b9cb17e4c6057025c1488d023a6e5b7f87341343de8c57b2d")
        self.assertEqual(EXPECTED_STEP70_SHA,
          "b738b82b038d229850e043f63796fd01db4cb50a404ad3247ef1a5962ee07c04")
if __name__=="__main__":
    unittest.main()
