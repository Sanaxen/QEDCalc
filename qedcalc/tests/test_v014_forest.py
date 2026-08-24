import sympy as sp

from qedcalc.operations.subdiagram import Subdiagram
from qedcalc.operations.forest import (
    contract_graph, taylor_operator, TaylorSubtractionSpec,
    apply_taylor_spec, bphz_local_counterterm, bphz_subtract, forest_formula,
)


def test_taylor_operator_univariate_degree_2():
    p = sp.Symbol("p")
    expr = sp.exp(p)
    result = taylor_operator(expr, (p,), 2)
    assert sp.simplify(result - (1 + p + p**2/2)) == 0


def test_taylor_operator_multivariate_total_degree():
    p, q = sp.symbols("p q")
    expr = 3 + 2*p + 5*q + 7*p*q + 11*p**2 + 13*q**2 + p**3
    result = taylor_operator(expr, (p, q), 1)
    assert sp.expand(result) == 3 + 2*p + 5*q


def test_taylor_spec_uses_superficial_degree():
    p = sp.Symbol("p")
    sub = Subdiagram("SE1", "self_energy", 1, {"e1", "v1"}, superficial_degree=1)
    spec = TaylorSubtractionSpec(sub, (p,))
    assert apply_taylor_spec(1 + 2*p + 3*p**2, spec) == 1 + 2*p


def test_contract_graph_disjoint_subdiagrams():
    a = Subdiagram("A", "vertex", 1, {"1", "2"})
    b = Subdiagram("B", "self_energy", 1, {"4", "5"})
    cg = contract_graph("G", {"1", "2", "3", "4", "5"}, (a, b))
    assert cg.members == frozenset({"3", "CT[A]", "CT[B]"})
    assert cg.contraction_vertices == ("CT[A]", "CT[B]")


def test_contract_graph_nested_keeps_only_outer_vertex():
    inner = Subdiagram("inner", "vertex", 1, {"1", "2"})
    outer = Subdiagram("outer", "vertex", 2, {"1", "2", "3"})
    cg = contract_graph("G", {"1", "2", "3", "4"}, (inner, outer))
    assert cg.members == frozenset({"4", "CT[outer]"})
    assert cg.contraction_vertices == ("CT[outer]",)


def test_forest_formula_signs_and_sum():
    a = Subdiagram("A", "vertex", 1, {"1"})
    b = Subdiagram("B", "self_energy", 1, {"2"})
    vals = {
        frozenset(): 100,
        frozenset({"A"}): 10,
        frozenset({"B"}): 20,
        frozenset({"A", "B"}): 3,
    }
    def provider(cg):
        key = frozenset(s.name for s in cg.forest)
        return vals[key]
    result = forest_formula("G", {"1", "2", "3"}, (a, b), provider)
    assert result.total == 100 - 10 - 20 + 3
    assert len(result.contributions) == 4


def test_bphz_local_counterterm_and_subtraction():
    p = sp.Symbol("p")
    sub = Subdiagram("V", "vertex", 1, {"1"}, superficial_degree=0)
    spec = TaylorSubtractionSpec(sub, (p,))
    expr = 5 + 7*p + 11*p**2
    assert bphz_local_counterterm(expr, spec) == -5
    assert sp.expand(bphz_subtract(expr, spec)) == 7*p + 11*p**2
