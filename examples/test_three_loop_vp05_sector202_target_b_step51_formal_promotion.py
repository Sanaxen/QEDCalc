"""Synthetic no-write promotion guard validation."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step51_formal_promotion import (
    B_STEP50_SHA, B_CANDIDATE_SHA, BACKUP, B_STATE,
)

class TargetBPromotionTests(unittest.TestCase):
    def test_hash_shapes(self):
        self.assertEqual(len(B_STEP50_SHA),64)
        self.assertEqual(len(B_CANDIDATE_SHA),64)
    def test_backup_distinct(self):
        self.assertNotEqual(BACKUP,B_STATE)
        self.assertIn("step50_before_step51",BACKUP.name)

if __name__=="__main__":
    unittest.main()
