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

The probe-aware entry point also performs substitution only for coefficients in
the forbidden+target projection.  This avoids materializing a second complete
specialized IBP system in memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

import sympy as sp

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


def _specialize_coeff_at_probe(coeff, point, values_by_name):
    """Apply the same two-stage Q01 probe substitution without copying a system."""
    expr = sp.sympify(coeff)
    if point:
        expr = expr.subs(point)
    if expr.free_symbols:
        remaining = {
            symbol: values_by_name[str(symbol)]
            for symbol in expr.free_symbols
            if str(symbol) in values_by_name
        }
        if remaining:
            expr = expr.subs(remaining)
    return sp.cancel(expr)


def _project_rows(
    equations: Iterable[IBPEquation],
    allowed: set[IntegralIndex],
    prime: int,
    *,
    point: Mapping | None = None,
) -> tuple[list[dict[IntegralIndex, int]], int]:
    """Project equations directly to a sparse mod-p row representation.

    When ``point`` is supplied, coefficients are specialized only after their
    integral column is known to belong to the requested projection.
    """
    p = int(prime)
    rows: list[dict[IntegralIndex, int]] = []
    input_count = 0
    values_by_name = (
        {str(symbol): sp.sympify(value) for symbol, value in point.items()}
        if point
        else {}
    )

    for equation in equations:
        input_count += 1
        row: dict[IntegralIndex, int] = {}
        for index, coeff in equation.terms.items():
            if index not in allowed:
                continue
            value_expr = (
                _specialize_coeff_at_probe(coeff, point, values_by_name)
                if point is not None
                else coeff
            )
            value = int(_rational_mod_p(value_expr, p)) % p
            if value:
                row[index] = value
        if row:
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


def _run_sparse_rank(
    equations: Iterable[IBPEquation],
    forbidden: Iterable[IntegralIndex],
    targets: Iterable[IntegralIndex],
    prime: int,
    *,
    point: Mapping | None,
) -> SparseConstrainedRank:
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

    forbidden_rank = _forward_eliminate_columns(rows, forbidden, p)

    residual: list[dict[IntegralIndex, int]] = []
    residual_term_count = 0
    for row in rows[forbidden_rank:]:
        if any(index in forbidden_set for index in row):
            raise RuntimeError("sparse forbidden elimination left a forbidden coefficient")
        if row:
            residual.append(row)
            residual_term_count += len(row)

    # Drop the large prefix as soon as the residual view has been extracted.
    rows.clear()

    target_rank = _forward_eliminate_columns(residual, targets, p)

    return SparseConstrainedRank(
        prime=p,
        forbidden_rank=forbidden_rank,
        target_rank=target_rank,
        conditional_free_dimension=len(targets) - target_rank,
        input_equation_count=input_count,
        projected_nonzero_row_count=forbidden_rank + len(residual),
        projected_term_count=projected_term_count,
        residual_row_count=len(residual),
        residual_term_count=residual_term_count,
    )


def sparse_constrained_target_rank(
    equations: Iterable[IBPEquation],
    forbidden: Iterable[IntegralIndex],
    targets: Iterable[IntegralIndex],
    prime: int,
) -> SparseConstrainedRank:
    """Compute constrained target rank from already-specialized equations."""
    return _run_sparse_rank(
        equations,
        forbidden,
        targets,
        prime,
        point=None,
    )


def sparse_constrained_target_rank_at_probe(
    equations: Iterable[IBPEquation],
    forbidden: Iterable[IntegralIndex],
    targets: Iterable[IntegralIndex],
    point: Mapping,
    prime: int,
) -> SparseConstrainedRank:
    """Specialize only projected coefficients and compute constrained rank.

    This is the preferred entry point for very large Q01 audits because it
    avoids building ``specialize_ibp_system(equations, point)`` and therefore
    avoids keeping symbolic and fully-specialized copies of the entire IBP
    system at the same time.
    """
    return _run_sparse_rank(
        equations,
        forbidden,
        targets,
        prime,
        point=point,
    )
