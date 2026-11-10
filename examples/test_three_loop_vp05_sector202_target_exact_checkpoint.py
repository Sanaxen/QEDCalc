"""Small offline tests for the sector202 exact-target checkpoint helpers.

No Kira files or existing checkpoints are read or modified.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_target_exact_checkpoint import (
    encoded,decoded,trace_encoded,trace_decoded,metrics,atomic_create,
    assert_modular_invariant,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import POINTS

class ExactTargetCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.z,self.d=sp.symbols("z d")

    def test_sparse_serialization_roundtrip(self):
        x={(9,3):sp.Rational(-19,2),(4,73):self.z+1}
        t={7:sp.Rational(-1,2),11:self.d+1}
        self.assertEqual(decoded(encoded(x),self.z,self.d),x)
        self.assertEqual(trace_decoded(trace_encoded(t),self.z,self.d),t)

    def test_modular_target_trace_residual_identity(self):
        original={11:{"terms":[{"key":[1,73],"coefficient":"z+2"},
                               {"key":[2,73],"coefficient":"-3*z+4"}]}}
        trace={11:sp.Rational(-1,2)}
        initial={(1,73):sp.Rational(-1,2)*(self.z+2),
                 (2,73):sp.Rational(-1,2)*(-3*self.z+4)}
        for point in POINTS:
            assert_modular_invariant(initial,{},trace,original,self.z,self.d,point)
        invalid={(1,73):sp.Integer(1)}
        with self.assertRaises(AssertionError):
            assert_modular_invariant(invalid,{},trace,original,
                                     self.z,self.d,POINTS[0])

    def test_atomic_creation_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"checkpoint.json"
            atomic_create(path,{"steps":8,"status":"TEST_ONLY"})
            self.assertEqual(json.loads(path.read_text())["steps"],8)
            with self.assertRaises(FileExistsError):
                atomic_create(path,{"steps":9})
            self.assertEqual(json.loads(path.read_text())["steps"],8)

    def test_metrics(self):
        x={(5,73):self.z+1}
        t={3:sp.Rational(-1,2)}
        info=metrics(x,t)
        self.assertEqual(info["remainder_terms"],1)
        self.assertEqual(info["original_support"],1)
        self.assertEqual(info["lead"],[5,73])

if __name__=="__main__":
    unittest.main()
