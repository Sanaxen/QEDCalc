import unittest
from examples.three_loop_vp05_sector202_target_b_step72_scratch import (
    START_STEP, EXPECTED_STEP71_SHA, formal_next_lead, validate_scratch,
    SCRATCH, TEMP, PROOF, B_STATE, STEP71_SCRATCH, STEP70_SCRATCH,
)
class Step72ScratchTests(unittest.TestCase):
    def setUp(self):
        self.old={"version":1,"config":{"target":"B"},"steps":71,
          "status":"EXACT_TARGET_PREFIX_NOT_PROOF",
          "pivot_path":[[i,139] for i in range(71)],
          "remaining":[[[500,139],"1"],[[510,139],"2"]],
          "source":[[10,"1"]],
          "exact_target_proven":False,
          "original_source_replay_proven":False,
          "protected_source_checkpoint_modified":False,
          "metrics":{"lead":[500,139],"remainder_terms":2,"original_support":1}}
    def test_sha_and_dynamic_pivot(self):
        self.assertEqual(START_STEP,71)
        self.assertEqual(EXPECTED_STEP71_SHA,
            "80d9eee0c153ddbef718bbccfc8b1d0087277d6a13ca51df1986f838436966f8")
        self.assertEqual(formal_next_lead(self.old),[500,139])
        with self.assertRaises(RuntimeError):
            formal_next_lead({**self.old,"metrics":{"lead":[510,139]}})
    def test_successor_and_bad_pivot(self):
        self.assertTrue(validate_scratch(self.old,self.old))
        after={**self.old,"steps":72,
            "pivot_path":self.old["pivot_path"]+[[500,139]],
            "remaining":[[[510,139],"2"]],
            "metrics":{"lead":[510,139],"remainder_terms":1,"original_support":1}}
        self.assertTrue(validate_scratch(self.old,after))
        with self.assertRaises(RuntimeError):
            validate_scratch(self.old,{**after,
                "pivot_path":self.old["pivot_path"]+[[505,139]]})
    def test_protected_paths_distinct(self):
        paths=[SCRATCH,TEMP,PROOF,B_STATE,STEP71_SCRATCH,STEP70_SCRATCH]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
if __name__=="__main__":
    unittest.main()
