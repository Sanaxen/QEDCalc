"""Structural factorization audit for remaining scalar Q01 subtopologies."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex, is_scaleless_zero_sector


@dataclass(frozen=True)
class ScalarFactorizationRecord:
    index: tuple[int, ...]
    component_sizes: tuple[int, ...]
    factorization: str
    free_loops: tuple[str, ...]
    conservative_scaleless_zero: bool
    free_loop_zero: bool

    @property
    def structurally_zero(self) -> bool:
        return self.conservative_scaleless_zero or self.free_loop_zero


def denominator_loop_support(
    family: IntegralFamily, denominator_index: int
) -> tuple[str, ...]:
    loops = set(family.loop_momenta)
    support: set[str] = set()
    expr = family.denominator_exprs[denominator_index]
    for atom in expr.free_symbols:
        name = str(atom)
        if not name.startswith("SP__"):
            continue
        _, a, b = name.split("__", 2)
        if a in loops:
            support.add(a)
        if b in loops:
            support.add(b)
    return tuple(sorted(support))


def loop_components_for_index(
    family: IntegralFamily,
    index: IntegralIndex,
    *,
    physical_count: int = 9,
) -> tuple[tuple[str, ...], ...]:
    """Connected loop-momentum components induced by active physical denominators."""
    index = family.validate_index(index)
    loops = tuple(family.loop_momenta)
    adjacency = {loop: {loop} for loop in loops}
    for i, power in enumerate(index.powers[:physical_count]):
        if power <= 0:
            continue
        support = denominator_loop_support(family, i)
        for a in support:
            adjacency[a].update(support)

    seen = set()
    components = []
    for loop in loops:
        if loop in seen:
            continue
        stack = [loop]
        comp = set()
        while stack:
            current = stack.pop()
            if current in comp:
                continue
            comp.add(current)
            stack.extend(adjacency[current] - comp)
        seen.update(comp)
        components.append(tuple(sorted(comp)))
    return tuple(sorted(components, key=lambda comp: (-len(comp), comp)))


def free_loops_for_index(
    family: IntegralFamily,
    index: IntegralIndex,
    *,
    physical_count: int = 9,
) -> tuple[str, ...]:
    active_support = set()
    for i, power in enumerate(index.powers[:physical_count]):
        if power > 0:
            active_support.update(denominator_loop_support(family, i))
    return tuple(loop for loop in family.loop_momenta if loop not in active_support)


def factorization_label(component_sizes: tuple[int, ...]) -> str:
    sizes = tuple(sorted(component_sizes, reverse=True))
    if sizes == (3,):
        return "connected-3loop"
    if sizes == (2, 1):
        return "factorized-2+1"
    if sizes == (1, 1, 1):
        return "factorized-1+1+1"
    return "factorized-" + "+".join(map(str, sizes))


def classify_scalar_subtopologies(
    family: IntegralFamily,
    indices: Iterable[IntegralIndex],
    *,
    physical_count: int = 9,
) -> tuple[ScalarFactorizationRecord, ...]:
    records = []
    for index in indices:
        index = family.validate_index(index)
        components = loop_components_for_index(
            family, index, physical_count=physical_count
        )
        component_sizes = tuple(len(comp) for comp in components)
        free_loops = free_loops_for_index(
            family, index, physical_count=physical_count
        )
        records.append(ScalarFactorizationRecord(
            index=index.powers,
            component_sizes=component_sizes,
            factorization=factorization_label(component_sizes),
            free_loops=free_loops,
            conservative_scaleless_zero=is_scaleless_zero_sector(family, index),
            free_loop_zero=bool(free_loops),
        ))
    return tuple(sorted(
        records,
        key=lambda record: (
            record.structurally_zero,
            record.factorization,
            record.index,
        ),
        reverse=True,
    ))
