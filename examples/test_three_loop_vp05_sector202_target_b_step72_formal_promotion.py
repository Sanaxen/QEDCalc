import unittest
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step72_formal_promotion import (
    promote, B_STATE, BACKUP, TEMP, SCRATCH, COEFF, IBP,
    EXPECTED_STEP71_SHA, EXPECTED_STEP72_SHA,
)
class Step72PromotionTests(unittest.TestCase):
    def test_read_only_default(self):
        self.assertEqual(promote.__defaults__,(True,))
        with patch("examples.three_loop_vp05_sector202_target_b_step72_formal_promotion.validate",
                   return_value={"status":"B_STEP72_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF"}) as v:
            self.assertIn("PREFLIGHT",promote()["status"])
            v.assert_called_once_with()
    def test_exclusive_paths(self):
        paths=[B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
    def test_sha(self):
        self.assertEqual(EXPECTED_STEP71_SHA,
          "80d9eee0c153ddbef718bbccfc8b1d0087277d6a13ca51df1986f838436966f8")
        self.assertEqual(EXPECTED_STEP72_SHA,
          "35cc49631d6f36c46a7f5e7f15f77a7ba825581e0a9b761a897832314ddca7ab")
if __name__=="__main__":
    unittest.main()
