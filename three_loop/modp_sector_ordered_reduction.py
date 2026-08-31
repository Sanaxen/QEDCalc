"""Sector-ordered finite-field block reduction.

Eliminate explicitly forbidden higher-sector columns from an IBP system first,
then solve a target block using only the residual row space.  This preserves a
triangular sector ordering: the resulting target rules cannot contain any of
the forbidden higher-sector integrals on their right-hand sides.

This is a finite-field structural reduction.  Exact rational reconstruction is
still required before the rules become exact symbolic identities.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from .modp_block_reduction import ModPBlockReduction, reduce_block_mod_p
from .sector_local_modp import _rational_mod_p


@dataclass(frozen=True)
class SectorOrderedModPReduction:
    prime: int
    forbidden_count: int
    forbidden_rank: int
    residual_equation_count: int
    block_reduction: ModPBlockReduction


def _specialize_row_mod_p(equation: IBPEquation, prime: int) -> dict[IntegralIndex, int]:
    p = int(prime)
    row: dict[IntegralIndex, int] = {}
    for index, coeff in equation.terms.items():
        value = int(_rational_mod_p(coeff, p)) % p
        if value:
            row[index] = value
    return row


def eliminate_forbidden_columns_mod_p(
    equations: Iterable[IBPEquation],
    forbidden: Iterable[IntegralIndex],
    prime: int,
) -> tuple[tuple[IBPEquation, ...], int]:
    """Return the row-space slice whose forbidden columns vanish.

    Gaussian elimination is performed only with respect to the forbidden
    columns, but row operations are applied to every coefficient in the row.
    After the forbidden pivots are isolated, the non-pivot rows span exactly
    the combinations of the original equations for which every forbidden
    coefficient is zero.
    """
    p = int(prime)
    forbidden = tuple(dict.fromkeys(forbidden))
    rows = [_specialize_row_mod_p(equation, p) for equation in equations]
    rows = [row for row in rows if row]

    pivot_row = 0
    for column in forbidden:
        pivot = next(
            (r for r in range(pivot_row, len(rows)) if rows[r].get(column, 0) % p),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        lead = rows[pivot_row][column] % p
        inv = pow(lead, -1, p)
        rows[pivot_row] = {
            index: (value * inv) % p
            for index, value in rows[pivot_row].items()
            if (value * inv) % p
        }
        pivot_data = rows[pivot_row]

        for r in range(len(rows)):
            if r == pivot_row:
                continue
            coeff = rows[r].get(column, 0) % p
            if not coeff:
                continue
            work = dict(rows[r])
            for index, value in pivot_data.items():
                new_value = (work.get(index, 0) - coeff * value) % p
                if new_value:
                    work[index] = new_value
                else:
                    work.pop(index, None)
            rows[r] = work
        pivot_row += 1
        if pivot_row == len(rows):
            break

    forbidden_rank = pivot_row
    forbidden_set = set(forbidden)
    residual = []
    for row in rows[forbidden_rank:]:
        if any(row.get(index, 0) % p for index in forbidden_set):
            raise RuntimeError("forbidden-column elimination left a nonzero forbidden coefficient")
        if row:
            residual.append(IBPEquation(dict(row), "sector_ordered_residual"))
    return tuple(residual), forbidden_rank


def reduce_block_sector_ordered_mod_p(
    equations: Iterable[IBPEquation],
    block: Iterable[IntegralIndex],
    forbidden: Iterable[IntegralIndex],
    prime: int,
) -> SectorOrderedModPReduction:
    equations = tuple(equations)
    block = tuple(dict.fromkeys(block))
    forbidden = tuple(dict.fromkeys(forbidden))
    residual, forbidden_rank = eliminate_forbidden_columns_mod_p(
        equations, forbidden, int(prime)
    )
    reduction = reduce_block_mod_p(residual, block, int(prime))
    forbidden_powers = {index.powers for index in forbidden}
    for rule in reduction.rules:
        if any(index in forbidden_powers for index, _ in rule.rhs):
            raise RuntimeError("sector-ordered block reduction emitted a forbidden RHS integral")
    return SectorOrderedModPReduction(
        prime=int(prime),
        forbidden_count=len(forbidden),
        forbidden_rank=forbidden_rank,
        residual_equation_count=len(residual),
        block_reduction=reduction,
    )
