from qedcalc.operations.ibp import IntegralIndex
from three_loop.expanded_sector_target_rescue import audit_expanded_sector_target_rescue
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family


def test_expanded_sector_profile_handles_small_fixture():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    targets = (
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)),
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 0)),
    )
    profile = audit_expanded_sector_target_rescue(
        family,
        targets,
        templates=templates,
        probe_points=(),
    )
    assert profile.original_target_count == 2
    assert profile.unresolved_target_count >= 0
    assert profile.total_seed_count >= profile.blocker_seed_count
    assert profile.predecessor_seed_count >= 0


def test_expanded_sector_rows_account_for_targets_when_present():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    target = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    profile = audit_expanded_sector_target_rescue(
        family,
        (target,),
        templates=templates,
        probe_points=(),
    )
    assert sum(row.target_count for row in profile.rows) == profile.unresolved_target_count
