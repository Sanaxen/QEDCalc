"""Step60 coefficient pilot hash and isolated-artefact regression tests."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step60_exact_candidate import (
    KNOWN_B_STEP59_SHA, OUT, STATE, STEP50_BACKUP,
    STEP51_BACKUP, STEP52_BACKUP, STEP58_BACKUP, get_jobs,
)
class BStep60PilotTests(unittest.TestCase):
    def test_checkpoint_pinned(self):
        self.assertEqual(KNOWN_B_STEP59_SHA,
            "a5a341737487cc4a1f2e20323b1adc927ead02e043af44db4442857a7cfdc38a")
        self.assertEqual(len({OUT,STATE,STEP50_BACKUP,STEP51_BACKUP,STEP52_BACKUP,STEP58_BACKUP}),6)
    def test_reject_wrong_prior_step(self):
        with self.assertRaises(RuntimeError):
            get_jobs({"steps":58,"config":{"target":"B"}}, {"pivots":[]})
if __name__=="__main__":
    unittest.main()
