"""Offline tests for VP05 sector202 finite-field versus exact-source scope audit."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from examples import three_loop_vp05_sector202_source_split_audit as m


def fixture():
    a = list(range(339))
    b = list(range(39, 389))
    cert = {
        "status": "MODULAR_ORIGINAL_ROW_CERTIFICATE_VERIFIED_NOT_EXACT_PROOF",
        "total_original_rows": 2678, "point": [1000003, 17, 7],
        "exact_target_reduction_proven": False,
        "union_nonzero_support": 389, "shared_nonzero_support": 300,
        "target_results": [
            {"target_index": 0, "target": list(m.gap.TARGETS[0]),
             "nonzero_original_support": 339,
             "support_original_ids": a,
             "modular_original_replay_verified": True},
            {"target_index": 1, "target": list(m.gap.TARGETS[1]),
             "nonzero_original_support": 350,
             "support_original_ids": b,
             "modular_original_replay_verified": True},
        ],
    }
    proof = {"status": "EXACT_SINGLE_TARGET_PROVEN",
             "target": "B", "original_source_replay_verified": True,
             "source_multipliers": [[i, "1"] for i in range(389)]}
    forensic = {
        "status": "VP05_SECTOR202_RAM_STOP_FORENSICS_READ_ONLY",
        "run_id": "sec202a", "project": "original-sec202a",
        "saved_elapsed_s": 1222.3,
        "resource_trace": {"max_ram_gib": 22.04},
        "last_log_sector_progress": {"sector": 202, "index": 5, "of": 5},
        "saved_project": {"masters_final": {"exists": False}},
        "conclusions": {"ram_guard_stop_verified": True, "no_automatic_retry": True},
    }
    return cert, proof, forensic


class VP05SourceSplitTests(unittest.TestCase):
    def test_a_is_modular_only_b_exact_c_reference(self):
        result = m.reconcile(*fixture())
        self.assertEqual(result["status"], "VP05_SECTOR202_A_EXACT_SOURCE_REVIEW_REQUIRED")
        sub = result["original_modular_support"]
        self.assertEqual(sub["target_a"]["row_count"], 339)
        self.assertEqual(sub["target_b"]["row_count"], 350)
        self.assertEqual(sub["intersection_count"], 300)
        self.assertEqual(sub["A_only_count"], 39)
        self.assertEqual(sub["union_count"], 389)
        self.assertFalse(sub["target_a"]["exact_QQ_z_d_proof"])
        self.assertTrue(result["step93_exact_b"]["symbolic_QQ_z_d_original_ibp_replay_verified"])
        self.assertFalse(result["step93_exact_b"]["substitutable_for_A_proof"])
        self.assertFalse(result["target_obligations"][2]["proven_master_retained_at_new_boundary"])
        self.assertFalse(result["r8s5d3_global_boundary_closure_proven"])
        self.assertFalse(result["kira_executed"])
        self.assertFalse(result["files_modified"])

    def test_reject_incorrect_or_unreplayed_modular_A(self):
        cert, proof, forensic = fixture()
        cert["target_results"][0]["modular_original_replay_verified"] = False
        with self.assertRaisesRegex(RuntimeError, "target identity"):
            m.reconcile(cert, proof, forensic)

    def test_reject_modified_support_inventory(self):
        cert, proof, forensic = fixture()
        cert["target_results"][0]["support_original_ids"].pop()
        with self.assertRaisesRegex(RuntimeError, "certificate support"):
            m.reconcile(cert, proof, forensic)

    def test_reject_invalid_original_id_or_duplicate(self):
        for bad in (-1, 2678, True):
            cert, proof, forensic = fixture()
            cert["target_results"][0]["support_original_ids"][10] = bad
            with self.assertRaisesRegex(RuntimeError, "Invalid original"):
                m.reconcile(cert, proof, forensic)

    def test_reject_missing_exact_b_proof(self):
        cert, proof, forensic = fixture()
        proof["original_source_replay_verified"] = False
        with self.assertRaisesRegex(RuntimeError, "Step93 proof"):
            m.reconcile(cert, proof, forensic)

    def test_reject_missing_ram_stop_evidence(self):
        cert, proof, forensic = fixture()
        forensic["conclusions"]["ram_guard_stop_verified"] = False
        with self.assertRaisesRegex(RuntimeError, "RAM-stop"):
            m.reconcile(cert, proof, forensic)

    def test_sha256_pinned_json_read_only(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "test.json"
            original = json.dumps({"test": True}).encode("utf-8")
            path.write_bytes(original)
            sha = hashlib.sha256(original).hexdigest()
            self.assertEqual(m.read_pinned(path, sha), {"test": True})
            self.assertEqual(path.read_bytes(), original)
            with self.assertRaisesRegex(RuntimeError, "SHA256 mismatch"):
                m.read_pinned(path, "0" * 64)

    def test_json_read_refuses_links_and_oversize(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "big.json"
            with path.open("wb") as f:
                f.truncate(m.MAX_JSON_BYTES + 1)
            with self.assertRaisesRegex(RuntimeError, "too large"):
                m.read_pinned(path, "0"*64)
            real = Path(root) / "regular.json"
            real.write_text("{}")
            link = Path(root) / "linked.json"
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError):
                return
            with self.assertRaisesRegex(RuntimeError, "nonregular"):
                m.read_pinned(link, hashlib.sha256(b"{}").hexdigest())

    def test_reject_corrupt_archived_B_multipliers(self):
        cert, proof, forensic = fixture()
        proof["source_multipliers"][0] = proof["source_multipliers"][1]
        with self.assertRaisesRegex(RuntimeError, "Duplicate exact B"):
            m.reconcile(cert, proof, forensic)

    def test_result_cannot_certify_new_boundary_by_modular_information(self):
        cert, proof, forensic = fixture()
        report = m.reconcile(cert, proof, forensic)
        self.assertFalse(report["sector202_all_three_masters_verified"])
        self.assertFalse(report["r8s6d2_global_boundary_closure_proven"])
        self.assertFalse(report["original_restricted_kira_source_context"][
            "source_to_new_r7s5d3_scope_equivalence_proven"])


if __name__ == "__main__":
    unittest.main()
