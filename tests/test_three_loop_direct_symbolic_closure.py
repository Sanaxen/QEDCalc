import sympy as sp

from qedcalc.operations.ibp import IntegralIndex
from three_loop.direct_symbolic_closure import (
    audit_direct_symbolic_closure,
    direct_rule_dependency_closure,
)
from three_loop.direct_symbolic_reduction import DirectSymbolicRule


def _rule(target, rhs):
    return DirectSymbolicRule(
        target=target.powers,
        source_label="fixture",
        target_coefficient=sp.Integer(1),
        rhs=tuple((index.powers, sp.Integer(1)) for index in rhs),
    )


def test_direct_rule_dependency_closure_follows_transitive_rules():
    a = IntegralIndex((3, 0))
    b = IntegralIndex((2, 0))
    c = IntegralIndex((1, 0))
    d = IntegralIndex((0, 1))
    rules = (_rule(a, (b,)), _rule(b, (c,)), _rule(c, (d,)))
    record = direct_rule_dependency_closure(a, rules)
    assert set(record.pivot_nodes) == {a.powers, b.powers, c.powers}
    assert record.terminal_integrals == (d.powers,)
    assert not record.fully_closed


def test_direct_symbolic_closure_counts_zero_terminated_target():
    a = IntegralIndex((2, 0))
    b = IntegralIndex((1, 0))
    rules = (_rule(a, (b,)), _rule(b, ()))
    profile = audit_direct_symbolic_closure((a, b), rules)
    assert profile.target_count == 2
    assert profile.rule_count == 2
    assert profile.fully_closed_target_count == 2
    assert profile.target_with_unresolved_terminals_count == 0
