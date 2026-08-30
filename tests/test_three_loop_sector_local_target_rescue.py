from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.sector_local_target_rescue import unresolved_targets_after_one_hop


def test_unresolved_targets_after_one_hop_is_subset():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    targets = (
        IntegralIndex((1,1,1,1,1,1,1,1,1,0,0,0)),
        IntegralIndex((1,1,1,1,1,1,1,1,1,-1,0,0)),
    )
    unresolved = unresolved_targets_after_one_hop(family, targets, templates=templates)
    assert set(unresolved) <= set(targets)


def test_unresolved_targets_after_one_hop_is_deduplicated():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    target = IntegralIndex((1,1,1,1,1,1,1,1,1,0,0,0))
    unresolved = unresolved_targets_after_one_hop(family, (target, target), templates=templates)
    assert len(unresolved) <= 1
