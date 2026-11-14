"""Fast invariants for Target B Step52 exact coefficient pilot."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step52_exact_candidate import (
    KNOWN_B_STEP51_SHA, OUT, STATE, get_jobs,
)

class TargetBStep52PilotTests(unittest.TestCase):
    def test_known_source_sha_and_isolation(self):
        self.assertEqual(KNOWN_B_STEP51_SHA,"382e76dbbfc6f57c0dbf6468b53329d91a869ed9267a98093ac7165d8c6c7aac")
        self.assertNotEqual(OUT,STATE)
        self.assertIn("B_step52",OUT.name)
    def test_reject_wrong_checkpoint(self):
        with self.assertRaises(RuntimeError):
            get_jobs({"steps":50,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF",
                      "config":{"target":"B"}},{"pivots":[]})

if __name__=="__main__":
    unittest.main()
