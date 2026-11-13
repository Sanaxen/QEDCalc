"""Offline regression tests for 16-step bounded sector202 continuation from Step70."""
import unittest
from examples.three_loop_vp05_sector202_multistep_from70 import classify


class MultiStepFrom70Tests(unittest.TestCase):
    def setUp(self):
        self.old={"steps":70,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                  "pivot_path":[[i,139] for i in range(70)],
                  "exact_target_proven":False,"config":{"target":"A"}}

    def after(self, steps, status="EXACT_TARGET_PREFIX_NOT_PROOF"):
        return {**self.old,"steps":steps,"status":status,
                "pivot_path":[[i,139] for i in range(steps)]}

    def test_full_batch(self):
        self.assertEqual(classify(self.old,self.after(86),16,0,False),
                         "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF")

    def test_partial_cap_and_timeout(self):
        self.assertEqual(classify(self.old,self.after(76,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_CAP_STOP_NOT_PROOF")
        self.assertEqual(classify(self.old,self.after(73),16,-1,True),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_TIME_CEILING_NOT_PROOF")
        self.assertEqual(classify(self.old,self.after(70),16,-1,True),
                         "MULTISTEP_NO_NEW_STEP_SAVED_NOT_PROOF")

    def test_proof_requires_inspection(self):
        self.assertEqual(classify(self.old,self.after(81),16,0,False,True),
                         "MULTISTEP_PROOF_FILE_REQUIRES_INSPECTION")

    def test_invalid_mutation(self):
        with self.assertRaises(RuntimeError):
            classify(self.old,self.after(87),16,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.old,{**self.after(74),"config":{}},16,0,False)
        with self.assertRaises(RuntimeError):
            classify(self.old,{**self.after(74),"pivot_path":[]},16,0,False)


if __name__=="__main__":
    unittest.main()
