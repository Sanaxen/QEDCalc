"""Focused Q01 diagnostic for targets left after expanded same-sector rescue."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex, prune_zero_sectors, specialize_ibp_system
from .blocker_reduction import collect_unresolved_blockers
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .laporta_plan import dot_degree, numerator_degree, physical_sector, total_complexity
from .local_block_elimination import local_same_seed_equations
from .reverse_dependency import predecessor_candidates_for_target
from .sector_local_modp import _forward_eliminate_mod_p, _specialize_remaining_symbols_by_name
from .sector_local_probe import default_q01_probe_points
from .sector_local_target_rescue import unresolved_targets_after_one_hop

ProgressCallback = Callable[[str, int | None, int | None], None]


@dataclass(frozen=True)
class RemainingTargetRecord:
    index: tuple[int, ...]
    sector: tuple[int, ...]
    dot_degree: int
    numerator_degree: int
    total_complexity: int
    active_physical_lines: int


@dataclass(frozen=True)
class RemainingTargetProfile:
    original_target_count: int
    unresolved_after_one_hop_count: int
    selected_sector_count: int
    recomputed_sector_target_count: int
    remaining_target_count: int
    prime: int
    records: tuple[RemainingTargetRecord, ...]


def _progress(cb, stage, current=None, total=None):
    if cb is not None:
        cb(stage, current, total)


def audit_remaining_expanded_targets(
    family: IntegralFamily,
    targets: Iterable[IntegralIndex],
    *,
    selected_sectors: Sequence[tuple[int, ...]],
    prime: int = 1000003,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    physical_count: int = 9,
    progress: ProgressCallback | None = None,
) -> RemainingTargetProfile:
    targets = tuple(dict.fromkeys(family.validate_index(t) for t in targets))
    selected = tuple(dict.fromkeys(tuple(sector) for sector in selected_sectors))
    selected_set = set(selected)
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    unresolved = unresolved_targets_after_one_hop(
        family, targets, templates=templates, progress=progress
    )
    blockers = collect_unresolved_blockers(family, targets, templates=templates)

    target_groups: dict[tuple[int, ...], list[IntegralIndex]] = defaultdict(list)
    blocker_groups: dict[tuple[int, ...], list[IntegralIndex]] = defaultdict(list)
    for target in unresolved:
        sector = physical_sector(target, physical_count)
        if sector in selected_set:
            target_groups[sector].append(target)
    for blocker in blockers:
        sector = physical_sector(blocker, physical_count)
        if sector in selected_set:
            blocker_groups[sector].append(blocker)

    point = default_q01_probe_points(family)[0]
    remaining: set[IntegralIndex] = set()
    recomputed_target_count = 0

    for sector_no, sector in enumerate(selected, start=1):
        sector_targets = tuple(target_groups.get(sector, ()))
        if not sector_targets:
            continue
        recomputed_target_count += len(sector_targets)
        blocker_seeds = set(blocker_groups.get(sector, ()))
        predecessor_seeds: set[IntegralIndex] = set()
        for target in sector_targets:
            for seed in predecessor_candidates_for_target(family, target, templates=templates):
                if physical_sector(seed, physical_count) == sector:
                    predecessor_seeds.add(seed)
        predecessor_seeds.difference_update(blocker_seeds)
        seeds = tuple(sorted(blocker_seeds | predecessor_seeds, key=lambda idx: idx.powers))

        _progress(
            progress,
            f"sector {sector_no}/{len(selected)} profile start: targets={len(sector_targets)} seeds={len(seeds)}",
        )
        equations = []
        for n, seed in enumerate(seeds, start=1):
            equations.extend(local_same_seed_equations(family, seed, templates=templates))
            if n == 1 or n == len(seeds) or n % 25 == 0:
                _progress(progress, f"sector {sector_no}/{len(selected)} build equations", n, len(seeds))
        equations = prune_zero_sectors(family, equations)
        probed = specialize_ibp_system(equations, point)
        probed = _specialize_remaining_symbols_by_name(probed, point)
        rules = _forward_eliminate_mod_p(probed, prime, progress=progress)
        unsolved = set(sector_targets) - set(rules)
        remaining.update(unsolved)
        _progress(
            progress,
            f"sector {sector_no}/{len(selected)} profile done: remaining={len(unsolved)}",
        )

    records = tuple(sorted(
        (
            RemainingTargetRecord(
                index=index.powers,
                sector=physical_sector(index, physical_count),
                dot_degree=dot_degree(index, physical_count),
                numerator_degree=numerator_degree(index, physical_count),
                total_complexity=total_complexity(index, physical_count),
                active_physical_lines=sum(physical_sector(index, physical_count)),
            )
            for index in remaining
        ),
        key=lambda record: (
            record.total_complexity,
            record.dot_degree,
            record.numerator_degree,
            record.active_physical_lines,
            record.sector,
            record.index,
        ),
        reverse=True,
    ))
    return RemainingTargetProfile(
        original_target_count=len(targets),
        unresolved_after_one_hop_count=len(unresolved),
        selected_sector_count=len(selected),
        recomputed_sector_target_count=recomputed_target_count,
        remaining_target_count=len(records),
        prime=prime,
        records=records,
    )
