"""Regression checks for hash-pinned Target B continuation from Step53."""
import unittest
from examples.three_loop_vp05_sector202_target_b_multistep_from53 import (
    START_SHA, START_STEP, START_REMAINING, START_SUPPORT, START_MAX_CHARS, classify,
)

class BFrom53Tests(unittest.TestCase):
    def setUp(self):
        self.before={"steps":53,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                     "pivot_path":[[i,139] for i in range(53)],
                     "config":{"target":"B"},"exact_target_proven":False}
    def after(self,n,status="EXACT_TARGET_PREFIX_NOT_PROOF"):
        return {**self.before,"steps":n,"status":status,
                "pivot_path":[[i,139] for i in range(n)]}
    def test_hash_and_shape(self):
        self.assertEqual(START_SHA,"684ee4ed3936a52d940e58f8292b9d7a8b38b7d6822492e9709bb8427ff64505")
        self.assertEqual((START_STEP,START_REMAINING,START_SUPPORT,START_MAX_CHARS),(53,101,188,7447))
    def test_cap_stop(self):
        self.assertEqual(classify(self.before,self.after(53,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_NO_NEW_STEP_SAVED_NOT_PROOF")
    def test_saved_steps(self):
        self.assertEqual(classify(self.before,self.after(69),16,0,False),
                         "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF")
    def test_reject_overshoot(self):
        with self.assertRaises(RuntimeError):
            classify(self.before,self.after(70),16,0,False)
    def test_proof_needs_review(self):
        self.assertEqual(classify(self.before,self.after(60),16,0,False,True),
                         "MULTISTEP_PROOF_FILE_REQUIRES_INSPECTION")

if __name__=="__main__":
    unittest.main()
