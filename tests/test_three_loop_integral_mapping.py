import sympy as sp

from qedcalc.operations.ibp import IntegralIndex
from three_loop import Q01_SEED, q01_scalar_numerator_to_integrals


def test_constant_numerator_maps_to_q01_seed():
    mapped = q01_scalar_numerator_to_integrals(sp.Integer(3))
    assert mapped.terms == {Q01_SEED: sp.Integer(3)}


def test_physical_denominator_numerator_lowers_corresponding_power():
    D1 = sp.Symbol("D1")
    # k^2 = -D7, so this checks the scalar-product -> family route.
    expr = sp.Symbol("SP__k__k")
    mapped = q01_scalar_numerator_to_integrals(expr)
    expected = IntegralIndex((1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0))
    assert mapped.terms == {expected: sp.Integer(-1)}


def test_isp_numerator_becomes_negative_index():
    expr = sp.Symbol("SP__k__r")
    mapped = q01_scalar_numerator_to_integrals(expr)
    expected = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 0))
    assert mapped.terms == {expected: sp.Integer(1)}


def test_linear_combination_aggregates_family_indices():
    expr = 2 * sp.Symbol("SP__k__k") + 3 * sp.Symbol("SP__k__r") + 5
    mapped = q01_scalar_numerator_to_integrals(expr)
    idx_k2 = IntegralIndex((1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0))
    idx_kr = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 0))
    assert mapped.terms[Q01_SEED] == 5
    assert mapped.terms[idx_k2] == -2
    assert mapped.terms[idx_kr] == 3
