import sympy as sp

from three_loop import (
    apply_finite_q_onshell,
    finite_q_onshell_substitutions,
    finite_q_pq_basis_substitutions,
    rewrite_to_pq_external_basis,
)


def test_finite_q_onshell_relations_preserve_z_dependence():
    m, z = sp.symbols("m z")
    subs = finite_q_onshell_substitutions(mass=m, z=z)
    assert subs[sp.Symbol("SP__p__p")] == m**2
    assert subs[sp.Symbol("SP__p'__p'")] == m**2
    assert sp.simplify(
        subs[sp.Symbol("SP__p__p'")] - m**2 * (1 - z / 2)
    ) == 0
    assert subs[sp.Symbol("SP__p__p'")].has(z)


def test_finite_q_onshell_reduction_removes_only_external_invariants():
    m, z = sp.symbols("m z")
    kp = sp.Symbol("SP__k__p")
    pp = sp.Symbol("SP__p__p")
    ppp = sp.Symbol("SP__p'__p'")
    cross = sp.Symbol("SP__p__p'")
    expr = kp + pp + ppp + cross

    reduced = apply_finite_q_onshell(expr, mass=m, z=z)

    expected = kp + 2 * m**2 + m**2 * (1 - z / 2)
    assert sp.expand(reduced.expression - expected) == 0
    assert reduced.before_scalar_product_atoms == (
        "SP__k__p", "SP__p'__p'", "SP__p__p", "SP__p__p'"
    )
    assert reduced.after_scalar_product_atoms == ("SP__k__p",)
    assert reduced.expression.has(z)


def test_pq_basis_substitutions_are_exact_pprime_equals_p_plus_q():
    subs = finite_q_pq_basis_substitutions()
    assert subs[sp.Symbol("SP__k__p'")] == sp.Symbol("SP__k__p") + sp.Symbol("SP__k__q")
    assert subs[sp.Symbol("SP__l__p'")] == sp.Symbol("SP__l__p") + sp.Symbol("SP__l__q")
    assert subs[sp.Symbol("SP__p'__r")] == sp.Symbol("SP__p__r") + sp.Symbol("SP__q__r")


def test_pq_basis_reduction_removes_pprime_loop_atoms_without_qzero_limit():
    expr = (
        sp.Symbol("SP__k__p'")
        + sp.Symbol("SP__l__p'")
        + sp.Symbol("SP__p'__r")
        + sp.Symbol("SP__k__l")
    )
    reduced = rewrite_to_pq_external_basis(expr)
    expected = (
        sp.Symbol("SP__k__p") + sp.Symbol("SP__k__q")
        + sp.Symbol("SP__l__p") + sp.Symbol("SP__l__q")
        + sp.Symbol("SP__p__r") + sp.Symbol("SP__q__r")
        + sp.Symbol("SP__k__l")
    )
    assert sp.expand(reduced.expression - expected) == 0
    assert not any("p'" in name for name in reduced.after_scalar_product_atoms)
    assert {"SP__k__q", "SP__l__q", "SP__q__r"}.issubset(
        set(reduced.after_scalar_product_atoms)
    )
