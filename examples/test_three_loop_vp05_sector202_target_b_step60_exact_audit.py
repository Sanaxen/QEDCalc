"""Isolated read-only B Step60 audit static regression checks."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step60_exact_audit import (
    REPORT, OUT, STATE, EXPECTED_B_STEP59_SHA,
    STEP50_BACKUP, STEP51_BACKUP, STEP52_BACKUP, STEP58_BACKUP,
)
class TestStep60Audit(unittest.TestCase):
    def test_checkpoint_hash(self):
        self.assertEqual(EXPECTED_B_STEP59_SHA,
            "a5a341737487cc4a1f2e20323b1adc927ead02e043af44db4442857a7cfdc38a")
    def test_unique_artifacts(self):
        paths=[REPORT, OUT, STATE, STEP50_BACKUP,STEP51_BACKUP,STEP52_BACKUP,STEP58_BACKUP]
        self.assertEqual(len({p.resolve() for p in paths}),len(paths))
        self.assertIn("step60",REPORT.name)
if __name__=="__main__":
    unittest.main()
