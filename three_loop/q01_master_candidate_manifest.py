"""Consolidated manifest for the Q01 integrals left by the finite IBP audits."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from qedcalc.operations.ibp import IntegralIndex
from .remaining_target_classification import classify_remaining_targets


@dataclass(frozen=True)
class Q01MasterCandidateEntry:
    index: tuple[int, ...]
    category: str
    sector: tuple[int, ...]
    note: str


@dataclass(frozen=True)
class Q01MasterCandidateManifest:
    remaining_count: int
    lower_loop_factorized_count: int
    connected_scalar_count: int
    nonscalar_count: int
    genuine_three_loop_candidate_count: int
    entries: tuple[Q01MasterCandidateEntry, ...]


def build_q01_master_candidate_manifest(
    remaining: Iterable[IntegralIndex],
    factorization_by_index: Mapping[tuple[int, ...], str],
) -> Q01MasterCandidateManifest:
    records = classify_remaining_targets(remaining)
    entries = []
    lower = connected = nonscalar = 0
    for record in records:
        factorization = factorization_by_index.get(record.index)
        if record.is_scalar_subtopology and factorization == "factorized-2+1":
            category = "lower-loop-factorized"
            note = "exactly factorizes into a two-loop integral times a one-loop integral"
            lower += 1
        elif record.is_scalar_subtopology:
            category = "connected-scalar-master-candidate"
            note = "connected three-loop scalar integral left unpivoted by the finite IBP audits"
            connected += 1
        else:
            category = "nonscalar-master-candidate"
            note = "three-loop integral with one negative physical-family power left unpivoted by the finite IBP audits"
            nonscalar += 1
        entries.append(Q01MasterCandidateEntry(
            index=record.index,
            category=category,
            sector=record.sector,
            note=note,
        ))
    return Q01MasterCandidateManifest(
        remaining_count=len(entries),
        lower_loop_factorized_count=lower,
        connected_scalar_count=connected,
        nonscalar_count=nonscalar,
        genuine_three_loop_candidate_count=connected + nonscalar,
        entries=tuple(entries),
    )
