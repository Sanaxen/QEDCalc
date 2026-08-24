from qedcalc.operations.ibp import (
    IntegralIndex, factorized_one_denominator_per_loop,
    has_free_scaleless_loop_direction, is_scaleless_zero_sector_extended,
)
from qedcalc.operations.ladder import ordinary_ladder_ibp_family


def test_free_loop_sector_is_zero():
    fam = ordinary_ladder_ibp_family()
    # Only E4 is present in a two-loop family: the second loop is a free,
    # scaleless integration direction.
    idx = IntegralIndex((0,0,0,0,0,0,2))
    assert has_free_scaleless_loop_direction(fam, idx)
    assert is_scaleless_zero_sector_extended(fam, idx)


def test_e3_e4_lower_sector_factorizes_unimodularly():
    fam = ordinary_ladder_ibp_family()
    idx = IntegralIndex((0,0,0,0,0,1,1))
    fac = factorized_one_denominator_per_loop(fam, idx)
    assert fac is not None
    assert fac.denominator_names == ('E3', 'E4')
    assert fac.unimodular


def test_e2_e4_lower_sector_factorizes_unimodularly():
    fam = ordinary_ladder_ibp_family()
    idx = IntegralIndex((0,0,0,0,1,0,1))
    fac = factorized_one_denominator_per_loop(fam, idx)
    assert fac is not None
    assert fac.denominator_names == ('E2', 'E4')
    assert fac.unimodular
