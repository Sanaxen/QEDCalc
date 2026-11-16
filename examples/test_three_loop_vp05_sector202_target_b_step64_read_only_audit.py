"""B Step64 post-promotion read-only audit regression guards."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step64_read_only_audit import (
    SAVED_STEP64_SHA, EXPECTED_STEP63_SHA, B_STATE,
    STEP63_BACKUP, STEP59_BACKUP, STEP58_BACKUP, A_STATE, A_PROOF,
)
class Step64ReadOnlyAuditTests(unittest.TestCase):
    def test_saved_step64_hash(self):
        self.assertEqual(SAVED_STEP64_SHA,
            "9e5ba49502e24f9367e15b42221086c470dd9670519798e8ab555e147a33992a")
        self.assertEqual(EXPECTED_STEP63_SHA,
            "78bcc7570d5bc8a85b0c478c3b750559e3d73154781889607ac3bde43badf9d5")
    def test_paths_distinct(self):
        paths=[B_STATE,STEP63_BACKUP,STEP59_BACKUP,STEP58_BACKUP,A_STATE,A_PROOF]
        self.assertEqual(len({x.resolve() for x in paths}),len(paths))
if __name__=="__main__":
    unittest.main()
