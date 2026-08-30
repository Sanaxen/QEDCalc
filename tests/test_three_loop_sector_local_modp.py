import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from three_loop.sector_local_modp import _rational_mod_p, _specialize_remaining_symbols_by_name


def test_rational_mod_p_matches_exact_fraction():
    prime = 1000003
    value = sp.Rational(7, 11)
    expected = (7 * pow(11, prime - 2, prime)) % prime
    assert _rational_mod_p(value, prime) == expected


def test_rational_mod_p_zero_is_zero():
    assert _rational_mod_p(sp.Integer(0), 1000003) == 0


def test_name_based_specialization_handles_assumption_distinct_symbols():
    m_coeff = sp.Symbol("m", positive=True)
    z_coeff = sp.Symbol("z", real=True)
    m_probe = sp.Symbol("m")
    z_probe = sp.Symbol("z")
    index = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    equation = IBPEquation({index: 2 * m_coeff**2 * z_coeff - 4 * m_coeff**2}, "probe")
    specialized = _specialize_remaining_symbols_by_name(
        (equation,),
        {m_probe: sp.Integer(1), z_probe: sp.Rational(2, 7)},
    )
    assert specialized[0].terms[index] == sp.Rational(-24, 7)
