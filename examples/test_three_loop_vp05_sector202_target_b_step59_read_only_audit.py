"""Pinned post-promotion Step59 checkpoint smoke tests."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step59_read_only_audit import (
    PROMOTED_STEP59_SHA, B_STATE, STEP50_BACKUP, STEP51_BACKUP,
    STEP52_BACKUP, STEP58_BACKUP, B_STEP58_SHA,
)

class BStep59ReadOnlyAuditTests(unittest.TestCase):
    def test_exact_sha(self):
        self.assertEqual(PROMOTED_STEP59_SHA,
            "88cab7046de7cab3f5733ffc788a375a795d8842d89a4b1c794f775dba2e8dda")
        self.assertEqual(B_STEP58_SHA,
            "565af78b3e8604782f614515fb2b93d8a25efa6022174a2ca4bcc9673fc56d4b")

    def test_protected_paths_distinct(self):
        self.assertEqual(len({B_STATE, STEP50_BACKUP, STEP51_BACKUP,
                              STEP52_BACKUP, STEP58_BACKUP}), 5)

if __name__ == "__main__":
    unittest.main()
