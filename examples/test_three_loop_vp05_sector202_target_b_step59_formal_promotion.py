"""Safety regression checks for B Step59 backup-first formal promotion."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step59_formal_promotion import (
    B_STEP58_SHA, B_CANDIDATE_SHA, BACKUP, B_STATE,
    STEP50_BACKUP, STEP51_BACKUP, STEP52_BACKUP, B_STEP52_SHA,
)

class BStep59FormalPromotionTests(unittest.TestCase):
    def test_pinned_input_hashes(self):
        self.assertEqual(B_STEP58_SHA,
            "565af78b3e8604782f614515fb2b93d8a25efa6022174a2ca4bcc9673fc56d4b")
        self.assertEqual(B_CANDIDATE_SHA,
            "5e6846ab084dac257db449063843ece82f9e021d379bc515cc9b48bf1a442c2c")
        self.assertEqual(B_STEP52_SHA,
            "b398b7f9630c2ea2c8a90c1939517a7e5095170d65c1c68d9dc47b294776aa95")

    def test_backup_is_unique(self):
        self.assertEqual(len({
            BACKUP, B_STATE, STEP50_BACKUP, STEP51_BACKUP, STEP52_BACKUP
        }), 5)
        self.assertIn("step58_before_step59", BACKUP.name)

if __name__ == "__main__":
    unittest.main()
