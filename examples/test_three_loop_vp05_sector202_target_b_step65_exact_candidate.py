"""Step65 pinned scratch and exact-coefficient pilot safety tests."""
import unittest
from examples.three_loop_vp05_sector202_target_b_step65_scratch_guard import (
    SCRATCH_SHA, SAVED_STEP64_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step65_exact_candidate import (
    KNOWN_B_STEP64_SHA, OUT, STATE, get_jobs,
)
from examples.three_loop_vp05_sector202_target_b_scratch_from64 import SCRATCH

class Step65PilotTests(unittest.TestCase):
    def test_pinned_immutable_formal(self):
        self.assertEqual(KNOWN_B_STEP64_SHA,SAVED_STEP64_SHA)
        self.assertEqual(SAVED_STEP64_SHA,"9e5ba49502e24f9367e15b42221086c470dd9670519798e8ab555e147a33992a")
        self.assertEqual(SCRATCH_SHA,"e7ef7c12cb68cb8492723a864ba80febda9a8a5415581ec4bd1cd2ad15989fcc")
    def test_candidate_does_not_alias_inputs(self):
        self.assertEqual(len({p.resolve() for p in (OUT,STATE,SCRATCH)}),3)
    def test_wrong_baseline_rejected(self):
        with self.assertRaises(RuntimeError):
            get_jobs({"steps":63,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                      "exact_target_proven":False,"config":{"target":"B","max_expression_chars":7500},
                      "remaining":[],"source":[]}, {"pivots":[]})
if __name__=="__main__":
    unittest.main()
