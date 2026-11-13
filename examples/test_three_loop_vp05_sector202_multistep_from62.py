"""Transition contract for multi-step bounded exact Target A continuation."""
import unittest
from examples.three_loop_vp05_sector202_multistep_from62 import classify


class MultiStepTests(unittest.TestCase):
    def setUp(self):
        self.old={"steps":62,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                  "pivot_path":[[i,139] for i in range(62)],
                  "exact_target_proven":False,"config":{"target":"A"}}

    def after(self,steps,status="EXACT_TARGET_PREFIX_NOT_PROOF"):
        return {**self.old,"steps":steps,"status":status,
                "pivot_path":[[i,139] for i in range(steps)]}

    def test_full_batch(self):
        self.assertEqual(classify(self.old,self.after(70),8,0,False),
                         "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF")

    def test_partial_cap_and_timeout(self):
        self.assertEqual(classify(self.old,self.after(66,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),8,0,False),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_CAP_STOP_NOT_PROOF")
        self.assertEqual(classify(self.old,self.after(65),8,-1,True),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_TIME_CEILING_NOT_PROOF")
        self.assertEqual(classify(self.old,self.after(62),8,-1,True),
                         "MULTISTEP_NO_NEW_STEP_SAVED_NOT_PROOF")

    def test_proof_is_not_automatically_claimed(self):
        self.assertEqual(classify(self.old,self.after(68),8,0,False,True),
                         "MULTISTEP_PROOF_FILE_REQUIRES_INSPECTION")

    def test_reject_bad_state(self):
        with self.assertRaises(RuntimeError):
            classify(self.old,self.after(71),8,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.old,{**self.after(63),"config":{}},8,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.old,{**self.after(63),"pivot_path":[]},8,0,False)


if __name__=="__main__":
    unittest.main()
