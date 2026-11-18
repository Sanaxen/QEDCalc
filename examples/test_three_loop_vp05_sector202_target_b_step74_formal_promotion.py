import unittest
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step74_formal_promotion import (
    promote,B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP,
    EXPECTED_STEP73_SHA,EXPECTED_STEP74_SHA,
)
class Step74PromotionTests(unittest.TestCase):
    def test_read_only_default(self):
        self.assertEqual(promote.__defaults__,(True,))
        with patch("examples.three_loop_vp05_sector202_target_b_step74_formal_promotion.validate",
                   return_value={"status":"B_STEP74_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF"}) as v:
            self.assertIn("PREFLIGHT",promote()["status"])
            v.assert_called_once_with()
    def test_distinct_paths(self):
        paths=[B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
    def test_expected_sha(self):
        self.assertEqual(EXPECTED_STEP73_SHA,
            "4ade410c0ecf50f10698d899a1ae14bc762e4f0107b044ee55a3fb7d5ec7004c")
        self.assertEqual(EXPECTED_STEP74_SHA,
            "ec7bf87037fc34bd73e730894bfe09a8e43287628a07ec7c861e6f777b36b694")
if __name__=="__main__":
    unittest.main()
