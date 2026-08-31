import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from three_loop.modp_pivot_trace import dependency_closure, forward_eliminate_mod_p_with_trace
from three_loop.sector_local_modp import _forward_eliminate_mod_p


def test_modp_pivot_trace_matches_existing_pivot_set():
    a = IntegralIndex((2, 0))
    b = IntegralIndex((1, 0))
    c = IntegralIndex((0, 1))
    equations = (
        IBPEquation({a: sp.Integer(2), b: sp.Integer(1)}, "eq0"),
        IBPEquation({b: sp.Integer(3), c: sp.Integer(1)}, "eq1"),
    )
    prime = 1000003
    rules = _forward_eliminate_mod_p(equations, prime)
    trace = forward_eliminate_mod_p_with_trace(equations, prime)
    assert set(trace.pivot_indices) == set(rules)
    assert trace.pivot_count == len(rules)


def test_dependency_closure_follows_pivot_rhs_graph():
    a = IntegralIndex((2, 0))
    b = IntegralIndex((1, 0))
    c = IntegralIndex((0, 1))
    equations = (
        IBPEquation({a: sp.Integer(1), b: sp.Integer(1)}, "eq0"),
        IBPEquation({b: sp.Integer(1), c: sp.Integer(1)}, "eq1"),
    )
    trace = forward_eliminate_mod_p_with_trace(equations, 1000003)
    closure = dependency_closure(trace, (a,))
    assert a in closure
    assert b in closure
