import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from three_loop.modp_pivot_trace import (
    dependency_closure,
    forward_eliminate_mod_p_with_trace,
    replay_dependency_closure,
)
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
    # Use a strictly lower-rank terminal integral so b is guaranteed to be
    # the second pivot under sector_rank.  With c=(0,1), c outranks b by
    # sector id and the second equation would pivot c instead.
    c = IntegralIndex((0, 0))
    equations = (
        IBPEquation({a: sp.Integer(1), b: sp.Integer(1)}, "eq0"),
        IBPEquation({b: sp.Integer(1), c: sp.Integer(1)}, "eq1"),
    )
    trace = forward_eliminate_mod_p_with_trace(equations, 1000003)
    closure = dependency_closure(trace, (a,))
    assert a in closure
    assert b in closure


def test_replay_dependency_closure_includes_eliminated_prior_pivots():
    a = IntegralIndex((3, 0))
    b = IntegralIndex((2, 0))
    c = IntegralIndex((1, 0))
    d = IntegralIndex((0, 0))
    equations = (
        # First establish a pivot rule for a.
        IBPEquation({a: sp.Integer(1), c: sp.Integer(1)}, "eq0"),
        # The second row initially contains a.  Forward elimination substitutes
        # the a rule before choosing b as the final pivot, so a disappears from
        # b's normalized RHS but remains essential provenance for exact replay.
        IBPEquation({a: sp.Integer(1), b: sp.Integer(1), d: sp.Integer(1)}, "eq1"),
    )
    trace = forward_eliminate_mod_p_with_trace(equations, 1000003)

    by_pivot = {record.pivot: record for record in trace.records}
    assert a.powers in by_pivot
    assert b.powers in by_pivot
    assert a.powers in by_pivot[b.powers].eliminated_prior_pivots

    final_rhs_closure = dependency_closure(trace, (b,))
    replay_closure = replay_dependency_closure(trace, (b,))

    assert b in final_rhs_closure
    assert a not in final_rhs_closure
    assert b in replay_closure
    assert a in replay_closure
