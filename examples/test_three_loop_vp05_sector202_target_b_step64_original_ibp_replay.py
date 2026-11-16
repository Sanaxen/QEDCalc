"""Regressions for bounded Step64 exact original-source IBP replay."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step64_original_ibp_replay import (
    REPLAY, REPORT, OUT, STATE, AUDIT, SOURCE, EXPECTED_STEP63_SHA,
    EXPECTED_CANDIDATE_SHA,
)
class Step64OriginalIBPReplayTests(unittest.TestCase):
    def test_expected_inputs_pinned(self):
        self.assertEqual(EXPECTED_STEP63_SHA,
            "78bcc7570d5bc8a85b0c478c3b750559e3d73154781889607ac3bde43badf9d5")
        self.assertEqual(EXPECTED_CANDIDATE_SHA,
            "f97a5eee3d99d80bd6bfae9761c2815e3655116a2548dc2e3a465dc12b52890f")
    def test_checkpoint_never_overwrites_inputs(self):
        inputs=[REPLAY,REPORT,OUT,STATE,AUDIT,SOURCE]
        self.assertEqual(len({p.resolve() for p in inputs}),len(inputs))
    def test_explicit_not_proof_name(self):
        self.assertIn("original_ibp_exact_replay_checkpoint",REPLAY.name)
if __name__=="__main__":
    unittest.main()
