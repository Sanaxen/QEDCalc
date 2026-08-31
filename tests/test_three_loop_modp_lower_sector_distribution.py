from qedcalc.operations.ibp import IntegralIndex
from three_loop.modp_lower_sector_distribution import profile_lower_sector_distribution


def test_lower_sector_distribution_groups_and_skips_source_sector():
    source = (1, 1, 0)
    same = IntegralIndex((1, 1, 0, 0))
    a = IntegralIndex((1, 0, 0, 0))
    b = IntegralIndex((1, 0, 0, -1))
    c = IntegralIndex((0, 1, 0, 0))
    profile = profile_lower_sector_distribution(
        (same, a, b, c),
        source_sector=source,
        physical_count=3,
    )
    assert profile.lower_terminal_count == 3
    assert profile.lower_sector_count == 2
    assert profile.largest_sector_terminal_count == 2
    assert profile.rows[0].sector == (1, 0, 0)
    assert profile.rows[0].terminal_count == 2
