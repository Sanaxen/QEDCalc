"""Finite-field block reduction for a small candidate integral block.

Given a homogeneous IBP system and a selected block of integrals whose
restricted coefficient matrix has full column rank, choose independent rows,
invert the block matrix modulo a prime, and express every block integral as a
linear combination of integrals outside the block.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from qedcalc.operations.ibp import IBPEquation, IntegralIndex
from .sector_local_modp import _rational_mod_p


@dataclass(frozen=True)
class ModPBlockRule:
    target: tuple[int, ...]
    rhs: tuple[tuple[tuple[int, ...], int], ...]

    @property
    def rhs_term_count(self) -> int:
        return len(self.rhs)


@dataclass(frozen=True)
class ModPBlockReduction:
    prime: int
    block_size: int
    selected_row_count: int
    outside_integral_count: int
    rules: tuple[ModPBlockRule, ...]


def _row_vector(equation: IBPEquation, block: Sequence[IntegralIndex], prime: int) -> list[int]:
    return [int(_rational_mod_p(equation.terms.get(index, 0), prime)) % prime for index in block]


def _select_independent_rows(
    equations: Sequence[IBPEquation], block: Sequence[IntegralIndex], prime: int
) -> tuple[int, ...]:
    """Select block_size rows whose block-restricted vectors are independent."""
    basis: list[tuple[int, list[int]]] = []
    selected: list[int] = []
    width = len(block)
    for row_no, equation in enumerate(equations):
        vec = _row_vector(equation, block, prime)
        work = vec[:]
        for pivot_col, basis_row in basis:
            coeff = work[pivot_col] % prime
            if coeff:
                work = [(a - coeff * b) % prime for a, b in zip(work, basis_row)]
        pivot = next((j for j, value in enumerate(work) if value % prime), None)
        if pivot is None:
            continue
        inv = pow(work[pivot] % prime, -1, prime)
        work = [(value * inv) % prime for value in work]
        for n, (pivot_col, basis_row) in enumerate(basis):
            coeff = basis_row[pivot] % prime
            if coeff:
                basis[n] = (
                    pivot_col,
                    [(a - coeff * b) % prime for a, b in zip(basis_row, work)],
                )
        basis.append((pivot, work))
        basis.sort(key=lambda item: item[0])
        selected.append(row_no)
        if len(basis) == width:
            return tuple(selected)
    raise ValueError(f"restricted block rank is {len(basis)}, expected {width}")


def _invert_matrix_mod_p(matrix: Sequence[Sequence[int]], prime: int) -> list[list[int]]:
    n = len(matrix)
    aug = [
        [int(value) % prime for value in row]
        + [1 if i == j else 0 for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col] % prime), None)
        if pivot is None:
            raise ValueError("selected block matrix is singular modulo prime")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        inv = pow(aug[col][col] % prime, -1, prime)
        aug[col] = [(value * inv) % prime for value in aug[col]]
        for row in range(n):
            if row == col:
                continue
            coeff = aug[row][col] % prime
            if coeff:
                aug[row] = [
                    (a - coeff * b) % prime for a, b in zip(aug[row], aug[col])
                ]
    return [row[n:] for row in aug]


def reduce_block_mod_p(
    equations: Iterable[IBPEquation],
    block: Iterable[IntegralIndex],
    prime: int,
) -> ModPBlockReduction:
    equations = tuple(equations)
    block = tuple(dict.fromkeys(block))
    if not block:
        raise ValueError("block reduction requires at least one target")
    p = int(prime)
    selected = _select_independent_rows(equations, block, p)
    chosen = tuple(equations[i] for i in selected)
    block_set = set(block)

    matrix = [_row_vector(equation, block, p) for equation in chosen]
    inverse = _invert_matrix_mod_p(matrix, p)

    outside = tuple(sorted(
        {index for equation in chosen for index in equation.terms if index not in block_set},
        key=lambda index: index.powers,
    ))
    outside_pos = {index: j for j, index in enumerate(outside)}
    rhs_rows = [[0 for _ in outside] for _ in chosen]
    for i, equation in enumerate(chosen):
        for index, coeff in equation.terms.items():
            if index in block_set:
                continue
            rhs_rows[i][outside_pos[index]] = int(_rational_mod_p(coeff, p)) % p

    rules = []
    for target_no, target in enumerate(block):
        rhs_terms = []
        for outside_no, outside_index in enumerate(outside):
            coefficient = 0
            for row_no in range(len(block)):
                coefficient -= inverse[target_no][row_no] * rhs_rows[row_no][outside_no]
            coefficient %= p
            if coefficient:
                rhs_terms.append((outside_index.powers, coefficient))
        rules.append(ModPBlockRule(target=target.powers, rhs=tuple(rhs_terms)))

    return ModPBlockReduction(
        prime=p,
        block_size=len(block),
        selected_row_count=len(selected),
        outside_integral_count=len(outside),
        rules=tuple(rules),
    )


def rule_support_signature(reduction: ModPBlockReduction) -> tuple[tuple[tuple[int, ...], ...], ...]:
    return tuple(tuple(index for index, _ in rule.rhs) for rule in reduction.rules)
