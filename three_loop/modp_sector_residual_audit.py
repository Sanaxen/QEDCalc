"""Audit same-sector residuals left by a saved finite-field sector descent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IntegralFamily, IntegralIndex
from .dependency_audit import target_direct_pivot_equations
from .ibp_frontier import IBPDerivativeTemplate, build_ibp_derivative_templates
from .reverse_dependency import reverse_pivot_equations_for_target


@dataclass(frozen=True)
class SectorResidualAuditProfile:
    residual_count: int
    direct_pivotable_count: int
    reverse_only_pivotable_count: int
    rescued_count: int
    unresolved_count: int
    direct_pivotable_indices: tuple[tuple[int, ...], ...]
    reverse_only_pivotable_indices: tuple[tuple[int, ...], ...]
    unresolved_indices: tuple[tuple[int, ...], ...]


def residual_union(
    unsolved_targets: Iterable[IntegralIndex],
    same_sector_terminals: Iterable[IntegralIndex],
) -> tuple[IntegralIndex, ...]:
    return tuple(sorted(set(unsolved_targets) | set(same_sector_terminals), key=lambda idx: idx.powers))


def audit_sector_residual_pivots(
    family: IntegralFamily,
    residuals: Iterable[IntegralIndex],
    *,
    templates: tuple[IBPDerivativeTemplate, ...] | None = None,
    progress=None,
) -> SectorResidualAuditProfile:
    residuals = tuple(dict.fromkeys(family.validate_index(idx) for idx in residuals))
    if templates is None:
        templates = build_ibp_derivative_templates(family)

    direct = []
    reverse_only = []
    unresolved = []
    total = len(residuals)
    for n, target in enumerate(residuals, start=1):
        if target_direct_pivot_equations(family, target, templates=templates):
            direct.append(target)
        elif reverse_pivot_equations_for_target(family, target, templates=templates):
            reverse_only.append(target)
        else:
            unresolved.append(target)
        if progress is not None and (n == 1 or n == total or n % 25 == 0):
            progress("audit residual direct/reverse pivots", n, total)

    return SectorResidualAuditProfile(
        residual_count=len(residuals),
        direct_pivotable_count=len(direct),
        reverse_only_pivotable_count=len(reverse_only),
        rescued_count=len(direct) + len(reverse_only),
        unresolved_count=len(unresolved),
        direct_pivotable_indices=tuple(idx.powers for idx in direct),
        reverse_only_pivotable_indices=tuple(idx.powers for idx in reverse_only),
        unresolved_indices=tuple(idx.powers for idx in unresolved),
    )
