"""Regression tests for Target B guarded Step52 to Step68 run."""
import unittest
from examples.three_loop_vp05_sector202_target_b_multistep_from52 import (
    START_SHA, START_STEP, START_REMAINING, START_SUPPORT, START_LEAD,
    START_MAX_CHARS, classify,
)

class TargetBFrom52Tests(unittest.TestCase):
    def setUp(self):
        self.before={"steps":52,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                     "pivot_path":[[i,139] for i in range(52)],
                     "config":{"target":"B"},"exact_target_proven":False}
    def after(self,n,status="EXACT_TARGET_PREFIX_NOT_PROOF"):
        return {**self.before,"steps":n,"status":status,
                "pivot_path":[[i,139] for i in range(n)]}
    def test_exact_anchors(self):
        self.assertEqual(START_SHA,"731147f8d8113e12684afbc21d9756991d0378361326d391693d2c671a0565f2")
        self.assertEqual((START_STEP,START_REMAINING,START_SUPPORT,START_MAX_CHARS),
                         (52,103,187,7447))
        self.assertEqual(START_LEAD,[166595341189122,139])
    def test_saved_and_cap(self):
        self.assertEqual(classify(self.before,self.after(68),16,0,False),
                         "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF")
        self.assertEqual(classify(self.before,self.after(52,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_NO_NEW_STEP_SAVED_NOT_PROOF")
        self.assertEqual(classify(self.before,self.after(55,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_CAP_STOP_NOT_PROOF")
    def test_proof_requires_audit(self):
        self.assertEqual(classify(self.before,self.after(60),16,0,False,True),
                         "MULTISTEP_PROOF_FILE_REQUIRES_INSPECTION")
    def test_bad_overshoot(self):
        with self.assertRaises(RuntimeError):
            classify(self.before,self.after(69),16,0,False)

if __name__=="__main__":
    unittest.main()
