"""Fast invariants for Target B Step51 independent exact coefficient pilot."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step51_exact_candidate import (
    KNOWN_B_STEP50_SHA, OUT, STATE, get_jobs,
)


class TargetBStep51PilotTests(unittest.TestCase):
    def test_known_source_sha_and_output_isolation(self):
        self.assertEqual(KNOWN_B_STEP50_SHA,
            "f4c480ee9cd555549f690817c7f6cc4c8d80fcec329fa795e53ef5165955ba47")
        self.assertNotEqual(OUT, STATE)
        self.assertIn("B_step51", OUT.name)
    def test_reject_unrelated_checkpoint(self):
        with self.assertRaises(RuntimeError):
            get_jobs({"steps":49,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF",
                      "config":{"target":"B"}}, {"pivots":[]})


if __name__ == "__main__":
    unittest.main()
