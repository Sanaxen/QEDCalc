"""Offline safety tests for the VP05 isolated sector202 r7s5d3 pilot."""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from unittest.mock import patch

from examples import three_loop_vp05_stage2_sector202_isolated as m


def valid_scope():
    return {"sector": 202, "targets": list(m.TARGETS),
            "requested_seed": "r8s5d3", "effective_seed": "r7s5d3"}


def evidence_report():
    return {"status": "VP05_SECTOR202_EVIDENCE_REUSED_FRONTIER_OPEN",
            "canonical_candidate_masters": 63,
            "sector202_all_three_targets_proven": False,
            "global_63_master_basis_proven": False,
            "sector202_local_effective_boundary": "r7s5d3",
            "remaining_sector_groups": [
                {"sector": s, "candidate_count": n, "targets": list(m.TARGETS)
                 if s == 202 else ["T%d_%d" % (s, k) for k in range(n)]}
                for s, n in m.evidence.EXPECTED_FRONTIER.items()]}


def inventory():
    return {"sector": 202, "candidate_count": 3,
            "targets": list(m.TARGETS), "matching_local_master_inventory": False,
            "restricted_exact_sector_audit_match": False,
            "project": "legacy-unmodified"}


class Sector202IsolatedSafetyTests(unittest.TestCase):
    def test_exact_three_targets_and_envelope(self):
        self.assertEqual(len(m.TARGETS), 3)
        self.assertEqual(m.EFFECTIVE.tag, "r7s5d3")
        self.assertEqual(m.SECTOR.bit_count(), 4)
        self.assertEqual(m.MAX_SECONDS, 5400)
        self.assertEqual((m.RAM_WARN, m.RAM_STOP, m.SWAP_WARN, m.SWAP_STOP),
                         (18, 22, 4, 8))

    def test_scope_uses_prior_proof_and_refuses_changed_standard(self):
        with patch.object(m.evidence, "inspect", return_value=evidence_report()), patch.object(
                m.inventory, "analyze_sector", return_value=inventory()):
            result = m.scope()
        self.assertEqual(result["targets"], list(m.TARGETS))
        self.assertFalse(result["step93_equivalence_to_this_new_kira_job_proven"])

    def test_scope_denies_unexpected_master_list_or_closure(self):
        old = inventory()
        old["matching_local_master_inventory"] = True
        with patch.object(m.evidence, "inspect", return_value=evidence_report()), patch.object(
                m.inventory, "analyze_sector", return_value=old):
            with self.assertRaisesRegex(RuntimeError, "Unexpected existing"):
                m.scope()

    def test_scope_denies_changed_candidate_group(self):
        bad = evidence_report()
        bad["remaining_sector_groups"][0]["candidate_count"] = 2
        with patch.object(m.evidence, "inspect", return_value=bad), patch.object(
                m.inventory, "analyze_sector", return_value=inventory()):
            with self.assertRaisesRegex(RuntimeError, "Canonical three"):
                m.scope()

    def test_missing_project_audit_does_not_create_anything(self):
        with TemporaryDirectory() as root:
            project = Path(root) / "missing"
            with patch.object(m, "scope", return_value=valid_scope()), patch.object(
                    m, "project_for", return_value=project):
                report = m.audit("sec202a")
            self.assertEqual(report["pilot"]["state"], "not_prepared")
            self.assertFalse(project.exists())
            self.assertFalse(report["r8s5d3_full_closure_proven"])
            self.assertFalse(report["files_modified"])

    def test_preparation_unique_and_verified_no_rewrites(self):
        with TemporaryDirectory() as root:
            root = Path(root)
            output = root / "output"
            output.mkdir()
            scripts = root / "scripts"
            scripts.mkdir()
            (scripts / m.MONITOR).write_text("# mock monitor\n", encoding="utf-8")
            target = output / "vp05_stage2_sector202_r7s5d3_sec202a"

            def mock_export(spec, directory, **kwargs):
                self.assertEqual(kwargs["seed"].tag, "r7s5d3")
                self.assertEqual(kwargs["top_level_sectors"], [202])
                self.assertEqual(kwargs["reduce_sectors"], [202])
                self.assertIs(kwargs["clean"], False)
                for item in m.FILES:
                    if item not in (m.MONITOR, m.MANDATORY, m.PREFERRED):
                        path = directory / item
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text("dummy config\n", encoding="utf-8")

            with patch.object(m, "ROOT", root), patch.object(
                    m, "OUTPUT", output), patch.object(m, "scope", return_value=valid_scope()), patch.object(
                    m, "build_family_spec", return_value=SimpleNamespace(
                        baseline_seed=m.Seed(8, 3, 0))), patch.object(
                    m, "export_kira_project", side_effect=mock_export):
                first = m.prepare("sec202a")
                self.assertEqual(first["status"], "VP05_SECTOR202_PREPARE_PASS_NO_KIRA")
                status = m.status("sec202a", valid_scope())
                self.assertEqual(status["state"], "prepared")
                before = {p.name: p.read_bytes() for p in target.rglob("*") if p.is_file()}
                again = m.prepare("sec202a")
                after = {p.name: p.read_bytes() for p in target.rglob("*") if p.is_file()}
                self.assertEqual(before, after)
                self.assertFalse(again["new_project_created"])
                # Deliberately corrupt a pinned input; fail closed without modifying it.
                (target / "jobs.yaml").write_text("tamper", encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "Pilot input changed"):
                    m.prepare("sec202a")

    def test_guard_stop_is_never_candidate_retention_or_rerun(self):
        with TemporaryDirectory() as root:
            directory = Path(root)
            for name in m.FILES:
                p = directory / name
                p.parent.mkdir(parents=True, exist_ok=True)
                if name in (m.MANDATORY, m.PREFERRED):
                    p.write_text("\n".join(m.TARGETS) + "\n", encoding="utf-8")
                else:
                    p.write_text("dummy", encoding="utf-8")
            import hashlib
            manifest = {"status": "VP05_SECTOR202_ISOLATED_PREPARED",
                        "run_id": "sec202a", "family": m.FAMILY,
                        "sector": m.SECTOR, "requested_seed": m.REQUESTED_SEED,
                        "effective_seed": m.EFFECTIVE.tag, "targets": list(m.TARGETS),
                        "input_sha256": {x: hashlib.sha256((directory/x).read_bytes()).hexdigest()
                                         for x in m.FILES}}
            (directory / m.MANIFEST).write_text(json.dumps(manifest), encoding="utf-8")
            (directory / "monitored_exit.json").write_text(json.dumps({
                "reason": "ram_stop", "success": False, "kira_returncode": -15}))
            with patch.object(m, "project_for", return_value=directory):
                state = m.status("sec202a", valid_scope())
                self.assertEqual(state["state"], "guard_stopped_ram_stop")
                self.assertFalse(state["candidate_retained"])
                with patch.object(m, "scope", return_value=valid_scope()), patch.object(
                        m, "os", SimpleNamespace(name="nt")):
                    with self.assertRaisesRegex(RuntimeError, "No automatic retry"):
                        m.execute("sec202a", m.ACK)

    def test_wrong_ack_blocks_all_kira_actions(self):
        with self.assertRaisesRegex(ValueError, "acknowledgement"):
            m.execute("sec202a", "something-else")

    def test_filename_rejects_traversal_and_invalid_run_ids(self):
        for key in ("../bad", "bad/run", "bad\\run", " ", "x"*33):
            with self.assertRaises(ValueError):
                m.project_for(key)

    def test_prepare_will_not_overwrite_existing_foreign_directory(self):
        with TemporaryDirectory() as root:
            directory = Path(root)
            (directory / "foreign.file").write_text("protected", encoding="utf-8")
            with patch.object(m, "scope", return_value=valid_scope()), patch.object(
                    m, "project_for", return_value=directory):
                with self.assertRaisesRegex(RuntimeError, "manifest"):
                    m.prepare("sec202a")
            self.assertEqual((directory / "foreign.file").read_text(), "protected")


if __name__ == "__main__":
    unittest.main()
