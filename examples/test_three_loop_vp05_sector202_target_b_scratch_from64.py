"""Guarded scratch-only continuation regression checks for Step64 to Step65 onward."""
import unittest
from examples.three_loop_vp05_sector202_target_b_scratch_from64 import (
    SCRATCH, B_STATE, START_STEP, START_REMAINING, START_SUPPORT,
    START_MAX_CHARS, SAVED_STEP64_SHA, PROTECTED, validate_scratch,
)
class Step64ScratchTests(unittest.TestCase):
    def test_baseline_pinned(self):
        self.assertEqual((START_STEP,START_REMAINING,START_SUPPORT,START_MAX_CHARS),(64,86,172,7310))
        self.assertEqual(SAVED_STEP64_SHA,"9e5ba49502e24f9367e15b42221086c470dd9670519798e8ab555e147a33992a")
    def test_no_protected_alias(self):
        paths=[p.resolve() for p,_ in PROTECTED]+[SCRATCH.resolve()]
        self.assertEqual(len(paths),len(set(paths)))
        self.assertNotEqual(SCRATCH.resolve(),B_STATE.resolve())
    def test_scratch_history_must_preserve_prefix(self):
        formal={"config":{"target":"B"},"pivot_path":[[k,139] for k in range(64)]}
        copy={"config":{"target":"B"},"steps":64,"pivot_path":formal["pivot_path"][:],
              "exact_target_proven":False,"status":"EXACT_TARGET_PREFIX_NOT_PROOF"}
        validate_scratch(formal,copy)
        tampered={**copy,"pivot_path":copy["pivot_path"][:]}
        tampered["pivot_path"][0]=[999,139]
        with self.assertRaises(RuntimeError):validate_scratch(formal,tampered)
    def test_scratch_step_boundary(self):
        formal={"config":{"target":"B"},"pivot_path":[[k,139] for k in range(64)]}
        beyond={"config":{"target":"B"},"steps":81,
                "pivot_path":formal["pivot_path"]+[[k,139] for k in range(64,81)],
                "exact_target_proven":False,"status":"EXACT_TARGET_PREFIX_NOT_PROOF"}
        with self.assertRaises(RuntimeError):validate_scratch(formal,beyond)

if __name__=="__main__":
    unittest.main()
