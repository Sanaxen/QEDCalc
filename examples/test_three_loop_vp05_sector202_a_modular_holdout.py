"""Offline tests: VP05 sector202 339-row modular holdouts are never proof."""
from __future__ import annotations

import gzip
import hashlib
import json
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from examples import three_loop_vp05_sector202_a_modular_holdout as m


class Codec:
    def __init__(self):
        self.forward = {v: k for k, v in zip((100, 200, 300), m.previous.TARGETS)}
        self.backward = {v: k for k, v in self.forward.items()}

    def encode(self, vector):
        return self.forward[tuple(vector)]

    def decode(self, key):
        return self.backward[key]


def source_selection():
    return {"status": "VP05_SECTOR202_A_EXACT_SOURCE_REVIEW_REQUIRED",
            "sector202_all_three_masters_verified": False,
            "original_restricted_kira_source_context": {
                "source_to_new_r7s5d3_scope_equivalence_proven": False},
            "step93_exact_b": {
                "exact_B_support_equal_to_modular_B_support": True},
            "original_modular_support": {
                "target_a": {"source_row_ids": list(range(339))},
                "target_b": {"source_row_ids": list(range(389))},
                "A_only_count": 0, "intersection_count": 339,
                "union_count": 389}}


class TargetAModularHoldoutTests(unittest.TestCase):
    def test_subset_exactly_339_not_just_count_overlap(self):
        ids = m.validate_selection(source_selection())
        self.assertEqual(len(ids), 339)
        self.assertEqual(ids[0], 0)
        self.assertEqual(ids[-1], 338)

    def test_reject_non_subset_even_with_same_sizes(self):
        broken = source_selection()
        broken["original_modular_support"]["target_a"]["source_row_ids"][-1] = 500
        with self.assertRaisesRegex(RuntimeError, "Unexpected A-subset-B"):
            m.validate_selection(broken)

    def test_reject_missing_exact_b_archive_link(self):
        broken = source_selection()
        broken["step93_exact_b"]["exact_B_support_equal_to_modular_B_support"] = False
        with self.assertRaisesRegex(RuntimeError, "Unexpected A-subset-B"):
            m.validate_selection(broken)

    def test_target_and_original_coefficient_uses_original_codec(self):
        codec = Codec()
        point = m.POINTS[1]
        p, z, d = point
        row = m.target_at_point(codec, point)
        self.assertEqual(row[(100, 139)], 1)
        self.assertEqual(row[(300, 139)],
                         (-m.coefficient(m.exact.FORMULAS[0], z, d, p)) % p)
        self.assertEqual(row[(4, 73)],
                         (-m.coefficient(m.exact.FORMULAS[1], z, d, p)) % p)
        self.assertEqual(m.row_at_point([{"key": [900, 139], "coefficient": "2*z/d"}], p, z, d),
                         {(900, 139): m.coefficient("2*z/d", z, d, p)})

    def test_sparse_forward_rowspan_reduction_and_rank(self):
        p = 1000003
        cutoff = time.monotonic() + 10
        pivots = {}
        self.assertEqual(m.insert({(3, 2): 3, (4, 2): 6}, pivots, p, 100, 100, cutoff)[1],
                         "PIVOT_ADDED")
        self.assertEqual(len(pivots), 1)
        rem, steps, status = m.forward({(3, 2): 1, (4, 2): 2}, pivots, p, 100, 100, cutoff)
        self.assertEqual((rem, status), ({}, "ZERO_REMAINDER"))
        self.assertEqual(steps, 1)
        self.assertEqual(m.insert({(3, 2): 1, (4, 2): 2}, pivots, p,
                                  100, 100, cutoff)[1], "ZERO_REMAINDER")

    def test_synthetic_A_holdout_pass_is_not_exact(self):
        codec, point = Codec(), m.POINTS[1]
        target = m.target_at_point(codec, point)
        terms = [{"key": list(k), "coefficient": str(v)}
                 for k, v in target.items()]
        rows = {1: terms, 2: [{"key": [900, 139], "coefficient": "1"}]}
        report = m.evaluate(point=point, ids=[1, 2], rows=rows, codec=codec,
                            max_fill=100, max_steps=100, max_seconds=5,
                            max_total_cells=100)
        self.assertEqual(report["status"], "A_MODULAR_HOLDOUT_SAVED_SOURCE_SPAN_PASS_NOT_EXACT_PROOF")
        self.assertTrue(report["source_rowspan_includes_candidate_A"])
        self.assertFalse(report["original_qq_z_d_identity_proven"])
        self.assertEqual(report["basis_rank"], 2)

    def test_synthetic_A_holdout_outside_span_is_open(self):
        codec, point = Codec(), m.POINTS[1]
        rows = {1: [{"key": [900, 139], "coefficient": "1"}]}
        report = m.evaluate(point=point, ids=[1], rows=rows, codec=codec,
                            max_fill=100, max_steps=100, max_seconds=5,
                            max_total_cells=100)
        self.assertEqual(report["status"], "A_MODULAR_HOLDOUT_SAVED_SOURCE_SPAN_GAP")
        self.assertFalse(report["source_rowspan_includes_candidate_A"])
        self.assertFalse(report["original_qq_z_d_identity_proven"])

    def test_fill_cap_does_not_fabricate_target_pass(self):
        point, codec = m.POINTS[1], Codec()
        row = [{"key": [int(i), 139], "coefficient": "1"} for i in range(10, 20)]
        report = m.evaluate(point=point, ids=[1], rows={1: row}, codec=codec,
                            max_fill=3, max_steps=100, max_seconds=5,
                            max_total_cells=100)
        self.assertEqual(report["stopped_by_cap"], "FILL_CAP")
        self.assertFalse(report["source_rowspan_includes_candidate_A"])

    def test_original_gzip_rejects_missing_protected_A_row(self):
        with tempfile.TemporaryDirectory() as dirname:
            source = Path(dirname) / "rows.json.gz"
            bundle = {
                "status": "ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED",
                "saved_equation_count": 2678,
                "selected_equation_count": 2241,
                "rows": [
                    {"global_zero_based": i, "terms": [{"key": [i, 139], "coefficient": "1"}]}
                    for i in range(2241)]
            }
            with gzip.open(source, "wb") as stream:
                stream.write(json.dumps(bundle).encode())
            sha = hashlib.sha256(source.read_bytes()).hexdigest()
            with patch.object(m, "SOURCE", source), patch.object(
                m.split, "read_pinned", return_value={
                    "source_and_evidence_sha256": {"original_source_rows.json.gz": sha}}):
                loaded = m.original_rows([10, 11])
                self.assertEqual(sorted(loaded), [10, 11])
                with self.assertRaisesRegex(RuntimeError, "missing"):
                    m.original_rows([2500])

    def test_source_sha_change_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as dirname:
            source = Path(dirname) / "rows.json.gz"
            source.write_bytes(b"invalid")
            with patch.object(m, "SOURCE", source), patch.object(
                m.split, "read_pinned", return_value={
                    "source_and_evidence_sha256": {"original_source_rows.json.gz": "0"*64}}):
                with self.assertRaisesRegex(RuntimeError, "differs"):
                    m.original_rows([0])

    def test_invalid_point_index_without_any_io(self):
        with self.assertRaisesRegex(ValueError, "three pinned"):
            m.inspect(5)

    def test_inspect_honors_original_codec_and_no_source_writes(self):
        with patch.object(m.split, "inspect", return_value=source_selection()), patch.object(
            m, "original_rows", return_value={}), patch.object(
            m, "load_codec", return_value=SimpleNamespace(
                from_kiradb=lambda _: (11, 5),
                WeightCodec=lambda **_: Codec())), patch.object(
            m, "evaluate", return_value={
                "status": "A_MODULAR_HOLDOUT_SAVED_SOURCE_SPAN_GAP",
                "source_rowspan_includes_candidate_A": False}):
            result = m.inspect(1)
        self.assertEqual(result["point_index"], 1)
        self.assertEqual(result["A_original_source_rows_selected"], 339)
        self.assertFalse(result["files_modified"])
        self.assertFalse(result["kira_executed"])
        self.assertTrue(result["original_exact_source_protected"])


if __name__ == "__main__":
    unittest.main()
