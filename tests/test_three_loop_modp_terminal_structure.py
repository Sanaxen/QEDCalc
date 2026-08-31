from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.modp_terminal_structure import classify_modp_terminal_structure


def test_modp_terminal_structure_separates_same_and_lower_sector():
    family = q01_integral_family()
    source_sector = (1, 0, 1, 0, 1, 1, 1, 1, 1)
    same = IntegralIndex((1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0))
    lower = IntegralIndex((1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0))
    profile = classify_modp_terminal_structure(
        family, (same, lower), source_sector=source_sector
    )
    assert profile.terminal_count == 2
    assert profile.same_sector_count == 1
    assert profile.lower_sector_count == 1
    assert profile.scalar_count == 2
