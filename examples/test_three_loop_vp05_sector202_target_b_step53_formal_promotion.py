"""Safety regression checks for B Step53 backup-first promotion."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step53_formal_promotion import (
    B_STEP52_SHA, B_CANDIDATE_SHA, BACKUP, B_STATE,
    STEP50_BACKUP, STEP51_BACKUP, B_STEP51_SHA,
)

class BStep53PromotionTests(unittest.TestCase):
    def test_exact_input_pins(self):
        self.assertEqual(B_STEP52_SHA, "b398b7f9630c2ea2c8a90c1939517a7e5095170d65c1c68d9dc47b294776aa95")
        self.assertEqual(B_CANDIDATE_SHA, "d4a915893ffeca2b8788538f53c0e0850310ac823b64e0ffc6a161c7398a0a2c")
        self.assertEqual(B_STEP51_SHA, "382e76dbbfc6f57c0dbf6468b53329d91a869ed9267a98093ac7165d8c6c7aac")

    def test_isolated_backup_path(self):
        self.assertEqual(len({BACKUP, B_STATE, STEP50_BACKUP, STEP51_BACKUP}),4)
        self.assertIn("step52_before_step53",BACKUP.name)

if __name__=="__main__":
    unittest.main()
