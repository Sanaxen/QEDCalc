import sympy as sp

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex
from three_loop.pivot_blockers import audit_pivot_blockers, blocker_indices_for_target
from three_loop.ibp_frontier import build_ibp_derivative_templates


def _toy_family():
    D1 = sp.Symbol("D1")
    return IntegralFamily(
        name="toy",
        denominator_names=("D1",),
        denominator_exprs=(sp.Symbol("SP__k__k"),),
        loop_momenta=("k",),
        external_momenta=(),
        scalar_product_rules={sp.Symbol("SP__k__k"): D1},
    )


def test_blocker_indices_returns_tuple():
    family = _toy_family()
    templates = build_ibp_derivative_templates(family)
    blockers = blocker_indices_for_target(
        family, IntegralIndex((1,)), templates=templates
    )
    assert isinstance(blockers, tuple)


def test_blocker_audit_is_deterministic():
    family = _toy_family()
    templates = build_ibp_derivative_templates(family)
    targets = [IntegralIndex((1,)), IntegralIndex((2,))]
    a = audit_pivot_blockers(family, targets, templates=templates, physical_count=1)
    b = audit_pivot_blockers(family, targets, templates=templates, physical_count=1)
    assert a == b
