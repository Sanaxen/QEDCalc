import unittest
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step75_formal_promotion import (
    promote,B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP,valid_nonmonotone_successor,
    EXPECTED_STEP74_SHA,EXPECTED_STEP75_SHA,
)
class Step75PromotionTests(unittest.TestCase):
    def test_read_only_default(self):
        self.assertEqual(promote.__defaults__,(True,))
        with patch("examples.three_loop_vp05_sector202_target_b_step75_formal_promotion.validate",
                   return_value={"status":"B_STEP75_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF"}) as v:
            self.assertIn("PREFLIGHT",promote()["status"])
            v.assert_called_once_with()
    def test_distinct_paths(self):
        paths=[B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
    def test_fill_in_is_allowed_but_pivot_must_disappear(self):
        formal={"remaining":[[[10,139],"1"],[[11,139],"2"]],
                "metrics":{"lead":[10,139]}}
        candidate={"remaining":[[[11,139],"2"],[[12,139],"3"],[[13,139],"4"]]}
        self.assertTrue(valid_nonmonotone_successor(formal,candidate))
        self.assertFalse(valid_nonmonotone_successor(formal,
            {"remaining":[[[10,139],"1"],[[12,139],"3"]]}))
        self.assertFalse(valid_nonmonotone_successor(formal,
            {"remaining":[[[9,139],"1"],[[12,139],"3"]]}))
        self.assertFalse(valid_nonmonotone_successor(formal,{"remaining":[]}))

    def test_expected_sha(self):
        self.assertEqual(EXPECTED_STEP74_SHA,
            "ec7bf87037fc34bd73e730894bfe09a8e43287628a07ec7c861e6f777b36b694")
        self.assertEqual(EXPECTED_STEP75_SHA,
            "2a7e2444c2cb5b65826df964c8e699d057963de4fbf7e68cac025d8c5c9a3dc9")
if __name__=="__main__":
    unittest.main()
