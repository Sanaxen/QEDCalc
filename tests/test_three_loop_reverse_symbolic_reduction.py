import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from three_loop.direct_symbolic_reduction import solve_equation_for_target


def test_solve_equation_for_target_keeps_exact_symbolic_coefficient():
    a = IntegralIndex((2, 0))
    b = IntegralIndex((1, 0))
    D = sp.Symbol("D")
    eq = IBPEquation({a: D - 4, b: sp.Integer(2)}, "fixture")
    rule = solve_equation_for_target(eq, a)
    assert rule.target == a.powers
    assert rule.rhs == ((b.powers, sp.cancel(-2 / (D - 4))),)
