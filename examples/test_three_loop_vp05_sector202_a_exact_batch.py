"""Offline contract tests for Target A fresh exact checkpoint batch."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from examples import three_loop_vp05_sector202_a_exact_batch as m


def report():
    return {
        "status": "VP05_SECTOR202_A_EXACT_SOURCE_REVIEW_REQUIRED",
        "original_modular_support": {
            "target_a": {"row_count": 339, "source_row_ids": list(range(339))},
            "A_only_count": 0, "intersection_count": 339},
        "step93_exact_b": {
            "symbolic_QQ_z_d_original_ibp_replay_verified": True},
        "target_obligations": [{"proven": False}],
    }


def saved_state(processed):
    support = list(range(339))
    return {
        "version": 1, "status": "EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF",
        "total": 339, "processed": processed, "dependent": processed,
        "pivots": [], "source_pivots_exact_replay_verified": True,
        "exact_target_reduction_proven": False,
        "config": {
            "target": "A",
            "source_sha256": m.SOURCE_SHA,
            "certificate_sha256": m.CERT_SHA,
            "ids_sha256": hashlib.sha256(json.dumps(support).encode()).hexdigest(),
            **m.PARAMS},
    }


class ExactABatchTests(unittest.TestCase):
    def test_dedicated_destination_distinct_from_union(self):
        ckpt, logs = m.project("a339a")
        self.assertNotEqual(ckpt, m.exact.CHECKPOINT)
        self.assertTrue(ckpt.name.startswith("vp05_sector202_A_339_exact_"))
        self.assertIn("a339a", str(logs))

    def test_reject_path_traversal_run_id(self):
        for val in ("../bad", "", "a"*25, "a/b", "你好"):
            with self.assertRaises(ValueError):
                m.project(val)

    def test_preflight_rechecks_original_pin(self):
        with patch.object(m.split, "inspect", return_value=report()), patch.object(
            m, "sha", side_effect=[m.SOURCE_SHA, m.CERT_SHA]):
            scope = m.preflight()
        self.assertEqual(scope["A_original_support_rows"], 339)

    def test_reject_corrupted_source_digest(self):
        with patch.object(m.split, "inspect", return_value=report()), patch.object(
            m, "sha", side_effect=["0"*64, m.CERT_SHA]):
            with self.assertRaisesRegex(RuntimeError, "differs"):
                m.preflight()

    def test_new_checkpoint_does_not_create_file(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "fresh.json"
            got = m.checkpoint_state(p)
            self.assertEqual(got["state"], "not_started")
            self.assertFalse(p.exists())

    def test_checkpoint_rejects_changed_input_hash_or_promotion(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "state.json"
            state = saved_state(3)
            state["exact_target_reduction_proven"] = True
            p.write_text(json.dumps(state))
            with patch.object(m.split, "inspect", return_value=report()):
                with self.assertRaisesRegex(RuntimeError, "schema/hash/scope"):
                    m.checkpoint_state(p)

    def test_checkpoint_partial_is_not_exact_target_proof(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "state.json"
            state = saved_state(5)
            p.write_text(json.dumps(state))
            with patch.object(m.split, "inspect", return_value=report()):
                result = m.checkpoint_state(p)
            self.assertEqual(result["processed"], 5)
            self.assertEqual(result["state"], "partial_source_checkpoint")

    def test_checkpoint_full_is_still_not_target_proof(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "state.json"
            p.write_text(json.dumps(saved_state(339)))
            with patch.object(m.split, "inspect", return_value=report()):
                result = m.checkpoint_state(p)
            self.assertEqual(result["state"], "source_rows_complete_NOT_target_proof")

    def test_checkpoint_refuses_unresolved_temporary_file(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "state.json"
            p.with_name(p.name + ".tmp").write_text("unfinished")
            with self.assertRaisesRegex(RuntimeError, "temporary"):
                m.checkpoint_state(p)

    def test_command_forces_target_A_and_fresh_path(self):
        p, _ = m.project("test")
        args = m.command(p, resume=True, rows=5)
        self.assertEqual(args[args.index("--target")+1], "A")
        self.assertEqual(args[args.index("--checkpoint")+1], str(p))
        self.assertIn("--resume", args)
        self.assertIn("--checkpoint-every-row", args)
        self.assertEqual(args[args.index("--rows-per-run")+1], "5")

    def test_run_rolling_limits_are_bounded(self):
        self.assertEqual(m.MAX_ROWS, 20)
        self.assertEqual(m.MAX_TIMEOUT, 3600)
        with self.assertRaisesRegex(ValueError, "safety"):
            m.run("test", acknowledge=m.ACK, batches=1, rows=21, timeout=3600)
        with self.assertRaisesRegex(ValueError, "safety"):
            m.run("test", acknowledge=m.ACK, batches=1, rows=20, timeout=3601)

    def test_missing_ack_refuses_all_mutation(self):
        with self.assertRaisesRegex(ValueError, "acknowledgement"):
            m.run("test", acknowledge="", batches=1, rows=5, timeout=90)

    def test_reject_unbounded_batches(self):
        with self.assertRaisesRegex(ValueError, "safety"):
            m.run("test", acknowledge=m.ACK, batches=99, rows=5, timeout=90)

    def test_read_only_audit_does_not_change_project(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname)
            with patch.object(m, "project", return_value=(p/"state", p/"logs")), patch.object(
                m, "preflight", return_value={"A_original_support_rows": 339}), patch.object(
                m, "checkpoint_state", return_value={
                    "state": "not_started", "processed": 0, "total": 339,
                    "checkpoint_sha256": None}):
                result = m.audit("fixture")
            self.assertFalse(result["files_modified"])
            self.assertFalse(result["exact_target_A_proven"])
            self.assertEqual(list(p.iterdir()), [])

    def test_run_mocked_subprocess_batches_and_logs_are_separate(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname)
            ckpt, logs = p/"state.json", p/"logs"
            states = [
                {"state": "not_started", "processed": 0, "checkpoint_sha256": None},
                {"state": "partial_source_checkpoint", "processed": 5,
                 "checkpoint_sha256": "first"},
                {"state": "partial_source_checkpoint", "processed": 10,
                 "checkpoint_sha256": "second"},
            ]
            with patch.object(m, "project", return_value=(ckpt, logs)), patch.object(
                m, "preflight", return_value={}), patch.object(
                m, "checkpoint_state", side_effect=states), patch.object(
                m, "DIR", p), patch.object(
                m.os, "name", "nt"), patch.object(
                m.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as runner:
                result = m.run("fixture", acknowledge=m.ACK, batches=2, rows=5, timeout=30)
            self.assertEqual([x["to"] for x in result["batches"]], [5,10])
            self.assertFalse(result["exact_A_target_proven"])
            self.assertEqual(runner.call_count, 2)
            self.assertEqual(len(list(logs.glob("*.log"))), 2)


if __name__ == "__main__":
    unittest.main()
