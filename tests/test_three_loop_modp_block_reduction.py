from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from three_loop.modp_block_reduction import reduce_block_mod_p


def test_block_reduction_solves_selected_integrals_in_terms_of_outside_columns():
    x = IntegralIndex((1,))
    y = IntegralIndex((2,))
    a = IntegralIndex((3,))
    b = IntegralIndex((4,))
    equations = (
        IBPEquation({x: 1, y: 1, a: 2}),
        IBPEquation({x: 2, y: 3, b: 5}),
    )
    prime = 1000003
    reduction = reduce_block_mod_p(equations, (x, y), prime)

    assert reduction.block_size == 2
    assert reduction.selected_row_count == 2
    assert tuple(rule.target for rule in reduction.rules) == (x.powers, y.powers)

    rule_x = dict(reduction.rules[0].rhs)
    rule_y = dict(reduction.rules[1].rhs)
    # Solve exactly: x + y = -2a, 2x + 3y = -5b
    # hence y = 4a - 5b and x = -6a + 5b.
    assert rule_x[a.powers] == (-6) % prime
    assert rule_x[b.powers] == 5 % prime
    assert rule_y[a.powers] == 4 % prime
    assert rule_y[b.powers] == (-5) % prime
