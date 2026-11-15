"""Static and pure validation of B Step60 backup-first formal promotion."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step60_formal_promotion import (
    B_STEP59_SHA, B_CANDIDATE_SHA, BACKUP, B_STATE,
    STEP50_BACKUP, STEP51_BACKUP, STEP52_BACKUP, STEP58_BACKUP,
)
class TestBStep60Promotion(unittest.TestCase):
    def test_pinned_hashes(self):
        self.assertEqual(B_STEP59_SHA,
            "a5a341737487cc4a1f2e20323b1adc927ead02e043af44db4442857a7cfdc38a")
        self.assertEqual(B_CANDIDATE_SHA,
            "3c75321db601464d35163838f712b675955ca5db9fec7290e116851ac8d4fd09")
    def test_backup_isolated(self):
        paths=[BACKUP,B_STATE,STEP50_BACKUP,STEP51_BACKUP,STEP52_BACKUP,STEP58_BACKUP]
        self.assertEqual(len({p.resolve() for p in paths}),len(paths))
        self.assertIn("step59_before_step60_promotion",BACKUP.name)
if __name__=="__main__":
    unittest.main()
