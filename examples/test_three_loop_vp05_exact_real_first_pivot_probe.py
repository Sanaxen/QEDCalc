"""Offline guards and exact original-IBP replay for the read-only pivot pilot."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sympy as sp

from examples import three_loop_vp05_exact_real_first_pivot_probe as pilot
from examples import three_loop_vp05_exact_arithmetic_probe as ar


class RealFirstPivotPilotTests(unittest.TestCase):
    def test_one_real_pivot_shape_with_exact_original_source_replay(self):
        z, d = ar.Z, ar.D
        a, b = (0,), (1,)
        rows = {
            10: {"terms": [
                {"key": [0], "coefficient": "z+1"},
                {"key": [1], "coefficient": "d"}]},
            20: {"terms": [
                {"key": [0], "coefficient": "1"},
                {"key": [1], "coefficient": "z"}]},
        }
        cur = {a: sp.Integer(1), b: z}
        trace = {20: sp.Integer(1)}
        brow = {a: sp.Integer(1), b: d/(z+1)}
        btrace = {10: 1/(z+1)}
        result = pilot.compare_pivot_step(
            cur, trace, brow, btrace, sp.Integer(1), rows, z, d)
        self.assertTrue(result["strict_exact_row_equal"])
        self.assertTrue(result["strict_exact_trace_equal"])
        self.assertTrue(result["original_ibp_source_replay_verified"])
        self.assertEqual(result["output_columns"], 1)
        self.assertEqual(result["output_provenance_support"], 2)
        self.assertEqual(cur[a], 1)
        self.assertEqual(trace[20], 1)

    def test_incorrect_original_source_provenance_refused(self):
        z, d = ar.Z, ar.D
        rows = {
            10: {"terms": [{"key": [0], "coefficient": "z+1"}]},
            20: {"terms": [{"key": [0], "coefficient": "1"}]},
        }
        # Deliberately wrong pivot provenance; parity may agree between both
        # arithmetic paths, but original-source replay MUST still reject.
        with self.assertRaisesRegex(AssertionError, "provenance mismatch"):
            pilot.compare_pivot_step(
                {(0,): sp.Integer(1)}, {20: sp.Integer(1)},
                {(0,): sp.Integer(1)}, {10: sp.Integer(2)},
                sp.Integer(1), rows, z, d)

    def test_unpinned_checkpoint_refused_before_parsing(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            checkpoint = folder / "checkpoint.json"
            source = folder / "source.json.gz"
            cert = folder / "certificate.json"
            checkpoint.write_text("{}", encoding="utf-8")
            source.write_bytes(b"x")
            cert.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "checkpoint SHA256 mismatch"):
                pilot.validated_inputs(checkpoint, source, cert)

    def test_symlink_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            original = folder / "original.json"
            original.write_text("{}", encoding="utf-8")
            checkpoint = folder / "checkpoint.json"
            checkpoint.symlink_to(original)
            source = folder / "source.json.gz"
            source.write_bytes(b"x")
            cert = folder / "certificate.json"
            cert.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "symbolic-link"):
                pilot.validated_inputs(checkpoint, source, cert)


if __name__ == "__main__":
    unittest.main()
