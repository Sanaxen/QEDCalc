"""Offline rigorous equivalence tests for the nonproduction QQ(z,d) probe."""
from __future__ import annotations

import hashlib
import json
import random
import tempfile
import unittest
from pathlib import Path

import sympy as sp

from examples import three_loop_vp05_exact_arithmetic_probe as probe

Z, D = probe.Z, probe.D


class ExactArithmeticProbeTests(unittest.TestCase):
    def test_zero_cancel(self):
        self.assertTrue(probe.exact_same(
            probe.sympy_sparse_subtract({1: Z + D}, {1: Z + D}, 1),
            probe.fraction_field_sparse_subtract(
                {1: Z + D}, {1: Z + D}, 1)))

    def test_exact_mixed_sparse_cases(self):
        for case in probe.basic_cases():
            with self.subTest(name=case[0]):
                _, dest, source, multiplier = case
                self.assertTrue(probe.exact_same(
                    probe.sympy_sparse_subtract(dest, source, multiplier),
                    probe.fraction_field_sparse_subtract(
                        dest, source, multiplier)))
                self.assertEqual(probe.bench_case(case)["exact_pass"], True)

    def test_seeded_exact_rational_cases(self):
        rng = random.Random(24601)
        for iteration in range(32):
            def rational():
                a, b, c, e = [rng.randint(-3, 3) for _ in range(4)]
                numerator = (a + 1) * Z + b * D + c + 1
                denominator = (e + 4) * Z + (b + 5) * D + 7
                return numerator / denominator
            dest = {key: rational() for key in range(4) if rng.randrange(2)}
            source = {key: rational() for key in range(4) if rng.randrange(2)}
            multiplier = rational()
            with self.subTest(iteration=iteration):
                previous_dest = dict(dest)
                previous_source = dict(source)
                baseline = probe.sympy_sparse_subtract(dest, source, multiplier)
                candidate = probe.fraction_field_sparse_subtract(
                    dest, source, multiplier)
                self.assertTrue(probe.exact_same(baseline, candidate))
                self.assertEqual(previous_dest, dest)
                self.assertEqual(previous_source, source)

    def test_stale_checkpoint_hash_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "existing.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                probe.sampled_cases_from_checkpoint(
                    path, expected_sha256="0" * 64)
            self.assertEqual(path.read_text(), "{}")

    def test_non_target_checkpoint_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "existing.json"
            path.write_text(json.dumps({
                "version": 1, "status": "EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF",
                "config": {"target": "B"}, "processed": 210, "dependent": 0,
                "pivots": [{} for _ in range(210)],
                "source_pivots_exact_replay_verified": True,
                "exact_target_reduction_proven": False,
            }))
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "valid fully-accounted"):
                probe.sampled_cases_from_checkpoint(path)
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
