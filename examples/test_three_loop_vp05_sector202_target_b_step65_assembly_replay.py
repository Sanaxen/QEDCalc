"""Step65 candidate assembly/original-IBP replay safety regressions."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step65_exact_assembly import (
    REPORT, STATE, OUT, AUDIT, EXPECTED_CANDIDATE_SHA, EXPECTED_STEP64_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step65_original_ibp_replay import (
    REPLAY, load, worker,
)
from examples.three_loop_vp05_sector202_target_b_step64_formal_promotion import BACKUP as STEP63_BACKUP, EXPECTED_STEP63_SHA

class Step65AssemblyReplayTests(unittest.TestCase):
    def test_immutable_hashes(self):
        self.assertEqual(EXPECTED_CANDIDATE_SHA,
            "9d4a2a24f0d6f15c54fd6cc72b0a542bcfc6fe6756bcd5965594fc73d4608d12")
        self.assertEqual(EXPECTED_STEP64_SHA,
            "9e5ba49502e24f9367e15b42221086c470dd9670519798e8ab555e147a33992a")
        self.assertEqual(EXPECTED_STEP63_SHA,
            "78bcc7570d5bc8a85b0c478c3b750559e3d73154781889607ac3bde43badf9d5")
    def test_file_isolation(self):
        paths=[REPORT,REPLAY,STATE,OUT,AUDIT,STEP63_BACKUP]
        self.assertEqual(len({p.resolve() for p in paths}),len(paths))
    def test_entrypoints(self):
        self.assertTrue(callable(load))
        self.assertTrue(callable(worker))

if __name__=="__main__":
    unittest.main()
