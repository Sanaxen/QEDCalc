import sympy as sp

from qedcalc.operations.crossed_ladder import (
    crossed_standard_integrals_derived,
    crossed_half_sector_result,
    crossed_endpoint_canonical_integral_derived,
    crossed_endpoint_asymptotics_derived,
    crossed_endpoint_total_result,
    crossed_final_result,
    crossed_expected_result,
    crossed_independent_analytic_checks,
)


def test_half_standard_integrals_are_derived_from_sums():
    d = crossed_standard_integrals_derived()
    assert sp.simplify(d.A + sp.Rational(7,4)*sp.zeta(3)) == 0
    assert sp.simplify(d.B - sp.pi**2/8) == 0
    assert sp.simplify(d.C + sp.Rational(7,16)*sp.zeta(3) - sp.pi**2*sp.log(2)/8) == 0


def test_half_sector_is_assembled_from_derived_integrals():
    expected = sp.pi**2 - sp.Rational(5,6)*sp.pi**2*sp.log(2) - sp.Rational(35,12)*sp.zeta(3)
    assert sp.simplify(crossed_half_sector_result() - expected) == 0


def test_endpoint_canonical_finite_is_derived_from_kernel_basis():
    r = crossed_endpoint_canonical_integral_derived()
    expected = sp.Rational(25,6)*sp.zeta(3) - sp.Rational(19,36)*sp.pi**2
    assert sp.simplify(r.finite - expected) == 0


def test_endpoint_boundary_is_regenerated_from_automatic_G():
    a = crossed_endpoint_asymptotics_derived()
    assert sp.simplify(a.finite_boundary - (sp.Rational(1,6)-sp.pi**2/9)) == 0
    assert sp.simplify(a.divergent_sum) == 0


def test_independent_final_assembly_matches_only_at_checkpoint():
    expected_endpoint = sp.Rational(1,6) - sp.Rational(23,36)*sp.pi**2 + sp.Rational(25,6)*sp.zeta(3)
    assert sp.simplify(crossed_endpoint_total_result() - expected_endpoint) == 0
    assert sp.simplify(crossed_final_result() - crossed_expected_result()) == 0
    assert crossed_independent_analytic_checks()["checkpoint_difference"] == 0
