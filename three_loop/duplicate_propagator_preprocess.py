"""Preprocess rank-deficient Q families by merging exactly duplicate propagators."""
from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from qedcalc.operations.denominator_normalization import DuplicateDenominatorRule
from three_loop.dependent_propagator_analysis import (
    DependentPropagatorAnalysis,
    analyze_dependent_physical_propagators,
)
from three_loop.family_sharing_algebraic import q_physical_denominators
from three_loop.registry import ThreeLoopTopology


@dataclass(frozen=True)
class DuplicatePropagatorPlan:
    diagram_id: str
    physical_rank: int
    independent_indices: tuple[int, ...]
    duplicate_rules: tuple[DuplicateDenominatorRule, ...]
    extra_isp_slots_needed: int

    def as_dict(self) -> dict[str, object]:
        return {
            "diagram_id": self.diagram_id,
            "physical_rank": self.physical_rank,
            "independent_indices": list(self.independent_indices),
            "duplicate_rules": [
                {
                    "dependent_index": rule.dependent_index,
                    "keep_index": rule.keep_index,
                    "scale": str(sp.factor(rule.scale)),
                }
                for rule in self.duplicate_rules
            ],
            "extra_isp_slots_needed": self.extra_isp_slots_needed,
            "post_merge_physical_count": len(self.independent_indices),
            "preprocessing_kind": "exact_duplicate_exponent_merge",
        }


def build_duplicate_propagator_plan(topology: ThreeLoopTopology) -> DuplicatePropagatorPlan:
    """Build and verify a simple merge plan when all dependencies are exact duplicates."""
    analysis: DependentPropagatorAnalysis = analyze_dependent_physical_propagators(topology)
    denominators = q_physical_denominators(topology)
    rules: list[DuplicateDenominatorRule] = []

    for relation in analysis.relations:
        if not relation.homogeneous:
            raise ValueError(
                f"{topology.diagram_id}: D{relation.dependent_index} has an affine dependency"
            )
        nonzero = [
            (index, sp.factor(coeff))
            for index, coeff in relation.independent_coefficients
            if sp.simplify(coeff) != 0
        ]
        if len(nonzero) != 1:
            raise ValueError(
                f"{topology.diagram_id}: D{relation.dependent_index} is not a single-denominator duplicate"
            )
        keep_index, scale = nonzero[0]
        dep_expr = denominators[relation.dependent_index - 1]
        keep_expr = denominators[keep_index - 1]
        if sp.simplify(dep_expr - scale * keep_expr) != 0:
            raise ValueError(
                f"{topology.diagram_id}: symbolic duplicate verification failed for D{relation.dependent_index}"
            )
        rules.append(
            DuplicateDenominatorRule(
                dependent_index=relation.dependent_index,
                keep_index=keep_index,
                scale=scale,
            )
        )

    if len(rules) != 9 - analysis.physical_rank:
        raise ValueError(
            f"{topology.diagram_id}: expected {9 - analysis.physical_rank} duplicate rules, got {len(rules)}"
        )

    return DuplicatePropagatorPlan(
        diagram_id=topology.diagram_id,
        physical_rank=analysis.physical_rank,
        independent_indices=analysis.independent_indices,
        duplicate_rules=tuple(rules),
        extra_isp_slots_needed=12 - analysis.physical_rank,
    )
