"""Synthetic non-destructive tests for formal Step51 promotion guards."""
import unittest
from examples.three_loop_vp05_sector202_step51_promote import (
    build_promoted, validate_replay,
)


class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.old = {
            "version": 1, "steps": 50, "status": "EXACT_TARGET_CAP_REACHED_NOT_PROOF",
            "config": {"target": "A", "max_columns": 256, "max_support": 400,
                       "max_expression_chars": 7500},
            "remaining": [[[1, 139], "z+1"]],
            "source": [],
            "pivot_path": [[i, 139] for i in range(-49, 1)],
            "exact_target_proven": False,
        }
        self.rem = {(i, 139): "1" for i in range(2, 102)}
        self.trace = {i: "1" for i in range(186)}

    def test_step51_checkpoint_shape(self):
        out = build_promoted(self.old, self.rem, self.trace, (1, 139))
        self.assertEqual(out["steps"], 51)
        self.assertEqual(out["metrics"]["remainder_terms"], 100)
        self.assertEqual(out["metrics"]["original_support"], 186)
        self.assertEqual(out["pivot_path"][-1], [1, 139])
        self.assertFalse(out["exact_target_proven"])
        self.assertEqual(self.old["steps"], 50)

    def test_refuse_oversized(self):
        with self.assertRaises(RuntimeError):
            build_promoted(self.old, {(2, 139): "z" * 7501}, self.trace, (1, 139))

    def test_replay_must_be_complete(self):
        cfg = {"example": 1}
        valid = {"version": 1, "config": cfg,
                 "status": "EXACT_IBP_REPLAY_PREFIX_NOT_TARGET_PROOF",
                 "checked": 364, "original_ibp_replay_verified": True,
                 "exact_target_proven": False,
                 "formal_target_state_modified": False,
                 "protected_source_checkpoint_modified": False}
        validate_replay(valid, cfg, 364)
        with self.assertRaises(RuntimeError):
            validate_replay({**valid, "checked": 363}, cfg, 364)
        with self.assertRaises(RuntimeError):
            validate_replay({**valid, "original_ibp_replay_verified": False}, cfg, 364)


if __name__ == "__main__":
    unittest.main()
