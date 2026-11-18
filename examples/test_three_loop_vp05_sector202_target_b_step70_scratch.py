import unittest
from examples.three_loop_vp05_sector202_target_b_step70_scratch import (
    START_STEP,EXPECTED_STEP69_SHA,formal_next_lead,validate_scratch,
    SCRATCH,TEMP,PROOF,B_STATE,STEP69_SCRATCH,STEP68_SCRATCH,
)
class Step70ScratchTests(unittest.TestCase):
    def setUp(self):
        self.old={"version":1,"config":{"target":"B"},"steps":69,
            "status":"EXACT_TARGET_PREFIX_NOT_PROOF",
            "pivot_path":[[i,139] for i in range(69)],
            "remaining":[[[500,139],"1"],[[510,139],"2"]],
            "source":[[10,"1"]],
            "exact_target_proven":False,"original_source_replay_proven":False,
            "protected_source_checkpoint_modified":False,
            "metrics":{"lead":[500,139],"remainder_terms":2,
                       "original_support":1}}
    def test_dynamic_lead_and_nonempty(self):
        self.assertEqual(formal_next_lead(self.old),[500,139])
        self.assertEqual(START_STEP,69)
        with self.assertRaises(RuntimeError):
            formal_next_lead({**self.old,"metrics":{"lead":[510,139]}})
    def test_saved_70_valid_and_wrong_pivot_fails(self):
        self.assertTrue(validate_scratch(self.old,self.old))
        new={**self.old,"steps":70,
             "pivot_path":self.old["pivot_path"]+[[500,139]],
             "remaining":[[[510,139],"2"]],
             "metrics":{"lead":[510,139],"remainder_terms":1,
                        "original_support":1}}
        self.assertTrue(validate_scratch(self.old,new))
        with self.assertRaises(RuntimeError):
            validate_scratch(self.old,{**new,"pivot_path":self.old["pivot_path"]+[[505,139]]})
    def test_historical_scratch_and_formal_paths_distinct(self):
        paths=[SCRATCH,TEMP,PROOF,B_STATE,STEP69_SCRATCH,STEP68_SCRATCH]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
        self.assertEqual(EXPECTED_STEP69_SHA,
            "97307fc660bc7a5b9cb17e4c6057025c1488d023a6e5b7f87341343de8c57b2d")
if __name__=="__main__":
    unittest.main()
