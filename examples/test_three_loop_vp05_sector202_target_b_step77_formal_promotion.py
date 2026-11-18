import unittest
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step77_formal_promotion import (
    promote,B_STATE,BACKUP,TEMP,SCRATCH,COEFF,IBP,valid_nonmonotone_successor,
    EXPECTED_STEP76_SHA,EXPECTED_STEP77_SHA,
)
class Step77PromotionTests(unittest.TestCase):
    def test_read_only_default(self):
        self.assertEqual(promote.__defaults__,(True,))
        with patch("examples.three_loop_vp05_sector202_target_b_step77_formal_promotion.validate",
                   return_value={"status":"B_STEP77_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF"}) as v:
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
        self.assertEqual(EXPECTED_STEP76_SHA,
            "33e29f0cd4e00522c27c748b0cbb45d58130db39788a2a26dfa66c71c0337222")
        self.assertEqual(EXPECTED_STEP77_SHA,
            "9df3d205bdee62f00533df12da0ee6918861f4d11ae31d91a474f3614d44622f")
if __name__=="__main__":
    unittest.main()
