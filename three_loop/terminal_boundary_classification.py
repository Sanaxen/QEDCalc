"""Classify unresolved terminals from the merged Q01 exact symbolic closure."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex, is_scaleless_zero_sector
from .remaining_target_classification import classify_remaining_targets
from .scalar_subtopology_factorization import classify_scalar_subtopologies


@dataclass(frozen=True)
class TerminalBoundaryRecord:
    index: tuple[int, ...]
    category: str
    active_physical_lines: int
    dot_degree: int
    full_numerator_degree: int
    corrected_complexity: int
    factorization: str | None


@dataclass(frozen=True)
class TerminalBoundaryProfile:
    terminal_count: int
    known_manifest_count: int
    conservative_zero_count: int
    scalar_factorized_count: int
    scalar_connected_count: int
    nonscalar_count: int
    category_histogram: tuple[tuple[str, int], ...]
    records: tuple[TerminalBoundaryRecord, ...]


def classify_terminal_boundary(
    family: IntegralFamily,
    terminals: Iterable[IntegralIndex],
    *,
    known_manifest_indices: Iterable[IntegralIndex] = (),
    physical_count: int = 9,
) -> TerminalBoundaryProfile:
    terminals = tuple(dict.fromkeys(family.validate_index(x) for x in terminals))
    known = {family.validate_index(x).powers for x in known_manifest_indices}
    structural = {r.index: r for r in classify_remaining_targets(terminals, physical_count=physical_count)}
    scalar_indices = [IntegralIndex(r.index) for r in structural.values() if r.is_scalar_subtopology]
    factorization = {
        r.index: r
        for r in classify_scalar_subtopologies(
            family, scalar_indices, physical_count=physical_count
        )
    }

    records = []
    hist = Counter()
    for index in terminals:
        s = structural[index.powers]
        fac = factorization.get(index.powers)
        if index.powers in known:
            category = "known-29-manifest"
        elif is_scaleless_zero_sector(family, index):
            category = "conservative-zero"
        elif s.is_scalar_subtopology and fac is not None and fac.structurally_zero:
            category = "structural-zero"
        elif s.is_scalar_subtopology and fac is not None and fac.factorization != "connected-3loop":
            category = "scalar-factorized"
        elif s.is_scalar_subtopology:
            category = "scalar-connected"
        else:
            category = "nonscalar"
        hist[category] += 1
        records.append(TerminalBoundaryRecord(
            index=index.powers,
            category=category,
            active_physical_lines=s.active_physical_lines,
            dot_degree=s.dot_degree,
            full_numerator_degree=s.full_numerator_degree,
            corrected_complexity=s.corrected_complexity,
            factorization=fac.factorization if fac is not None else None,
        ))

    return TerminalBoundaryProfile(
        terminal_count=len(terminals),
        known_manifest_count=hist["known-29-manifest"],
        conservative_zero_count=hist["conservative-zero"] + hist["structural-zero"],
        scalar_factorized_count=hist["scalar-factorized"],
        scalar_connected_count=hist["scalar-connected"],
        nonscalar_count=hist["nonscalar"],
        category_histogram=tuple(sorted(hist.items())),
        records=tuple(records),
    )
