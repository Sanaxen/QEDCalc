"""Regression tests for exact rational specialization into finite fields.

Run from QEDCalc root:
    python -m unittest examples.test_three_loop_vp05_sector202_modular
No local Kira database or saved project is required.
"""
from __future__ import annotations
import unittest
import sympy as sp
from examples.three_loop_vp05_sector202_target_exact_reduction import modular

class ModularSpecializationTests(unittest.TestCase):
    def setUp(self):
        self.z,self.d=sp.symbols("z d")
        self.point=(1000003,17,7)
        self.p=self.point[0]

    def test_negative_half_polynomial_pivot93(self):
        expression=-sp.Rational(1,2)*(self.z+2)
        expected=(-19*pow(2,-1,self.p))%self.p
        self.assertEqual(expected,499992)
        self.assertEqual(modular(expression,self.z,self.d,self.point),expected)
        self.assertEqual(modular(sp.cancel(expression),self.z,self.d,self.point),expected)

    def test_pivot93_four_columns(self):
        cases=[("z+2",499992),("-3*z+4",500025),
               ("-z-2",500011)]
        for raw,expected in cases:
            with self.subTest(raw=raw):
                expr=sp.Rational(-1,2)*sp.sympify(raw,locals={"z":self.z})
                self.assertEqual(modular(expr,self.z,self.d,self.point),expected)

    def test_addition_and_multiplication_homomorphism(self):
        a=sp.Rational(-1,2)
        b=self.z+2
        x=(self.d+1)/(self.z-3)
        self.assertEqual(
            modular(a*b,self.z,self.d,self.point),
            modular(a,self.z,self.d,self.point)*
            modular(b,self.z,self.d,self.point)%self.p)
        self.assertEqual(
            modular(x+a*b,self.z,self.d,self.point),
            (modular(x,self.z,self.d,self.point)+
             modular(a*b,self.z,self.d,self.point))%self.p)

    def test_negative_rationals_never_truncated(self):
        cases=[sp.Rational(-19,2),sp.Rational(19,2),
               sp.Rational(1,3),sp.Rational(-7,6)]
        for q in cases:
            with self.subTest(q=q):
                expected=int(q.p)%self.p*pow(int(q.q)%self.p,-1,self.p)%self.p
                self.assertEqual(modular(q,self.z,self.d,self.point),expected)

    def test_singular_denominator_raises(self):
        expr=1/(self.z-17)
        with self.assertRaises(ZeroDivisionError):
            modular(expr,self.z,self.d,self.point)
        expr=1/(self.z-17+self.p)
        with self.assertRaises(ZeroDivisionError):
            modular(expr,self.z,self.d,self.point)

if __name__=="__main__":
    unittest.main()
