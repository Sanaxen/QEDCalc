"""Offline, read-only regression tests for sector202 evidence reuse."""
from __future__ import annotations

import hashlib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from examples import three_loop_vp05_sector202_reuse_audit as m
from examples import three_loop_vp05_stage2_step93_gap_audit as gap


NON202 = {
    73: 1, 78: 1, 79: 2, 101: 2, 109: 2, 116: 1, 117: 1,
    118: 1, 126: 2, 127: 2, 199: 1, 201: 1, 204: 1,
    205: 1, 228: 2, 229: 6, 230: 3, 231: 5, 237: 5,
}


def row_for(sector, count):
    result = []
    for i in range(count):
        powers = [1 if sector & (1 << bit) else 0 for bit in range(12)]
        missing = next(bit for bit in range(12) if not sector & (1 << bit))
        powers[missing] = -i - 1
        result.append("VP05_full[" + ",".join(str(v) for v in powers) + "]")
    return result


def fixture():
    groups = {sector: row_for(sector, count) for sector, count in NON202.items()}
    groups.update({sector: row_for(sector, count)
                   for sector, count in m.EXPECTED_FRONTIER.items()})
    groups[202] = ["VP05_full[" + ",".join(map(str, row)) + "]"
                   for row in gap.TARGETS]
    values = [x for sector in sorted(groups) for x in groups[sector]]
    assert len(values) == 63 and len(set(values)) == 63
    manifest = {"family": "VP05_full", "candidate_master_count": 63,
                "candidate_masters": values}
    archive = {
        "status": "FORMAL_STEP93_SECTOR202_TARGET_B_INDEPENDENT_EXACT_PROOF",
        "target_b_proven_within_pinned_source": True,
        "entire_vp05_family_proven": False,
    }
    passed = {
        "status": "VP05_NON202_SAVED_AUDIT_READ_ONLY", "run_id": "no202a",
        "verified_local_sectors": 6, "selected_candidate_integrals": 23,
        "guard_stopped_sectors": [],
        "sector_rows": [{"state": "completed_local_retained",
                         "candidate_retained": True} for _ in range(6)],
    }
    source = {"sha256_pinned_original_inputs": {
        key: {"matches_formal_archive": True}
        for key in ("original_source_rows.json.gz",
                    "original_exact_support_checkpoint.json",
                    "original_source_provenance_certificate.json")}}
    parents = [{"sector": sec, "state": "ram_guard_stopped_not_master_proof",
                "candidate_master_retention_verified": False} for sec in m.BLOCKED]
    seed202 = {"sector": 202, "candidate_count": 3, "targets": groups[202],
               "project_exists": True, "matching_local_master_inventory": False,
               "restricted_exact_sector_audit_match": False,
               "classification": "existing_project_requires_forensics"}
    return manifest, archive, passed, source, parents, seed202


class Sector202ReadOnlyTests(unittest.TestCase):
    def test_frontier_exact_23_and_step93_only_target_b(self):
        report = m.reconcile(*fixture())
        self.assertEqual(report["status"], "VP05_SECTOR202_EVIDENCE_REUSED_FRONTIER_OPEN")
        self.assertEqual([r["sector"] for r in report["remaining_sector_groups"]],
                         sorted(m.EXPECTED_FRONTIER))
        self.assertEqual(sum(r["candidate_count"] for r in report["remaining_sector_groups"]), 23)
        self.assertEqual(report["local_master_retention_previously_verified"]["candidate_masters"], 40)
        target = report["sector202_exact_target_obligations"]
        self.assertEqual([x["target"] for x in target], ["A", "B", "C"])
        self.assertEqual([x["step93_pinned_source_exact_identity_proven"] for x in target],
                         [False, True, False])
        self.assertEqual(report["sector202_local_effective_boundary"], "r7s5d3")
        for key in ("sector202_all_three_targets_proven",
                    "parent_sector206_234_closure_proven",
                    "r8s5d3_standard_seed_closure_proven",
                    "r8s6d2_standard_seed_closure_proven",
                    "global_63_master_basis_proven", "promotion_ready_created",
                    "kira_executed", "files_modified"):
            self.assertFalse(report[key])

    def test_changed_canonical_sector202_target_fails_closed(self):
        values = list(fixture())
        manifest = dict(values[0])
        candidates = list(manifest["candidate_masters"])
        candidates.remove("VP05_full[" + ",".join(map(str, gap.TARGETS[0])) + "]")
        candidates.append(row_for(202, 12)[-1])
        manifest["candidate_masters"] = candidates
        values[0] = manifest
        with self.assertRaisesRegex(RuntimeError, "sector202 targets"):
            m.reconcile(*values)

    def test_missing_one_non202_success_fails_closed(self):
        values = list(fixture())
        report = dict(values[2])
        rows = list(report["sector_rows"])
        rows[0] = {"state": "guard_stopped_ram_stop", "candidate_retained": False}
        report["sector_rows"] = rows
        values[2] = report
        with self.assertRaisesRegex(RuntimeError, "passes"):
            m.reconcile(*values)

    def test_guard_stop_cannot_be_reinterpreted_as_proof(self):
        values = list(fixture())
        rows = [dict(x) for x in values[4]]
        rows[0]["candidate_master_retention_verified"] = True
        values[4] = rows
        with self.assertRaisesRegex(RuntimeError, "Stopped parent"):
            m.reconcile(*values)

    def test_incomplete_original_source_hashes_fail_closed(self):
        values = list(fixture())
        values[3] = {"sha256_pinned_original_inputs": {
            "original_source_rows.json.gz": {"matches_formal_archive": True}}}
        with self.assertRaisesRegex(RuntimeError, "Source integrity"):
            m.reconcile(*values)

    def test_safe_sha256_rejects_symlinks_and_detects_changed_bytes(self):
        with TemporaryDirectory() as name:
            root = Path(name)
            source = root / "source.json"
            source.write_bytes(b"original")
            self.assertEqual(m.sha256_regular(source),
                             hashlib.sha256(b"original").hexdigest())
            linked = root / "linked.json"
            try:
                linked.symlink_to(source)
            except (OSError, NotImplementedError):
                return  # Windows without symlink permission
            with self.assertRaisesRegex(RuntimeError, "non-regular"):
                m.sha256_regular(linked)

    def test_exact_source_three_hashes_read_only(self):
        with TemporaryDirectory() as name:
            root = Path(name)
            paths = [root / x for x in ("source.gz", "checkpoint.json", "cert.json")]
            for i, p in enumerate(paths):
                p.write_bytes(("unchanged-%d" % i).encode("ascii"))
            expected = {
                key: hashlib.sha256(p.read_bytes()).hexdigest()
                for key, p in zip(("original_source_rows.json.gz",
                                   "original_exact_support_checkpoint.json",
                                   "original_source_provenance_certificate.json"), paths)}
            with patch.object(m.exact, "SOURCE", paths[0]), patch.object(
                    m.exact, "CHECKPOINT", paths[1]), patch.object(
                    m.exact, "CERT", paths[2]):
                report = m.source_audit({"source_and_evidence_sha256": expected})
                self.assertEqual(len(report["sha256_pinned_original_inputs"]), 3)
                self.assertTrue(all(r["matches_formal_archive"] for r in
                                    report["sha256_pinned_original_inputs"].values()))
                paths[0].write_bytes(b"tampered")
                with self.assertRaisesRegex(RuntimeError, "bytes changed"):
                    m.source_audit({"source_and_evidence_sha256": expected})
            self.assertEqual(paths[1].read_bytes(), b"unchanged-1")

    def test_parent_guard_record_and_project_inspection_are_read_only(self):
        targets = row_for(206, 1)
        with TemporaryDirectory() as name:
            root = Path(name)
            with patch.object(m.continuation, "pilot_dir", return_value=root), patch.object(
                m.continuation, "status_one", return_value={
                    "state": "finished_needs_review",
                    "monitor_result": {"reason": "ram_stop",
                                       "kira_returncode": -15, "success": False}
            }), patch.object(m.forensic, "project_profile", return_value={
                "mandatory_input_set_matches_expected": True,
                "preferred_input_set_matches_expected": True,
                "log_files": [{"last_sector_progress": {
                    "sector": 202, "index": 9, "of": 13}}],
                "metadata": {"system_equations": {"count": 3},
                             "masters": {"exists": False},
                             "masters_final": {"exists": False}},
            }), patch.object(m.continuation, "read_resource_peaks",
                             return_value={"peak_ram_used_gib": 22.11}):
                report = m.inspect_blocked(206, targets)
            self.assertEqual(report["last_logged_recursive_sector"]["sector"], 202)
            self.assertFalse(report["candidate_master_retention_verified"])
            self.assertEqual(list(root.iterdir()), [])

    def test_parent_guard_missing_is_not_a_success(self):
        with patch.object(m.continuation, "status_one", return_value={
            "state": "completed_local_retained", "monitor_result": {"success": True}}):
            with self.assertRaisesRegex(RuntimeError, "guard-stop"):
                m.inspect_blocked(234, row_for(234, 2))

    def test_inspect_glues_readers_without_generating_output(self):
        values = fixture()
        archive_path = m.gap.ARCHIVE / "formal_manifest.json"
        with patch.object(m.no202, "audit", return_value=values[2]) as checker, patch.object(
            m.gap, "read", side_effect=[values[0], values[1]]
        ), patch.object(m, "sha256_regular",
                        return_value=m.gap.EXPECTED_MANIFEST_SHA256
        ), patch.object(m, "source_audit", return_value=values[3]), patch.object(
            m, "inspect_blocked", side_effect=values[4]
        ), patch(
            "examples.three_loop_vp05_stage2_sector_inventory.analyze_sector",
            return_value=values[5]
        ):
            result = m.inspect()
        checker.assert_called_once_with("no202a")
        self.assertEqual(result["status"], "VP05_SECTOR202_EVIDENCE_REUSED_FRONTIER_OPEN")
        self.assertFalse(result["files_modified"])


if __name__ == "__main__":
    unittest.main()
