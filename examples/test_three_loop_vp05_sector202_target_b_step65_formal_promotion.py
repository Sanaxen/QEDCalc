"""Static safety regressions for SHA-pinned Step65 promotion."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step65_formal_promotion import (
    BACKUP, STATE, OUT, AUDIT, REPORT, REPLAY, ASSEMBLED_SHA,
    EXPECTED_STEP64_SHA, EXPECTED_CANDIDATE_SHA, valid_replay_method,
)
class BStep65PromotionTests(unittest.TestCase):
    def test_immutable_pins(self):
        self.assertEqual(ASSEMBLED_SHA,"ea51e8c0661fdd68c676d4daf1be03c0bace659156f10ee58b021587a0597861")
        self.assertEqual(EXPECTED_STEP64_SHA,"9e5ba49502e24f9367e15b42221086c470dd9670519798e8ab555e147a33992a")
        self.assertEqual(EXPECTED_CANDIDATE_SHA,"9d4a2a24f0d6f15c54fd6cc72b0a542bcfc6fe6756bcd5965594fc73d4608d12")
    def test_distinct_protected_paths(self):
        paths=(BACKUP,STATE,OUT,AUDIT,REPORT,REPLAY)
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
    def test_exact_worker_method_only(self):
        self.assertTrue(valid_replay_method({"method":"unscaled_source_pivot_exact_with_40_certificates"}))
        for bad in ({"method":"numeric"},{},{ "method":"unscaled_source_pivot_exact_with_259_certificates"}):
            self.assertFalse(valid_replay_method(bad))
if __name__=="__main__":
    unittest.main()
