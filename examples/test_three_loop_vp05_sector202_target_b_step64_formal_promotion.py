"""Regression checks for SHA-bound B Step64 backup-first promotion."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step64_formal_promotion import (
    BACKUP, STATE, REPORT, REPLAY, OUT, AUDIT,
    ASSEMBLED_SHA, EXPECTED_STEP63_SHA, EXPECTED_CANDIDATE_SHA,
    valid_replay_method,
)
class Step64PromotionTests(unittest.TestCase):
    def test_exact_sha_pins(self):
        self.assertEqual(EXPECTED_STEP63_SHA,
            "78bcc7570d5bc8a85b0c478c3b750559e3d73154781889607ac3bde43badf9d5")
        self.assertEqual(EXPECTED_CANDIDATE_SHA,
            "f97a5eee3d99d80bd6bfae9761c2815e3655116a2548dc2e3a465dc12b52890f")
        self.assertEqual(ASSEMBLED_SHA,
            "1d21672a3cccc8e4402091f6a120924107f2da07f612be97dfec60850e420d80")
    def test_legacy_direct_exact_certificate_without_method(self):
        self.assertTrue(valid_replay_method({"index":0,"key":[1,139]}))
    def test_current_methods_accepted(self):
        self.assertTrue(valid_replay_method({"method":"direct_original_ibp_exact"}))
        self.assertTrue(valid_replay_method({"method":"unscaled_source_pivot_exact_with_259_certificates"}))
    def test_unrecognized_or_false_method_rejected(self):
        for value in ("",None,"modular_only","numeric","unknown"):
            self.assertFalse(valid_replay_method({"method":value}))
        self.assertFalse(valid_replay_method([]))
    def test_backup_and_inputs_are_separate(self):
        paths=[BACKUP,STATE,REPORT,REPLAY,OUT,AUDIT]
        self.assertEqual(len({p.resolve() for p in paths}),len(paths))
        self.assertIn("step63_before_step64_promotion",BACKUP.name)

if __name__=="__main__":
    unittest.main()
