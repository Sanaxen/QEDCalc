"""Offline regression tests for bounded sector202 coefficient rewrite probes."""
import unittest
import sympy as sp
from examples.three_loop_vp05_sector202_target_compaction_probe import (
    chosen_entry, compact_candidate,
)
class CompactionProbeTests(unittest.TestCase):
    def test_select_coefficient(self):
        data={"remaining":[[[1,73],"(z+2)/(d-1)"]],
              "source":[[604,"-1/2"]]}
        self.assertEqual(chosen_entry(data,"remainder","[1, 73]"),"(z+2)/(d-1)")
        self.assertEqual(chosen_entry(data,"source_trace","604"),"-1/2")
        with self.assertRaises(ValueError):
            chosen_entry(data,"remainder","[2,73]")
    def test_exact_rewrites(self):
        z,d=sp.symbols("z d")
        value=(z**2-1)/(z-1)*(d+1)
        for method in ("factor_terms","factor_numden","factor"):
            candidate=compact_candidate(value,method)
            self.assertEqual(sp.cancel(sp.together(candidate-value)),0)
    def test_method_guard(self):
        with self.assertRaises(ValueError):
            compact_candidate(sp.Integer(1),"unknown")
if __name__=="__main__":
    unittest.main()
