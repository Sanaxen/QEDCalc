"""Decompose Q01 non-scalar symbolic terminals into dot and numerator classes.

The earlier terminal-boundary category named ``nonscalar`` means
``not a scalar subtopology``.  It therefore contains both genuine numerator
integrals (negative family powers) and dot-only integrals (positive powers >1).
This module makes that distinction explicit.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralIndex
from .laporta_plan import dot_degree, numerator_degree, physical_sector
from .remaining_target_classification import physical_negative_degree


@dataclass(frozen=True)
class NonScalarBoundaryRecord:
    index: tuple[int, ...]
    sector: tuple[int, ...]
    dot_degree: int
    physical_negative_degree: int
    auxiliary_numerator_degree: int
    category: str


@dataclass(frozen=True)
class NonScalarBoundaryProfile:
    terminal_count: int
    numerator_bearing_count: int
    dot_only_count: int
    dot_and_numerator_count: int
    records: tuple[NonScalarBoundaryRecord, ...]


def decompose_non_scalar_boundary(
    indices: Iterable[IntegralIndex], *, physical_count: int = 9
) -> NonScalarBoundaryProfile:
    records = []
    numerator_bearing = dot_only = dot_and_numerator = 0
    for index in dict.fromkeys(indices):
        dot = dot_degree(index, physical_count)
        pneg = physical_negative_degree(index, physical_count)
        aux = numerator_degree(index, physical_count)
        has_num = (pneg + aux) > 0
        has_dot = dot > 0
        if has_num and has_dot:
            category = "dot+numerator"
            dot_and_numerator += 1
            numerator_bearing += 1
        elif has_num:
            category = "numerator-only"
            numerator_bearing += 1
        elif has_dot:
            category = "dot-only"
            dot_only += 1
        else:
            category = "unexpected-scalar"
        records.append(NonScalarBoundaryRecord(
            index=index.powers,
            sector=physical_sector(index, physical_count),
            dot_degree=dot,
            physical_negative_degree=pneg,
            auxiliary_numerator_degree=aux,
            category=category,
        ))
    records.sort(key=lambda r: (r.category, r.dot_degree, r.physical_negative_degree + r.auxiliary_numerator_degree, r.sector, r.index), reverse=True)
    return NonScalarBoundaryProfile(
        terminal_count=len(records),
        numerator_bearing_count=numerator_bearing,
        dot_only_count=dot_only,
        dot_and_numerator_count=dot_and_numerator,
        records=tuple(records),
    )


def decomposition_histograms(profile: NonScalarBoundaryProfile) -> dict[str, dict]:
    category = Counter(record.category for record in profile.records)
    dot_hist = Counter(record.dot_degree for record in profile.records)
    num_hist = Counter(
        (record.physical_negative_degree, record.auxiliary_numerator_degree)
        for record in profile.records
    )
    return {
        "category_histogram": dict(sorted(category.items())),
        "dot_degree_histogram": dict(sorted(dot_hist.items())),
        "physical_aux_degree_histogram": {str(key): value for key, value in sorted(num_hist.items())},
    }
