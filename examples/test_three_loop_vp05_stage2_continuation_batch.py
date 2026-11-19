"""Mock-only tests: VP05 continuation six-sector guarded and resumable batch."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from examples import three_loop_vp05_stage2_continuation_batch as m
from scripts import vp05_stage2_monitored_kira as monitor

TARGETS = {
    205: ["VP05_full[1,0,1,1,0,0,1,1,0,0,0,0]"],
    206: ["VP05_full[0,1,1,1,0,0,1,1,0,0,0,0]"],
    79: ["VP05_full[1,1,1,1,0,0,1,0,0,0,0,0]", "VP05_full[2,1,1,1,0,0,1,0,0,0,0,0]"],
    109: ["VP05_full[1,0,1,1,0,1,1,0,0,0,0,0]", "VP05_full[2,0,1,1,0,1,1,0,0,0,0,0]"],
    234: ["VP05_full[0,1,0,1,0,1,1,1,0,0,0,0]", "VP05_full[0,2,0,1,0,1,1,1,0,0,0,0]"],
    230: ["VP05_full[0,1,1,0,0,1,1,1,0,0,0,0]", "VP05_full[0,2,1,0,0,1,1,1,0,0,0,0]", "VP05_full[0,3,1,0,0,1,1,1,0,0,0,0]"],
}


def selection():
    return [{"sector": i, "targets": ts,
             "effective_seed": f"r{min(8, i.bit_count() + 3)}s5d3"}
            for i, ts in TARGETS.items()]


def scope():
    return {
        "status": "VP05_STAGE2_TWO_SEED_SECTOR_EVIDENCE_INVENTORY_ONLY",
        "canonical_candidate_masters": 63, "canonical_candidate_sectors": 26,
        "step93_target_b_original_source_proof_verified": True,
        "unverified_standard_boundaries": ["r8s6d2", "r8s5d3"],
        "boundary_inventory": {
            "r8s5d3": {"sector_rows": [
                {"sector": i, "targets": ts, "candidate_count": len(ts),
                 "project_exists": False,
                 "restricted_exact_sector_audit_match": False,
                 "matching_local_master_inventory": False} for i, ts in TARGETS.items()
            ]}
        }
    }


def old_success():
    return {"sector_rows": [
        {"sector": i, "state": "completed_local_retained",
         "candidate_retained": True, "resources": {"peak_swap_used_gib": 0}}
        for i in (205, 206, 79, 109, 234, 230)
    ]}


class VP05ContinuationBatchTests(unittest.TestCase):
    def test_sector_scope_uses_actual_candidate_sets_and_effective_r(self):
        with patch.object(m.inventory, "inspect", return_value=scope()), \
             patch.object(m.first_pilot, "audit", return_value={
                 "status": "VP05_PILOT_SECTOR73_MASTER_RETAINED_PENDING_CROSS_SECTOR_REVIEW"}), \
             patch.object(m.previous_batch, "report_all", return_value=old_success()):
            values = m.sector_input_scope()
        self.assertEqual([x["sector"] for x in values], list(TARGETS))
        self.assertEqual([len(x["targets"]) for x in values], [1, 1, 2, 2, 2, 3])
        self.assertEqual([x["effective_seed"] for x in values],
                         ["r8s5d3"] * 6)

    def test_prior_batch_incomplete_refuses_new_selection(self):
        old = old_success()
        old["sector_rows"][1]["candidate_retained"] = False
        with patch.object(m.inventory, "inspect", return_value=scope()), \
             patch.object(m.first_pilot, "audit", return_value={
                 "status": "VP05_PILOT_SECTOR73_MASTER_RETAINED_PENDING_CROSS_SECTOR_REVIEW"}), \
             patch.object(m.previous_batch, "report_all", return_value=old):
            with self.assertRaises(RuntimeError):
                m.sector_input_scope()

    def test_resumable_paths_are_isolated_and_run_ids_checked(self):
        self.assertEqual(m.SECTORS, (205, 206, 79, 109, 234, 230))
        for bad in ("../bad", "space name", "", "X" * 33):
            with self.assertRaises(ValueError):
                m.pilot_dir(bad, 205)
        with self.assertRaises(ValueError):
            m.pilot_dir("valid", 203)

    def test_no_kira_plan_does_not_create_directory(self):
        with TemporaryDirectory() as td, patch.object(m, "OUTPUT", Path(td)), \
             patch.object(m, "sector_input_scope", return_value=selection()), \
             patch.object(m.previous_batch, "report_all", return_value=old_success()):
            report = m.report_all("next01")
            self.assertEqual(len(report["sector_rows"]), 6)
            self.assertTrue(all(x["state"] == "not_prepared" for x in report["sector_rows"]))
            self.assertEqual(list(Path(td).iterdir()), [])
            self.assertFalse(report["kira_executed"])

    def test_prepare_has_exclusive_paths_and_validates_hashes(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            output = root / "output"
            output.mkdir()
            shared_monitor = root / "scripts" / "vp05_stage2_monitored_kira.py"
            shared_monitor.parent.mkdir()
            shared_monitor.write_text("# guarded monitor\n")
            protected = output / "kira_vp05_full_masters_candidate_closure_r8s3d0_r8s6d2"
            protected.mkdir()
            (protected / "sentinel").write_text("keep")
            def fake_export(spec, dest, **kwargs):
                self.assertFalse(kwargs["clean"])
                self.assertEqual(kwargs["top_level_sectors"],
                                 [int(dest.name.rsplit("sec", 1)[1])])
                sector = kwargs["top_level_sectors"][0]
                self.assertEqual(kwargs["seed"].tag,
                                 f"r{min(8, sector.bit_count()+3)}s5d3")
                (dest / "config").mkdir()
                for filename in ("jobs.yaml", "config/integralfamilies.yaml",
                                 "config/kinematics.yaml",
                                 "qedcalc_master_basis_manifest.json"):
                    (dest / filename).write_text("mock\n")
            with patch.object(m, "OUTPUT", output), patch.object(m, "ROOT", root), \
                 patch.object(m, "sector_input_scope", return_value=selection()), \
                 patch.object(m, "build_family_spec", return_value=SimpleNamespace(
                     baseline_seed=m.Seed(8, 3, 0))), \
                 patch.object(m, "export_kira_project", side_effect=fake_export):
                report = m.prepare("next01")
                self.assertEqual(report["status"], "VP05_CONTINUATION_BATCH_PREPARE_PASS_NO_KIRA")
                self.assertEqual(len(report["projects"]), 6)
                self.assertEqual((protected / "sentinel").read_text(), "keep")
                self.assertTrue(all(m.status_one("next01", row)["state"] == "prepared"
                                    for row in selection()))
                with self.assertRaises(FileExistsError):
                    m.prepare("next01")
                (m.pilot_dir("next01", 205) / "jobs.yaml").write_text("tampered")
                with self.assertRaises(RuntimeError):
                    m.status_one("next01", selection()[0])

    def test_resume_does_not_claim_global_proof(self):
        with TemporaryDirectory() as td:
            output = Path(td)
            target = selection()[0]
            project = output / "vp05_stage2_r8s5d3_continuation_next01_sec205"
            project.mkdir()
            (project / "config").mkdir()
            for name in m.FILES:
                path = project / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(target["targets"][0] + "\n"
                                if name in (m.MANDATORY, m.PREFERRED) else "content\n")
            data = {"status": "VP05_CONTINUATION_PILOT_PREPARED",
                    "run_id": "next01", "sector": 201,
                    "requested_seed": "r8s5d3", "effective_seed": "r8s5d3",
                    "targets": target["targets"],
                    "input_sha256": {name: m.digest(project / name) for name in m.FILES}}
            (project / "continuation_pilot_manifest.json").write_text(json.dumps(data))
            (project / "monitored_exit.json").write_text(json.dumps({
                "success": True, "reason": "kira_exit", "kira_returncode": 0
            }))
            with patch.object(m, "OUTPUT", output), patch.object(
                m, "find_or_infer_masters", return_value=(
                    project / "results/VP05_full/masters", target["targets"], "initiate-only")):
                row = m.status_one("next01", target)
            self.assertEqual(row["state"], "completed_local_retained")
            self.assertFalse(row["global_closure_proven"])

    def test_guard_has_ram_and_swap_stop(self):
        kwargs = {"swap_stop": 8, "ram_stop": 22, "max_seconds": 5400}
        self.assertIsNone(monitor.resource_stop_reason(0, 5, 50, **kwargs))
        self.assertEqual(monitor.resource_stop_reason(9, 5, 50, **kwargs), "swap_stop")
        self.assertEqual(monitor.resource_stop_reason(0, 22.2, 50, **kwargs), "ram_stop")
        self.assertEqual(monitor.resource_stop_reason(0, 5, 5400, **kwargs), "time_stop")

    def test_explicit_acknowledgement_required(self):
        with self.assertRaises(ValueError):
            m.execute("next01", "wrong", 43200)
        with patch.object(m, "os", SimpleNamespace(name="posix")):
            with self.assertRaises(RuntimeError):
                m.execute("next01", m.ACK, 43200)

    def test_run_stops_at_first_failed_job(self):
        with TemporaryDirectory() as td:
            output = Path(td)
            sel = selection()
            (output / "vp05_stage2_r8s5d3_continuation_next01_sec205").mkdir()
            with patch.object(m, "OUTPUT", output), patch.object(m, "os", SimpleNamespace(name="nt")), \
                 patch.object(m, "sector_input_scope", return_value=sel), \
                 patch.object(m, "status_one", side_effect=[
                     *[{"state": "prepared"} for _ in sel], {"state": "finished_needs_review"}]), \
                 patch.object(m, "_no_other_kira"), \
                 patch.object(m.subprocess, "run", return_value=SimpleNamespace(returncode=125)) as runner, \
                 patch.object(m, "read_resource_peaks", return_value={"metrics_available": False}):
                result = m.execute("next01", m.ACK, 43200)
            self.assertEqual(result["status"], "VP05_CONTINUATION_BATCH_HALTED_REVIEW_REQUIRED")
            self.assertEqual(len(result["sectors"]), 1)
            runner.assert_called_once()
            self.assertFalse(result["global_closure_proven"])


if __name__ == "__main__":
    unittest.main()
