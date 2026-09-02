"""Memory-efficient constrained free-column extraction over a finite field.

This companion to modp_sparse_constrained_rank records which target columns do
not receive pivots after forbidden-column elimination.  It uses the same sparse
forward-elimination strategy and therefore avoids dense forbidden+target
matrices and full RREF construction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from .modp_sparse_constrained_rank import _forward_eliminate_columns, _project_rows


@dataclass(frozen=True)
class SparseConstrainedFreeColumns:
    prime: int
    forbidden_rank: int
    target_rank: int
    conditional_free_dimension: int
    free_columns: tuple[IntegralIndex, ...]
    pivot_columns: tuple[IntegralIndex, ...]
    input_equation_count: int
    projected_nonzero_row_count: int
    projected_term_count: int
    residual_row_count: int
    residual_term_count: int


def _forward_eliminate_columns_with_pivots(
    rows: list[dict[IntegralIndex, int]],
    columns: tuple[IntegralIndex, ...],
    prime: int,
) -> tuple[int, tuple[IntegralIndex, ...]]:
    """Forward eliminate selected columns and return the actual pivot columns."""
    p = int(prime)
    pivot_row = 0
    nrows = len(rows)
    pivots: list[IntegralIndex] = []

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
            for index in tuple(pivot_data):
                value = (pivot_data[index] * inv) % p
                if value:
                    pivot_data[index] = value
                else:
                    del pivot_data[index]

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

        pivots.append(column)
        pivot_row += 1
        if pivot_row >= nrows:
            break

    return pivot_row, tuple(pivots)


def sparse_constrained_free_columns_at_probe(
    equations: Iterable[IBPEquation],
    forbidden: Iterable[IntegralIndex],
    targets: Iterable[IntegralIndex],
    point: Mapping,
    prime: int,
) -> SparseConstrainedFreeColumns:
    """Return deterministic free target columns after forbidden elimination."""
    p = int(prime)
    forbidden = tuple(dict.fromkeys(forbidden))
    targets = tuple(dict.fromkeys(targets))
    forbidden_set = set(forbidden)
    target_set = set(targets)
    overlap = forbidden_set & target_set
    if overlap:
        raise ValueError(f"forbidden and target columns overlap: {len(overlap)}")

    allowed = forbidden_set | target_set
    rows, input_count = _project_rows(equations, allowed, p, point=point)
    projected_term_count = sum(len(row) for row in rows)
    projected_nonzero_row_count = len(rows)

    forbidden_rank = _forward_eliminate_columns(rows, forbidden, p)

    residual: list[dict[IntegralIndex, int]] = []
    residual_term_count = 0
    for row in rows[forbidden_rank:]:
        if any(index in forbidden_set for index in row):
            raise RuntimeError("sparse forbidden elimination left a forbidden coefficient")
        if row:
            residual.append(row)
            residual_term_count += len(row)
    rows.clear()

    target_rank, pivot_columns = _forward_eliminate_columns_with_pivots(
        residual, targets, p
    )
    pivot_set = set(pivot_columns)
    free_columns = tuple(index for index in targets if index not in pivot_set)

    return SparseConstrainedFreeColumns(
        prime=p,
        forbidden_rank=forbidden_rank,
        target_rank=target_rank,
        conditional_free_dimension=len(free_columns),
        free_columns=free_columns,
        pivot_columns=pivot_columns,
        input_equation_count=input_count,
        projected_nonzero_row_count=projected_nonzero_row_count,
        projected_term_count=projected_term_count,
        residual_row_count=len(residual),
        residual_term_count=residual_term_count,
    )
