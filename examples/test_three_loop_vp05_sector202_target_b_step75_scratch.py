import unittest
from examples.three_loop_vp05_sector202_target_b_step75_scratch import (
    START_STEP, EXPECTED_STEP74_SHA, formal_next_lead, validate_scratch,
    SCRATCH, TEMP, PROOF, B_STATE, STEP74_SCRATCH, STEP73_SCRATCH,
)
class Step75ScratchTests(unittest.TestCase):
    def setUp(self):
        self.old={"version":1,"config":{"target":"B"},"steps":74,
            "status":"EXACT_TARGET_PREFIX_NOT_PROOF",
            "pivot_path":[[i,139] for i in range(74)],
            "remaining":[[[500,139],"1"],[[510,139],"2"]],
            "source":[[10,"1"]],
            "exact_target_proven":False,"original_source_replay_proven":False,
            "protected_source_checkpoint_modified":False,
            "metrics":{"lead":[500,139],"remainder_terms":2,"original_support":1}}
    def test_sha_and_next_pivot(self):
        self.assertEqual(START_STEP,74)
        self.assertEqual(EXPECTED_STEP74_SHA,
            "ec7bf87037fc34bd73e730894bfe09a8e43287628a07ec7c861e6f777b36b694")
        self.assertEqual(formal_next_lead(self.old),[500,139])
        with self.assertRaises(RuntimeError):
            formal_next_lead({**self.old,"metrics":{"lead":[510,139]}})
    def test_single_step_and_wrong_pivot(self):
        self.assertTrue(validate_scratch(self.old,self.old))
        new={**self.old,"steps":75,
            "pivot_path":self.old["pivot_path"]+[[500,139]],
            "remaining":[[[510,139],"2"]],
            "metrics":{"lead":[510,139],"remainder_terms":1,"original_support":1}}
        self.assertTrue(validate_scratch(self.old,new))
        with self.assertRaises(RuntimeError):
            validate_scratch(self.old,{**new,
                "pivot_path":self.old["pivot_path"]+[[505,139]]})
    def test_paths_distinct(self):
        paths=[SCRATCH,TEMP,PROOF,B_STATE,STEP74_SCRATCH,STEP73_SCRATCH]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
if __name__=="__main__":
    unittest.main()
