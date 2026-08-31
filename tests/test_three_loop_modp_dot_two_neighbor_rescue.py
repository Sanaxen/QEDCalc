import pytest

from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.modp_dot_two_neighbor_rescue import dot_focused_two_neighbor_seeds


def test_dot_focused_two_neighbor_keeps_targets_and_zero_numerator_seeds():
    family = q01_integral_family()
    target = IntegralIndex((1, 0, 1, 0, 1, 2, 0, 0, 0, 0, 0, 0))
    layer1, all_seeds = dot_focused_two_neighbor_seeds(family, (target,))
    assert target in layer1
    assert target in all_seeds
    assert set(layer1).issubset(set(all_seeds))


def test_dot_focused_two_neighbor_rejects_numerator_target():
    family = q01_integral_family()
    target = IntegralIndex((1, 0, 1, 0, 1, 1, 0, 0, 0, -1, 0, 0))
    with pytest.raises(ValueError, match="numerator-free"):
        dot_focused_two_neighbor_seeds(family, (target,))
