import unittest
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step66_formal_promotion import (
    promote,BACKUP,TEMP,PROTECTED,B_STATE,SCRATCH,NORMALIZED,DIRECT,COEFFICIENT,
)
class Step66FormalPromotionTest(unittest.TestCase):
    def test_preflight_never_writes(self):
        summary={"old_sha256":"a","new_sha256":"b","target_b_proven":False}
        with patch("examples.three_loop_vp05_sector202_target_b_step66_formal_promotion.validate",return_value=summary):
            self.assertEqual(promote(check_only=True)["status"],
                             "B_STEP66_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF")
    def test_unique_protected_paths(self):
        paths=[p.resolve() for p,_ in PROTECTED]+[
            SCRATCH.resolve(),NORMALIZED.resolve(),DIRECT.resolve(),
            COEFFICIENT.resolve(),BACKUP.resolve(),TEMP.resolve()]
        self.assertEqual(len(paths),len(set(paths)))
        self.assertIn(B_STATE.resolve(),paths)
        self.assertNotEqual(BACKUP.resolve(),B_STATE.resolve())
    def test_explicit_promotion_required(self):
        self.assertEqual(promote.__defaults__,(True,))
if __name__=="__main__":
    unittest.main()
