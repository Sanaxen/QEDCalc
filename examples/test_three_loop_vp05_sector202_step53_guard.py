"""Offline synthetic tests for guarded Step53 continuation."""
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from examples.three_loop_vp05_sector202_step53_guard import interpret, validate_state


class Step53Tests(unittest.TestCase):
    def setUp(self):
        self.old = {"steps":52,"pivot_path":[[i,139] for i in range(52)],
                    "exact_target_proven":False}
        self.new = {"steps":53,"pivot_path":[[i,139] for i in range(53)],
                    "exact_target_proven":False}

    def test_real_reducer_schema_drops_extra_audit_flags(self):
        # The reducer persists only its canonical fields, not extension flags.
        state = {"steps": 52, "config": {"target": "A",
                 "max_expression_chars": 7500, "source_checkpoint_sha256": "h",
                 "source_sha256": "h", "certificate_sha256": "h"},
                 "status": "EXACT_TARGET_PREFIX_NOT_PROOF",
                 "exact_target_proven": False,
                 "remaining": [[[i + 100, 139], "1"] for i in range(103)],
                 "source": [[i, "1"] for i in range(187)],
                 "pivot_path": [[i, 139] for i in range(52)],
                 "metrics": {"max_expression_chars": 7312}}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "step52.json"
            path.write_text(json.dumps(state), encoding="utf-8")
            with patch("examples.three_loop_vp05_sector202_step53_guard.sha", return_value="h"):
                self.assertEqual(validate_state(path), state)

    def test_completed_step(self):
        self.assertEqual(interpret(0,self.old,self.new),
                         "STEP53_COMMITTED_CHECKPOINT_NOT_TARGET_PROOF")

    def test_unchanged_and_cap_stop(self):
        self.assertEqual(interpret(-1,self.old,self.old),
                         "STEP53_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")
        capped={**self.old,"status":"EXACT_TARGET_CAP_REACHED_NOT_PROOF"}
        self.assertEqual(interpret(0,self.old,capped),
                         "STEP53_NOT_COMMITTED_BOUNDED_OR_CAP_STOP_NOT_PROOF")

    def test_reject_error_or_inconsistent_checkpoint(self):
        with self.assertRaises(RuntimeError):
            interpret(1,self.old,self.new)
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"pivot_path":[]})
        with self.assertRaises(RuntimeError):
            interpret(0,self.old,{**self.new,"exact_target_proven":True})


if __name__ == "__main__":
    unittest.main()
