"""Regression checks for SHA-pinned B continuation from audited Step60."""
import unittest
from examples.three_loop_vp05_sector202_target_b_multistep_from60 import (
    START_SHA, START_STEP, START_REMAINING, START_SUPPORT, START_MAX_CHARS,
    STEP59_BACKUP, B_STEP59_SHA, classify,
)

class BFrom60Tests(unittest.TestCase):
    def setUp(self):
        self.before={"steps":60,"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
            "pivot_path":[[i,139] for i in range(60)],
            "config":{"target":"B"},"exact_target_proven":False,
            "remaining":[[[100,139],"1/(z+1)"]],"source":[[9,"1"]],
            "metrics":{"max_expression_chars":7}}
    def after(self,steps,status="EXACT_TARGET_PREFIX_NOT_PROOF"):
        return {**self.before,"steps":steps,"status":status,
            "pivot_path":[[i,139] for i in range(steps)]}
    def test_hash_and_baseline(self):
        self.assertEqual(START_SHA,
            "4eebc9694e460654e1224fa72e6d6385ae1689dedf3004bbf5934be27f3075c8")
        self.assertEqual((START_STEP,START_REMAINING,START_SUPPORT,START_MAX_CHARS),
            (60,85,164,7356))
        self.assertEqual(B_STEP59_SHA,
            "a5a341737487cc4a1f2e20323b1adc927ead02e043af44db4442857a7cfdc38a")
        self.assertIn("step59",STEP59_BACKUP.name)
    def test_zero_step_status_only(self):
        self.assertEqual(classify(self.before,self.after(60,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
            "MULTISTEP_NO_NEW_STEP_SAVED_NOT_PROOF")
    def test_zero_step_reserialization_requires_audit(self):
        changed=self.after(60,"EXACT_TARGET_CAP_REACHED_NOT_PROOF")
        changed["remaining"]=[[[100,139],"(z+1)**(-1)"]]
        changed["metrics"]={"max_expression_chars":11}
        self.assertEqual(classify(self.before,changed,16,0,False),
            "MULTISTEP_NO_NEW_STEP_RESERIALIZED_REQUIRES_EXACT_AUDIT")
    def test_zero_step_key_mutation_rejected(self):
        changed=self.after(60,"EXACT_TARGET_CAP_REACHED_NOT_PROOF")
        changed["remaining"]=[[[101,139],"1/(z+1)"]]
        with self.assertRaises(RuntimeError):
            classify(self.before,changed,16,0,False)
    def test_zero_step_unexpected_status_rejected(self):
        changed=self.after(60,"EXACT_TARGET_CAP_REACHED_NOT_PROOF")
        changed["status"]="EXACT_SINGLE_TARGET_PROVEN"
        with self.assertRaises(RuntimeError):
            classify(self.before,changed,16,0,False)
    def test_cap_stop_after_steps(self):
        self.assertEqual(classify(self.before,self.after(64,"EXACT_TARGET_CAP_REACHED_NOT_PROOF"),16,0,False),
            "MULTISTEP_PARTIAL_STEPS_SAVED_CAP_STOP_NOT_PROOF")
    def test_saved_steps(self):
        self.assertEqual(classify(self.before,self.after(76),16,0,False),
            "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF")
    def test_overshoot_rejected(self):
        with self.assertRaises(RuntimeError):
            classify(self.before,self.after(77),16,0,False)
    def test_mutated_prefix_rejected(self):
        after=self.after(61)
        after["pivot_path"][0]=[10000,139]
        with self.assertRaises(RuntimeError):
            classify(self.before,after,16,0,False)

if __name__=="__main__":
    unittest.main()
