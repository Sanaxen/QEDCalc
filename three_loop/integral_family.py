"""Three-loop integral-family construction for the quenched Q01 vertex graph.

The family is written at finite q in the external basis (p,q), with

    p^2 = m^2,
    q^2 = z m^2,
    p.q = -z m^2/2.

Q01 has nine physical propagators.  Three additional auxiliary denominators
(ISPs) complete the 12-dimensional loop scalar-product basis required for IBP.
"""
from __future__ import annotations

import sympy as sp

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex, sp_atom


Q01_PHYSICAL_DENOMINATOR_COUNT = 9
Q01_FAMILY_SIZE = 12
Q01_SEED = IntegralIndex((1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0))


def _q01_loop_scalar_products() -> tuple[sp.Symbol, ...]:
    return (
        sp_atom("k", "k"),
        sp_atom("l", "l"),
        sp_atom("r", "r"),
        sp_atom("k", "l"),
        sp_atom("k", "r"),
        sp_atom("l", "r"),
        sp_atom("k", "p"),
        sp_atom("l", "p"),
        sp_atom("p", "r"),
        sp_atom("k", "q"),
        sp_atom("l", "q"),
        sp_atom("q", "r"),
    )


def q01_denominator_expressions() -> tuple[sp.Expr, ...]:
    """Return the nine physical Q01 denominators plus three ISP auxiliaries.

    The six electron denominators are ``m^2 - X^2`` after scalarizing the
    fermion propagators and applying the finite-q on-shell relations.  The
    three photon denominators retain QEDCalc's ``-k^2`` convention.
    """
    kk = sp_atom("k", "k")
    ll = sp_atom("l", "l")
    rr = sp_atom("r", "r")
    kl = sp_atom("k", "l")
    kr = sp_atom("k", "r")
    lr = sp_atom("l", "r")
    kp = sp_atom("k", "p")
    lp = sp_atom("l", "p")
    pr = sp_atom("p", "r")
    kq = sp_atom("k", "q")
    lq = sp_atom("l", "q")
    qr = sp_atom("q", "r")

    return (
        -kk + 2 * kp + 2 * kq,                  # m^2 - (p+q-k)^2
        -kk + 2 * kp,                           # m^2 - (p-k)^2
        -kk - ll - 2 * kl + 2 * kp + 2 * lp,  # m^2 - (p-k-l)^2
        -ll + 2 * lp,                           # m^2 - (p-l)^2
        -ll - rr - 2 * lr + 2 * lp + 2 * pr,  # m^2 - (p-l-r)^2
        -rr + 2 * pr,                           # m^2 - (p-r)^2
        -kk,                                     # photon k
        -ll,                                     # photon l
        -rr,                                     # photon r
        kr,                                      # ISP 1
        lq,                                      # ISP 2
        qr,                                      # ISP 3
    )


def q01_scalar_product_rules() -> dict[sp.Symbol, sp.Expr]:
    """Solve the complete Q01 scalar-product basis in family variables."""
    denominator_symbols = sp.symbols("D1:13")
    denominator_exprs = q01_denominator_expressions()
    unknowns = _q01_loop_scalar_products()
    equations = [
        sp.Eq(symbol, expr)
        for symbol, expr in zip(denominator_symbols, denominator_exprs)
    ]
    solutions = sp.solve(equations, unknowns, dict=True, simplify=False)
    if len(solutions) != 1 or any(atom not in solutions[0] for atom in unknowns):
        raise ValueError("Q01 denominator/ISP basis does not span all loop scalar products")

    m = sp.Symbol("m")
    z = sp.Symbol("z")
    rules = dict(solutions[0])
    rules.update({
        sp_atom("p", "p"): m**2,
        sp_atom("p", "q"): -z * m**2 / 2,
        sp_atom("q", "q"): z * m**2,
    })
    return rules


def q01_integral_family() -> IntegralFamily:
    """Build the finite-q 12-denominator Q01 family for existing IBP tools."""
    return IntegralFamily(
        name="3loop_Q01_pq",
        denominator_names=tuple(f"D{i}" for i in range(1, Q01_FAMILY_SIZE + 1)),
        denominator_exprs=q01_denominator_expressions(),
        loop_momenta=("k", "l", "r"),
        external_momenta=("p", "q"),
        scalar_product_rules=q01_scalar_product_rules(),
        dimension_symbol=sp.Symbol("D"),
    )


def q01_family_checkpoint() -> dict[str, object]:
    family = q01_integral_family()
    return {
        "name": family.name,
        "size": family.size,
        "physical_denominator_count": Q01_PHYSICAL_DENOMINATOR_COUNT,
        "auxiliary_denominator_count": family.size - Q01_PHYSICAL_DENOMINATOR_COUNT,
        "loop_momenta": family.loop_momenta,
        "external_momenta": family.external_momenta,
        "seed": Q01_SEED.as_tuple(),
        "scalar_product_rule_count": len(family.scalar_product_rules),
    }
