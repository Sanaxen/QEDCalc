import unittest
from examples.three_loop_vp05_sector202_target_b_step67_scratch import (
    validate_scratch,SCRATCH,TEMP,PROOF,START_STEP,NEXT_LEAD,protected_inputs,
)
class Step67ScratchTests(unittest.TestCase):
    def setUp(self):
        self.formal={"version":1,"config":{"target":"B"},
            "status":"EXACT_TARGET_PREFIX_NOT_PROOF","steps":66,
            "pivot_path":[[i,139] for i in range(66)],
            "remaining":[[[99,139],"1"]],"source":[[1,"1"]],
            "exact_target_proven":False,
            "original_source_replay_proven":False,
            "protected_source_checkpoint_modified":False,
            "metrics":{"remainder_terms":1,"original_support":1}}
    def test_exact_copy(self):
        self.assertTrue(validate_scratch(self.formal,dict(self.formal)))
    def test_step67_pivot_and_bounds(self):
        state=dict(self.formal)
        state.update({"steps":67,"pivot_path":self.formal["pivot_path"]+[NEXT_LEAD]})
        self.assertTrue(validate_scratch(self.formal,state))
        bad=dict(state);bad["pivot_path"]=self.formal["pivot_path"]+[[1,139]]
        with self.assertRaises(RuntimeError):validate_scratch(self.formal,bad)
    def test_zero_step_coefficients_protected(self):
        bad=dict(self.formal);bad["remaining"]=[[[99,139],"2"]]
        with self.assertRaises(RuntimeError):validate_scratch(self.formal,bad)
    def test_scratch_paths_distinct(self):
        self.assertEqual(len({SCRATCH.resolve(),TEMP.resolve(),PROOF.resolve()}),3)
if __name__=="__main__":
    unittest.main()
