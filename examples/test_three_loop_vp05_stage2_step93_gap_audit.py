"""Offline tests for strict Stage-2 vs Step93 evidence separation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import json
from examples import three_loop_vp05_stage2_step93_gap_audit as m


def entry(x):
    return "VP05_full[" + ",".join(map(str, x)) + "]"


def candidate_manifest():
    masters = [entry((i + 1,) + (0,) * 11) for i in range(63)]
    return {
        "family": "VP05_full", "candidate_master_count": 63,
        "candidate_masters": masters,
        "closure_targets": [entry(m.TARGETS[1]), entry(m.TARGETS[0])],
    }


class Stage2GapTests(TestCase):
    def test_scope_independent_of_step93_exact_proof(self):
        result = m.review(candidate_manifest(), {}, {}, {}, True)
        self.assertEqual(result["status"], "VP05_STAGE2_BOUNDARY_GAPS_REMAIN")
        self.assertTrue(result["step93_target_b"]["formal_archive_verified"])
        self.assertTrue(result["step93_target_b"]["in_standard_closure_targets"])
        self.assertFalse(result["step93_target_b"]["eligible_to_replace_any_full_boundary_closure"])
        self.assertEqual(result["unresolved_standard_seed_closures"], list(m.SEEDS))
        self.assertFalse(result["standard_63_candidate_closure_saved_audit_pass"])
        self.assertFalse(result["family_registry_changed"])

    def test_sector202_and_exact_tuple(self):
        self.assertEqual(m.sector(m.TARGETS[1]), 202)
        self.assertEqual(m.indices(entry(m.TARGETS[1])), m.TARGETS[1])
        self.assertIsNone(m.indices("VP05_full[0,1,2]"))

    def test_unproven_restricted_audit_cannot_promote(self):
        local = {seed: {"family": "VP05_full", "test_seed": seed,
                 "candidate_master_count": 63, "retained_candidate_count": 63,
                 "sector_count": 1, "sector_rows": [{"sector": 202, "stable": True}],
                 "audit_pass": True, "stable_under_sector_local_closure": True,
                 "errors": [], "missing_candidate_masters": []} for seed in m.SEEDS}
        result = m.review(candidate_manifest(), {}, local, {}, True)
        self.assertTrue(all(x["candidate63_sector_local_pass"]
                            for x in result["sector_local_boundary_diagnostics"].values()))
        self.assertFalse(result["standard_63_candidate_closure_saved_audit_pass"])

    def test_three_exact_standard_boundaries(self):
        audit = {"family": "VP05_full", "candidate_master_count": 63,
                 "audit_pass": True, "stable_under_one_axis_extensions": True,
                 "boundary_rows": [{"seed": s, "stable": True} for s in m.SEEDS]}
        result = m.review(candidate_manifest(), audit, {}, {}, True)
        self.assertTrue(result["standard_63_candidate_closure_saved_audit_pass"])
        self.assertFalse(result["standard_promotion_ready_saved_audit_pass"])
        audit["boundary_rows"][0]["stable"] = False
        self.assertFalse(m.review(candidate_manifest(), audit, {}, {}, True)
                         ["standard_63_candidate_closure_saved_audit_pass"])

    def test_no_mutation_and_missing_archive(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / f"{m.PREFIX}_candidate_{m.CANDIDATE_SEED}_closure_manifest.json").write_text(
                json.dumps(candidate_manifest()), encoding="utf-8"
            )
            original = sorted(p.name for p in root.iterdir())
            with patch.object(m, "AUDIT", root), patch.object(m, "ARCHIVE", root / "not_present"):
                report = m.inspect()
            self.assertFalse(report["step93_target_b"]["formal_archive_verified"])
            self.assertEqual(sorted(p.name for p in root.iterdir()), original)


if __name__ == "__main__":
    import unittest
    unittest.main()
