"""Mock-only, no-Kira safety tests for VP05 non-sector202 continuation."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from examples import three_loop_vp05_stage2_non202_batch as m


def target(sector: int, variation: int) -> str:
    indices = [int(bool(sector & (1 << i))) for i in range(12)]
    if variation:
        indices[9] = -variation
    return "VP05_full[" + ",".join(str(x) for x in indices) + "]"


def selected():
    return [{"sector": s,
             "targets": [target(s, j) for j in range(count)],
             "effective_seed": "r8s5d3"}
            for s, count in zip(m.SECTORS, m.EXPECTED_COUNTS)]


def old_states():
    return [
        {"sector": 205, "state": "completed_local_retained"},
        {"sector": 206, "state": "finished_needs_review",
         "monitor_result": {"reason": "ram_stop", "kira_returncode": -15,
                            "success": False, "last_sector": ["202", "9", "13"]}},
        {"sector": 79, "state": "completed_local_retained"},
        {"sector": 109, "state": "completed_local_retained"},
        {"sector": 234, "state": "finished_needs_review",
         "monitor_result": {"reason": "ram_stop", "kira_returncode": -15,
                            "success": False, "last_sector": ["202", "9", "10"]}},
        {"sector": 230, "state": "prepared"},
    ]


def canonical():
    return {
        "status": "VP05_STAGE2_TWO_SEED_SECTOR_EVIDENCE_INVENTORY_ONLY",
        "canonical_candidate_masters": 63,
        "canonical_candidate_sectors": 26,
        "step93_target_b_original_source_proof_verified": True,
        "boundary_inventory": {"r8s5d3": {"sector_rows": [
            {"sector": x["sector"], "candidate_count": len(x["targets"]),
             "targets": x["targets"], "project_exists": False,
             "restricted_exact_sector_audit_match": False,
             "matching_local_master_inventory": False}
            for x in selected()
        ]}}
    }


class Non202BatchTests(unittest.TestCase):
    def test_chosen_sector_groups_exclude_202(self):
        self.assertEqual(m.SECTORS, (230, 126, 127, 229, 231, 237))
        self.assertEqual(sum(m.EXPECTED_COUNTS), 23)
        self.assertTrue(all(s & 202 != 202 for s in m.SECTORS))
        self.assertTrue(all(min(8, s.bit_count() + 3) == 8 for s in m.SECTORS))

    def test_provenance_gate_validates_stopped206_and234(self):
        with patch.object(m.follow, "verified_scope", return_value=(
                [{"sector": 230, "targets": selected()[0]["targets"]}], old_states()
             )), patch.object(m.inventory, "inspect", return_value=canonical()):
            items, saved = m.verified_context()
        self.assertEqual(len(items), 6)
        self.assertEqual(saved[206]["monitor_result"]["reason"], "ram_stop")

    def test_changed_guard_stop_rejected(self):
        altered = old_states()
        altered[4]["monitor_result"]["reason"] = "kira_exit"
        with patch.object(m.follow, "verified_scope", return_value=(
                [{"sector": 230, "targets": selected()[0]["targets"]}], altered
             )), patch.object(m.inventory, "inspect", return_value=canonical()):
            with self.assertRaises(RuntimeError):
                m.verified_context()

    def test_projects_reuse_next01_for230_only(self):
        with TemporaryDirectory() as td, patch.object(m, "OUTPUT", Path(td)):
            self.assertTrue(str(m.project_for("a", 230)).endswith("next01_sec230"))
            self.assertTrue(str(m.project_for("a", 126)).endswith("a_sec126"))
            with self.assertRaises(ValueError):
                m.project_for("../bad", 229)
            with self.assertRaises(ValueError):
                m.project_for("good", 202)

    def test_guard_classification_is_not_mathematical_success(self):
        x = {"state": "finished_needs_review",
             "monitor_result": {"success": False,
                                "reason": "ram_stop", "kira_returncode": -15}}
        self.assertEqual(m.classify(x), "guard_stopped_ram_stop")
        x["monitor_result"]["kira_returncode"] = 0
        self.assertEqual(m.classify(x), "finished_needs_review")

    def test_plan_audit_never_writes_or_promotes(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            with patch.object(m, "OUTPUT", root), \
                 patch.object(m, "verified_context", return_value=(
                     selected(), {s["sector"]: s for s in old_states()})), \
                 patch.object(m, "status_one", side_effect=lambda runid, item:
                     {"sector": item["sector"], "state": "not_prepared",
                      "project": str(root / str(item["sector"]))}), \
                 patch.object(m.previous, "read_resource_peaks", return_value={}):
                report = m.audit("test01")
            self.assertFalse(report["global_63_master_closure_proven"])
            self.assertEqual(report["selected_candidate_integrals"], 23)
            self.assertEqual(report["verified_local_sectors"], 0)
            self.assertFalse(report["files_modified"])
            self.assertEqual(list(root.iterdir()), [])

    def test_prepare_exclusive_no_mutation_of_next01(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            output = root / "output"
            output.mkdir()
            original = output / "vp05_stage2_r8s5d3_continuation_next01_sec230"
            original.mkdir()
            (original / "do_not_touch.log").write_text("protected")
            monitor = root / "scripts" / "vp05_stage2_monitored_kira.py"
            monitor.parent.mkdir()
            monitor.write_text("# saved monitor")
            def fake_export(spec, dest, **kwargs):
                self.assertFalse(kwargs["clean"])
                self.assertEqual(kwargs["seed"].tag, "r8s5d3")
                self.assertEqual(kwargs["top_level_sectors"],
                                 [int(dest.name.rsplit("sec", 1)[1])])
                (dest / "config").mkdir()
                for name in ("jobs.yaml", "config/integralfamilies.yaml",
                             "config/kinematics.yaml",
                             "qedcalc_master_basis_manifest.json"):
                    (dest / name).write_text("mock")
            with patch.object(m, "ROOT", root), patch.object(m, "OUTPUT", output), \
                 patch.object(m, "verified_context", return_value=(selected(), {})), \
                 patch.object(m, "build_family_spec", return_value=SimpleNamespace(
                     baseline_seed=m.Seed(8, 3, 0))), \
                 patch.object(m, "export_kira_project", side_effect=fake_export):
                report = m.prepare("test01")
                self.assertEqual(report["status"], "VP05_NON202_PREPARE_PASS_NO_KIRA")
                self.assertEqual(len(report["projects_created"]), 5)
                self.assertEqual((original / "do_not_touch.log").read_text(), "protected")
                with self.assertRaises(FileExistsError):
                    m.prepare("test01")
                first = next(x for x in selected() if x["sector"] == 126)
                self.assertEqual(m.status_one("test01", first)["state"], "prepared")
                (m.project_for("test01", 126) / "jobs.yaml").write_text("tampered")
                with self.assertRaises(RuntimeError):
                    m.status_one("test01", first)

    def test_wsl_resource_preflight_parses_kib_and_rejects_pressure(self):
        healthy = ("MemTotal: 31457280\nMemAvailable: 20971520\n"
                   "SwapTotal: 251658240\nSwapFree: 251658240\n")
        with patch.object(m.subprocess, "run", return_value=SimpleNamespace(
            returncode=0, stdout=healthy, stderr="")):
            row = m.wsl_resource_preflight()
            self.assertAlmostEqual(row["ram_used_gib"], 10)
        low = healthy.replace("MemAvailable: 20971520", "MemAvailable: 4194304")
        with patch.object(m.subprocess, "run", return_value=SimpleNamespace(
            returncode=0, stdout=low, stderr="")):
            with self.assertRaises(RuntimeError):
                m.wsl_resource_preflight()

    def test_acknowledgement_and_windows_required(self):
        with self.assertRaises(ValueError):
            m.run("test01", "wrong", 43200)
        with patch.object(m, "os", SimpleNamespace(name="posix")):
            with self.assertRaises(RuntimeError):
                m.run("test01", m.ACK, 43200)

    def test_automatic_recovery_after_guard_stop_preserves_failed_job(self):
        with TemporaryDirectory() as td:
            base = Path(td)
            for sector in m.SECTORS:
                (base / f"sec{sector}").mkdir()
            count = {}
            def fake_status(runid, item):
                sector = item["sector"]
                count[sector] = count.get(sector, 0) + 1
                state = "prepared" if count[sector] == 1 else (
                    "guard_stopped_ram_stop" if sector == 230 else
                    "completed_local_retained")
                return {"sector": sector, "state": state,
                        "project": str(base / f"sec{sector}"),
                        "monitor_result": {"reason": "ram_stop", "success": False,
                                           "kira_returncode": -15} if sector == 230 else
                                          {"reason": "kira_exit", "success": True,
                                           "kira_returncode": 0}}
            exits = [125, 0, 0, 0, 0, 0]
            with patch.object(m, "os", SimpleNamespace(name="nt")), \
                 patch.object(m, "verified_context", return_value=(selected(), {})), \
                 patch.object(m, "status_one", side_effect=fake_status), \
                 patch.object(m, "project_for", side_effect=lambda runid, sector:
                     base / f"sec{sector}"), \
                 patch.object(m.previous, "_no_other_kira"), \
                 patch.object(m, "wsl_resource_preflight", return_value={}), \
                 patch.object(m.shutil, "disk_usage", return_value=SimpleNamespace(
                     free=20 * 1024**3)), \
                 patch.object(m.subprocess, "run", side_effect=lambda *args, **kw:
                     SimpleNamespace(returncode=exits.pop(0))) as runner, \
                 patch.object(m.previous, "read_resource_peaks", return_value={}):
                report = m.run("test01", m.ACK, 43200)
            self.assertEqual(report["status"], "VP05_NON202_PARTIAL_WITH_GUARD_STOPS")
            self.assertEqual(len(report["records"]), 6)
            self.assertEqual(runner.call_count, 6)
            self.assertTrue(all(
                call.args[0][call.args[0].index("--interval") + 1] == "5"
                for call in runner.call_args_list))
            self.assertTrue(report["sector206_234_remain_unresolved"])

    def test_previously_guard_stopped_jobs_never_relaunched(self):
        with patch.object(m, "os", SimpleNamespace(name="nt")), \
             patch.object(m, "verified_context", return_value=(selected(), {})), \
             patch.object(m, "status_one", side_effect=[
                 {"state": "guard_stopped_ram_stop", "sector": 230},
                 *[{"state": "completed_local_retained", "sector": x}
                   for x in m.SECTORS[1:]]]), \
             patch.object(m.subprocess, "run") as runner:
            report = m.run("test01", m.ACK, 43200)
        self.assertEqual(report["records"][0]["action"], "guard_stop_preserved_no_rerun")
        runner.assert_not_called()
        self.assertEqual(report["status"], "VP05_NON202_PARTIAL_WITH_GUARD_STOPS")


if __name__ == "__main__":
    unittest.main()
