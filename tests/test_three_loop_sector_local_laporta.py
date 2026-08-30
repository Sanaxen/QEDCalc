from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.sector_local_laporta import (
    audit_sector_local_laporta,
    largest_blocker_sector,
)


def test_largest_blocker_sector_returns_nine_bit_sector():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    targets = (
        IntegralIndex((1,1,1,1,1,1,1,1,1,0,0,0)),
        IntegralIndex((1,1,1,1,1,1,1,1,1,-1,0,0)),
    )
    sector = largest_blocker_sector(family, targets, templates=templates)
    assert len(sector) == 9
    assert set(sector) <= {0, 1}


def test_sector_local_profile_is_consistent():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    targets = (
        IntegralIndex((1,1,1,1,1,1,1,1,1,0,0,0)),
        IntegralIndex((1,1,1,1,1,1,1,1,1,-1,0,0)),
    )
    profile = audit_sector_local_laporta(family, targets, templates=templates)
    assert profile.blocker_count == profile.solved_blocker_count + profile.unsolved_blocker_count
    assert profile.dot_one_blocker_count == profile.solved_dot_one_count + profile.unsolved_dot_one_count
    assert profile.equation_count == 15 * profile.blocker_count
