import unittest
from unittest.mock import patch
from examples.three_loop_vp05_sector202_target_b_step66_read_only_audit import (
    inspect,BACKUP,B_STATE,SCRATCH,DIRECT,COEFFICIENT,NORMALIZED,PROTECTED,
)
class SavedStep66AuditTests(unittest.TestCase):
    def test_distinct_paths(self):
        paths=[BACKUP,B_STATE,SCRATCH,DIRECT,COEFFICIENT,NORMALIZED]
        paths.extend(path for path,digest in PROTECTED if path.resolve()!=B_STATE.resolve())
        self.assertEqual(len(set(p.resolve() for p in paths)),len(paths))
    def test_expected_saved_target_is_distinct(self):
        self.assertNotEqual(BACKUP.resolve(),B_STATE.resolve())
        self.assertNotEqual(SCRATCH.resolve(),B_STATE.resolve())
if __name__=="__main__":
    unittest.main()
