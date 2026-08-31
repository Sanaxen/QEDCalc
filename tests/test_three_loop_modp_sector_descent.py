import sympy as sp

from qedcalc.operations.ibp import IntegralIndex
from three_loop.integral_family import q01_integral_family
from three_loop.modp_sector_descent import audit_modp_sector_descent
from three_loop.sector_local_probe import default_q01_probe_points


def test_sector_descent_rejects_mixed_physical_sectors():
    family = q01_integral_family()
    a = IntegralIndex((1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0))
    b = IntegralIndex((1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0))
    point = default_q01_probe_points(family)[0]
    try:
        audit_modp_sector_descent(family, (a, b), probe_point=point)
    except ValueError as exc:
        assert "multiple sectors" in str(exc)
    else:
        raise AssertionError("mixed sectors must be rejected")


def test_sector_descent_requires_targets():
    family = q01_integral_family()
    point = default_q01_probe_points(family)[0]
    try:
        audit_modp_sector_descent(family, (), probe_point=point)
    except ValueError as exc:
        assert "at least one target" in str(exc)
    else:
        raise AssertionError("empty target set must be rejected")
