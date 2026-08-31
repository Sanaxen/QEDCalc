import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from three_loop.direct_symbolic_reduction import solve_equation_for_target


def test_solve_equation_for_target_keeps_exact_symbolic_coefficients():
    D = sp.Symbol("D")
    a = IntegralIndex((2, 0))
    b = IntegralIndex((1, 0))
    equation = IBPEquation({a: D - 2, b: sp.Integer(3)}, "fixture")
    rule = solve_equation_for_target(equation, a)
    assert rule.target == a.powers
    assert rule.source_label == "fixture"
    assert rule.target_coefficient == D - 2
    assert rule.rhs == ((b.powers, -sp.Integer(3) / (D - 2)),)


def test_solve_equation_for_target_rejects_nonpivot_target():
    a = IntegralIndex((2, 0))
    b = IntegralIndex((1, 0))
    equation = IBPEquation({a: sp.Integer(1), b: sp.Integer(1)}, "fixture")
    try:
        solve_equation_for_target(equation, b)
    except ValueError as exc:
        assert "highest-ranked" in str(exc)
    else:
        raise AssertionError("expected ValueError")
