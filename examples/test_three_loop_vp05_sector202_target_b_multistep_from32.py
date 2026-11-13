"""Synthetic transition tests for Target B 32→48 continuation."""
import unittest
from examples.three_loop_vp05_sector202_target_b_multistep_from32 import classify

class TargetBStep32Tests(unittest.TestCase):
    def setUp(self):
        self.old={"steps":32,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                  "pivot_path":[[i,139] for i in range(32)],
                  "exact_target_proven":False,"config":{"target":"B"}}
    def after(self,n,status="EXACT_TARGET_PREFIX_NOT_PROOF"):
        return {**self.old,"steps":n,"status":status,
                "pivot_path":[[i,139] for i in range(n)]}
    def test_full(self):
        self.assertEqual(classify(self.old,self.after(48),16,0,False),
                         "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF")
    def test_bounded(self):
        self.assertEqual(classify(self.old,self.after(39,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_CAP_STOP_NOT_PROOF")
        self.assertEqual(classify(self.old,self.after(36),16,-1,True),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_TIME_CEILING_NOT_PROOF")
    def test_proof_file_needs_review(self):
        self.assertEqual(classify(self.old,self.after(44),16,0,False,True),
                         "MULTISTEP_PROOF_FILE_REQUIRES_INSPECTION")
    def test_invalid(self):
        with self.assertRaises(RuntimeError):
            classify(self.old,self.after(49),16,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.old,{**self.after(44),"config":{"target":"A"}},16,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.old,{**self.after(44),"pivot_path":[]},16,0,False)

if __name__=="__main__":
    unittest.main()
