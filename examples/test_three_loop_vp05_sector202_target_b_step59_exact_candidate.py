"""Structural regression checks for B Step59 coefficient pilot."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step59_exact_candidate import (
    KNOWN_B_STEP58_SHA, OUT, STATE, get_jobs,
    STEP50_BACKUP, STEP51_BACKUP, STEP52_BACKUP,
)

class BStep59PilotTests(unittest.TestCase):
    def test_exact_state_anchor(self):
        self.assertEqual(KNOWN_B_STEP58_SHA,
            "565af78b3e8604782f614515fb2b93d8a25efa6022174a2ca4bcc9673fc56d4b")
        self.assertEqual(len({OUT, STATE, STEP50_BACKUP, STEP51_BACKUP, STEP52_BACKUP}), 5)
        self.assertIn("B_step59", OUT.name)

    def test_reject_wrong_step(self):
        with self.assertRaises(RuntimeError):
            get_jobs({"steps": 53, "status": "EXACT_TARGET_CAP_REACHED_NOT_PROOF",
                      "config": {"target": "B"}}, {"pivots": []})

if __name__ == "__main__":
    unittest.main()
