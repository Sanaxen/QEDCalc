import unittest
from examples.three_loop_vp05_sector202_target_b_step68_scratch import (
    SCRATCH,TEMP,PROOF,validate_scratch,NEXT_LEAD,
)
class Step68ScratchTests(unittest.TestCase):
    def setUp(self):
        self.formal={"version":1,"config":{"target":"B"},
            "status":"EXACT_TARGET_PREFIX_NOT_PROOF","steps":67,
            "pivot_path":[[i,139] for i in range(67)],
            "remaining":[[[100,139],"1"]],"source":[[1,"1"]],
            "exact_target_proven":False,"original_source_replay_proven":False,
            "protected_source_checkpoint_modified":False,
            "metrics":{"remainder_terms":1,"original_support":1}}
    def test_exact_unchanged_zero_step(self):
        self.assertTrue(validate_scratch(self.formal,dict(self.formal)))
    def test_saved_step68_pivot(self):
        candidate=dict(self.formal)
        candidate["steps"]=68
        candidate["pivot_path"]=self.formal["pivot_path"]+[NEXT_LEAD]
        self.assertTrue(validate_scratch(self.formal,candidate))
        bad=dict(candidate)
        bad["pivot_path"]=self.formal["pivot_path"]+[[1,139]]
        with self.assertRaises(RuntimeError):validate_scratch(self.formal,bad)
    def test_detect_zero_step_mutation(self):
        bad=dict(self.formal);bad["remaining"]=[[[100,139],"2"]]
        with self.assertRaises(RuntimeError):validate_scratch(self.formal,bad)
    def test_scratch_paths_unique(self):
        self.assertEqual(len({SCRATCH.resolve(),TEMP.resolve(),PROOF.resolve()}),3)
if __name__=="__main__":
    unittest.main()
