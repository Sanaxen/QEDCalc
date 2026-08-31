import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from three_loop.boundary_layer_pivot_audit import audit_boundary_layer_direct_pivots


class DummyFamily:
    def validate_index(self, index):
        return index


def test_boundary_layer_profile_groups_categories(monkeypatch):
    a = IntegralIndex((2, 0))
    b = IntegralIndex((1, -1))
    c = IntegralIndex((1, 0))

    def fake_direct(_family, target, templates=None):
        if target in (a, b):
            return (IBPEquation({target: sp.Integer(1)}, "eq"),)
        return ()

    monkeypatch.setattr(
        "three_loop.boundary_layer_pivot_audit.target_direct_pivot_equations",
        fake_direct,
    )
    profile = audit_boundary_layer_direct_pivots(
        DummyFamily(),
        {"dot-only": (a, c), "numerator-only": (b,)},
        templates=(),
    )
    rows = {row.category: row for row in profile.rows}
    assert profile.target_count == 3
    assert profile.directly_pivotable_count == 2
    assert rows["dot-only"].target_count == 2
    assert rows["dot-only"].directly_pivotable_count == 1
    assert rows["numerator-only"].directly_pivotable_count == 1
