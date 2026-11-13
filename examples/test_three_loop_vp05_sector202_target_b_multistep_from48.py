"""Synthetic regression tests for exact Target B Step48 to Step64."""
import unittest
from examples.three_loop_vp05_sector202_target_b_multistep_from48 import classify

class TargetBStep48Tests(unittest.TestCase):
    def setUp(self):
        self.before={"steps":48,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                     "pivot_path":[[i,139] for i in range(48)],
                     "exact_target_proven":False,"config":{"target":"B"}}
    def after(self,n,status="EXACT_TARGET_PREFIX_NOT_PROOF"):
        return {**self.before,"steps":n,"status":status,
                "pivot_path":[[i,139] for i in range(n)]}
    def test_full_batch(self):
        self.assertEqual(classify(self.before,self.after(64),16,0,False),
                         "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF")
    def test_cap_and_timeout(self):
        self.assertEqual(classify(self.before,self.after(53,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_CAP_STOP_NOT_PROOF")
        self.assertEqual(classify(self.before,self.after(54),16,-1,True),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_TIME_CEILING_NOT_PROOF")
    def test_proof_requires_audit(self):
        self.assertEqual(classify(self.before,self.after(60),16,0,False,True),
                         "MULTISTEP_PROOF_FILE_REQUIRES_INSPECTION")
    def test_invalid_mutations(self):
        with self.assertRaises(RuntimeError):
            classify(self.before,self.after(65),16,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.before,{**self.after(55),"config":{"target":"A"}},16,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.before,{**self.after(55),"pivot_path":[]},16,0,False)

if __name__=="__main__":
    unittest.main()
