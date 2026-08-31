"""Detailed profile of nonscalar Q01 symbolic-boundary terminals."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralIndex
from .remaining_target_classification import (
    corrected_total_complexity,
    full_numerator_degree,
    physical_negative_degree,
)
from .laporta_plan import dot_degree, numerator_degree, physical_sector


@dataclass(frozen=True)
class NonscalarTerminalRecord:
    index: tuple[int, ...]
    sector: tuple[int, ...]
    corrected_complexity: int
    dot_degree: int
    physical_negative_degree: int
    auxiliary_numerator_degree: int
    full_numerator_degree: int
    negative_slots: tuple[int, ...]
    physical_negative_slots: tuple[int, ...]
    auxiliary_negative_slots: tuple[int, ...]


@dataclass(frozen=True)
class NonscalarTerminalProfile:
    terminal_count: int
    physical_only_count: int
    auxiliary_only_count: int
    mixed_count: int
    records: tuple[NonscalarTerminalRecord, ...]


def classify_nonscalar_terminals(
    indices: Iterable[IntegralIndex], *, physical_count: int = 9
) -> NonscalarTerminalProfile:
    records = []
    physical_only = auxiliary_only = mixed = 0
    for index in dict.fromkeys(indices):
        powers = index.powers
        pslots = tuple(i + 1 for i, power in enumerate(powers[:physical_count]) if power < 0)
        aslots = tuple(i + 1 for i, power in enumerate(powers[physical_count:], start=physical_count) if power < 0)
        if not pslots and not aslots:
            continue
        if pslots and aslots:
            mixed += 1
        elif pslots:
            physical_only += 1
        else:
            auxiliary_only += 1
        records.append(NonscalarTerminalRecord(
            index=powers,
            sector=physical_sector(index, physical_count),
            corrected_complexity=corrected_total_complexity(index, physical_count),
            dot_degree=dot_degree(index, physical_count),
            physical_negative_degree=physical_negative_degree(index, physical_count),
            auxiliary_numerator_degree=numerator_degree(index, physical_count),
            full_numerator_degree=full_numerator_degree(index, physical_count),
            negative_slots=pslots + aslots,
            physical_negative_slots=pslots,
            auxiliary_negative_slots=aslots,
        ))
    records.sort(key=lambda r: (r.corrected_complexity, r.negative_slots, r.sector, r.index), reverse=True)
    return NonscalarTerminalProfile(
        terminal_count=len(records),
        physical_only_count=physical_only,
        auxiliary_only_count=auxiliary_only,
        mixed_count=mixed,
        records=tuple(records),
    )


def profile_histograms(profile: NonscalarTerminalProfile) -> dict[str, dict]:
    slot_hist = Counter()
    pattern_hist = Counter()
    degree_hist = Counter()
    complexity_hist = Counter()
    active_line_hist = Counter()
    for record in profile.records:
        for slot in record.negative_slots:
            slot_hist[slot] += 1
        pattern_hist[record.negative_slots] += 1
        degree_hist[(record.physical_negative_degree, record.auxiliary_numerator_degree)] += 1
        complexity_hist[record.corrected_complexity] += 1
        active_line_hist[sum(record.sector)] += 1
    return {
        "negative_slot_histogram": dict(sorted(slot_hist.items())),
        "negative_slot_pattern_histogram": {str(key): value for key, value in sorted(pattern_hist.items())},
        "physical_aux_degree_histogram": {str(key): value for key, value in sorted(degree_hist.items())},
        "corrected_complexity_histogram": dict(sorted(complexity_hist.items())),
        "active_line_histogram": dict(sorted(active_line_hist.items())),
    }
