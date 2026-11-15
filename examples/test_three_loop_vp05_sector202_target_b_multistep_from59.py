"""Regression checks for hash-pinned B continuation from formal Step59."""
import unittest
from examples.three_loop_vp05_sector202_target_b_multistep_from59 import (
    START_SHA, START_STEP, START_REMAINING, START_SUPPORT, START_MAX_CHARS,
    STEP58_BACKUP, B_STEP58_SHA, classify,
)
class BFrom59Tests(unittest.TestCase):
    def setUp(self):
        self.before={"steps":59,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
            "pivot_path":[[i,139] for i in range(59)],
            "config":{"target":"B"},"exact_target_proven":False}
    def after(self,n,status="EXACT_TARGET_PREFIX_NOT_PROOF"):
        return {**self.before,"steps":n,"status":status,
            "pivot_path":[[i,139] for i in range(n)]}
    def test_pinned_inputs(self):
        self.assertEqual(START_SHA,"88cab7046de7cab3f5733ffc788a375a795d8842d89a4b1c794f775dba2e8dda")
        self.assertEqual((START_STEP, START_REMAINING, START_SUPPORT, START_MAX_CHARS),(59,86,163,7439))
        self.assertEqual(B_STEP58_SHA,"565af78b3e8604782f614515fb2b93d8a25efa6022174a2ca4bcc9673fc56d4b")
        self.assertIn("step58", STEP58_BACKUP.name)
    def test_cap_stop_without_step(self):
        self.assertEqual(classify(self.before,self.after(59,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_NO_NEW_STEP_SAVED_NOT_PROOF")
    def test_partial_cap_stop(self):
        self.assertEqual(classify(self.before,self.after(62,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
                         "MULTISTEP_PARTIAL_STEPS_SAVED_CAP_STOP_NOT_PROOF")
    def test_saved_steps(self):
        self.assertEqual(classify(self.before,self.after(75),16,0,False),
                         "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF")
    def test_overshoot_rejected(self):
        with self.assertRaises(RuntimeError):
            classify(self.before,self.after(76),16,0,False)
    def test_proof_artifact_requires_inspection(self):
        self.assertEqual(classify(self.before,self.after(60),16,0,False,True),
                         "MULTISTEP_PROOF_FILE_REQUIRES_INSPECTION")
if __name__=="__main__":
    unittest.main()
