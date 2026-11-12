"""Pure offline exact Step53 coefficient regression tests."""
import unittest
from examples.three_loop_vp05_sector202_step53_exact_candidate import exact_coefficient


class Step53CoefficientTests(unittest.TestCase):
    def test_exact_subtraction(self):
        result, chars, shortened = exact_coefficient(
            "z**2 + 2*z + 1", "z+1", "z+1", -1)
        self.assertEqual(result, "0")

    def test_exact_addition(self):
        result, chars, shortened = exact_coefficient(
            "d", "z+1", "1/2", 1)
        self.assertTrue(result)
        import sympy as sp
        z, d = sp.symbols("z d")
        self.assertEqual(sp.cancel(sp.sympify(result) - d - (z+1)/2), 0)


if __name__ == "__main__":
    unittest.main()
