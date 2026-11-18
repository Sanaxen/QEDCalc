import unittest
from examples.three_loop_vp05_sector202_target_b_step67_read_only_audit import (
    B_STATE,BACKUP,SCRATCH,COEFF,IBP,STEP65_BACKUP,OLD_SCRATCH,
    STEP66_DIRECT,STEP66_COEFF,STEP66_NORMALIZED,
)
class Step67SavedAuditTests(unittest.TestCase):
    def test_paths_unique(self):
        paths=[B_STATE,BACKUP,SCRATCH,COEFF,IBP,STEP65_BACKUP,OLD_SCRATCH,
               STEP66_DIRECT,STEP66_COEFF,STEP66_NORMALIZED]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
    def test_formal_and_backup_are_distinct(self):
        self.assertNotEqual(B_STATE.resolve(),BACKUP.resolve())
if __name__=="__main__":
    unittest.main()
