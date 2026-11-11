"""Synthetic tests; no production inputs or target checkpoint changes."""
import copy
import unittest
from examples.three_loop_vp05_sector202_step51_candidate_audit import audit
from examples.three_loop_vp05_sector202_step51_scratch import key_id


class CandidateAuditTests(unittest.TestCase):
    def setUp(self):
        self.target = {
            "steps": 50, "config": {"target": "A", "max_expression_chars": 7500},
            "remaining": [[[1, 73], "z+1"], [[2, 73], "z+3"]],
            "source": [[11, "d-1"]],
        }
        self.pivot = {
            "row": [[[1, 73], "1"], [[2, 73], "z+2"], [[3, 73], "-1/2"]],
            "trace": [[11, "1/2"], [12, "-1"]],
        }
        self.jobs = [("remainder", k, v) for k, v in self.pivot["row"]]
        self.jobs += [("source_trace", k, v) for k, v in self.pivot["trace"]]
        results = ("0", "(z+3)-(z+1)*(z+2)", "(z+1)/2",
                   "(d-1)+(z+1)/2", "-(z+1)")
        self.scratch = {
            "config": {"target_max_expression_chars": 7500},
            "done": [
                {"id": key_id(kind, key), "value": value, "chars": len(value)}
                for (kind, key, _), value in zip(self.jobs, results)
            ],
        }
        # 0.5*row11-row12 == pivot.
        self.originals = {
            11: {"terms": [
                {"key": [1, 73], "coefficient": "2"},
                {"key": [2, 73], "coefficient": "2*(z+2)"},
                {"key": [3, 73], "coefficient": "-1"},
                {"key": [9, 73], "coefficient": "2"}]},
            12: {"terms": [{"key": [9, 73], "coefficient": "1"}]},
        }

    def test_modular_invariant_and_proof_boundary(self):
        original = copy.deepcopy(self.target)
        result = audit(self.target, self.scratch, self.pivot,
                       self.jobs, self.originals)
        self.assertEqual(len(result["verified_points"]), 3)
        self.assertEqual(result["eliminated_pivot"], [1, 73])
        self.assertFalse(result["exact_target_proven"])
        self.assertEqual(original, self.target)

    def test_reject_corrupt_candidate(self):
        broken = copy.deepcopy(self.scratch)
        broken["done"][1]["value"] = "17"
        with self.assertRaises(AssertionError):
            audit(self.target, broken, self.pivot, self.jobs, self.originals)

    def test_reject_incomplete_scratch(self):
        broken = copy.deepcopy(self.scratch)
        broken["done"].pop()
        with self.assertRaises(RuntimeError):
            audit(self.target, broken, self.pivot, self.jobs, self.originals)


if __name__ == "__main__":
    unittest.main()
