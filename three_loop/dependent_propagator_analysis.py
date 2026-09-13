"""Exact linear/affine relation analysis for dependent Q propagators.

Some three-loop quenched Q topologies contain nine physical propagators whose
scalar-product coefficient rank is below nine.  Such a graph is still a valid
reflection family, but a standard Kira family first needs the redundant
propagators to be eliminated/partial-fractioned.

This module finds a deterministic independent subset of physical denominators
and writes every remaining denominator as

    D_dep = sum_i c_i D_i + invariant_shift,

where the coefficients are exact SymPy rationals and ``invariant_shift``
contains no loop scalar products.  These identities are the input needed for a
later preprocessing/partial-fraction stage; this module itself does not modify
integrals.
"""
from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from three_loop.family_sharing_algebraic import SP_ATOMS, q_physical_denominators
from three_loop.registry import ThreeLoopTopology


def _sp_row(expr: sp.Expr) -> list[sp.Expr]:
    expanded = sp.expand(expr)
    return [expanded.coeff(atom) for atom in SP_ATOMS]


def _loop_free_part(expr: sp.Expr) -> sp.Expr:
    out = sp.expand(expr)
    for atom in SP_ATOMS:
        out = out.subs(atom, 0)
    return sp.factor(sp.simplify(out))


def _pivot_row_indices(rows: list[list[sp.Expr]]) -> tuple[int, ...]:
    """Return deterministic independent row indices using pivots of A.T."""
    if not rows:
        return ()
    matrix = sp.Matrix(rows)
    _rref, pivots = matrix.T.rref()
    return tuple(int(i) for i in pivots)


@dataclass(frozen=True)
class DependentPropagatorRelation:
    dependent_index: int
    independent_coefficients: tuple[tuple[int, sp.Expr], ...]
    invariant_shift: sp.Expr

    @property
    def homogeneous(self) -> bool:
        return sp.simplify(self.invariant_shift) == 0

    def as_dict(self) -> dict[str, object]:
        return {
            "dependent_index": self.dependent_index,
            "independent_coefficients": [
                {"index": index, "coefficient": str(sp.factor(coeff))}
                for index, coeff in self.independent_coefficients
            ],
            "invariant_shift": str(sp.factor(self.invariant_shift)),
            "homogeneous": self.homogeneous,
        }

    def identity_string(self) -> str:
        pieces: list[str] = []
        for index, coeff in self.independent_coefficients:
            pieces.append(f"({sp.factor(coeff)})*D{index}")
        rhs = " + ".join(pieces) if pieces else "0"
        shift = sp.factor(self.invariant_shift)
        if shift != 0:
            rhs += f" + ({shift})"
        return f"D{self.dependent_index} = {rhs}"


@dataclass(frozen=True)
class DependentPropagatorAnalysis:
    diagram_id: str
    physical_rank: int
    independent_indices: tuple[int, ...]
    dependent_indices: tuple[int, ...]
    relations: tuple[DependentPropagatorRelation, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "diagram_id": self.diagram_id,
            "physical_rank": self.physical_rank,
            "independent_indices": list(self.independent_indices),
            "dependent_indices": list(self.dependent_indices),
            "relation_count": len(self.relations),
            "homogeneous_relation_count": sum(r.homogeneous for r in self.relations),
            "affine_relation_count": sum(not r.homogeneous for r in self.relations),
            "relations": [
                {**relation.as_dict(), "identity": relation.identity_string()}
                for relation in self.relations
            ],
        }


def analyze_dependent_physical_propagators(
    topology: ThreeLoopTopology,
) -> DependentPropagatorAnalysis:
    """Find exact redundant-propagator identities for one quenched Q graph."""
    denominators = q_physical_denominators(topology)
    rows = [_sp_row(expr) for expr in denominators]
    independent_zero = _pivot_row_indices(rows)
    independent_indices = tuple(i + 1 for i in independent_zero)
    dependent_zero = tuple(i for i in range(len(rows)) if i not in independent_zero)
    dependent_indices = tuple(i + 1 for i in dependent_zero)

    basis_matrix = sp.Matrix([rows[i] for i in independent_zero])
    basis_t = basis_matrix.T
    relations: list[DependentPropagatorRelation] = []

    for dep_zero in dependent_zero:
        target = sp.Matrix(rows[dep_zero])
        solution_set = sp.linsolve((basis_t, target))
        solutions = list(solution_set)
        if len(solutions) != 1:
            raise ValueError(
                f"{topology.diagram_id}: could not solve dependent D{dep_zero + 1} uniquely"
            )
        coeffs = tuple(sp.factor(c) for c in solutions[0])
        reconstructed = sp.Integer(0)
        coefficient_pairs: list[tuple[int, sp.Expr]] = []
        for basis_zero, coeff in zip(independent_zero, coeffs):
            if coeff == 0:
                continue
            reconstructed += coeff * denominators[basis_zero]
            coefficient_pairs.append((basis_zero + 1, coeff))
        shift = sp.factor(sp.simplify(denominators[dep_zero] - reconstructed))
        if any(shift.has(atom) for atom in SP_ATOMS):
            raise ValueError(
                f"{topology.diagram_id}: residual for D{dep_zero + 1} still contains loop scalar products"
            )
        relations.append(
            DependentPropagatorRelation(
                dependent_index=dep_zero + 1,
                independent_coefficients=tuple(coefficient_pairs),
                invariant_shift=shift,
            )
        )

    return DependentPropagatorAnalysis(
        diagram_id=topology.diagram_id,
        physical_rank=len(independent_indices),
        independent_indices=independent_indices,
        dependent_indices=dependent_indices,
        relations=tuple(relations),
    )
