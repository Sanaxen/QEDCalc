"""Synthetic transition checks for Target B exact Step16→32 batch."""
import unittest
from examples.three_loop_vp05_sector202_target_b_multistep_from16 import classify


class BMultiStepTests(unittest.TestCase):
    def setUp(self):
        self.old = {"steps":16,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                    "pivot_path":[[i,139] for i in range(16)],
                    "exact_target_proven":False,"config":{"target":"B"}}
    def after(self,steps,status="EXACT_TARGET_PREFIX_NOT_PROOF"):
        return {**self.old,"steps":steps,"status":status,
                "pivot_path":[[i,139] for i in range(steps)]}
    def test_full(self):
        self.assertEqual(classify(self.old,self.after(32),16,0,False),
                         "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF")
    def test_cap_timeout(self):
        self.assertEqual(classify(self.old,self.after(21,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_CAP_STOP_NOT_PROOF")
        self.assertEqual(classify(self.old,self.after(23),16,-1,True),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_TIME_CEILING_NOT_PROOF")
    def test_proof_held_for_audit(self):
        self.assertEqual(classify(self.old,self.after(29),16,0,False,True),
                         "MULTISTEP_PROOF_FILE_REQUIRES_INSPECTION")
    def test_reject_invalid(self):
        with self.assertRaises(RuntimeError):
            classify(self.old,self.after(33),16,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.old,{**self.after(23),"config":{"target":"A"}},16,0,False)


if __name__=="__main__":
    unittest.main()
