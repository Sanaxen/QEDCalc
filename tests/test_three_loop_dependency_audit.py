import sympy as sp

from qedcalc.operations.ibp import IntegralIndex, sector_rank
from three_loop import q01_integral_family
from three_loop.dependency_audit import (
    ibp_equation_from_templates,
    target_direct_pivot_equations,
    audit_target_direct_pivots,
)
from three_loop.ibp_frontier import build_ibp_derivative_templates


def test_template_ibp_equation_contains_seed_for_matching_divergence():
    family = q01_integral_family()
    seed = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    templates = build_ibp_derivative_templates(family)
    group = tuple(t for t in templates if t.loop == "k" and t.vector == "k")
    eq = ibp_equation_from_templates(family, seed, "k", "k", group)
    assert seed in eq.terms
    assert eq.terms[seed].has(sp.Symbol("D"))


def test_direct_pivot_equations_really_pivot_on_target():
    family = q01_integral_family()
    seed = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))
    templates = build_ibp_derivative_templates(family)
    equations = target_direct_pivot_equations(family, seed, templates=templates)
    for eq in equations:
        assert max(eq.terms, key=sector_rank) == seed


def test_audit_counts_targets_consistently():
    family = q01_integral_family()
    targets = (
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)),
        IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 0, 0)),
    )
    audit = audit_target_direct_pivots(family, targets)
    assert audit.target_count == 2
    assert audit.equation_count == 30
    assert audit.directly_pivotable_target_count + audit.nonpivotable_target_count == 2
    assert audit.direct_pivot_equation_count >= audit.directly_pivotable_target_count
