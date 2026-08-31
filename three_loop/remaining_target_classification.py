"""Structural classification helpers for remaining Q01 integral targets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralIndex
from .laporta_plan import dot_degree, numerator_degree, physical_sector


@dataclass(frozen=True)
class RemainingTargetClass:
    index: tuple[int, ...]
    sector: tuple[int, ...]
    active_physical_lines: int
    dot_degree: int
    auxiliary_numerator_degree: int
    physical_negative_degree: int
    full_numerator_degree: int
    corrected_complexity: int
    is_scalar_subtopology: bool


def physical_negative_degree(index: IntegralIndex, physical_count: int = 9) -> int:
    """Count numerator powers represented by negative physical-family indices."""
    return sum(max(-power, 0) for power in index.powers[:physical_count])


def full_numerator_degree(index: IntegralIndex, physical_count: int = 9) -> int:
    """Count negative powers in both physical and auxiliary family slots."""
    return physical_negative_degree(index, physical_count) + numerator_degree(index, physical_count)


def corrected_total_complexity(index: IntegralIndex, physical_count: int = 9) -> int:
    return dot_degree(index, physical_count) + full_numerator_degree(index, physical_count)


def classify_remaining_targets(
    indices: Iterable[IntegralIndex], *, physical_count: int = 9
) -> tuple[RemainingTargetClass, ...]:
    records = []
    for index in indices:
        sector = physical_sector(index, physical_count)
        pneg = physical_negative_degree(index, physical_count)
        aux = numerator_degree(index, physical_count)
        dot = dot_degree(index, physical_count)
        full_num = pneg + aux
        records.append(RemainingTargetClass(
            index=index.powers,
            sector=sector,
            active_physical_lines=sum(sector),
            dot_degree=dot,
            auxiliary_numerator_degree=aux,
            physical_negative_degree=pneg,
            full_numerator_degree=full_num,
            corrected_complexity=dot + full_num,
            is_scalar_subtopology=(dot == 0 and full_num == 0),
        ))
    return tuple(sorted(
        records,
        key=lambda record: (
            record.corrected_complexity,
            record.full_numerator_degree,
            record.active_physical_lines,
            record.sector,
            record.index,
        ),
        reverse=True,
    ))
