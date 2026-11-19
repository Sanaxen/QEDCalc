"""Offline tests for read-only VP05 residual Kira evidence inspection."""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from examples import three_loop_vp05_stage2_residual_forensics as m


class ResidualForensicsTests(unittest.TestCase):
    def test_missing_project_does_not_create_folders(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "missing"
            row = m.project_profile(p, expected_targets=["VP05_full[1,0,0,0,0,0,0,0,0,0,0,0]"],
                                    mandatory_name="mandatory.txt")
            self.assertFalse(p.exists())
            self.assertEqual(row["finding"], "project_missing")
            self.assertFalse(row["scientific_reduction_proven"])

    def test_prepared_inputs_and_exact_copy_check(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "project"
            p.mkdir()
            target = "VP05_full[0,1,0,1,-2,0,1,1,0,0,0,0]"
            (p / "mandatory.txt").write_text(target + "\n")
            (p / "preferred.txt").write_text(target + "\n")
            row = m.project_profile(p, expected_targets=[target], mandatory_name="mandatory.txt",
                                    preferred_name="preferred.txt")
            self.assertTrue(row["mandatory_input_set_matches_expected"])
            self.assertTrue(row["preferred_input_set_matches_expected"])
            self.assertEqual(row["finding"], "prepared_inputs_only_or_no_execution_evidence")
            self.assertFalse(row["scientific_reduction_proven"])

    def test_log_tail_bounded_and_no_false_success(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "project"
            p.mkdir()
            (p / "kira.log").write_text("old output\n" * 10000 +
                "Generate equations for topology VP05_full, sector 197 (4 of 12)\n" +
                "swap rising; computation stopped by user\n")
            with patch.object(m, "LOG_TAIL_BYTES", 512):
                row = m.project_profile(p, expected_targets=None, mandatory_name="mandatory.txt")
            self.assertEqual(row["log_files"][0]["last_sector_progress"]["sector"], 197)
            self.assertLessEqual(row["log_files"][0]["tail_bytes_read"], 512)
            self.assertEqual(row["finding"], "intermediate_state_present_no_proven_master_list")
            self.assertFalse(row["scientific_reduction_proven"])

    def test_partial_system_is_not_a_proof(self):
        with TemporaryDirectory() as td:
            p = Path(td) / "project"
            d = p / "tmp" / "VP05_full"
            d.mkdir(parents=True)
            (d / "SYSTEM_VP05_full_202.gz").write_bytes(b"test only")
            row = m.project_profile(p, expected_targets=None, mandatory_name="mandatory.txt")
            self.assertEqual(row["metadata"]["system_equations"]["count"], 1)
            self.assertEqual(row["finding"], "partial_system_gz_present_requires_exact_source_audit")
            self.assertFalse(row["scientific_reduction_proven"])

    def test_equal_set_different_order_does_not_create_closure_proof(self):
        with TemporaryDirectory() as td:
            p = Path(td)
            a = "VP05_full[0,1,0,1,-2,0,1,1,0,0,0,0]"
            b = "VP05_full[0,1,0,1,0,0,1,1,0,0,0,0]"
            (p / "mandatory.txt").write_text(b + "\n" + a + "\n")
            row = m.project_profile(p, expected_targets=[a, b], mandatory_name="mandatory.txt")
            self.assertTrue(row["mandatory_input_set_matches_expected"])
            self.assertFalse(row["mandatory_input_order_matches_expected"])
            self.assertFalse(row["scientific_reduction_proven"])

    def test_symlink_project_blocked(self):
        with TemporaryDirectory() as td:
            p = Path(td)
            link = p / "redirect"
            try:
                link.symlink_to(p, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink not supported")
            with self.assertRaises(RuntimeError):
                m.project_profile(link, expected_targets=None, mandatory_name="mandatory.txt")

    def test_incomplete_input_not_mistaken_for_full(self):
        with TemporaryDirectory() as td:
            p = Path(td)
            (p / "mandatory.txt").write_text("VP05_full[1,0,0,0,0,0,0,0,0,0,0,0]\n")
            x = m.project_profile(p, expected_targets=["VP05_full[0,1,0,0,0,0,0,0,0,0,0,0]"],
                                  mandatory_name="mandatory.txt")
            self.assertFalse(x["mandatory_input_set_matches_expected"])


if __name__ == "__main__":
    unittest.main()
