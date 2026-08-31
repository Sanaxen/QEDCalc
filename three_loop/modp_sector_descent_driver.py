"""Reusable helpers for sector-by-sector Q01 finite-field descent.

The saved descent JSON from one sector contains the terminal integral indices and
lower-sector counts.  These helpers select the largest strictly lower physical
sector and recover exactly the terminal integrals that seed the next descent.
"""
from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from qedcalc.operations.ibp import IntegralIndex
from .laporta_plan import physical_sector


def largest_lower_sector_from_saved(data: Mapping) -> tuple[int, ...]:
    """Return the largest lower sector recorded in a saved descent JSON."""
    rows = data.get("lower_sector_rows")
    if not rows:
        raise ValueError("saved descent has no lower_sector_rows")
    ordered = sorted(
        rows,
        key=lambda row: (-int(row["terminal_count"]), tuple(row["sector"])),
    )
    return tuple(int(x) for x in ordered[0]["sector"])


def targets_for_sector_from_saved(
    data: Mapping,
    sector: Sequence[int],
    *,
    physical_count: int = 9,
) -> tuple[IntegralIndex, ...]:
    """Recover unique saved terminal indices belonging to one physical sector."""
    raw = data.get("terminal_indices")
    if raw is None:
        raise ValueError("saved descent has no terminal_indices")
    wanted = tuple(int(x) for x in sector)
    out = []
    for powers in raw:
        index = IntegralIndex(tuple(int(x) for x in powers))
        if physical_sector(index, physical_count) == wanted:
            out.append(index)
    return tuple(dict.fromkeys(out))
