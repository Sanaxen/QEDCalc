import sympy as sp

from qedcalc.operations.ibp import IntegralIndex
from three_loop.direct_symbolic_reduction import DirectSymbolicRule
from three_loop.merged_symbolic_closure import audit_merged_symbolic_closure, merge_symbolic_rules


def _rule(target, rhs):
    return DirectSymbolicRule(
        target=target.powers,
        source_label="test",
        target_coefficient=sp.Integer(1),
        rhs=tuple((index.powers, sp.Integer(coeff)) for index, coeff in rhs),
    )


def test_merge_symbolic_rules_combines_nonoverlapping_targets():
    a = IntegralIndex((2, 0))
    b = IntegralIndex((1, 0))
    c = IntegralIndex((0, 0))
    direct = (_rule(a, ((b, 1),)),)
    reverse = (_rule(b, ((c, 1),)),)
    merged = merge_symbolic_rules(direct, reverse)
    assert {rule.target for rule in merged} == {a.powers, b.powers}


def test_merged_closure_extends_through_reverse_rule():
    a = IntegralIndex((2, 0))
    b = IntegralIndex((1, 0))
    direct = (_rule(a, ((b, 1),)),)
    reverse = (_rule(b, ()),)
    profile = audit_merged_symbolic_closure((a, b), direct, reverse)
    assert profile.merged_rule_count == 2
    assert profile.closure.fully_closed_target_count == 2
