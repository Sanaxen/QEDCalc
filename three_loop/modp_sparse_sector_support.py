"""Memory-efficient same-sector RHS support extraction for a full-rank block.

For closure we do not need the full finite-field inverse of the target block.
It is enough to know which same-sector outside columns survive in the chosen
full-rank target row space after forbidden columns have been eliminated.

If B is the square full-rank target matrix and C the same-sector outside block,
then the actual rules contain -B^{-1} C.  Since B^{-1} is invertible, a column
of C is zero iff the corresponding column of -B^{-1} C is zero.  Therefore the
union of same-sector RHS support can be read from any full-rank target row basis
without constructing B^{-1}.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

import sympy as sp

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from .sector_local_modp import _rational_mod_p


@dataclass(frozen=True)
class SparseSectorSupportResult:
    prime: int
    forbidden_rank: int
    target_rank: int
    conditional_free_dimension: int
    input_equation_count: int
    projected_nonzero_row_count: int
    projected_term_count: int
    residual_row_count: int
    selected_row_count: int
    same_sector_support: tuple[IntegralIndex, ...]


def _coefficient_mod_p(
    coeff,
    prime: int,
    values_by_name: Mapping[str, sp.Expr] | None = None,
) -> int:
    value = sp.sympify(coeff)
    if values_by_name:
        remaining = {
            symbol: values_by_name[str(symbol)]
            for symbol in value.free_symbols
            if str(symbol) in values_by_name
        }
        if remaining:
            value = value.subs(remaining)
    return int(_rational_mod_p(value, int(prime))) % int(prime)


def _project_rows(
    equations: Iterable[IBPEquation],
    allowed: set[IntegralIndex],
    prime: int,
    *,
    probe_point: Mapping[sp.Symbol, sp.Expr] | None = None,
) -> tuple[list[dict[IntegralIndex, int]], int, int]:
    p = int(prime)
    values_by_name = None
    if probe_point is not None:
        values_by_name = {str(symbol): sp.sympify(value) for symbol, value in probe_point.items()}

    rows: list[dict[IntegralIndex, int]] = []
    input_count = 0
    term_count = 0
    for equation in equations:
        input_count += 1
        row: dict[IntegralIndex, int] = {}
        for index, coeff in equation.terms.items():
            if index not in allowed:
                continue
            value = _coefficient_mod_p(coeff, p, values_by_name)
            if value:
                row[index] = value
        if row:
            term_count += len(row)
            rows.append(row)
    return rows, input_count, term_count


def _forward_eliminate(
    rows: list[dict[IntegralIndex, int]],
    columns: tuple[IntegralIndex, ...],
    prime: int,
    *,
    pivot_row_start: int = 0,
) -> int:
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
        pivot_row += 1
        if pivot_row >= nrows:
            break
    return pivot_row - int(pivot_row_start)


def sparse_same_sector_support(
    equations: Iterable[IBPEquation],
    forbidden: Iterable[IntegralIndex],
    targets: Iterable[IntegralIndex],
    same_sector_outside: Iterable[IntegralIndex],
    prime: int,
    *,
    probe_point: Mapping[sp.Symbol, sp.Expr] | None = None,
) -> SparseSectorSupportResult:
    """Return union support of same-sector outside columns for a full-rank target block."""
    p = int(prime)
    forbidden = tuple(dict.fromkeys(forbidden))
    targets = tuple(dict.fromkeys(targets))
    outside = tuple(dict.fromkeys(same_sector_outside))

    forbidden_set = set(forbidden)
    target_set = set(targets)
    outside_set = set(outside)
    if forbidden_set & target_set:
        raise ValueError("forbidden and target columns overlap")
    if outside_set & (forbidden_set | target_set):
        raise ValueError("same-sector outside columns overlap forbidden/target columns")

    allowed = forbidden_set | target_set | outside_set
    rows, input_count, projected_terms = _project_rows(
        equations, allowed, p, probe_point=probe_point
    )
    projected_row_count = len(rows)

    forbidden_rank = _forward_eliminate(rows, forbidden, p)
    residual = []
    for row in rows[forbidden_rank:]:
        if any(index in forbidden_set for index in row):
            raise RuntimeError("forbidden elimination left a forbidden coefficient")
        if row:
            residual.append(row)

    target_rank = _forward_eliminate(residual, targets, p)
    selected = residual[:target_rank]
    support = tuple(
        sorted(
            {index for row in selected for index in row if index in outside_set},
            key=lambda index: index.powers,
        )
    )

    return SparseSectorSupportResult(
        prime=p,
        forbidden_rank=forbidden_rank,
        target_rank=target_rank,
        conditional_free_dimension=len(targets) - target_rank,
        input_equation_count=input_count,
        projected_nonzero_row_count=projected_row_count,
        projected_term_count=projected_terms,
        residual_row_count=len(residual),
        selected_row_count=len(selected),
        same_sector_support=support,
    )
