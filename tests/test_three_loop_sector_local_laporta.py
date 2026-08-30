import pytest

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.sector_local_laporta import (
    audit_sector_local_laporta,
    largest_blocker_sector,
)


def _blocker_free_fixture():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    targets = (
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)),
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 0)),
    )
    return family, templates, targets


def test_largest_blocker_sector_rejects_blocker_free_fixture():
    family, templates, targets = _blocker_free_fixture()
    with pytest.raises(ValueError, match="No unresolved blocker sectors found"):
        largest_blocker_sector(family, targets, templates=templates)


def test_sector_local_profile_with_explicit_empty_sector_is_consistent():
    family, templates, targets = _blocker_free_fixture()
    sector = (1, 1, 1, 1, 1, 1, 1, 1, 1)
    profile = audit_sector_local_laporta(
        family,
        targets,
        sector=sector,
        templates=templates,
    )
    assert profile.sector == sector
    assert profile.blocker_count == 0
    assert profile.equation_count == 0
    assert profile.rule_count == 0
    assert profile.blocker_count == profile.solved_blocker_count + profile.unsolved_blocker_count
    assert profile.dot_one_blocker_count == profile.solved_dot_one_count + profile.unsolved_dot_one_count
