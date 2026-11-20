"""Offline exact parity tests for opt-in persistent field sequence pilot."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from examples import three_loop_vp05_exact_sequential_probe as probe
from examples import three_loop_vp05_exact_arithmetic_probe as arithmetic


class SequentialProbeTests(unittest.TestCase):
    def test_two_update_rounds_strict_exact(self):
        z, d = arithmetic.Z, arithmetic.D
        samples = [
            {1: (z+d)/(d+1), 2: z/(d+2)},
            {1: (z-d)/(z+2), 3: (d+1)/(z+1)},
            {2: (z+3)/(d+3), 3: (z+d+1)/(z-d+2)},
        ]
        results, conversion_s = probe.compare_sequence(samples)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(item["exact_pass"] for item in results))
        self.assertGreaterEqual(conversion_s, 0)

    def test_zero_cancellation_across_rounds(self):
        z = arithmetic.Z
        samples = [{10: z+1}, {10: z+1}, {11: z+2}]
        results, _ = probe.compare_sequence(samples, multipliers=[1, 1])
        self.assertEqual(results[0]["output_terms"], 0)
        self.assertEqual(results[1]["output_terms"], 1)
        self.assertTrue(all(item["exact_pass"] for item in results))

    def test_bad_multiplier_count_rejected(self):
        with self.assertRaisesRegex(ValueError, "Multiplier count"):
            probe.compare_sequence([{}, {}], multipliers=[])

    def test_checkpoint_sha_and_distinct_trace_selection(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "saved.json"
            pivots = []
            for i in range(200):
                support = 50 if i >= 197 else 1
                pivots.append({
                    "lead": [i,139],
                    "trace": [[k, "(z+1)/(d+2)"] for k in range(support)]
                })
            path.write_text(json.dumps({
                "version":1, "status":"EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF",
                "config":{"target":"A"}, "processed":200, "dependent":0,
                "pivots":pivots, "exact_target_reduction_proven":False,
                "source_pivots_exact_replay_verified":True,
            }),encoding="utf-8")
            content = path.read_bytes()
            sha = hashlib.sha256(content).hexdigest()
            sequences, actual, processed = probe.trace_sequence(
                path, expected_sha256=sha, terms=50, max_chars=600, rounds=2)
            self.assertEqual((actual,processed), (sha,200))
            self.assertEqual(len(sequences), 3)
            self.assertEqual([len(x) for x in sequences], [50]*3)
            self.assertEqual(content, path.read_bytes())
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                probe.trace_sequence(path,expected_sha256="0"*64,
                                     terms=50,max_chars=600,rounds=2)

    def test_insufficient_qualifying_sources_rejected(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/"saved.json"
            pivots=[{"lead":[i,139],
                     "trace":[[k,"z+1"] for k in range(
                         50 if i==199 else 1)]} for i in range(200)]
            path.write_text(json.dumps({
                "version":1,"status":"EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF",
                "config":{"target":"A"},"processed":200,"dependent":0,
                "pivots":pivots,"exact_target_reduction_proven":False,
                "source_pivots_exact_replay_verified":True,
            }),encoding="utf-8")
            sha=hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError,"Insufficient distinct"):
                probe.trace_sequence(path,expected_sha256=sha,
                                     terms=50,max_chars=600,rounds=2)


if __name__ == "__main__":
    unittest.main()
