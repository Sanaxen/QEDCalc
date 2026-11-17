"""Step65 saved formal-state read-only audit regression guards."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step65_read_only_audit import (
    SAVED_STEP65_SHA, EXPECTED_STEP64_SHA, EXPECTED_STEP63_SHA,
    B_STATE, STEP64_BACKUP, STEP63_BACKUP, STEP59_BACKUP, A_STATE, A_PROOF,
)
class BStep65ReadOnlyAuditTests(unittest.TestCase):
    def test_pinned_formal_and_backup_hashes(self):
        self.assertEqual(SAVED_STEP65_SHA,"eeab74cfde337424db3e8d54de8078c3f82c994a0a35a689531842d79a8c941f")
        self.assertEqual(EXPECTED_STEP64_SHA,"9e5ba49502e24f9367e15b42221086c470dd9670519798e8ab555e147a33992a")
        self.assertEqual(EXPECTED_STEP63_SHA,"78bcc7570d5bc8a85b0c478c3b750559e3d73154781889607ac3bde43badf9d5")
    def test_no_alias_to_backup_or_target_a(self):
        paths=(B_STATE,STEP64_BACKUP,STEP63_BACKUP,STEP59_BACKUP,A_STATE,A_PROOF)
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
        self.assertIn("step63_before_step64",STEP63_BACKUP.name)
        self.assertIn("step64_before_step65",STEP64_BACKUP.name)
if __name__=="__main__":
    unittest.main()
