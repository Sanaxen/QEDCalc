"""Memory-efficient finite-field constrained rank for large IBP blocks.

This module is intentionally rank-only.  It projects every IBP equation onto
forbidden + target columns and keeps only nonzero coefficients in sparse dicts.
Unlike the older dense audit helper, it never materializes a Python list with
one entry per forbidden/target column.

For rank we only need row-echelon form, not full reduced row-echelon form.
Therefore elimination is forward-only.  This substantially reduces both row
copies and fill-in while preserving the two ranks needed for

    conditional_free_dimension = len(targets) - rank(target block after
    forbidden-column elimination).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from .sector_local_modp import _rational_mod_p


@dataclass(frozen=True)
class SparseConstrainedRank:
    prime: int
    forbidden_rank: int
    target_rank: int
    conditional_free_dimension: int
    input_equation_count: int
    projected_nonzero_row_count: int
    projected_term_count: int
    residual_row_count: int
    residual_term_count: int


def _project_rows(
    equations: Iterable[IBPEquation],
    allowed: set[IntegralIndex],
    prime: int,
) -> tuple[list[dict[IntegralIndex, int]], int]:
    """Project equations directly to a sparse mod-p row representation."""
    p = int(prime)
    rows: list[dict[IntegralIndex, int]] = []
    input_count = 0
    term_count = 0
    for equation in equations:
        input_count += 1
        row: dict[IntegralIndex, int] = {}
        for index, coeff in equation.terms.items():
            if index not in allowed:
                continue
            value = int(_rational_mod_p(coeff, p)) % p
            if value:
                row[index] = value
        if row:
            term_count += len(row)
            rows.append(row)
    return rows, input_count


def _forward_eliminate_columns(
    rows: list[dict[IntegralIndex, int]],
    columns: tuple[IntegralIndex, ...],
    prime: int,
    *,
    pivot_row_start: int = 0,
) -> int:
    """Forward Gaussian elimination over selected sparse columns.

    Only rows below the pivot are modified.  This is enough for rank and avoids
    the much larger memory/fill cost of producing RREF.
    """
    p = int(prime)
    pivot_row = int(pivot_row_start)
    nrows = len(rows)

    for column in columns:
        pivot = None
        for r in range(pivot_row, nrows):
            if rows[r].get(column, 0) % p:
                pivot = r
                break
        if pivot is None:
            continue

        if pivot != pivot_row:
            rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]

        pivot_data = rows[pivot_row]
        lead = pivot_data[column] % p
        inv = pow(lead, -1, p)
        if lead != 1:
            # Normalize in place instead of allocating a replacement row.
            for index in tuple(pivot_data):
                value = (pivot_data[index] * inv) % p
                if value:
                    pivot_data[index] = value
                else:
                    del pivot_data[index]

        # Eliminate only below the pivot.  Mutate rows in place to avoid
        # work = dict(row) copies for every elimination step.
        for r in range(pivot_row + 1, nrows):
            row = rows[r]
            coeff = row.get(column, 0) % p
            if not coeff:
                continue
            for index, value in pivot_data.items():
                new_value = (row.get(index, 0) - coeff * value) % p
                if new_value:
                    row[index] = new_value
                else:
                    row.pop(index, None)

        pivot_row += 1
        if pivot_row >= nrows:
            break

    return pivot_row - int(pivot_row_start)


def sparse_constrained_target_rank(
    equations: Iterable[IBPEquation],
    forbidden: Iterable[IntegralIndex],
    targets: Iterable[IntegralIndex],
    prime: int,
) -> SparseConstrainedRank:
    """Compute constrained target rank without a dense forbidden+target matrix."""
    p = int(prime)
    forbidden = tuple(dict.fromkeys(forbidden))
    targets = tuple(dict.fromkeys(targets))
    forbidden_set = set(forbidden)
    target_set = set(targets)
    overlap = forbidden_set & target_set
    if overlap:
        raise ValueError(f"forbidden and target columns overlap: {len(overlap)}")

    allowed = forbidden_set | target_set
    rows, input_count = _project_rows(equations, allowed, p)
    projected_term_count = sum(len(row) for row in rows)

    forbidden_rank = _forward_eliminate_columns(rows, forbidden, p)

    # Rows below forbidden_rank span exactly the combinations with all pivoted
    # forbidden columns zero.  Because forward elimination processes every
    # forbidden column, no forbidden coefficient may remain there.
    residual: list[dict[IntegralIndex, int]] = []
    residual_term_count = 0
    for row in rows[forbidden_rank:]:
        if any(index in forbidden_set for index in row):
            raise RuntimeError("sparse forbidden elimination left a forbidden coefficient")
        # At this point rows contain target columns only.  Empty rows carry no
        # target-rank information and are dropped immediately.
        if row:
            residual.append(row)
            residual_term_count += len(row)

    target_rank = _forward_eliminate_columns(residual, targets, p)

    return SparseConstrainedRank(
        prime=p,
        forbidden_rank=forbidden_rank,
        target_rank=target_rank,
        conditional_free_dimension=len(targets) - target_rank,
        input_equation_count=input_count,
        projected_nonzero_row_count=len(rows),
        projected_term_count=projected_term_count,
        residual_row_count=len(residual),
        residual_term_count=residual_term_count,
    )
