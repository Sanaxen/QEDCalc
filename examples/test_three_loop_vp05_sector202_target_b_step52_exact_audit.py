"""Fast invariants for B Step52 independent IBP audit."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step52_exact_audit import (
    REPORT,OUT,STATE,EXPECTED_B_STEP51_SHA,
)

class BStep52AuditSmoke(unittest.TestCase):
    def test_paths_and_sha(self):
        self.assertEqual(len({REPORT,OUT,STATE}),3)
        self.assertEqual(EXPECTED_B_STEP51_SHA,
            "382e76dbbfc6f57c0dbf6468b53329d91a869ed9267a98093ac7165d8c6c7aac")
        self.assertIn("step52",REPORT.name)

if __name__=="__main__":
    unittest.main()
