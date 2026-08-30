import sympy as sp
from qedcalc.operations.crossed_ladder import (
    crossed_projective_numerator_px,
    crossed_projective_numerator_px_checks,
)


def test_crossed_px_is_integer_homogeneous_degree8_polynomial():
    c = crossed_projective_numerator_px_checks()
    assert c["term_count"] == 244
    assert c["total_degree"] == 8
    assert c["homogeneous"]
    assert c["integer_real_coefficients"]
    assert c["sample_11111"] == 2048
    assert c["sample_12345"] == 630936


def test_crossed_px_has_graph_reversal_symmetry():
    c = crossed_projective_numerator_px_checks()
    assert c["reversal_difference"] == 0


def test_crossed_px_apparent_rank4_uv_pole_cancels():
    c = crossed_projective_numerator_px_checks()
    assert c["apparent_gamma0_coefficient"] == 0


def test_crossed_px_projective_reduction_has_expected_v_decay():
    c = crossed_projective_numerator_px_checks()
    assert c["projective_term_count"] == 227
    assert c["projective_v_degree"] == 4
    assert c["v_log_coefficient_zero_by_degree"]


def test_crossed_px_common_laurent_support_is_delta4_w2_compatible():
    r = crossed_projective_numerator_px()
    keys = {key for key, _ in r.laurent_coefficients}
    assert min(p for p, q in keys) == -4
    assert min(q for p, q in keys) == -2
    # The only would-be W^0 term is the rank-4 Gamma(0) sector and cancels.
    nonzero = [(key, sp.expand(value)) for key, value in r.laurent_coefficients]
    for (p, q), value in nonzero:
        if q == 0:
            assert sp.expand(value).subs(sp.Symbol("GAMMA_0"), 1) == 0

from qedcalc.operations.crossed_ladder import crossed_v_partial_fraction_checks


def test_crossed_v_partial_fraction_bridge_and_log_cancellation():
    c = crossed_v_partial_fraction_checks()
    assert c["sample_differences"] == (0,0,0)
    assert c["log_coefficient"] == 0
    assert c["h_log_argument_difference"] == 0
