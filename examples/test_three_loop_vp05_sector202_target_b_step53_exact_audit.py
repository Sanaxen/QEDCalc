"""Fast structural checks for read-only B Step53 original-IBP audit."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step53_exact_audit import (
    REPORT, OUT, STATE, EXPECTED_B_STEP52_SHA, STEP50_BACKUP, STEP51_BACKUP,
)

class BStep53ExactAuditTests(unittest.TestCase):
    def test_protected_paths_distinct(self):
        self.assertEqual(len({REPORT, OUT, STATE, STEP50_BACKUP, STEP51_BACKUP}), 5)
        self.assertIn("step53", REPORT.name)
    def test_state_sha_pinned(self):
        self.assertEqual(EXPECTED_B_STEP52_SHA,
            "b398b7f9630c2ea2c8a90c1939517a7e5095170d65c1c68d9dc47b294776aa95")

if __name__ == "__main__":
    unittest.main()
