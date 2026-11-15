"""Static invariants for post-promotion B Step53 read-only audit."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step53_read_only_audit import (
    PROMOTED_STEP53_SHA, B_STATE, STEP50_BACKUP, STEP51_BACKUP, STEP52_BACKUP,
)

class TestReadOnlyBStep53Audit(unittest.TestCase):
    def test_pinned_state_sha(self):
        self.assertEqual(PROMOTED_STEP53_SHA,
            "684ee4ed3936a52d940e58f8292b9d7a8b38b7d6822492e9709bb8427ff64505")

    def test_separate_backups(self):
        self.assertEqual(len({B_STATE, STEP50_BACKUP, STEP51_BACKUP, STEP52_BACKUP}), 4)

if __name__ == "__main__":
    unittest.main()
