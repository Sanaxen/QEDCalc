"""Static regression checks for Target B Step53 exact coefficient pilot."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step53_exact_candidate import (
    KNOWN_B_STEP52_SHA, OUT, STATE, get_jobs, STEP50_BACKUP, STEP51_BACKUP,
)

class TargetBStep53PilotTests(unittest.TestCase):
    def test_anchored_state_and_isolation(self):
        self.assertEqual(KNOWN_B_STEP52_SHA,
            "b398b7f9630c2ea2c8a90c1939517a7e5095170d65c1c68d9dc47b294776aa95")
        self.assertEqual(len({OUT,STATE,STEP50_BACKUP,STEP51_BACKUP}),4)
        self.assertIn("B_step53",OUT.name)
    def test_reject_wrong_checkpoint(self):
        with self.assertRaises(RuntimeError):
            get_jobs({"steps":51,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF",
                      "config":{"target":"B"}},{"pivots":[]})
if __name__=="__main__":
    unittest.main()
