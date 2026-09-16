"""Kira project export for the Q05/Q42 canonical family."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import sympy as sp

from qedcalc.operations.ibp import sp_atom
from three_loop.canonical_family_bootstrap import (
    SP_BASIS,
    _rank,
    complete_with_quadratic_auxiliaries,
    deduplicate_exact_denominators,
    find_family_witness,
    topology_physical_denominators,
)
from three_loop.integral_family_classification import load_topologies
from three_loop.q01_family_equivalence import _square, _vec

Q05_KIRA_NAME = "Q05_full"
Q05_KIRA_TOP_SECTOR = 255
Q05_RAW_TO_UNIQUE = (1, 2, 3, 2, 4, 5, 6, 7, 8)
Q05_DUPLICATE_GROUPS = ((2, 4),)
Q05_AUXILIARY_NAMES = ("(k-l)^2", "(l-r)^2", "(l+q)^2", "(r+q)^2")
Q05_COVERED_DIAGRAMS = ("Q05", "Q42")


@dataclass(frozen=True)
class Q05SeedLimits:
    r: int = 8
    s: int = 3
    d: int = 0

    def __post_init__(self) -> None:
        if self.r < 8:
            raise ValueError("Q05 eight-line physical sector requires r >= 8")
        if self.s < 0 or self.d < 0:
            raise ValueError("Kira s and d limits must be non-negative")


def _rows() -> dict[str, dict[str, object]]:
    return {str(row["id"]): row for row in load_topologies()}


def _q05_row() -> dict[str, object]:
    return _rows()["Q05"]


def q05_unique_qed_denominators() -> tuple[sp.Expr, ...]:
    raw = topology_physical_denominators(_q05_row())
    unique, mapping, duplicates = deduplicate_exact_denominators(raw)
    if tuple(mapping) != Q05_RAW_TO_UNIQUE:
        raise ValueError(f"Q05 raw-to-unique mapping changed: {mapping}")
    if tuple(tuple(group) for group in duplicates) != Q05_DUPLICATE_GROUPS:
        raise ValueError(f"Q05 duplicate groups changed: {duplicates}")
    if len(unique) != 8 or _rank(unique) != 8:
        raise ValueError(
            f"Q05 unique physical basis changed: count={len(unique)} rank={_rank(unique)}"
        )
    return tuple(unique)


def _q05_auxiliary_data() -> tuple[tuple[str, ...], tuple[dict[str, sp.Expr], ...], tuple[sp.Expr, ...]]:
    unique = list(q05_unique_qed_denominators())
    names, vecs, exprs = complete_with_quadratic_auxiliaries(unique)
    if tuple(names) != Q05_AUXILIARY_NAMES:
        raise ValueError(f"Q05 auxiliary selection changed: {names}")
    return tuple(names), tuple(vecs), tuple(exprs)


def q05_kira_inverse_propagator_expressions() -> tuple[sp.Expr, ...]:
    physical = tuple(-expr for expr in q05_unique_qed_denominators())
    _, _, auxiliaries = _q05_auxiliary_data()
    return physical + auxiliaries


def validate_q05_family_equivalence() -> dict[str, object]:
    rows = _rows()
    reference = rows["Q05"]
    unique = list(q05_unique_qed_denominators())
    names, vecs, exprs = _q05_auxiliary_data()
    records: dict[str, object] = {}
    for diagram_id in Q05_COVERED_DIAGRAMS:
        witness = find_family_witness(rows[diagram_id], reference, unique, list(vecs), list(exprs))
        if witness is None:
            raise ValueError(f"{diagram_id}: no exact canonical-family witness to Q05")
        records[diagram_id] = witness.to_dict()
    return {
        "family": Q05_KIRA_NAME,
        "covered_diagrams": list(Q05_COVERED_DIAGRAMS),
        "auxiliary_names": list(names),
        "records": records,
        "all_exact": True,
    }


def validate_q05_kira_basis() -> dict[str, object]:
    expressions = q05_kira_inverse_propagator_expressions()
    rank = int(
        sp.Matrix(
            [[sp.expand(expr).coeff(atom) for atom in SP_BASIS] for expr in expressions]
        ).rank()
    )
    if len(expressions) != 12 or rank != 12:
        raise ValueError(
            f"Q05 Kira basis is not full rank: count={len(expressions)} rank={rank}/12"
        )
    equivalence = validate_q05_family_equivalence()
    return {
        "inverse_propagator_count": 12,
        "coefficient_matrix_rank": 12,
        "full_rank": True,
        "unique_physical_count": 8,
        "auxiliary_count": 4,
        "top_sector": Q05_KIRA_TOP_SECTOR,
        "family_equivalence_exact": bool(equivalence["all_exact"]),
    }


def render_q05_kira_integralfamilies_yaml() -> str:
    return """integralfamilies:
  - name: \"Q05_full\"
    loop_momenta: [k, l, r]
    top_level_sectors: [255]
    propagators:
      - [\"k-p-q\", \"m2\"]
      - [\"k-p\", \"m2\"]
      - [\"k+l-p\", \"m2\"]
      - [\"k+r-p\", \"m2\"]
      - [\"r-p\", \"m2\"]
      - [\"k\", 0]
      - [\"l\", 0]
      - [\"r\", 0]
      - [\"k-l\", 0]
      - [\"l-r\", 0]
      - [\"l+q\", 0]
      - [\"r+q\", 0]
"""


def render_q05_kira_kinematics_yaml() -> str:
    return """kinematics:
  outgoing_momenta: [p, q]
  kinematic_invariants:
    - [m2, 2]
    - [z, 0]
  scalarproduct_rules:
    - [[p,p], \"m2\"]
    - [[q,q], \"z*m2\"]
    - [[p,q], \"-z*m2/2\"]
  symbol_to_replace_by_one: m2
"""


def render_q05_kira_jobs_yaml(
    limits: Q05SeedLimits, *, back_substitution: bool = False
) -> str:
    back = "true" if back_substitution else "false"
    return f"""jobs:
  - reduce_sectors:
      reduce:
        - {{topologies: [Q05_full], sectors: [255], r: {limits.r}, s: {limits.s}, d: {limits.d}}}
      select_integrals:
        select_mandatory_recursively:
          - {{topologies: [Q05_full], sectors: [255], r: {limits.r}, s: {limits.s}, d: {limits.d}}}
      run_symmetries: true
      run_initiate: true
      run_triangular: sectorwise
      run_back_substitution: {back}
"""


def q05_kira_manifest(limits: Q05SeedLimits) -> dict[str, object]:
    return {
        "backend": "kira",
        "canonical_family": Q05_KIRA_NAME,
        "representative": "Q05",
        "covered_diagrams": list(Q05_COVERED_DIAGRAMS),
        "top_sector": Q05_KIRA_TOP_SECTOR,
        "seed_limits": {"r": limits.r, "s": limits.s, "d": limits.d},
        "basis_validation": validate_q05_kira_basis(),
        "family_equivalence": validate_q05_family_equivalence(),
        "raw_physical_to_unique_mapping": list(Q05_RAW_TO_UNIQUE),
        "duplicate_physical_groups": [list(g) for g in Q05_DUPLICATE_GROUPS],
        "auxiliary_names": list(Q05_AUXILIARY_NAMES),
        "physical_sign_convention": (
            "Kira P1..P8 = -QEDCalc unique physical denominators; "
            "P9..P12 are positive quadratic auxiliaries."
        ),
        "status": "preflight_only_until_local_Kira_master_and_boundary_audits_pass",
    }


def export_q05_kira_project(
    root: str | Path,
    *,
    limits: Q05SeedLimits = Q05SeedLimits(),
    back_substitution: bool = False,
) -> Path:
    root = Path(root)
    config = root / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "integralfamilies.yaml").write_text(
        render_q05_kira_integralfamilies_yaml(), encoding="utf-8", newline="\n"
    )
    (config / "kinematics.yaml").write_text(
        render_q05_kira_kinematics_yaml(), encoding="utf-8", newline="\n"
    )
    (root / "jobs.yaml").write_text(
        render_q05_kira_jobs_yaml(limits, back_substitution=back_substitution),
        encoding="utf-8",
        newline="\n",
    )
    (root / "qedcalc_kira_manifest.json").write_text(
        json.dumps(q05_kira_manifest(limits), indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )
    return root
