"""Algebraic bridge from native QEDCalc Q01 ISPs to the Kira quadratic basis.

QEDCalc uses three linear scalar products as auxiliary denominators::

    D10 = k.r
    D11 = l.q
    D12 = q.r

The Kira Q01 family instead uses quadratic auxiliary inverse propagators P10,
P11,P12.  With the Kira physical ordering used by :mod:`kira_backend` and
m2=1, the exact relations are

    D10 = (P7 + P9 - P10)/2
    D11 = (P11 - P8 - z)/2
    D12 = (P12 - P9 - z)/2.

Negative native ISP indices are numerator powers and can therefore be expanded
as a finite polynomial in the Kira P_i.  Positive native ISP indices would put
a linear scalar product in a denominator; those are deliberately rejected by
this bridge because they do not admit this finite polynomial conversion.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import sympy as sp

from three_loop.kira_backend import Q01_KIRA_TO_QED_PHYSICAL
from three_loop.kira_reducer import (
    IndexTuple,
    KiraReductionTable,
    ReducedTerm,
    ReductionResult,
)


_P = sp.symbols("P1:13")
_Z = sp.Symbol("z")


@dataclass(frozen=True)
class KiraBasisExpansionTerm:
    coefficient: sp.Expr
    kira_indices: IndexTuple


@dataclass(frozen=True)
class QEDToKiraExpansion:
    qed_indices: IndexTuple
    terms: tuple[KiraBasisExpansionTerm, ...]
    physical_normalization_sign: int
    native_isp_degree: int


@dataclass(frozen=True)
class QEDKiraReductionResult:
    qed_indices: IndexTuple
    terms: tuple[ReducedTerm, ...]
    status: str  # "reduced", "master", "not_in_table"
    expansion_term_count: int
    missing_kira_integrals: tuple[IndexTuple, ...]

    @property
    def is_available(self) -> bool:
        return not self.missing_kira_integrals


def _indices12(values: Iterable[int]) -> IndexTuple:
    result = tuple(int(v) for v in values)
    if len(result) != 12:
        raise ValueError(f"expected 12 integral indices, got {len(result)}")
    return result


def q01_native_isp_polynomial(*, z: sp.Expr | None = None) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """Return native D10,D11,D12 in the Kira P basis for m2=1."""
    z_value = _Z if z is None else sp.sympify(z)
    p = _P
    return (
        (p[6] + p[8] - p[9]) / 2,
        (p[10] - p[7] - z_value) / 2,
        (p[11] - p[8] - z_value) / 2,
    )


def expand_qedcalc_integral_to_kira(
    indices: Iterable[int],
    *,
    z: sp.Expr | None = None,
) -> QEDToKiraExpansion:
    """Expand one native Q01 integral into Kira-basis integrals.

    The first nine native powers are mapped by the physical propagator
    permutation.  Kira uses P_i=-D_j for those nine propagators, giving the
    overall factor ``(-1)**sum(a1..a9)``.  Native D10-D12 are accepted only
    for zero or negative powers; a negative power ``-n`` contributes the
    numerator polynomial ``D_i**n``.
    """
    qed = _indices12(indices)
    native_isp = qed[9:12]
    positive = [(10 + i, power) for i, power in enumerate(native_isp) if power > 0]
    if positive:
        detail = ", ".join(f"D{idx}^{power}" for idx, power in positive)
        raise ValueError(
            "positive native linear-ISP denominator powers cannot be converted "
            f"by finite Kira polynomial expansion: {detail}"
        )

    physical = qed[:9]
    kira_physical = tuple(
        physical[qed_index - 1] for qed_index in Q01_KIRA_TO_QED_PHYSICAL
    )
    base = list(kira_physical + (0, 0, 0))
    sign = -1 if (sum(physical) % 2) else 1

    d10, d11, d12 = q01_native_isp_polynomial(z=z)
    numerator = sp.Integer(sign)
    for power, expr in zip(native_isp, (d10, d11, d12)):
        if power < 0:
            numerator *= expr ** (-power)
    numerator = sp.Poly(sp.expand(numerator), *_P, domain="EX")

    combined: dict[IndexTuple, sp.Expr] = {}
    for powers, coefficient in numerator.terms():
        kira = tuple(base[i] - int(powers[i]) for i in range(12))
        combined[kira] = sp.expand(combined.get(kira, sp.Integer(0)) + coefficient)

    terms = tuple(
        KiraBasisExpansionTerm(sp.factor(coeff), kira)
        for kira, coeff in sorted(combined.items())
        if coeff != 0
    )
    return QEDToKiraExpansion(
        qed_indices=qed,
        terms=terms,
        physical_normalization_sign=sign,
        native_isp_degree=sum(-power for power in native_isp if power < 0),
    )


def reduce_qedcalc_integral_via_kira(
    table: KiraReductionTable,
    indices: Iterable[int],
    *,
    z: sp.Expr | None = None,
) -> QEDKiraReductionResult:
    """Expand a native Q01 numerator and reduce every Kira term to masters.

    The result is returned only as a complete master combination.  If even one
    expanded Kira integral is outside the loaded reduction table, no partial
    master sum is exposed as a successful reduction; missing integrals are
    reported explicitly so a larger Kira seed can be generated.
    """
    expansion = expand_qedcalc_integral_to_kira(indices, z=z)
    missing: list[IndexTuple] = []
    accumulated: dict[IndexTuple, sp.Expr] = {}
    all_master_inputs = True

    for expanded in expansion.terms:
        reduced: ReductionResult = table.reduce_kira(expanded.kira_indices)
        if reduced.status == "not_in_table":
            missing.append(expanded.kira_indices)
            continue
        if reduced.status != "master":
            all_master_inputs = False
        for term in reduced.terms:
            accumulated[term.master] = accumulated.get(term.master, sp.Integer(0)) + (
                expanded.coefficient * term.coefficient
            )

    missing_unique = tuple(sorted(set(missing)))
    if missing_unique:
        return QEDKiraReductionResult(
            qed_indices=expansion.qed_indices,
            terms=(),
            status="not_in_table",
            expansion_term_count=len(expansion.terms),
            missing_kira_integrals=missing_unique,
        )

    reduced_terms = tuple(
        ReducedTerm(coefficient=sp.factor(coeff), master=master)
        for master, coeff in sorted(accumulated.items())
        if sp.factor(coeff) != 0
    )
    status = "master" if all_master_inputs and len(expansion.terms) == 1 else "reduced"
    return QEDKiraReductionResult(
        qed_indices=expansion.qed_indices,
        terms=reduced_terms,
        status=status,
        expansion_term_count=len(expansion.terms),
        missing_kira_integrals=(),
    )
