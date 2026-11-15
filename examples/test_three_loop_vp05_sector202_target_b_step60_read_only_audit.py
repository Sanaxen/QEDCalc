"""Regression checks for SHA-pinned read-only formal Step60 audit."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step60_read_only_audit import (
    PROMOTED_STEP60_SHA, B_STATE, STEP50_BACKUP, STEP51_BACKUP,
    STEP52_BACKUP, STEP58_BACKUP, STEP59_BACKUP, B_STEP59_SHA,
)

class BStep60ReadOnlyAuditTests(unittest.TestCase):
    def test_exact_sha(self):
        self.assertEqual(PROMOTED_STEP60_SHA,
            "4eebc9694e460654e1224fa72e6d6385ae1689dedf3004bbf5934be27f3075c8")
        self.assertEqual(B_STEP59_SHA,
            "a5a341737487cc4a1f2e20323b1adc927ead02e043af44db4442857a7cfdc38a")

    def test_protected_paths_distinct(self):
        paths=[B_STATE,STEP50_BACKUP,STEP51_BACKUP,STEP52_BACKUP,
               STEP58_BACKUP,STEP59_BACKUP]
        self.assertEqual(len({p.resolve() for p in paths}),len(paths))

if __name__=="__main__":
    unittest.main()
