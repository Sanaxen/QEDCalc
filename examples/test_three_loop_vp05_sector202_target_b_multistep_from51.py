"""Bounded exact Step51→67 Target B transition tests."""
import unittest
from examples.three_loop_vp05_sector202_target_b_multistep_from51 import classify

class BFrom51Tests(unittest.TestCase):
    def setUp(self):
        self.start={"steps":51,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                    "pivot_path":[[i,139] for i in range(51)],
                    "exact_target_proven":False,"config":{"target":"B"}}
    def after(self,n,status="EXACT_TARGET_PREFIX_NOT_PROOF"):
        return {**self.start,"steps":n,"status":status,
                "pivot_path":[[i,139] for i in range(n)]}
    def test_full(self):
        self.assertEqual(classify(self.start,self.after(67),16,0,False),
                         "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF")
    def test_cap_and_timeout(self):
        self.assertEqual(classify(self.start,self.after(51,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_NO_NEW_STEP_SAVED_NOT_PROOF")
        self.assertEqual(classify(self.start,self.after(55,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_CAP_STOP_NOT_PROOF")
        self.assertEqual(classify(self.start,self.after(54),16,-1,True),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_TIME_CEILING_NOT_PROOF")
    def test_proof_and_errors(self):
        self.assertEqual(classify(self.start,self.after(60),16,0,False,True),
                         "MULTISTEP_PROOF_FILE_REQUIRES_INSPECTION")
        with self.assertRaises(RuntimeError):
            classify(self.start,self.after(68),16,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.start,{**self.after(57),"config":{"target":"A"}},16,0,False)

if __name__=="__main__":
    unittest.main()
