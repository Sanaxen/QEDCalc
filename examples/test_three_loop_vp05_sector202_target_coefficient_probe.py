"""Offline tests: isolate exact step51 coefficient without state mutation."""
import json
import tempfile
import unittest
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_target_coefficient_probe import operands, calculation

class SingleCoefficientTests(unittest.TestCase):
    def test_isolated_operands_and_methods(self):
        state={"remaining":[[[1,73],"z+1"],[[2,73],"z+3"]]}
        source={"pivots":[{"lead":[1,73],
                 "row":[[[1,73],"1"],[[2,73],"z+2"]],"trace":[]}]}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"pivot.json"
            p.write_text(json.dumps(source),encoding="utf-8")
            before=p.read_bytes()
            a,f,b,lead=operands(state,p,(2,73))
            self.assertEqual(lead,(1,73))
            self.assertEqual(sp.cancel(a-(sp.Symbol("z")+3)),0)
            results=[]
            for method in ("cancel","together_cancel","factor_first"):
                result=calculation(a,f,b,method)
                self.assertEqual(sp.cancel(result-(a-f*b)),0)
                results.append(result)
            self.assertTrue(all(sp.cancel(results[0]-x)==0 for x in results))
            self.assertEqual(before,p.read_bytes())
    def test_missing_key_rejected(self):
        state={"remaining":[[[1,73],"z+1"]]}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"pivot.json"
            p.write_text(json.dumps({"pivots":[{"lead":[1,73],
                "row":[[[1,73],"1"]],"trace":[]}]}))
            with self.assertRaisesRegex(RuntimeError,"not in next pivot"):
                operands(state,p,(2,73))
if __name__=="__main__":
    unittest.main()
