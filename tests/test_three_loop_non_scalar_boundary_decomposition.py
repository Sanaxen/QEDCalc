from qedcalc.operations.ibp import IntegralIndex
from three_loop.non_scalar_boundary_decomposition import decompose_non_scalar_boundary


def test_non_scalar_boundary_separates_dot_only_and_numerator_bearing():
    dot_only = IntegralIndex((2,1,1,1,1,1,1,1,1,0,0,0))
    numerator_only = IntegralIndex((1,1,1,1,1,1,1,1,1,-1,0,0))
    dot_and_num = IntegralIndex((2,1,1,1,1,1,1,1,1,0,-1,0))
    profile = decompose_non_scalar_boundary((dot_only, numerator_only, dot_and_num))
    assert profile.terminal_count == 3
    assert profile.numerator_bearing_count == 2
    assert profile.dot_only_count == 1
    assert profile.dot_and_numerator_count == 1
    categories = {record.index: record.category for record in profile.records}
    assert categories[dot_only.powers] == "dot-only"
    assert categories[numerator_only.powers] == "numerator-only"
    assert categories[dot_and_num.powers] == "dot+numerator"
