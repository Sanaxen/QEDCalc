import sympy as sp

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.sector_local_probe import default_q01_probe_points


def test_default_q01_probe_points_are_two_exact_points():
    family = q01_integral_family()
    points = default_q01_probe_points(family)
    assert len(points) == 2
    assert all(family.dimension_symbol in point for point in points)
    assert all(all(isinstance(value, sp.Expr) for value in point.values()) for point in points)


def test_q01_probe_points_use_distinct_dimension_values():
    family = q01_integral_family()
    points = default_q01_probe_points(family)
    assert points[0][family.dimension_symbol] != points[1][family.dimension_symbol]
