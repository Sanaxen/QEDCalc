"""Queryable reduction-table API for Kira-exported Q01 rules.

This module intentionally separates two notions of index basis:

* the Kira quadratic 12-propagator basis used by ``kira2form``;
* QEDCalc's native Q01 basis, whose D10-D12 are linear scalar products.

A Kira table can therefore be queried directly for arbitrary Kira indices.
For QEDCalc input, the helper in this module only accepts integrals with zero
powers on native D10-D12; those nine physical propagator powers can be mapped
exactly by permutation and the physical sign convention.  Native ISP powers
must first be expanded through the manifest basis relations by a later layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import sympy as sp

from three_loop.kira_backend import Q01_KIRA_TO_QED_PHYSICAL, Q01_KIRA_NAME
from three_loop.kira_form_coefficients import form_coefficient_to_sympy
from three_loop.kira_form_parser import KiraFormIntegral, iter_kira_form_rules


IndexTuple = tuple[int, ...]


@dataclass(frozen=True)
class ReducedTerm:
    coefficient: sp.Expr
    master: IndexTuple
    coefficient_form: str | None = None


@dataclass(frozen=True)
class ReductionResult:
    input_indices: IndexTuple
    terms: tuple[ReducedTerm, ...]
    status: str  # "reduced", "master", "not_in_table"

    @property
    def is_available(self) -> bool:
        return self.status != "not_in_table"


@dataclass(frozen=True)
class QEDPhysicalMap:
    """Exact map for native QEDCalc integrals with no D10-D12 powers."""

    qed_indices: IndexTuple
    kira_indices: IndexTuple
    normalization_sign: int


def _indices12(values: Iterable[int]) -> IndexTuple:
    result = tuple(int(v) for v in values)
    if len(result) != 12:
        raise ValueError(f"expected 12 integral indices, got {len(result)}")
    return result


def load_master_indices(path: str | Path, *, family: str = Q01_KIRA_NAME) -> tuple[IndexTuple, ...]:
    """Read Kira's plain ``masters.final``/``masters`` list."""
    masters: list[IndexTuple] = []
    prefix = family + "["
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or not line.startswith(prefix) or "]" not in line:
            continue
        payload = line[len(prefix): line.index("]")]
        masters.append(_indices12(int(part.strip()) for part in payload.split(",")))
    if not masters:
        raise ValueError(f"no {family} masters found in {path}")
    return tuple(masters)


class KiraReductionTable:
    """In-memory lookup table for a fully back-substituted Kira FORM export."""

    def __init__(
        self,
        *,
        family: str,
        masters: Iterable[IndexTuple],
        rules: dict[IndexTuple, tuple[ReducedTerm, ...]],
    ) -> None:
        self.family = str(family)
        self.masters = frozenset(_indices12(v) for v in masters)
        self.rules = dict(rules)

    @classmethod
    def from_form_export(
        cls,
        form_path: str | Path,
        masters_path: str | Path,
        *,
        family: str = Q01_KIRA_NAME,
    ) -> "KiraReductionTable":
        masters = load_master_indices(masters_path, family=family)
        master_set = set(masters)
        rules: dict[IndexTuple, tuple[ReducedTerm, ...]] = {}

        for rule in iter_kira_form_rules(form_path, family=family):
            lhs = _indices12(rule.lhs.indices)
            if lhs in rules:
                raise ValueError(f"duplicate Kira reduction rule for {lhs}")
            converted: list[ReducedTerm] = []
            for term in rule.terms:
                rhs = _indices12(term.integral.indices)
                if rhs not in master_set:
                    raise ValueError(
                        "back-substituted Kira table contains non-master RHS integral: "
                        f"{rhs}"
                    )
                converted.append(
                    ReducedTerm(
                        coefficient=form_coefficient_to_sympy(term.coefficient_form),
                        master=rhs,
                        coefficient_form=term.coefficient_form,
                    )
                )
            rules[lhs] = tuple(converted)

        return cls(family=family, masters=masters, rules=rules)

    def reduce_kira(self, indices: Iterable[int]) -> ReductionResult:
        key = _indices12(indices)
        if key in self.masters:
            return ReductionResult(
                input_indices=key,
                terms=(ReducedTerm(sp.Integer(1), key, "+(1)"),),
                status="master",
            )
        if key not in self.rules:
            return ReductionResult(input_indices=key, terms=(), status="not_in_table")
        return ReductionResult(input_indices=key, terms=self.rules[key], status="reduced")


def map_qedcalc_physical_integral_to_kira(indices: Iterable[int]) -> QEDPhysicalMap:
    """Map a native QEDCalc Q01 integral with D10=D11=D12 powers equal to zero.

    The first nine Kira propagators are the QEDCalc physical denominators in
    the order D1,D3,D5,D6,D2,D4,D7,D8,D9.  Because Kira_Pi=-QEDCalc_Dj for
    these propagators, the integral normalization differs by
    ``(-1)**sum(a1..a9)``.  The three native linear ISP indices cannot be
    mapped by permutation and are therefore rejected here.
    """
    qed = _indices12(indices)
    if any(qed[i] != 0 for i in range(9, 12)):
        raise ValueError(
            "native QEDCalc D10-D12 are linear ISPs and cannot be mapped to "
            "Kira auxiliary indices by permutation; expand the ISP basis first"
        )

    physical = qed[:9]
    kira_physical = tuple(physical[qed_index - 1] for qed_index in Q01_KIRA_TO_QED_PHYSICAL)
    kira = kira_physical + (0, 0, 0)
    sign = -1 if (sum(physical) % 2) else 1
    return QEDPhysicalMap(qed_indices=qed, kira_indices=kira, normalization_sign=sign)


def reduce_qedcalc_physical_integral(
    table: KiraReductionTable,
    indices: Iterable[int],
) -> ReductionResult:
    """Reduce a native physical-only Q01 integral through the Kira table.

    Returned coefficients are normalized to the native QEDCalc input integral.
    Masters remain expressed in the Kira quadratic basis; converting Kira
    auxiliary masters back to native linear-ISP expressions is deliberately a
    separate algebraic step.
    """
    mapped = map_qedcalc_physical_integral_to_kira(indices)
    result = table.reduce_kira(mapped.kira_indices)
    if not result.is_available or mapped.normalization_sign == 1:
        return result
    return ReductionResult(
        input_indices=result.input_indices,
        terms=tuple(
            ReducedTerm(
                coefficient=sp.Integer(mapped.normalization_sign) * term.coefficient,
                master=term.master,
                coefficient_form=term.coefficient_form,
            )
            for term in result.terms
        ),
        status=result.status,
    )
