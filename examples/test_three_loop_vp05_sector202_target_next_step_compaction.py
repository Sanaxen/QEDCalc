"""Offline tests of read-only next-pivot coefficient compaction diagnostic."""
import json
import tempfile
import unittest
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_target_next_step_compaction import one_step

class NextStepCompactionTests(unittest.TestCase):
    def test_one_step_does_not_change_saved_state(self):
        state={"steps":50,
               "config":{"max_expression_chars":5},
               "remaining":[[[1,73],"z+1"]],
               "source":[]}
        pivot={"pivots":[{"lead":[1,73],
                          "row":[[[1,73],"1"],[[2,73],"z+2"]],
                          "trace":[[604,"1"]]}]}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"pivots.json"
            p.write_text(json.dumps(pivot),encoding="utf-8")
            before=json.dumps(state,sort_keys=True)
            result=one_step(state,p,3)
            self.assertEqual(result["attempted_step"],51)
            self.assertEqual(result["candidate_before"]["remainder_terms"],1)
            self.assertTrue(all(x["exact_equal"] for x in result["results"]))
            self.assertFalse(result["checkpoint_modified"])
            self.assertFalse(result["next_step_saved"])
            self.assertEqual(json.dumps(state,sort_keys=True),before)
            self.assertEqual(json.loads(p.read_text()),pivot)

    def test_missing_pivot_is_rejected(self):
        state={"steps":50,"config":{"max_expression_chars":7500},
               "remaining":[[[1,73],"z+1"]],"source":[]}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"pivots.json"
            p.write_text('{"pivots":[]}',encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError,"No unique next pivot"):
                one_step(state,p,1)
if __name__=="__main__":
    unittest.main()
