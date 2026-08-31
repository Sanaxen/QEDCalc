"""Classify non-pivot terminal support reached by finite-field Q01 reductions."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex
from .laporta_plan import dot_degree, physical_sector
from .remaining_target_classification import (
    corrected_total_complexity,
    full_numerator_degree,
)
from .scalar_subtopology_factorization import classify_scalar_subtopologies


@dataclass(frozen=True)
class ModPTerminalStructureRecord:
    index: tuple[int, ...]
    sector: tuple[int, ...]
    active_physical_lines: int
    corrected_complexity: int
    dot_degree: int
    full_numerator_degree: int
    scalar_subtopology: bool
    factorization: str | None
    structurally_zero: bool
    same_sector_as_source: bool


@dataclass(frozen=True)
class ModPTerminalStructureProfile:
    terminal_count: int
    same_sector_count: int
    lower_sector_count: int
    scalar_count: int
    factorized_scalar_count: int
    connected_scalar_count: int
    structurally_zero_count: int
    nonscalar_count: int
    records: tuple[ModPTerminalStructureRecord, ...]


def classify_modp_terminal_structure(
    family: IntegralFamily,
    terminals: Iterable[IntegralIndex],
    *,
    source_sector: tuple[int, ...],
    physical_count: int = 9,
) -> ModPTerminalStructureProfile:
    terminals = tuple(dict.fromkeys(family.validate_index(index) for index in terminals))
    scalar = [
        index for index in terminals
        if dot_degree(index, physical_count) == 0
        and full_numerator_degree(index, physical_count) == 0
    ]
    scalar_records = {
        tuple(record.index): record
        for record in classify_scalar_subtopologies(
            family, scalar, physical_count=physical_count
        )
    }

    records = []
    same_sector = lower_sector = scalar_count = factorized = connected = zero = nonscalar = 0
    for index in terminals:
        sector = physical_sector(index, physical_count)
        is_same = sector == source_sector
        if is_same:
            same_sector += 1
        else:
            lower_sector += 1

        is_scalar = (
            dot_degree(index, physical_count) == 0
            and full_numerator_degree(index, physical_count) == 0
        )
        factorization = None
        structurally_zero = False
        if is_scalar:
            scalar_count += 1
            scalar_record = scalar_records[index.powers]
            factorization = scalar_record.factorization
            structurally_zero = scalar_record.structurally_zero
            if structurally_zero:
                zero += 1
            if factorization.startswith("factorized-"):
                factorized += 1
            else:
                connected += 1
        else:
            nonscalar += 1

        records.append(ModPTerminalStructureRecord(
            index=index.powers,
            sector=sector,
            active_physical_lines=sum(sector),
            corrected_complexity=corrected_total_complexity(index, physical_count),
            dot_degree=dot_degree(index, physical_count),
            full_numerator_degree=full_numerator_degree(index, physical_count),
            scalar_subtopology=is_scalar,
            factorization=factorization,
            structurally_zero=structurally_zero,
            same_sector_as_source=is_same,
        ))

    records.sort(
        key=lambda record: (
            record.same_sector_as_source,
            record.corrected_complexity,
            record.active_physical_lines,
            record.sector,
            record.index,
        ),
        reverse=True,
    )
    return ModPTerminalStructureProfile(
        terminal_count=len(records),
        same_sector_count=same_sector,
        lower_sector_count=lower_sector,
        scalar_count=scalar_count,
        factorized_scalar_count=factorized,
        connected_scalar_count=connected,
        structurally_zero_count=zero,
        nonscalar_count=nonscalar,
        records=tuple(records),
    )


def terminal_structure_histograms(profile: ModPTerminalStructureProfile) -> dict[str, dict]:
    complexity = Counter(record.corrected_complexity for record in profile.records)
    active_lines = Counter(record.active_physical_lines for record in profile.records)
    sectors = Counter(record.sector for record in profile.records)
    dot = Counter(record.dot_degree for record in profile.records)
    numerator = Counter(record.full_numerator_degree for record in profile.records)
    return {
        "corrected_complexity_histogram": dict(sorted(complexity.items())),
        "active_line_histogram": dict(sorted(active_lines.items())),
        "dot_degree_histogram": dict(sorted(dot.items())),
        "full_numerator_degree_histogram": dict(sorted(numerator.items())),
        "sector_histogram": {str(key): value for key, value in sorted(sectors.items())},
    }
