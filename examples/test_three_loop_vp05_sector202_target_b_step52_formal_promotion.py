"""Fast invariant tests for hash-pinned Target B Step52 promotion."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step52_formal_promotion import (
    B_STEP51_SHA, B_CANDIDATE_SHA, BACKUP, B_STATE, STEP50_BACKUP, B_STEP50_SHA,
)

class TargetBStep52PromotionTests(unittest.TestCase):
    def test_known_hashes(self):
        self.assertEqual(B_STEP51_SHA,"382e76dbbfc6f57c0dbf6468b53329d91a869ed9267a98093ac7165d8c6c7aac")
        self.assertEqual(B_CANDIDATE_SHA,"d5a9a5cbe02fde86e3069dccde979a61ca9b1d92a263d7d7991c2107aa4e126d")
        self.assertEqual(len(B_STEP50_SHA),64)
    def test_unique_backup(self):
        self.assertEqual(len({BACKUP,B_STATE,STEP50_BACKUP}),3)
        self.assertIn("step51_before_step52",BACKUP.name)

if __name__=="__main__":
    unittest.main()
