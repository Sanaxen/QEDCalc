"""Translate Kira ``kira2form`` scalar coefficients into SymPy expressions.

The structural FORM parser deliberately preserves coefficient source text.
This module performs the next import stage for the scalar syntax emitted by
Kira 3.1 in the Q01 reduction table.  The original FORM string should still be
kept alongside the translated expression by callers for traceability.
"""
from __future__ import annotations

import re

import sympy as sp


_ALLOWED_NAME_RE = re.compile(r"[A-Za-z_]\w*")


def _num(value: sp.Expr) -> sp.Expr:
    """Kira/FORM ``num(x)`` denotes the numerator factor x."""
    return value


def _den(value: sp.Expr) -> sp.Expr:
    """Kira/FORM ``den(x)`` denotes the reciprocal denominator factor 1/x."""
    return sp.Integer(1) / value


def form_coefficient_to_sympy(
    source: str,
    *,
    symbols: dict[str, sp.Symbol] | None = None,
) -> sp.Expr:
    """Convert one scalar Kira FORM coefficient to a SymPy expression.

    Supported constructs are the exact scalar constructs observed in the
    Q01 Kira 3.1 FORM export: integer/rational arithmetic, parentheses,
    powers written with ``^``, and Kira's ``num(...)`` / ``den(...)`` wrappers.
    Unknown identifiers are rejected instead of being silently converted into
    arbitrary SymPy functions.
    """
    text = source.strip()
    if not text:
        raise ValueError("empty FORM coefficient")

    local_symbols = dict(symbols or {})
    local_symbols.setdefault("d", sp.Symbol("d"))
    local_symbols.setdefault("z", sp.Symbol("z"))

    names = set(_ALLOWED_NAME_RE.findall(text))
    allowed_names = set(local_symbols) | {"num", "den"}
    unknown = sorted(names - allowed_names)
    if unknown:
        raise ValueError(f"unsupported FORM coefficient identifiers: {unknown}")

    python_text = text.replace("^", "**")
    locals_map: dict[str, object] = {
        **local_symbols,
        "num": _num,
        "den": _den,
    }
    try:
        expr = sp.sympify(python_text, locals=locals_map, evaluate=False)
    except Exception as exc:  # pragma: no cover - diagnostic path
        raise ValueError(
            f"failed to translate FORM coefficient {source!r}: {exc}"
        ) from exc

    # Rebuild in normal SymPy canonical arithmetic after syntax import.  Do not
    # aggressively simplify here; large Kira coefficients should remain cheap
    # to import.  together/cancel can be requested later where useful.
    return sp.sympify(expr)


def coefficient_symbol_names(expr: sp.Expr) -> tuple[str, ...]:
    return tuple(sorted(str(symbol) for symbol in expr.free_symbols))
