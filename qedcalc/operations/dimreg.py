from __future__ import annotations

import sympy as sp

from qedcalc.core.expression import QEDExpr, Symbol, PoleTerm, LaurentResult
from qedcalc.operations.scalar_sympy import to_sympy_scalar, from_sympy_scalar
from qedcalc.operations.simplify import simplify_expression


def extract_laurent_poles(expr: QEDExpr, regulator="epsilon", kind="UV", max_order=2):
    """Separate negative Laurent powers of a regulator from a scalar expression.

    This is a scalar-algebra utility.  For UV and IR poles kept separately,
    call it with distinct regulator symbols, for example epsilon_UV and
    epsilon_IR.
    """
    if max_order < 1:
        raise ValueError("max_order must be at least 1.")
    atom_map = {}
    sexpr, reverse = to_sympy_scalar(expr, atom_map)
    reg = atom_map.get(f"S__{regulator}", sp.Symbol(f"S__{regulator}"))
    expanded = sp.expand(sexpr)
    poles = []
    pole_sum = sp.Integer(0)
    for order in range(max_order, 0, -1):
        coeff = sp.simplify(expanded.coeff(reg, -order))
        if coeff != 0:
            qcoeff = simplify_expression(from_sympy_scalar(coeff, reverse))
            poles.append(PoleTerm(kind.upper(), order, qcoeff, regulator))
            pole_sum += coeff * reg**(-order)
    finite_sym = sp.simplify(expanded.coeff(reg, 0))
    finite = simplify_expression(from_sympy_scalar(finite_sym, reverse))
    return LaurentResult(finite, tuple(poles))


def pole_coefficient(result: LaurentResult, kind="UV", order=1):
    """Return the coefficient of a selected pole, or zero when absent."""
    for pole in result.poles:
        if pole.kind.upper() == kind.upper() and pole.order == order:
            return pole.coefficient
    return Symbol("0")


from dataclasses import dataclass


@dataclass(frozen=True)
class UVIRBookkeepingResult:
    """Classified Laurent terms in independent UV and IR regulators."""
    uv_terms: tuple
    ir_terms: tuple
    mixed_terms: tuple
    finite: object
    regular_remainder: object


def bookkeep_uv_ir(expr, uv_regulator="epsilon_UV", ir_regulator="epsilon_IR"):
    """Classify scalar Laurent terms into UV, IR, mixed, finite, and regular pieces.

    ``expr`` may be a QEDExpr or a SymPy expression.  UV and IR regulators are
    treated as independent symbols.  A term with negative powers of both is
    classified as mixed.  Terms with exactly zero powers of both regulators
    form the finite part; positive regulator powers are kept as the regular
    remainder.
    """
    if isinstance(expr, QEDExpr):
        atom_map = {}
        sexpr, reverse = to_sympy_scalar(expr, atom_map)
        uv = atom_map.get(f"S__{uv_regulator}", sp.Symbol(f"S__{uv_regulator}"))
        ir = atom_map.get(f"S__{ir_regulator}", sp.Symbol(f"S__{ir_regulator}"))
    else:
        sexpr = sp.sympify(expr)
        reverse = {}
        uv = sp.Symbol(uv_regulator)
        ir = sp.Symbol(ir_regulator)

    uv_terms = []
    ir_terms = []
    mixed_terms = []
    finite_terms = []
    regular_terms = []

    for term in sp.Add.make_args(sp.expand(sexpr)):
        powers = term.as_powers_dict()
        puv = powers.get(uv, sp.Integer(0))
        pir = powers.get(ir, sp.Integer(0))
        uv_neg = bool(puv.is_number and puv < 0)
        ir_neg = bool(pir.is_number and pir < 0)
        uv_zero = puv == 0
        ir_zero = pir == 0
        if uv_neg and ir_neg:
            mixed_terms.append(term)
        elif uv_neg:
            uv_terms.append(term)
        elif ir_neg:
            ir_terms.append(term)
        elif uv_zero and ir_zero:
            finite_terms.append(term)
        else:
            regular_terms.append(term)

    def pack(items):
        return sp.simplify(sp.Add(*items)) if items else sp.Integer(0)

    return UVIRBookkeepingResult(
        tuple(uv_terms), tuple(ir_terms), tuple(mixed_terms),
        pack(finite_terms), pack(regular_terms)
    )
