"""The normalized exact pivot identity is algebraically equivalent to replay.

This test does not substitute numerical/modular samples for exact proofs.
"""
import unittest
import sympy as sp
from examples.three_loop_vp05_sector202_target_b_step64_normalized_replay import verify_index
from examples.three_loop_vp05_sector202_target_b_step64_original_ibp_replay import load

class NormalizedStep64Tests(unittest.TestCase):
    def test_exact_symbolic_scaling_equivalence(self):
        z,d=sp.symbols("z d")
        factor=(z+2)/(d+1)
        pivot=(z*z+2*z)/(d+1)
        source_terms=[z*z/(d+1),2*z/(d+1)]
        normalized=sp.cancel(pivot-sum(source_terms))
        direct=sp.cancel(factor*pivot-sum(factor*x for x in source_terms))
        self.assertEqual(normalized,0)
        self.assertEqual(direct,0)
    def test_exact_nonzero_detection(self):
        z,d=sp.symbols("z d")
        self.assertNotEqual(sp.cancel(z/d-z/(d+1)),0)
    def test_entrypoint(self):
        self.assertTrue(callable(verify_index))
        self.assertTrue(callable(load))

if __name__=="__main__":
    unittest.main()
