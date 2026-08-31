import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from three_loop.modp_pivot_trace import forward_eliminate_mod_p_with_trace
from three_loop.modp_terminal_support import (
    profile_terminal_support_mod_p,
    reduce_pivot_to_terminals_mod_p,
)


def test_modp_terminal_support_back_substitutes_to_nonpivots():
    a = IntegralIndex((2, 0))
    b = IntegralIndex((1, 0))
    c = IntegralIndex((0, 0))
    equations = (
        IBPEquation({a: sp.Integer(1), b: sp.Integer(-2)}, "eq0"),
        IBPEquation({b: sp.Integer(1), c: sp.Integer(-3)}, "eq1"),
    )
    trace = forward_eliminate_mod_p_with_trace(equations, 1000003)
    reduction = reduce_pivot_to_terminals_mod_p(trace, a)
    assert set(reduction) == {c}
    assert reduction[c] == 6


def test_modp_terminal_support_profile_counts_shared_support():
    a = IntegralIndex((3, 0))
    b = IntegralIndex((2, 0))
    c = IntegralIndex((1, 0))
    t = IntegralIndex((0, 0))
    equations = (
        IBPEquation({a: sp.Integer(1), b: sp.Integer(-1)}, "eq0"),
        IBPEquation({b: sp.Integer(1), t: sp.Integer(-1)}, "eq1"),
        IBPEquation({c: sp.Integer(1), t: sp.Integer(-2)}, "eq2"),
    )
    trace = forward_eliminate_mod_p_with_trace(equations, 1000003)
    profile = profile_terminal_support_mod_p(trace, (a, c))
    assert profile.solved_target_count == 2
    assert profile.distinct_terminal_count == 1
    assert profile.common_terminal_count == 1
    assert profile.min_terminal_count == 1
    assert profile.max_terminal_count == 1
