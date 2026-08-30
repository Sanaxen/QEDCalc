from __future__ import annotations

from fractions import Fraction as PyFraction
import sympy as sp

from qedcalc.core.expression import (
    QEDExpr, Symbol, Vector, ScalarProduct, Add, Product, NCProduct, ScalarMul, Power
)
from qedcalc.operations.simplify import simplify_expression


class ScalarSympyBridgeError(ValueError):
    pass


def _is_int_text(s: str) -> bool:
    return s.lstrip('-').isdigit()


def to_sympy_scalar(expr: QEDExpr, atom_map=None):
    """Convert a commutative scalar QEDExpr to SymPy.

    Scalar products are represented as atomic SymPy symbols.  Non-commutative
    QED objects are deliberately rejected.
    """
    atom_map = {} if atom_map is None else atom_map
    reverse = {}

    def atom_for(e: QEDExpr, key: str):
        if key not in atom_map:
            atom_map[key] = sp.Symbol(key)
        reverse[atom_map[key]] = e
        return atom_map[key]

    def rec(e):
        if isinstance(e, Symbol):
            if _is_int_text(e.name):
                return sp.Integer(int(e.name))
            return atom_for(e, f"S__{e.name}")
        if isinstance(e, ScalarProduct):
            if not isinstance(e.left, Vector) or not isinstance(e.right, Vector):
                raise ScalarSympyBridgeError("Only vector-vector scalar products are supported by the scalar SymPy bridge.")
            a, b = sorted((e.left.name, e.right.name))
            canonical = ScalarProduct(Vector(a), Vector(b))
            return atom_for(canonical, f"SP__{a}__{b}")
        if isinstance(e, ScalarMul):
            c = e.coeff
            if isinstance(c, float):
                c = sp.Rational(str(c))
            else:
                c = sp.sympify(c)
            return c * rec(e.expr)
        if isinstance(e, (Product, NCProduct)):
            out = sp.Integer(1)
            for f in e.factors:
                out *= rec(f)
            return out
        if isinstance(e, Add):
            return sp.Add(*(rec(t) for t in e.terms))
        if isinstance(e, Power):
            return rec(e.base) ** e.exponent
        raise ScalarSympyBridgeError(
            f"Unsupported non-scalar structure for SymPy conversion: {type(e).__name__}"
        )

    return rec(expr), reverse


def from_sympy_scalar(expr, reverse_atoms):
    """Convert a SymPy scalar expression back to QEDExpr."""
    if expr in reverse_atoms:
        return reverse_atoms[expr]
    if expr.is_Integer:
        return Symbol(str(int(expr)))
    if expr.is_Rational and not expr.is_Integer:
        # Keep exact rational coefficients as SymPy Rational in ScalarMul.
        return ScalarMul(expr, Symbol("1"))
    if expr.is_Symbol:
        name = str(expr)
        if name.startswith("S__"):
            return Symbol(name[3:])
        raise ScalarSympyBridgeError(f"Unknown SymPy atom while converting back: {name}")
    if expr.is_Add:
        return simplify_expression(Add(*(from_sympy_scalar(a, reverse_atoms) for a in expr.args)))
    if expr.is_Mul:
        coeff, rest = expr.as_coeff_Mul()
        factors = []
        if rest != 1:
            raw = rest.args if rest.is_Mul else (rest,)
            factors = [from_sympy_scalar(a, reverse_atoms) for a in raw]
        base = Symbol("1") if not factors else (factors[0] if len(factors) == 1 else Product(*factors))
        if coeff == 1:
            return simplify_expression(base)
        return simplify_expression(ScalarMul(coeff, base))
    if expr.is_Pow:
        base, exp = expr.args
        if not exp.is_Integer:
            raise ScalarSympyBridgeError("Only integer powers are supported when converting from SymPy.")
        return Power(from_sympy_scalar(base, reverse_atoms), int(exp))
    raise ScalarSympyBridgeError(f"Unsupported SymPy expression: {expr}")


def simplify_scalar_with_sympy(expr: QEDExpr, mode: str = "simplify") -> QEDExpr:
    """Simplify/factor/expand a commutative scalar expression through SymPy.

    mode: 'simplify', 'factor', or 'expand'.
    """
    sexpr, reverse = to_sympy_scalar(expr)
    if mode == "simplify":
        result = sp.simplify(sexpr)
    elif mode == "factor":
        result = sp.factor(sexpr)
    elif mode == "expand":
        result = sp.expand(sexpr)
    else:
        raise ValueError("mode must be 'simplify', 'factor', or 'expand'.")
    return simplify_expression(from_sympy_scalar(result, reverse))


def factor_scalar_polynomial(expr: QEDExpr) -> QEDExpr:
    return simplify_scalar_with_sympy(expr, "factor")
