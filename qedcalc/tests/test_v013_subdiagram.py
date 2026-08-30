import sympy as sp

from qedcalc.operations.subdiagram import Subdiagram, relation, is_forest, enumerate_forests
from qedcalc.operations.r_operation import (
    CountertermAssignment, assemble_renormalized_amplitude,
    validate_counterterm_coverage, renormalization_plan,
)


def test_subdiagram_relations():
    a = Subdiagram("A", "vertex", 1, {"v1", "e1", "e2"})
    b = Subdiagram("B", "self_energy", 1, {"e3", "v3"})
    c = Subdiagram("C", "larger", 2, {"v1", "e1", "e2", "x"})
    d = Subdiagram("D", "overlap", 1, {"e2", "x", "y"})
    assert relation(a, b) == "disjoint"
    assert relation(a, c) == "nested"
    assert relation(a, d) == "overlapping"
    assert is_forest((a, b, c))
    assert not is_forest((a, d))


def test_enumerate_forests_excludes_overlap_pair():
    a = Subdiagram("A", "vertex", 1, {"1", "2"})
    b = Subdiagram("B", "self_energy", 1, {"2", "3"})
    forests = enumerate_forests((a, b))
    names = [{x.name for x in f} for f in forests]
    assert set() in names
    assert {"A"} in names
    assert {"B"} in names
    assert {"A", "B"} not in names


def test_counterterm_coverage():
    a = Subdiagram("A", "vertex", 1, {"1"})
    b = Subdiagram("B", "self_energy", 1, {"2"})
    aa = CountertermAssignment(a, 1)
    result = validate_counterterm_coverage((a, b), (aa,))
    assert result["missing"] == ("B",)
    assert not result["complete"]


def test_assemble_counterterms_cancels_pole():
    eps = sp.Symbol("epsilon")
    finite = sp.Symbol("F")
    bare = 3/eps + finite
    sub = Subdiagram("V1", "vertex", 1, {"v1", "e1"})
    ct = CountertermAssignment(sub, -3/eps, "vertex CT")
    result = assemble_renormalized_amplitude(bare, (ct,), eps)
    assert sp.simplify(result.pole_part) == 0
    assert sp.simplify(result.finite_or_regular - finite) == 0


def test_plan_contains_forests_and_coverage():
    a = Subdiagram("A", "vertex", 1, {"1"})
    aa = CountertermAssignment(a, -1)
    plan = renormalization_plan((a,), (aa,))
    assert plan["coverage"]["complete"]
    assert len(plan["forests"]) == 2


def test_minimal_counterterm_from_poles():
    from qedcalc.operations.r_operation import minimal_counterterm_from_poles
    eps = sp.Symbol("epsilon")
    A, B = sp.symbols("A B")
    ct = minimal_counterterm_from_poles(A/eps**2 + B/eps + 7, eps)
    assert sp.simplify(ct + A/eps**2 + B/eps) == 0


def test_minimal_r_operation_subdivergence_then_overall():
    from qedcalc.operations.r_operation import minimal_r_operation
    eps = sp.Symbol("epsilon")
    A, C, F = sp.symbols("A C F")
    sub = Subdiagram("sub", "vertex", 1, {"1", "2"})
    # Bare has a subdivergence A/eps and an overall pole C/eps.
    bare = A/eps + C/eps + F
    assignment = CountertermAssignment(sub, -A/eps)
    result = minimal_r_operation(bare, (assignment,), eps)
    assert sp.simplify(result.overall_counterterm + C/eps) == 0
    assert sp.simplify(result.renormalized - F) == 0
    assert result.remaining_pole == 0
