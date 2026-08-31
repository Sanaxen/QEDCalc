import sympy as sp

from qedcalc.operations.ibp import IntegralIndex
from three_loop.direct_symbolic_reduction import DirectSymbolicRule
from three_loop.extended_symbolic_closure import audit_extended_symbolic_closure


def rule(target, rhs):
    return DirectSymbolicRule(
        target=target,
        source_label="test",
        target_coefficient=sp.Integer(1),
        rhs=tuple((powers, sp.Integer(1)) for powers in rhs),
    )


def test_extended_symbolic_closure_uses_dot_boundary_rules_transitively():
    a = IntegralIndex((2, 0))
    b = IntegralIndex((1, 0))
    c = IntegralIndex((0, 1))
    direct = (rule(a.powers, (b.powers,)),)
    reverse = ()
    dot = (rule(b.powers, ()),)
    profile = audit_extended_symbolic_closure((a, c), direct, reverse, dot)
    assert profile.merged_rule_count == 2
    by_target = {record.target: record for record in profile.closure.records}
    assert by_target[a.powers].fully_closed
    assert by_target[c.powers].terminal_integrals == (c.powers,)
