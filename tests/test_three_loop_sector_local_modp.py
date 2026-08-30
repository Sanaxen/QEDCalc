import sympy as sp

from three_loop.sector_local_modp import _rational_mod_p


def test_rational_mod_p_matches_exact_fraction():
    prime = 1000003
    value = sp.Rational(7, 11)
    expected = (7 * pow(11, prime - 2, prime)) % prime
    assert _rational_mod_p(value, prime) == expected


def test_rational_mod_p_zero_is_zero():
    assert _rational_mod_p(sp.Integer(0), 1000003) == 0
