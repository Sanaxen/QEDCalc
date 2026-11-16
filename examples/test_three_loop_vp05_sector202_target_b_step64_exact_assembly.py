"""Step64 immutable exact assembly safety regression."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step64_exact_assembly import (
    REPORT, EXPECTED_CANDIDATE_SHA, EXPECTED_STEP63_SHA, AUDIT, OUT, STATE,
)
class TestStep64Assembly(unittest.TestCase):
    def test_pinned_candidate(self):
        self.assertEqual(EXPECTED_CANDIDATE_SHA,
            "f97a5eee3d99d80bd6bfae9761c2815e3655116a2548dc2e3a465dc12b52890f")
        self.assertEqual(EXPECTED_STEP63_SHA,
            "78bcc7570d5bc8a85b0c478c3b750559e3d73154781889607ac3bde43badf9d5")
    def test_no_alias(self):
        paths=[REPORT,AUDIT,OUT,STATE]
        self.assertEqual(len({p.resolve() for p in paths}),len(paths))
if __name__=="__main__":
    unittest.main()
