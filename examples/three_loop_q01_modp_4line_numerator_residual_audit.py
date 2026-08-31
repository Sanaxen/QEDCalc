from __future__ import annotations

import json
from pathlib import Path

from qedcalc.operations.ibp import IntegralIndex
from three_loop.ibp_frontier import build_ibp_derivative_templates
from three_loop.integral_family import q01_integral_family
from three_loop.laporta_plan import physical_sector
from three_loop.modp_sector_residual_audit import audit_sector_residual_pivots
from three_loop.remaining_target_classification import full_numerator_degree

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_modp_4line_block_reduction.json"
OUTPUT = ROOT / "output" / "3loop_q01_modp_4line_numerator_residual_audit.json"
SOURCE_SECTOR = (1, 0, 1, 0, 1, 1, 0, 0, 0)


def stable_rhs_indices(data: dict) -> tuple[IntegralIndex, ...]:
    reductions = data.get("reductions", [])
    if not reductions:
        raise RuntimeError("block reduction JSON contains no reductions")
    per_prime = []
    for reduction in reductions:
        indices = {
            IntegralIndex(tuple(index))
            for rule in reduction["rules"]
            for index, _coefficient in rule["rhs"]
        }
        per_prime.append(indices)
    common = set.intersection(*per_prime)
    if any(indices != common for indices in per_prime):
        raise RuntimeError("RHS support differs across primes; numerator audit requires stable support")
    return tuple(sorted(common, key=lambda idx: idx.powers))


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    rhs = stable_rhs_indices(data)
    same_sector = tuple(
        index
        for index in rhs
        if physical_sector(index, 9) == SOURCE_SECTOR
    )
    numerator_targets = tuple(
        index for index in same_sector if full_numerator_degree(index, 9) > 0
    )

    if len(rhs) != 32:
        raise RuntimeError(f"expected 32 stable RHS integrals, got {len(rhs)}")
    if len(same_sector) != 28:
        raise RuntimeError(f"expected 28 same-sector RHS integrals, got {len(same_sector)}")
    if len(numerator_targets) != 28:
        raise RuntimeError(
            f"expected all 28 same-sector RHS integrals to be numerator-bearing, got {len(numerator_targets)}"
        )

    family = q01_integral_family()
    templates = build_ibp_derivative_templates(family)
    profile = audit_sector_residual_pivots(
        family,
        numerator_targets,
        templates=templates,
    )

    out = {
        "sector": SOURCE_SECTOR,
        "rhs_integral_count": len(rhs),
        "same_sector_numerator_count": len(numerator_targets),
        "direct_pivotable_count": profile.direct_pivotable_count,
        "reverse_only_pivotable_count": profile.reverse_only_pivotable_count,
        "rescued_count": profile.rescued_count,
        "unresolved_count": profile.unresolved_count,
        "target_indices": [index.powers for index in numerator_targets],
        "direct_pivotable_indices": profile.direct_pivotable_indices,
        "reverse_only_pivotable_indices": profile.reverse_only_pivotable_indices,
        "unresolved_indices": profile.unresolved_indices,
    }
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("QEDCalc Q01 four-line numerator residual pivot audit")
    print(f"sector: {SOURCE_SECTOR}")
    print(f"same-sector numerator residuals: {len(numerator_targets)}")
    print(f"direct pivotable: {profile.direct_pivotable_count}")
    print(f"reverse-only pivotable: {profile.reverse_only_pivotable_count}")
    print(f"rescued by direct/reverse: {profile.rescued_count}")
    print(f"still unresolved: {profile.unresolved_count}")
    print(f"generated: {OUTPUT}")
    print("Q01 four-line numerator residual pivot audit PASS")


if __name__ == "__main__":
    main()
