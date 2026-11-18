import unittest
from examples.three_loop_vp05_sector202_target_b_step69_scratch import (
    SCRATCH,TEMP,PROOF,NEXT_LEAD,START_STEP,validate_scratch,
    B_STATE,STEP68_SCRATCH,STEP67_SCRATCH,STEP66_SCRATCH,
    EXPECTED_STEP68_SHA,
)
class Step69ScratchTests(unittest.TestCase):
    def setUp(self):
        self.formal={"version":1,"config":{"target":"B"},
            "status":"EXACT_TARGET_PREFIX_NOT_PROOF","steps":68,
            "pivot_path":[[i,139] for i in range(68)],
            "remaining":[[[100,139],"1"]],"source":[[1,"1"]],
            "exact_target_proven":False,"original_source_replay_proven":False,
            "protected_source_checkpoint_modified":False,
            "metrics":{"remainder_terms":1,"original_support":1}}
    def test_unchanged_zero_step(self):
        self.assertTrue(validate_scratch(self.formal,dict(self.formal)))
    def test_exact_new_pivot(self):
        candidate=dict(self.formal);candidate["steps"]=69
        candidate["pivot_path"]=self.formal["pivot_path"]+[NEXT_LEAD]
        self.assertTrue(validate_scratch(self.formal,candidate))
        candidate["pivot_path"]=self.formal["pivot_path"]+[[1,139]]
        with self.assertRaises(RuntimeError):validate_scratch(self.formal,candidate)
    def test_mutated_zero_step_fails(self):
        mutated=dict(self.formal);mutated["remaining"]=[[[100,139],"2"]]
        with self.assertRaises(RuntimeError):validate_scratch(self.formal,mutated)
    def test_unique_and_formal_pin(self):
        self.assertEqual(START_STEP,68)
        self.assertEqual(EXPECTED_STEP68_SHA,"09368c634e482c40a8ae7dd9e7657c0d0667608f82f7d5b6537cc66067ac5ae8")
        paths=[SCRATCH,TEMP,PROOF,B_STATE,STEP68_SCRATCH,STEP67_SCRATCH,STEP66_SCRATCH]
        self.assertEqual(len(paths),len({p.resolve() for p in paths}))
if __name__=="__main__":
    unittest.main()
