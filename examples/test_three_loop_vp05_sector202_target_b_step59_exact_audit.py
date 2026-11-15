"""Safety checks for independent exact B Step59 original-IBP replay."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step59_exact_audit import (
    REPORT, OUT, STATE, EXPECTED_B_STEP58_SHA, STEP50_BACKUP,
    STEP51_BACKUP, STEP52_BACKUP,
)

class BStep59AuditTests(unittest.TestCase):
    def test_hash(self):
        self.assertEqual(EXPECTED_B_STEP58_SHA,
            "565af78b3e8604782f614515fb2b93d8a25efa6022174a2ca4bcc9673fc56d4b")
    def test_isolated_artifacts(self):
        self.assertEqual(len({REPORT,OUT,STATE,STEP50_BACKUP,STEP51_BACKUP,STEP52_BACKUP}),6)
        self.assertIn("step59", REPORT.name)

if __name__ == "__main__":
    unittest.main()
