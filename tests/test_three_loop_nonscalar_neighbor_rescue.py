from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.nonscalar_neighbor_rescue import focused_neighbor_seeds


def test_focused_neighbor_seeds_include_targets():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    target = IntegralIndex((1, 1, 1, 0, 1, 1, 0, -1, 1, 0, 0, 0))
    seeds = focused_neighbor_seeds(family, (target,), templates=templates)
    assert target in seeds


def test_focused_neighbor_seeds_allow_at_most_one_active_line_change():
    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    target = IntegralIndex((1, 1, 1, 0, 1, 1, 0, -1, 1, 0, 0, 0))
    seeds = focused_neighbor_seeds(family, (target,), templates=templates)
    target_active = sum(1 for p in target.powers[:9] if p > 0)
    assert all(abs(sum(1 for p in seed.powers[:9] if p > 0) - target_active) <= 1 for seed in seeds)
