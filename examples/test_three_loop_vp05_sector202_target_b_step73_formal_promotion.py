import unittest
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step73_formal_promotion import (
    promote,B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP,
    EXPECTED_STEP72_SHA,EXPECTED_STEP73_SHA,
)
class Step73PromotionTests(unittest.TestCase):
    def test_read_only_default(self):
        self.assertEqual(promote.__defaults__,(True,))
        with patch("examples.three_loop_vp05_sector202_target_b_step73_formal_promotion.validate",
                   return_value={"status":"B_STEP73_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF"}) as v:
            self.assertIn("PREFLIGHT",promote()["status"])
            v.assert_called_once_with()
    def test_distinct_paths(self):
        paths=[B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
    def test_expected_sha(self):
        self.assertEqual(EXPECTED_STEP72_SHA,
            "35cc49631d6f36c46a7f5e7f15f77a7ba825581e0a9b761a897832314ddca7ab")
        self.assertEqual(EXPECTED_STEP73_SHA,
            "4ade410c0ecf50f10698d899a1ae14bc762e4f0107b044ee55a3fb7d5ec7004c")
if __name__=="__main__":
    unittest.main()
