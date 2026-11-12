"""Offline regression tests for guarded Step53 formal promotion."""
import unittest
from examples.three_loop_vp05_sector202_step53_promote import (
    validate_complete_replay, build_promoted,
)


class Step53PromotionTests(unittest.TestCase):
    def setUp(self):
        self.old = {
            "steps":52, "config":{"target":"A","max_columns":256,
                                  "max_support":400,"max_expression_chars":7500,
                                  "max_steps_total":128},
            "status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF",
            "exact_target_proven":False,
            "remaining":[[[10,139],"z"]],
            "source":[],
            "pivot_path":[[i,139] for i in range(52)],
        }
        self.rem = {(i,139):"1" for i in range(11,112)}
        self.trace = {i:"1" for i in range(188)}

    def test_promote_only_one_step(self):
        out = build_promoted(self.old,self.rem,self.trace,(10,139))
        self.assertEqual(out["steps"],53)
        self.assertEqual(len(out["remaining"]),101)
        self.assertEqual(len(out["source"]),188)
        self.assertEqual(len(out["pivot_path"]),53)
        self.assertFalse(out["exact_target_proven"])
        self.assertEqual(self.old["steps"],52)

    def test_reject_oversize(self):
        with self.assertRaises(RuntimeError):
            build_promoted(self.old,{**self.rem,(11,139):"z"*7501},
                           self.trace,(10,139))

    def test_replay_requires_all_columns(self):
        cfg={"column_count":369}
        good={"version":1,"config":cfg,
              "status":"STEP53_EXACT_IBP_REPLAY_PREFIX_NOT_TARGET_PROOF",
              "checked":369,"original_ibp_replay_verified":True,
              "exact_target_proven":False,
              "formal_target_state_modified":False,
              "protected_source_checkpoint_modified":False}
        validate_complete_replay(good,cfg,369)
        with self.assertRaises(RuntimeError):
            validate_complete_replay({**good,"checked":368},cfg,369)


if __name__ == "__main__":
    unittest.main()
