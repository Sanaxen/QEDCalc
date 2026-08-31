import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from three_loop.boundary_dot_symbolic_reduction import is_dot_only
from three_loop.direct_symbolic_reduction import solve_equation_for_target


def test_is_dot_only_distinguishes_dots_from_numerators():
    assert is_dot_only(IntegralIndex((2,1,1,1,1,1,1,1,1,0,0,0)))
    assert not is_dot_only(IntegralIndex((1,1,1,1,1,1,1,1,1,-1,0,0)))
    assert not is_dot_only(IntegralIndex((1,1,1,1,1,1,1,1,1,0,0,0)))


def test_solve_equation_for_dot_target_keeps_exact_coefficient():
    target = IntegralIndex((2,0))
    lower = IntegralIndex((1,0))
    equation = IBPEquation({target: sp.Symbol("D"), lower: sp.Integer(2)}, "dot-test")
    rule = solve_equation_for_target(equation, target)
    assert rule.target == target.powers
    assert rule.rhs == ((lower.powers, -sp.Integer(2) / sp.Symbol("D")),)
