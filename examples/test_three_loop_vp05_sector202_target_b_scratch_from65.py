"""SHA-pinned Step66 isolated scratch safety regression."""
import unittest
from examples.three_loop_vp05_sector202_target_b_scratch_from65 import (
    SCRATCH, B_STATE, START_STEP, START_REMAINING, START_SUPPORT,
    START_MAX_CHARS, SAVED_STEP65_SHA, PROTECTED, validate_scratch,
    STEP63_BACKUP, STEP64_BACKUP, EXPECTED_STEP63_SHA, EXPECTED_STEP64_SHA,
)
class Step66ScratchTests(unittest.TestCase):
    def test_audited_baseline(self):
        self.assertEqual((START_STEP,START_REMAINING,START_SUPPORT,START_MAX_CHARS),(65,85,173,7426))
        self.assertEqual(SAVED_STEP65_SHA,"eeab74cfde337424db3e8d54de8078c3f82c994a0a35a689531842d79a8c941f")
        self.assertEqual(EXPECTED_STEP64_SHA,"9e5ba49502e24f9367e15b42221086c470dd9670519798e8ab555e147a33992a")
        self.assertEqual(EXPECTED_STEP63_SHA,"78bcc7570d5bc8a85b0c478c3b750559e3d73154781889607ac3bde43badf9d5")
    def test_distinct_protected_paths(self):
        paths=[p.resolve() for p,_ in PROTECTED]+[SCRATCH.resolve()]
        self.assertEqual(len(paths),len(set(paths)))
        self.assertIn("step63_before_step64",STEP63_BACKUP.name)
        self.assertIn("step64_before_step65",STEP64_BACKUP.name)
        self.assertNotEqual(SCRATCH.resolve(),B_STATE.resolve())
    def test_prefix_guard_rejects_modified_pivot(self):
        formal={"config":{"target":"B"},"pivot_path":[[k,139] for k in range(65)]}
        scratch={"config":{"target":"B"},"steps":65,"pivot_path":formal["pivot_path"][:],
                 "exact_target_proven":False,"status":"EXACT_TARGET_PREFIX_NOT_PROOF"}
        validate_scratch(formal,scratch)
        mutated={**scratch,"pivot_path":[[123456,139]]+scratch["pivot_path"][1:]}
        with self.assertRaises(RuntimeError):validate_scratch(formal,mutated)
if __name__=="__main__":
    unittest.main()
