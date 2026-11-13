"""Regression tests for 16-step bounded Target A continuation from Step86."""
import unittest
from examples.three_loop_vp05_sector202_multistep_from86 import classify

class MultiStepFrom86Tests(unittest.TestCase):
    def setUp(self):
        self.old={"steps":86,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                  "pivot_path":[[i,139] for i in range(86)],
                  "exact_target_proven":False,"config":{"target":"A"}}

    def after(self,steps,status="EXACT_TARGET_PREFIX_NOT_PROOF"):
        return {**self.old,"steps":steps,"status":status,
                "pivot_path":[[i,139] for i in range(steps)]}

    def test_full(self):
        self.assertEqual(classify(self.old,self.after(102),16,0,False),
                         "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF")
    def test_partial_cap_timeout(self):
        self.assertEqual(classify(self.old,self.after(89,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_CAP_STOP_NOT_PROOF")
        self.assertEqual(classify(self.old,self.after(91),16,-1,True),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_TIME_CEILING_NOT_PROOF")
        self.assertEqual(classify(self.old,self.after(86),16,-1,True),
                         "MULTISTEP_NO_NEW_STEP_SAVED_NOT_PROOF")
    def test_proof_requires_inspection(self):
        self.assertEqual(classify(self.old,self.after(93),16,0,False,True),
                         "MULTISTEP_PROOF_FILE_REQUIRES_INSPECTION")
    def test_invalid(self):
        with self.assertRaises(RuntimeError):
            classify(self.old,self.after(103),16,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.old,{**self.after(91),"config":{}},16,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.old,{**self.after(91),"pivot_path":[]},16,0,False)

if __name__ == "__main__":
    unittest.main()
