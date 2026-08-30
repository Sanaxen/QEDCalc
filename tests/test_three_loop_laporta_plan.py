from qedcalc.operations.ibp import IntegralIndex
from three_loop.laporta_plan import (
    physical_sector,
    dot_degree,
    numerator_degree,
    total_complexity,
    build_sector_demand_profiles,
)


def test_integral_complexity_measures():
    idx = IntegralIndex((2, 1, 0, 1, 1, 1, 1, 1, 1, -2, 0, -1))
    assert physical_sector(idx) == (1, 1, 0, 1, 1, 1, 1, 1, 1)
    assert dot_degree(idx) == 1
    assert numerator_degree(idx) == 3
    assert total_complexity(idx) == 4


def test_sector_demand_profiles_group_and_bound_targets():
    indices = [
        IntegralIndex((1,1,1,1,1,1,1,1,1,0,0,0)),
        IntegralIndex((2,1,1,1,1,1,1,1,1,-1,0,0)),
        IntegralIndex((1,1,0,1,1,1,1,1,1,0,-2,0)),
    ]
    profiles = build_sector_demand_profiles(indices)
    assert len(profiles) == 2
    full = next(p for p in profiles if p.sector == (1,1,1,1,1,1,1,1,1))
    assert full.target_count == 2
    assert full.max_dot_degree == 1
    assert full.max_numerator_degree == 1
    assert full.max_total_complexity == 2
    assert full.min_powers[9] == -1
    assert full.max_powers[0] == 2
