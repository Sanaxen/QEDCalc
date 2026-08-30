from qedcalc.operations.ibp import IntegralIndex
from three_loop.all_sector_target_rescue import audit_all_sector_target_rescue
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family


def test_all_sector_rescue_handles_blocker_free_fixture():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    targets = (
        IntegralIndex((1,1,1,1,1,1,1,1,1,0,0,0)),
        IntegralIndex((1,1,1,1,1,1,1,1,1,-1,0,0)),
    )
    profile = audit_all_sector_target_rescue(family, targets, templates=templates)
    assert profile.original_target_count == 2
    assert profile.unresolved_target_count == 0
    assert profile.sector_count == 0
    assert profile.solved_target_counts == (0, 0)
    assert profile.unsolved_target_counts == (0, 0)
    assert profile.stable_across_runs


def test_all_sector_rescue_rows_partition_unresolved_targets():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    targets = (
        IntegralIndex((1,1,1,1,1,1,1,1,1,0,0,0)),
        IntegralIndex((1,1,1,1,1,1,1,1,1,-1,0,0)),
    )
    profile = audit_all_sector_target_rescue(family, targets, templates=templates)
    assert sum(row.unresolved_target_count for row in profile.rows) == profile.unresolved_target_count
