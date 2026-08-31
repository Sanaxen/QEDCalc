"""Conservative exact symmetry search for the finite-q Q01 physical denominator family.

Only signed permutations of the loop variables (k,l,r) are admitted. External
momenta p,q are held fixed. A candidate is accepted only when every transformed
physical denominator is exactly one of D1..D9, with no rescaling or invariant
specialization. This deliberately under-approximates the full change-of-variable
symmetry group, but every accepted symmetry is exact.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product
from typing import Iterable

import sympy as sp

from qedcalc.operations.ibp import IntegralIndex, sp_atom
from .integral_family import q01_denominator_expressions

LOOPS = ("k", "l", "r")
EXTERNALS = ("p", "q")
PHYSICAL_COUNT = 9


@dataclass(frozen=True)
class Q01ExactSymmetry:
    loop_images: tuple[str, str, str]
    loop_signs: tuple[int, int, int]
    physical_permutation: tuple[int, ...]

    def apply_scalar_index(self, index: IntegralIndex) -> IntegralIndex:
        if len(index.powers) != 12:
            raise ValueError("Q01 index must have 12 powers")
        out = [0] * 12
        for source, target in enumerate(self.physical_permutation):
            out[target] = index.powers[source]
        out[9:] = index.powers[9:]
        return IntegralIndex(tuple(out))


def _transform_sp_atom(atom: sp.Symbol, mapping: dict[str, tuple[int, str]]) -> sp.Expr:
    name = str(atom)
    if not name.startswith("SP__"):
        return atom
    _, a, b = name.split("__", 2)
    sa, aa = mapping.get(a, (1, a))
    sb, bb = mapping.get(b, (1, b))
    return sp.Integer(sa * sb) * sp_atom(aa, bb)


def _transform_expr(expr: sp.Expr, mapping: dict[str, tuple[int, str]]) -> sp.Expr:
    replacements = {
        atom: _transform_sp_atom(atom, mapping)
        for atom in expr.free_symbols
        if str(atom).startswith("SP__")
    }
    return sp.expand(expr.xreplace(replacements))


def discover_q01_exact_signed_loop_symmetries() -> tuple[Q01ExactSymmetry, ...]:
    physical = tuple(sp.expand(expr) for expr in q01_denominator_expressions()[:PHYSICAL_COUNT])
    symmetries = []
    for perm in permutations(LOOPS):
        for signs in product((-1, 1), repeat=3):
            mapping = {
                source: (sign, target)
                for source, sign, target in zip(LOOPS, signs, perm)
            }
            transformed = tuple(_transform_expr(expr, mapping) for expr in physical)
            target_slots = []
            valid = True
            used = set()
            for expr in transformed:
                matches = [j for j, candidate in enumerate(physical) if sp.expand(expr - candidate) == 0]
                if len(matches) != 1 or matches[0] in used:
                    valid = False
                    break
                used.add(matches[0])
                target_slots.append(matches[0])
            if valid:
                symmetries.append(Q01ExactSymmetry(
                    loop_images=tuple(perm),
                    loop_signs=tuple(int(s) for s in signs),
                    physical_permutation=tuple(target_slots),
                ))
    return tuple(sorted(
        symmetries,
        key=lambda s: (s.physical_permutation, s.loop_images, s.loop_signs),
    ))


def canonicalize_scalar_under_exact_symmetry(
    index: IntegralIndex,
    symmetries: Iterable[Q01ExactSymmetry],
) -> IntegralIndex:
    orbit = [sym.apply_scalar_index(index) for sym in symmetries]
    return min(orbit, key=lambda idx: idx.powers) if orbit else index
