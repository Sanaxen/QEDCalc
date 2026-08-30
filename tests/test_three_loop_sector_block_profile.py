from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.sector_block_profile import build_sector_block_profiles


def test_sector_block_profiles_are_sorted_and_consistent():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    targets = (
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)),
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 0)),
    )
    profiles = build_sector_block_profiles(
        family,
        targets,
        templates=templates,
    )
    assert all(profile.blocker_count >= profile.dot_one_count for profile in profiles)
    counts = [profile.blocker_count for profile in profiles]
    assert counts == sorted(counts, reverse=True)


def test_sector_block_profiles_have_nine_bit_sector_masks():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    target = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    profiles = build_sector_block_profiles(
        family,
        (target,),
        templates=templates,
    )
    assert all(len(profile.sector) == 9 for profile in profiles)
