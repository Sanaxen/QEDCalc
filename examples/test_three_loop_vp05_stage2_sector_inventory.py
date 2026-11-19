"""Offline read-only regression tests for VP05 two-seed per-sector inventory."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from examples import three_loop_vp05_stage2_sector_inventory as m


class VP05SectorEvidenceTests(unittest.TestCase):
    def test_classifications_do_not_equal_global_proof(self):
        self.assertEqual(m.category(True, False, False, True),
            "restricted_equivalent_audit_candidate_for_review")
        self.assertEqual(m.category(False, True, True, True),
            "matching_local_master_inventory_needs_closure_audit")
        self.assertEqual(m.category(False, False, True, True),
            "existing_project_requires_forensics")
        self.assertEqual(m.category(False, False, False, True),
            "no_matching_verified_sector_evidence")

    def test_missing_sector_project_does_not_write(self):
        with TemporaryDirectory() as folder:
            project = Path(folder) / "missing"
            with patch.object(m, "_project", return_value=project), patch.object(
                m, "_restricted_equivalent_audit", return_value=(False, "no audit")
            ):
                row = m.analyze_sector(m.SEEDS[0], 202, ["VP05_full[0,1,0,1,-2,0,1,1,0,0,0,0]"])
            self.assertFalse(project.exists())
            self.assertFalse(row["whole_family_closure_proven_by_this_entry"])
            self.assertFalse(row["safe_to_auto_promote"])
            self.assertEqual(row["classification"], "no_matching_verified_sector_evidence")

    def test_restricted_audit_without_project_is_only_review_candidate(self):
        with TemporaryDirectory() as folder:
            with patch.object(m, "_project", return_value=Path(folder) / "missing"), patch.object(
                m, "_restricted_equivalent_audit", return_value=(True, "matching scope")
            ):
                row = m.analyze_sector(m.SEEDS[1], 202, ["VP05_full[0,1,0,1,-2,0,1,1,0,0,0,0]"])
            self.assertEqual(row["classification"], "restricted_equivalent_audit_candidate_for_review")
            self.assertFalse(row["whole_family_closure_proven_by_this_entry"])

    def test_existing_input_compatible_master_list_is_not_promotion(self):
        target = "VP05_full[0,1,0,1,-2,0,1,1,0,0,0,0]"
        with TemporaryDirectory() as folder:
            p = Path(folder)
            with patch.object(m, "_project", return_value=p), patch.object(
                m, "_restricted_equivalent_audit", return_value=(False, "absent")
            ), patch.object(
                m, "_reusable_project", return_value=(True, "input validated")
            ), patch.object(
                m, "find_or_infer_masters", return_value=(p/"masters", [target], "saved-list")
            ):
                row = m.analyze_sector(m.SEEDS[0], 202, [target])
            self.assertTrue(row["matching_local_master_inventory"])
            self.assertEqual(row["classification"], "matching_local_master_inventory_needs_closure_audit")
            self.assertFalse(row["safe_to_auto_promote"])

    def test_seeds_are_expected_axes(self):
        self.assertEqual([s.tag for s in m.SEEDS], ["r8s6d2", "r8s5d3"])
        self.assertEqual(m.BASELINE.tag, "r8s3d0")


if __name__ == "__main__":
    unittest.main()
