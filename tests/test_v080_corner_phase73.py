import sympy as sp
from qedcalc.operations.corner import corner_phase73_finite_rho_cancellation_wick_audit

def test_phase73_exact_cancellation_and_wick_ownership():
    a=corner_phase73_finite_rho_cancellation_wick_audit()
    assert a['electron_scalar_cancellation_residual'] == 0
    assert a['photon_scalar_cancellation_residual'] == 0
    assert a['D_cancel_euclidean_coefficient'] == 1
    assert a['k2_cancel_euclidean_coefficient'] == -sp.Rational(1,2)
    assert a['k2_mass_residual_euclidean_coefficient'] == -sp.Rational(1,2)
    assert a['rational_regrouping_quotient_residual'] == 0
    assert a['rational_regrouping_remainder_residual'] == 0
    assert a['direct_log_scalar_split_residual'] == 0
    assert a['analytic_matching_constant'] == 0
