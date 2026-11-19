"""Mocked, no-Kira safety tests for the VP05 r8s5d3 three-sector light batch."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from examples import three_loop_vp05_stage2_light_batch as m

ROWS = [
    {"sector": 78, "targets": ["VP05_full[0,1,1,1,0,0,1,0,0,0,0,0]"], "candidate_count": 1},
    {"sector": 101, "targets": ["VP05_full[1,0,1,0,-1,1,1,0,0,0,0,0]",
                                 "VP05_full[1,0,1,0,0,1,1,0,0,0,0,0]"], "candidate_count": 2},
    {"sector": 116, "targets": ["VP05_full[0,0,1,0,1,1,1,0,0,0,0,0]"], "candidate_count": 1},
]


def scope():
    return {
        "status": "VP05_STAGE2_TWO_SEED_SECTOR_EVIDENCE_INVENTORY_ONLY",
        "canonical_candidate_masters": 63, "canonical_candidate_sectors": 26,
        "step93_target_b_original_source_proof_verified": True,
        "unverified_standard_boundaries": ["r8s6d2", "r8s5d3"],
        "boundary_inventory": {"r8s5d3": {
            "sector_rows": [{**r, "project_exists": False,
                "restricted_exact_sector_audit_match": False,
                "matching_local_master_inventory": False} for r in ROWS]}},
    }


def selections():
    return [{"sector": r["sector"], "targets": r["targets"], "effective_seed": "r7s5d3"}
            for r in ROWS]


class Stage2LightBatchTests(unittest.TestCase):
    def test_exact_scoped_selection(self):
        with patch.object(m.inventory, "inspect", return_value=scope()), patch.object(
            m.first_pilot, "audit", return_value={
                "status": "VP05_PILOT_SECTOR73_MASTER_RETAINED_PENDING_CROSS_SECTOR_REVIEW"}):
            rows = m.sector_input_scope()
        self.assertEqual([r["sector"] for r in rows], [78, 101, 116])
        self.assertEqual([len(r["targets"]) for r in rows], [1, 2, 1])

    def test_scope_breaks_on_unverified_first_pilot(self):
        with patch.object(m.inventory, "inspect", return_value=scope()), patch.object(
            m.first_pilot, "audit", return_value={"status": "VP05_PILOT_NOT_COMPLETED"}):
            with self.assertRaises(RuntimeError):
                m.sector_input_scope()

    def test_invalid_run_id_rejected(self):
        for bad in ("", ".", "../x", "two words", "A" * 33):
            with self.assertRaises(ValueError):
                m.pilot_dir(bad, 78)
        with self.assertRaises(ValueError):
            m.pilot_dir("fine", 202)

    def test_status_does_not_create_project(self):
        with TemporaryDirectory() as td, patch.object(m, "OUTPUT", Path(td)):
            row = m.status_one("batch01", selections()[0])
            self.assertEqual(row["state"], "not_prepared")
            self.assertFalse(Path(row["project"]).exists())

    def test_prepare_exclusive_and_hashes(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            output = root / "output"
            output.mkdir()
            monitor = root / "scripts" / "sector203_monitored_kira.py"
            monitor.parent.mkdir()
            monitor.write_text("# copied monitor")
            original = output / "kira_vp05_full_masters_candidate_closure_r8s3d0_r8s6d2"
            original.mkdir()
            (original / "original.log").write_text("do-not-touch")

            def fake_export(spec, project, **kw):
                self.assertFalse(kw["clean"])
                self.assertEqual(kw["seed"].tag, "r7s5d3")
                self.assertEqual(kw["top_level_sectors"], [int(project.name.rsplit("sec", 1)[1])])
                (project / "config").mkdir()
                for rel in ("jobs.yaml", "config/integralfamilies.yaml",
                            "config/kinematics.yaml", "qedcalc_master_basis_manifest.json"):
                    (project / rel).write_text("test\n")
            with patch.object(m, "ROOT", root), patch.object(m, "OUTPUT", output), \
                 patch.object(m, "sector_input_scope", return_value=selections()), \
                 patch.object(m, "build_family_spec", return_value=SimpleNamespace(
                     baseline_seed=m.Seed(8, 3, 0))), patch.object(
                     m, "export_kira_project", side_effect=fake_export):
                result = m.prepare("batch_01")
                self.assertEqual(result["status"], "VP05_LIGHT_BATCH_PREPARE_PASS_NO_KIRA")
                self.assertEqual(len(result["projects"]), 3)
                self.assertEqual((original / "original.log").read_text(), "do-not-touch")
                self.assertTrue(all(m.status_one("batch_01", x)["state"] == "prepared"
                                    for x in selections()))
                with self.assertRaises(FileExistsError):
                    m.prepare("batch_01")
                (m.pilot_dir("batch_01", 78) / "jobs.yaml").write_text("altered")
                with self.assertRaises(RuntimeError):
                    m.status_one("batch_01", selections()[0])

    def test_resource_peaks_from_existing_monitor(self):
        with TemporaryDirectory() as td:
            project = Path(td)
            (project / "monitored_metrics.jsonl").write_text(
                '{"ram_used_gib": 5, "swap_used_gib": 0.1}\n'
                '{"ram_used_gib": 7.25, "swap_used_gib": 1.2}\n')
            result = m.read_resource_peaks(project)
            self.assertTrue(result["metrics_available"])
            self.assertEqual(result["peak_ram_used_gib"], 7.25)
            self.assertEqual(result["peak_swap_used_gib"], 1.2)

    def test_execution_requires_ack_and_windows(self):
        with self.assertRaises(ValueError):
            m.execute("batch", "wrong-token", 6000)
        with patch.object(m, "os", SimpleNamespace(name="posix")):
            with self.assertRaises(RuntimeError):
                m.execute("batch", m.ACK, 6000)

    def test_execute_stops_on_failed_first_job_without_touching_second(self):
        import subprocess
        with TemporaryDirectory() as td:
            out = Path(td)
            for r in selections():
                m.pilot_dir("safe", r["sector"]).name  # Validate mapping.
                (out / f"vp05_stage2_r8s5d3_light_safe_sec{r['sector']}").mkdir()
            rows = selections()
            first = [{"state": "prepared"} for _ in rows]
            outcome = {"state": "finished_needs_review"}
            with patch.object(m, "OUTPUT", out), patch.object(m, "os", SimpleNamespace(name="nt")), \
                 patch.object(m, "sector_input_scope", return_value=rows), \
                 patch.object(m, "status_one", side_effect=[*first, outcome]), \
                 patch.object(m, "_no_other_kira"), patch.object(
                     m.subprocess, "run", return_value=SimpleNamespace(returncode=125)) as runner, \
                 patch.object(m, "read_resource_peaks", return_value={"metrics_available": False}):
                result = m.execute("safe", m.ACK, 6000)
            self.assertEqual(result["status"], "VP05_LIGHT_BATCH_HALTED_REVIEW_REQUIRED")
            self.assertEqual(len(result["sectors"]), 1)
            self.assertEqual(result["sectors"][0]["sector"], 78)
            runner.assert_called_once()
            self.assertFalse(result["global_closure_proven"])


if __name__ == "__main__":
    unittest.main()
