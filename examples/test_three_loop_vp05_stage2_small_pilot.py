"""No-Kira regression tests for the isolated VP05 r8s5d3 / sector73 pilot."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from examples import three_loop_vp05_stage2_small_pilot as m

TARGET = "VP05_full[1,0,0,1,0,0,1,0,0,0,0,0]"


def scope():
    return {
        "status": "VP05_STAGE2_TWO_SEED_SECTOR_EVIDENCE_INVENTORY_ONLY",
        "canonical_candidate_masters": 63,
        "canonical_candidate_sectors": 26,
        "step93_target_b_original_source_proof_verified": True,
        "unverified_standard_boundaries": ["r8s6d2", "r8s5d3"],
        "boundary_inventory": {
            "r8s5d3": {"sector_rows": [{
                "sector": 73, "candidate_count": 1, "targets": [TARGET],
                "project_exists": False, "restricted_exact_sector_audit_match": False,
                "matching_local_master_inventory": False,
            }]}
        },
    }


class PilotSafetyTests(unittest.TestCase):
    def test_run_id_validation_and_underscore(self):
        with TemporaryDirectory() as td, patch.object(m, "OUTPUT", Path(td)):
            self.assertTrue(str(m.pilot_dir("test_001")).endswith("test_001"))
            for bad in ("", "../bad", "a/b", "a\\b", "x" * 33, "a b"):
                with self.assertRaises(ValueError):
                    m.pilot_dir(bad)

    def test_parameter_scope_and_effective_seed(self):
        with patch.object(m.inventory, "inspect", return_value=scope()):
            result = m.parameters()
        self.assertEqual(result["target"], TARGET)
        self.assertEqual(result["effective_seed"].tag, "r6s5d3")

    def test_changed_scope_is_rejected(self):
        bad = scope()
        bad["step93_target_b_original_source_proof_verified"] = False
        with patch.object(m.inventory, "inspect", return_value=bad):
            with self.assertRaises(RuntimeError):
                m.parameters()

    def test_plan_does_not_create_directory(self):
        with TemporaryDirectory() as td, patch.object(m, "OUTPUT", Path(td)):
            with patch.object(m, "parameters", return_value={"target": TARGET,
                   "effective_seed": m.Seed(6, 5, 3), "requested_seed": "r8s5d3"}):
                data = m.plan("dry_run")
            self.assertTrue(data["destination_absent"])
            self.assertFalse(m.pilot_dir("dry_run").exists())
            self.assertFalse(data["kira_executed"])

    def test_prepare_exclusive_no_existing_project_mutated(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            output = root / "output"
            output.mkdir()
            monitor = root / "scripts" / "sector203_monitored_kira.py"
            monitor.parent.mkdir()
            monitor.write_text("# saved monitor\n")
            original = output / "kira_vp05_full_masters_candidate_closure_r8s3d0_r8s6d2"
            original.mkdir()
            sentinel = original / "original.log"
            sentinel.write_text("do not touch")
            def fake_export(spec, project, **kwargs):
                self.assertFalse(kwargs["clean"])
                self.assertEqual(kwargs["seed"].tag, "r6s5d3")
                self.assertEqual(kwargs["top_level_sectors"], [73])
                (project / "config").mkdir()
                for name in ("jobs.yaml", "config/integralfamilies.yaml",
                             "config/kinematics.yaml", "qedcalc_master_basis_manifest.json"):
                    (project / name).write_text("mock content\n", encoding="utf-8")
            with patch.object(m, "ROOT", root), patch.object(m, "OUTPUT", output), \
                 patch.object(m, "parameters", return_value={
                     "target": TARGET, "effective_seed": m.Seed(6, 5, 3), "requested_seed": "r8s5d3"}), \
                 patch.object(m, "build_family_spec", return_value=SimpleNamespace(
                     baseline_seed=m.Seed(8, 3, 0))), patch.object(
                     m, "export_kira_project", side_effect=fake_export):
                report = m.prepare("run_001")
                self.assertEqual(report["status"], "VP05_PILOT_PREPARE_PASS_NO_KIRA")
                self.assertEqual(m.check("run_001")["status"], "VP05_PILOT_EXECUTION_PREFLIGHT_PASS_NO_KIRA")
                self.assertEqual(sentinel.read_text(), "do not touch")
                with self.assertRaises(FileExistsError):
                    m.prepare("run_001")
                pilot = m.pilot_dir("run_001")
                (pilot / "monitored_kira.log").write_text("failed")
                with self.assertRaises(RuntimeError):
                    m.check("run_001")

    def test_audit_success_is_only_single_sector_candidate(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            output = root / "output"
            output.mkdir()
            project = output / "vp05_stage2_pilot_r8s5d3_sec73_result"
            project.mkdir()
            (project / "config").mkdir()
            for name in m.FILES:
                p = project / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(TARGET + "\n" if name in (m.MANDATORY, m.PREFERRED) else "payload\n")
            metadata = {
                "status": "VP05_ISOLATED_PILOT_PREPARED", "run_id": "result",
                "family": "VP05_full", "sector": 73, "target": TARGET,
                "requested_seed": "r8s5d3", "effective_seed": "r6s5d3",
                "input_sha256": {name: m.sha(project / name) for name in m.FILES},
            }
            (project / "isolated_pilot_manifest.json").write_text(json.dumps(metadata))
            (project / "monitored_exit.json").write_text(json.dumps({
                "success": True, "reason": "kira_exit", "kira_returncode": 0,
            }))
            with patch.object(m, "OUTPUT", output), patch.object(m, "find_or_infer_masters",
                return_value=(project / "results/VP05_full/masters", [TARGET], "initiate-only")):
                result = m.audit("result")
            self.assertTrue(result["candidate_retained_in_local_master_list"])
            self.assertFalse(result["full_stage2_closure_proven"])
            self.assertFalse(result["promotion_ready_generated"])

    def test_audit_missing_exit_is_not_success(self):
        with TemporaryDirectory() as td:
            project = Path(td) / "vp05_stage2_pilot_r8s5d3_sec73_missing"
            project.mkdir()
            with patch.object(m, "OUTPUT", Path(td)), \
                 patch.object(m, "stable_manifest", return_value={}):
                (project / "isolated_pilot_manifest.json").write_text("{}")
                self.assertEqual(m.audit("missing")["status"], "VP05_PILOT_NOT_COMPLETED")


if __name__ == "__main__":
    unittest.main()
