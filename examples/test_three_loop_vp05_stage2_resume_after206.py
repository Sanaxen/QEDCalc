"""Safety-focused mocked tests: continue four next01 pilots but preserve 206."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from examples import three_loop_vp05_stage2_resume_after206 as m


def selected():
    return [{"sector": sector, "targets": [f"VP05_full[{sector}]"]}
            for sector in (205, 206, 79, 109, 234, 230)]


def states():
    return [
        {"sector": 205, "state": "completed_local_retained",
         "candidate_retained": True,
         "monitor_result": {"success": True, "kira_returncode": 0}},
        {"sector": 206, "state": "finished_needs_review",
         "candidate_retained": False,
         "monitor_result": {"success": False, "kira_returncode": -15,
                            "reason": "ram_stop"}},
        *[{"sector": s, "state": "prepared"} for s in (79, 109, 234, 230)],
    ]


class VP05ResumeAfter206Tests(unittest.TestCase):
    def test_verified_scope_gates_original_completed_and_stopped(self):
        with patch.object(m.base, "sector_input_scope", return_value=selected()), \
             patch.object(m.base, "status_one", side_effect=states()):
            targets, rows = m.verified_scope()
        self.assertEqual([i["sector"] for i in targets], [205, 206, 79, 109, 234, 230])
        self.assertEqual(rows[1]["monitor_result"]["reason"], "ram_stop")

    def test_deny_unverified_ram_stop(self):
        altered = states()
        altered[1]["monitor_result"] = {
            "success": False, "reason": "kira_exit", "kira_returncode": -15}
        with patch.object(m.base, "sector_input_scope", return_value=selected()), \
             patch.object(m.base, "status_one", side_effect=altered):
            with self.assertRaises(RuntimeError):
                m.verified_scope()

    def test_interrupted_job_audit_remains_readable_but_run_is_blocked(self):
        altered = states()
        altered[2]["state"] = "interrupted_manual_review"
        with patch.object(m.base, "sector_input_scope", return_value=selected()), \
             patch.object(m.base, "status_one", side_effect=altered):
            selected_rows, saved = m.verified_scope()
        self.assertEqual(saved[2]["state"], "interrupted_manual_review")
        with patch.object(m, "os", SimpleNamespace(name="nt")), \
             patch.object(m, "verified_scope", return_value=(selected_rows, saved)):
            with self.assertRaises(RuntimeError):
                m.execute(acknowledge=m.ACK)

    def test_deny_missing_original_sector205_pass(self):
        altered = states()
        altered[0]["candidate_retained"] = False
        with patch.object(m.base, "sector_input_scope", return_value=selected()), \
             patch.object(m.base, "status_one", side_effect=altered):
            with self.assertRaises(RuntimeError):
                m.verified_scope()

    def test_explicit_ack_and_windows_only(self):
        with self.assertRaises(ValueError):
            m.execute(acknowledge="unsafe")
        with patch.object(m, "os", SimpleNamespace(name="posix")):
            with self.assertRaises(RuntimeError):
                m.execute(acknowledge=m.ACK)

    def test_plan_is_read_only_and_keeps_promotion_false(self):
        with TemporaryDirectory() as td, patch.object(m.base, "OUTPUT", Path(td)), \
             patch.object(m, "verified_scope", return_value=(selected(), states())), \
             patch.object(m, "summarize_206", return_value={
                 "sector": 206, "stop_reason": "ram_stop"}), \
             patch.object(m.base, "read_resource_peaks", return_value={
                 "metrics_available": False}):
            report = m.plan()
            self.assertEqual(report["status"], "VP05_AFTER206_REMAINING_FOUR_READ_ONLY")
            self.assertTrue(report["skip_206_is_not_a_pass"])
            self.assertFalse(report["global_closure_proven"])
            self.assertEqual(len(report["remaining"]), 4)
            self.assertEqual(list(Path(td).iterdir()), [])

    def test_execute_uses_only_four_prepared_dirs_and_skips_206(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            for sec in m.REMAINING:
                (root / f"vp05_stage2_r8s5d3_continuation_next01_sec{sec}").mkdir()
            paths = []
            def run(args, **kwargs):
                paths.append(args[2])
                self.assertNotIn("sec206", args[2])
                self.assertEqual(args[0], "wsl.exe")
                self.assertIn("--ram-stop-gib", args)
                self.assertIn("--stop-gib", args)
                return SimpleNamespace(returncode=0)
            success = [{"state": "completed_local_retained",
                        "monitor_result": {"success": True}}
                       for _ in m.REMAINING]
            with patch.object(m, "os", SimpleNamespace(name="nt")), \
                 patch.object(m, "verified_scope", return_value=(selected(), states())), \
                 patch.object(m.base, "pilot_dir", side_effect=lambda runid, sector:
                     root / f"vp05_stage2_r8s5d3_continuation_next01_sec{sector}"), \
                 patch.object(m.base, "_no_other_kira"), \
                 patch.object(m.base, "status_one", side_effect=success), \
                 patch.object(m.subprocess, "run", side_effect=run), \
                 patch.object(m.base, "read_resource_peaks", return_value={
                     "metrics_available": True}):
                report = m.execute(acknowledge=m.ACK)
            self.assertEqual(report["status"], m.STATUS_ALL)
            self.assertEqual(len(paths), 4)
            self.assertTrue(report["sector206_still_unresolved"])
            self.assertFalse(report["global_63_master_closure_proven"])
            self.assertFalse(report["formal_promotion_ready_created"])

    def test_fail_closed_and_does_not_start_later_sectors(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "vp05_stage2_r8s5d3_continuation_next01_sec79").mkdir()
            with patch.object(m, "os", SimpleNamespace(name="nt")), \
                 patch.object(m, "verified_scope", return_value=(selected(), states())), \
                 patch.object(m.base, "pilot_dir", side_effect=lambda runid, sector:
                     root / f"vp05_stage2_r8s5d3_continuation_next01_sec{sector}"), \
                 patch.object(m.base, "_no_other_kira"), \
                 patch.object(m.base, "status_one", return_value={
                     "state": "finished_needs_review"}), \
                 patch.object(m.subprocess, "run", return_value=SimpleNamespace(
                     returncode=125)) as runner, \
                 patch.object(m.base, "read_resource_peaks", return_value={}):
                report = m.execute(acknowledge=m.ACK)
            self.assertEqual(report["status"], m.STATUS_HALTED)
            self.assertEqual(len(report["four_sector_run_records"]), 1)
            runner.assert_called_once()

    def test_reuse_completed_sector_does_not_run_it_again(self):
        prior = states()
        prior[2]["state"] = "completed_local_retained"
        with TemporaryDirectory() as td:
            root = Path(td)
            for sec in (109,234,230):
                (root / f"vp05_stage2_r8s5d3_continuation_next01_sec{sec}").mkdir()
            with patch.object(m, "os", SimpleNamespace(name="nt")), \
                 patch.object(m, "verified_scope", return_value=(selected(), prior)), \
                 patch.object(m.base, "pilot_dir", side_effect=lambda runid, sector:
                     root / f"vp05_stage2_r8s5d3_continuation_next01_sec{sector}"), \
                 patch.object(m.base, "_no_other_kira"), \
                 patch.object(m.base, "status_one", return_value={
                     "state": "completed_local_retained"}), \
                 patch.object(m.subprocess, "run", return_value=SimpleNamespace(
                     returncode=0)) as runner, \
                 patch.object(m.base, "read_resource_peaks", return_value={}):
                result = m.execute(acknowledge=m.ACK)
            self.assertEqual(result["four_sector_run_records"][0]["action"],
                             "reused_saved_local_pass")
            self.assertEqual(runner.call_count, 3)


if __name__ == "__main__":
    unittest.main()
