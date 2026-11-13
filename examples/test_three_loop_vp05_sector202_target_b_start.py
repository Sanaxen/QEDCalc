"""Synthetic safety checks for isolated Target B startup."""
import unittest
from examples.three_loop_vp05_sector202_target_b_start import classify_b

class TargetBStartTests(unittest.TestCase):
    def test_progress(self):
        state={"steps":16,"pivot_path":list(range(16)),
               "config":{"target":"B"},"exact_target_proven":False,
               "status":"EXACT_TARGET_PREFIX_NOT_PROOF"}
        self.assertEqual(classify_b(False,state,16,0,False,False),
                         "B_STEPS_SAVED_NOT_PROOF")
        cap={**state,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF"}
        self.assertEqual(classify_b(False,cap,16,0,False,False),
                         "B_PARTIAL_SAVED_CAP_STOP_NOT_PROOF")
        self.assertEqual(classify_b(False,state,16,0,False,True),
                         "B_PROOF_FILE_REQUIRES_INDEPENDENT_AUDIT")
    def test_stop_and_reject(self):
        self.assertEqual(classify_b(False,None,16,-1,True,False),
                         "B_NOT_STARTED_NOT_PROOF")
        with self.assertRaises(RuntimeError):
            classify_b(True,None,16,0,False,False)
        with self.assertRaises(RuntimeError):
            classify_b(False,{"steps":17,"pivot_path":list(range(17)),
                         "config":{"target":"B"},"exact_target_proven":False,
                         "status":"EXACT_TARGET_PREFIX_NOT_PROOF"},16,0,False,False)

if __name__=="__main__":
    unittest.main()
