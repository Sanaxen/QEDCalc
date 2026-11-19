"""Offline tests for read-only VP05 sector202 RAM-stop forensics."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from examples import three_loop_vp05_stage2_sector202_stop_forensics as m


def monitor_state(reason="ram_stop"):
    return {"state": "guard_stopped_ram_stop",
            "monitor_result": {"reason": reason, "success": False,
                               "kira_returncode": -15, "elapsed_s": 125.0}}


def profile():
    return {"project_exists": True,
            "mandatory_input_set_matches_expected": True,
            "preferred_input_set_matches_expected": True,
            "log_files": [{"file": "monitored_kira.log",
                           "last_sector_progress": {"sector": 202, "index": 5, "of": 5},
                           "last_lines": ["Generate equations for topology VP05_full, sector 202 (5 of 5)"]}],
            "log_files_truncated": False,
            "metadata": {"kira_db": {"exists": True}, "system_equations": {"count": 0},
                         "masters": {"exists": False}, "masters_final": {"exists": False},
                         "results_dir_present": True, "tmp_dir_present": True,
                         "sectormappings_dir_present": False}}


def trace():
    return {"samples": 3, "first": {"elapsed_s": 0.0},
            "last": {"elapsed_s": 120.0},
            "max_ram_gib": 22.04, "max_swap_gib": 0.0, "time_buckets": []}


class Sector202StopForensicsTests(unittest.TestCase):
    def test_metrics_resource_trace_is_bounded_and_reports_thresholds(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "monitored_metrics.jsonl"
            records = [
                {"elapsed_s": 0, "ram_used_gib": 1.2, "swap_used_gib": 0, "last_sector": None},
                {"elapsed_s": 60, "ram_used_gib": 18.2, "swap_used_gib": 0,
                 "last_sector": ["202", "3", "5"]},
                {"elapsed_s": 90, "ram_used_gib": 20.2, "swap_used_gib": 0},
                {"elapsed_s": 120, "ram_used_gib": 22.04, "swap_used_gib": 0,
                 "last_sector": ["202", "5", "5"]},
            ]
            p.write_text("\n".join(map(json.dumps, records)) + "\n", encoding="utf-8")
            before = p.read_bytes()
            summary = m.metrics(p)
            self.assertEqual(summary["samples"], 4)
            self.assertEqual(summary["max_ram_gib"], 22.04)
            self.assertEqual(summary["first_warning"], {
                "18_gib": 60.0, "20_gib": 90.0, "22_gib": 120.0})
            self.assertEqual(summary["time_buckets"][-1]["minute"], 2)
            self.assertEqual(p.read_bytes(), before)

    def test_metrics_rejects_backwards_time(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "metrics"
            p.write_text("\n".join([
                json.dumps({"elapsed_s": 5, "ram_used_gib": 1, "swap_used_gib": 0}),
                json.dumps({"elapsed_s": 4, "ram_used_gib": 2, "swap_used_gib": 0})]))
            with self.assertRaisesRegex(RuntimeError, "Non-monotonic"):
                m.metrics(p)

    def test_metrics_refuses_non_numeric_or_negative_memory(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "metrics"
            p.write_text(json.dumps({"elapsed_s": 2, "ram_used_gib": -3,
                                      "swap_used_gib": 0}))
            with self.assertRaisesRegex(RuntimeError, "Non-monotonic"):
                m.metrics(p)
            p.write_text(json.dumps({"elapsed_s": 2, "ram_used_gib": "unknown",
                                      "swap_used_gib": 0}))
            with self.assertRaisesRegex(RuntimeError, "Missing or malformed"):
                m.metrics(p)

    def test_metrics_refuses_linked_input(self):
        with tempfile.TemporaryDirectory() as dirname:
            root = Path(dirname)
            p = root / "real"
            p.write_text("{}")
            link = root / "linked"
            try:
                link.symlink_to(p)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink unavailable")
            with self.assertRaisesRegex(RuntimeError, "non-linked"):
                m.metrics(link)

    def test_metrics_cap_does_not_read_large_file(self):
        with tempfile.TemporaryDirectory() as dirname:
            p = Path(dirname) / "large"
            with p.open("wb") as f:
                f.truncate(m.MAX_METRIC_BYTES + 1)
            with self.assertRaisesRegex(RuntimeError, "bounded read cap"):
                m.metrics(p)

    def test_metrics_missing_is_not_fake_success(self):
        with tempfile.TemporaryDirectory() as dirname:
            with self.assertRaisesRegex(RuntimeError, "Expected non-linked"):
                m.metrics(Path(dirname) / "does_not_exist")

    def test_inspect_preserves_original_and_no_closure_claim(self):
        with tempfile.TemporaryDirectory() as dirname:
            directory = Path(dirname)
            with patch.object(m.isolated, "scope", return_value={"targets": ["A", "B", "C"]}), patch.object(
                m.isolated, "status", return_value=monitor_state()), patch.object(
                m.isolated, "project_for", return_value=directory), patch.object(
                m.forensic, "project_profile", return_value=profile()), patch.object(
                m, "metrics", return_value=trace()):
                report = m.inspect("sec202a")
            self.assertEqual(report["status"], "VP05_SECTOR202_RAM_STOP_FORENSICS_READ_ONLY")
            self.assertEqual(report["last_log_sector_progress"]["index"], 5)
            self.assertFalse(report["conclusions"]["sector202_local_master_retention_proven"])
            self.assertFalse(report["conclusions"]["kira_mathematical_failure_demonstrated"])
            self.assertFalse(report["kira_executed"])
            self.assertFalse(report["files_modified"])
            self.assertEqual(list(directory.iterdir()), [])

    def test_inspect_denies_success_label_instead_of_expected_ram_stop(self):
        altered = monitor_state()
        altered["state"] = "completed_local_retained"
        with patch.object(m.isolated, "scope", return_value={"targets": ["A", "B", "C"]}), patch.object(
                m.isolated, "status", return_value=altered):
            with self.assertRaisesRegex(RuntimeError, "Expected preserved"):
                m.inspect()

    def test_inspect_denies_modified_original_target_inputs(self):
        data = profile()
        data["mandatory_input_set_matches_expected"] = False
        with tempfile.TemporaryDirectory() as dirname:
            with patch.object(m.isolated, "scope", return_value={"targets": ["A", "B", "C"]}), patch.object(
                m.isolated, "status", return_value=monitor_state()), patch.object(
                m.isolated, "project_for", return_value=Path(dirname)), patch.object(
                m.forensic, "project_profile", return_value=data):
                with self.assertRaisesRegex(RuntimeError, "inputs mismatch"):
                    m.inspect()

    def test_inspect_denies_resource_trace_inconsistent_with_stop(self):
        weak = trace()
        weak["max_ram_gib"] = 12
        with tempfile.TemporaryDirectory() as dirname:
            with patch.object(m.isolated, "scope", return_value={"targets": ["A", "B", "C"]}), patch.object(
                m.isolated, "status", return_value=monitor_state()), patch.object(
                m.isolated, "project_for", return_value=Path(dirname)), patch.object(
                m.forensic, "project_profile", return_value=profile()), patch.object(
                m, "metrics", return_value=weak):
                with self.assertRaisesRegex(RuntimeError, "never reached"):
                    m.inspect()

    def test_inspect_denies_elapsed_disagreement(self):
        altered = trace()
        altered["last"] = {"elapsed_s": 30}
        with tempfile.TemporaryDirectory() as dirname:
            with patch.object(m.isolated, "scope", return_value={"targets": ["A", "B", "C"]}), patch.object(
                m.isolated, "status", return_value=monitor_state()), patch.object(
                m.isolated, "project_for", return_value=Path(dirname)), patch.object(
                m.forensic, "project_profile", return_value=profile()), patch.object(
                m, "metrics", return_value=altered):
                with self.assertRaisesRegex(RuntimeError, "elapsed timing mismatch"):
                    m.inspect()


if __name__ == "__main__":
    unittest.main()
