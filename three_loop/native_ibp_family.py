"""Bridge a canonical three-loop Kira FamilySpec into QEDCalc native IBP form."""
from __future__ import annotations

import sympy as sp

from qedcalc.operations.ibp import IntegralFamily, sp_atom
from three_loop.master_basis_api import FamilySpec, build_family_spec

VARS = ("k", "l", "r", "p", "q")
LOOPS = ("k", "l", "r")
EXTERNALS = ("p", "q")


def _parse_linear_momentum(text: str) -> dict[str, sp.Expr]:
    symbols = {name: sp.Symbol(name) for name in VARS}
    expr = sp.expand(sp.sympify(text, locals=symbols))
    out = {}
    for name in VARS:
        coeff = sp.expand(expr).coeff(symbols[name])
        out[name] = sp.simplify(coeff)
    remainder = sp.expand(expr - sum(out[name] * symbols[name] for name in VARS))
    if remainder != 0:
        raise ValueError(f"nonlinear/non-vector remainder in momentum {text!r}: {remainder}")
    return out


def _dot(a: dict[str, sp.Expr], b: dict[str, sp.Expr]) -> sp.Expr:
    m2, z = sp.symbols("m2 z")
    out = sp.Integer(0)
    for i, x in enumerate(VARS):
        for y in VARS[i:]:
            coeff = a.get(x, 0) * b.get(y, 0)
            if x != y:
                coeff += a.get(y, 0) * b.get(x, 0)
            if coeff == 0:
                continue
            if x == y == "p":
                atom = m2
            elif x == y == "q":
                atom = z * m2
            elif {x, y} == {"p", "q"}:
                atom = -z * m2 / 2
            else:
                atom = sp_atom(x, y)
            out += coeff * atom
    return sp.expand(out)


def _square(v: dict[str, sp.Expr]) -> sp.Expr:
    return _dot(v, v)


def _loop_sp_basis() -> tuple[sp.Symbol, ...]:
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


def family_spec_denominator_expressions(spec: FamilySpec) -> tuple[sp.Expr, ...]:
    m2 = sp.Symbol("m2")
    out = []
    for prop in spec.propagators:
        vec = _parse_linear_momentum(prop.momentum)
        mass2 = sp.Integer(0) if str(prop.mass) == "0" else m2
        out.append(sp.expand(_square(vec) - mass2))
    return tuple(out)


def family_spec_scalar_product_rules(
    spec: FamilySpec,
    denominator_exprs: tuple[sp.Expr, ...] | None = None,
) -> dict[sp.Symbol, sp.Expr]:
    exprs = denominator_exprs or family_spec_denominator_expressions(spec)
    ds = sp.symbols("D1:13")
    unknowns = _loop_sp_basis()
    equations = [sp.Eq(d, expr) for d, expr in zip(ds, exprs)]
    solutions = sp.solve(equations, unknowns, dict=True, simplify=False)
    if len(solutions) != 1:
        raise ValueError(
            f"{spec.family_id}: denominator basis did not yield a unique scalar-product solution "
            f"(solutions={len(solutions)})"
        )
    sol = dict(solutions[0])
    missing = [x for x in unknowns if x not in sol]
    if missing:
        raise ValueError(f"{spec.family_id}: scalar-product basis incomplete: {missing}")

    m2, z = sp.symbols("m2 z")
    sol.update({
        sp_atom("p", "p"): m2,
        sp_atom("q", "q"): z * m2,
        sp_atom("p", "q"): -z * m2 / 2,
    })
    return sol


def family_spec_to_native_ibp(spec: FamilySpec) -> IntegralFamily:
    exprs = family_spec_denominator_expressions(spec)
    rules = family_spec_scalar_product_rules(spec, exprs)
    return IntegralFamily(
        name=spec.family_id,
        denominator_names=tuple(f"D{i}" for i in range(1, 13)),
        denominator_exprs=exprs,
        loop_momenta=LOOPS,
        external_momenta=EXTERNALS,
        scalar_product_rules=rules,
        dimension_symbol=sp.Symbol("D"),
    )


def build_native_ibp_family(family_id: str) -> IntegralFamily:
    return family_spec_to_native_ibp(build_family_spec(family_id))
