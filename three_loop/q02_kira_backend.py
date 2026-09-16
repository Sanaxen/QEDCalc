"""Kira project export for the Q02/Q45 canonical family."""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
import sympy as sp
from qedcalc.operations.ibp import sp_atom
from three_loop.canonical_family_bootstrap import SP_BASIS, _rank, deduplicate_exact_denominators, topology_physical_denominators
from three_loop.integral_family_classification import load_topologies
from three_loop.q01_family_equivalence import _square, _vec

Q02_KIRA_NAME = "Q02_full"
Q02_KIRA_TOP_SECTOR = 255
Q02_RAW_TO_UNIQUE = (1, 2, 3, 4, 5, 4, 6, 7, 8)
Q02_DUPLICATE_GROUPS = ((4, 6),)
Q02_AUXILIARY_NAMES = ("(k-r)^2", "(l-r)^2", "(l+q)^2", "(r+q)^2")

@dataclass(frozen=True)
class Q02SeedLimits:
    r: int = 8
    s: int = 3
    d: int = 0
    def __post_init__(self) -> None:
        if self.r < 8:
            raise ValueError("Q02 eight-line physical sector requires r >= 8")
        if self.s < 0 or self.d < 0:
            raise ValueError("Kira s and d limits must be non-negative")

def _q02_row() -> dict[str, object]:
    return next(row for row in load_topologies() if row.get("id") == "Q02")

def q02_unique_qed_denominators() -> tuple[sp.Expr, ...]:
    raw = topology_physical_denominators(_q02_row())
    unique, mapping, duplicates = deduplicate_exact_denominators(raw)
    if tuple(mapping) != Q02_RAW_TO_UNIQUE:
        raise ValueError(f"Q02 raw-to-unique mapping changed: {mapping}")
    if tuple(tuple(group) for group in duplicates) != Q02_DUPLICATE_GROUPS:
        raise ValueError(f"Q02 duplicate groups changed: {duplicates}")
    if len(unique) != 8 or _rank(unique) != 8:
        raise ValueError(f"Q02 unique physical basis changed: count={len(unique)} rank={_rank(unique)}")
    return tuple(unique)

def q02_kira_inverse_propagator_expressions() -> tuple[sp.Expr, ...]:
    physical = tuple(-expr for expr in q02_unique_qed_denominators())
    auxiliaries = (
        sp.expand(_square(_vec(k=1, r=-1))),
        sp.expand(_square(_vec(l=1, r=-1))),
        sp.expand(_square(_vec(l=1, q=1))),
        sp.expand(_square(_vec(r=1, q=1))),
    )
    return physical + auxiliaries

def validate_q02_kira_basis() -> dict[str, object]:
    expressions = q02_kira_inverse_propagator_expressions()
    rank = int(sp.Matrix([[sp.expand(expr).coeff(atom) for atom in SP_BASIS] for expr in expressions]).rank())
    if len(expressions) != 12 or rank != 12:
        raise ValueError(f"Q02 Kira basis is not full rank: count={len(expressions)} rank={rank}/12")
    return {"inverse_propagator_count": 12, "coefficient_matrix_rank": 12, "full_rank": True, "unique_physical_count": 8, "auxiliary_count": 4, "top_sector": Q02_KIRA_TOP_SECTOR}

def render_q02_kira_integralfamilies_yaml() -> str:
    return """integralfamilies:
  - name: \"Q02_full\"
    loop_momenta: [k, l, r]
    top_level_sectors: [255]
    propagators:
      - [\"k-p-q\", \"m2\"]
      - [\"k-p\", \"m2\"]
      - [\"k+l-p\", \"m2\"]
      - [\"l-p\", \"m2\"]
      - [\"l+r-p\", \"m2\"]
      - [\"k\", 0]
      - [\"l\", 0]
      - [\"r\", 0]
      - [\"k-r\", 0]
      - [\"l-r\", 0]
      - [\"l+q\", 0]
      - [\"r+q\", 0]
"""

def render_q02_kira_kinematics_yaml() -> str:
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

def render_q02_kira_jobs_yaml(limits: Q02SeedLimits, *, back_substitution: bool = False) -> str:
    back = "true" if back_substitution else "false"
    return f"""jobs:
  - reduce_sectors:
      reduce:
        - {{topologies: [Q02_full], sectors: [255], r: {limits.r}, s: {limits.s}, d: {limits.d}}}
      select_integrals:
        select_mandatory_recursively:
          - {{topologies: [Q02_full], sectors: [255], r: {limits.r}, s: {limits.s}, d: {limits.d}}}
      run_symmetries: true
      run_initiate: true
      run_triangular: sectorwise
      run_back_substitution: {back}
"""

def q02_kira_manifest(limits: Q02SeedLimits) -> dict[str, object]:
    return {"backend":"kira","canonical_family":Q02_KIRA_NAME,"representative":"Q02","covered_diagrams":["Q02","Q45"],"top_sector":Q02_KIRA_TOP_SECTOR,"seed_limits":{"r":limits.r,"s":limits.s,"d":limits.d},"basis_validation":validate_q02_kira_basis(),"raw_physical_to_unique_mapping":list(Q02_RAW_TO_UNIQUE),"duplicate_physical_groups":[list(g) for g in Q02_DUPLICATE_GROUPS],"auxiliary_names":list(Q02_AUXILIARY_NAMES),"physical_sign_convention":"Kira P1..P8 = -QEDCalc unique physical denominators; P9..P12 are positive quadratic auxiliaries.","status":"preflight_only_until_local_Kira_master_and_boundary_audits_pass"}

def export_q02_kira_project(root: str | Path, *, limits: Q02SeedLimits = Q02SeedLimits(), back_substitution: bool = False) -> Path:
    root = Path(root); config = root / "config"; config.mkdir(parents=True, exist_ok=True)
    (config / "integralfamilies.yaml").write_text(render_q02_kira_integralfamilies_yaml(), encoding="utf-8", newline="\n")
    (config / "kinematics.yaml").write_text(render_q02_kira_kinematics_yaml(), encoding="utf-8", newline="\n")
    (root / "jobs.yaml").write_text(render_q02_kira_jobs_yaml(limits, back_substitution=back_substitution), encoding="utf-8", newline="\n")
    (root / "qedcalc_kira_manifest.json").write_text(json.dumps(q02_kira_manifest(limits), indent=2), encoding="utf-8", newline="\n")
    return root
