"""Pinned structural integrity checks for saved B Step63."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step63_read_only_audit import (
    SAVED_STEP63_SHA, B_STATE, STEP50_BACKUP, STEP51_BACKUP,
    STEP52_BACKUP, STEP58_BACKUP, STEP59_BACKUP,
)
class BStep63ReadOnlyTests(unittest.TestCase):
    def test_hash_pin(self):
        self.assertEqual(SAVED_STEP63_SHA,
            "78bcc7570d5bc8a85b0c478c3b750559e3d73154781889607ac3bde43badf9d5")
    def test_distinct_protected_paths(self):
        paths=[B_STATE,STEP50_BACKUP,STEP51_BACKUP,STEP52_BACKUP,
               STEP58_BACKUP,STEP59_BACKUP]
        self.assertEqual(len({x.resolve() for x in paths}),len(paths))
if __name__=="__main__":
    unittest.main()
