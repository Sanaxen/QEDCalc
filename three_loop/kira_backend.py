"""Kira export helpers for the three-loop Q01 integral family.

This module deliberately keeps the Kira representation separate from the
native QEDCalc IBP representation.  QEDCalc's D10-D12 are linear scalar
products.  Kira is most robust with a complete basis of quadratic inverse
propagators, so the Kira benchmark family replaces those three linear ISPs by
quadratic auxiliaries while preserving the same 12-dimensional scalar-product
space.

The first four Kira propagators are the active lines of the source sector
(1,0,1,0,1,1,0,0,0), so the dedicated four-line benchmark has Kira top sector
15.  A JSON manifest records the permutation and the exact basis relations.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

import sympy as sp

from qedcalc.operations.ibp import sp_atom
from three_loop.integral_family import q01_denominator_expressions


Q01_KIRA_NAME = "Q01_4line"
Q01_SOURCE_SECTOR = (1, 0, 1, 0, 1, 1, 0, 0, 0)
Q01_KIRA_TOP_SECTOR = 15
Q01_KIRA_TO_QED_PHYSICAL = (1, 3, 5, 6, 2, 4, 7, 8, 9)


@dataclass(frozen=True)
class KiraSeedLimits:
    r: int = 4
    s: int = 0
    d: int = 0

    def __post_init__(self) -> None:
        if self.r < 4:
            raise ValueError("Q01 four-line Kira seed requires r >= 4")
        if self.s < 0 or self.d < 0:
            raise ValueError("Kira s and d limits must be non-negative")


def _q01_sp_basis() -> tuple[sp.Symbol, ...]:
    return (
        sp_atom("k", "k"),
        sp_atom("l", "l"),
        sp_atom("r", "r"),
        sp_atom("k", "l"),
        sp_atom("k", "r"),
        sp_atom("l", "r"),
        sp_atom("k", "p"),
        sp_atom("l", "p"),
        sp_atom("p", "r"),
        sp_atom("k", "q"),
        sp_atom("l", "q"),
        sp_atom("q", "r"),
    )


def q01_kira_inverse_propagator_expressions() -> tuple[sp.Expr, ...]:
    """Return the algebraic Kira P_i basis in QEDCalc scalar products.

    Kira uses P=q^2-m^2 while QEDCalc's nine physical D_i use the opposite
    sign.  The order is chosen so the active source-sector lines are first.
    """
    qed = q01_denominator_expressions()
    kk = sp_atom("k", "k")
    ll = sp_atom("l", "l")
    rr = sp_atom("r", "r")
    kr = sp_atom("k", "r")
    lq = sp_atom("l", "q")
    qr = sp_atom("q", "r")
    m2 = sp.Symbol("m2")
    z = sp.Symbol("z")

    physical = tuple(-qed[i - 1] for i in Q01_KIRA_TO_QED_PHYSICAL)
    auxiliaries = (
        kk + rr - 2 * kr,              # (k-r)^2
        ll + z * m2 + 2 * lq,          # (l+q)^2
        rr + z * m2 + 2 * qr,          # (r+q)^2
    )
    return physical + auxiliaries


def validate_q01_kira_basis() -> dict[str, object]:
    """Verify that the twelve Kira inverse propagators span all loop SPs."""
    basis = _q01_sp_basis()
    expressions = q01_kira_inverse_propagator_expressions()
    matrix = sp.Matrix(
        [[sp.expand(expr).coeff(atom) for atom in basis] for expr in expressions]
    )
    rank = int(matrix.rank())
    if rank != len(basis):
        raise ValueError(f"Q01 Kira basis is singular: rank {rank}/{len(basis)}")
    return {
        "scalar_product_count": len(basis),
        "inverse_propagator_count": len(expressions),
        "coefficient_matrix_rank": rank,
        "full_rank": True,
    }


def render_q01_kira_integralfamilies_yaml() -> str:
    return """integralfamilies:
  - name: \"Q01_4line\"
    loop_momenta: [k, l, r]
    top_level_sectors: [15]
    propagators:
      - [\"k-p-q\", \"m2\"]
      - [\"k+l-p\", \"m2\"]
      - [\"l+r-p\", \"m2\"]
      - [\"r-p\", \"m2\"]
      - [\"k-p\", \"m2\"]
      - [\"l-p\", \"m2\"]
      - [\"k\", 0]
      - [\"l\", 0]
      - [\"r\", 0]
      - [\"k-r\", 0]
      - [\"l+q\", 0]
      - [\"r+q\", 0]
"""


def render_q01_kira_kinematics_yaml() -> str:
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


def render_q01_kira_jobs_yaml(
    limits: KiraSeedLimits,
    *,
    back_substitution: bool = False,
) -> str:
    back = "true" if back_substitution else "false"
    return f"""jobs:
  - reduce_sectors:
      reduce:
        - {{topologies: [Q01_4line], sectors: [15], r: {limits.r}, s: {limits.s}, d: {limits.d}}}
      select_integrals:
        select_mandatory_recursively:
          - {{topologies: [Q01_4line], sectors: [15], r: {limits.r}, s: {limits.s}, d: {limits.d}}}
      run_symmetries: true
      run_initiate: true
      run_triangular: sectorwise
      run_back_substitution: {back}
"""


def q01_kira_manifest(limits: KiraSeedLimits) -> dict[str, object]:
    validation = validate_q01_kira_basis()
    return {
        "backend": "kira",
        "family": Q01_KIRA_NAME,
        "purpose": "Q01 four-line source-sector benchmark",
        "qedcalc_source_sector": list(Q01_SOURCE_SECTOR),
        "kira_top_sector": Q01_KIRA_TOP_SECTOR,
        "seed_limits": {"r": limits.r, "s": limits.s, "d": limits.d},
        "basis_validation": validation,
        "kira_index_order": [
            "QED_D1", "QED_D3", "QED_D5", "QED_D6",
            "QED_D2", "QED_D4", "QED_D7", "QED_D8", "QED_D9",
            "A10=(k-r)^2", "A11=(l+q)^2", "A12=(r+q)^2",
        ],
        "physical_sign_convention": {
            "relation": "Kira_Pi = -QEDCalc_Dj for the first nine physical propagators",
            "kira_to_qed_physical_indices": list(Q01_KIRA_TO_QED_PHYSICAL),
        },
        "linear_isp_to_kira_auxiliary_relations": [
            "QED_D10=k.r=(Kira_P7+Kira_P9-Kira_P10)/2",
            "QED_D11=l.q=(Kira_P11-Kira_P8-z*m2)/2",
            "QED_D12=q.r=(Kira_P12-Kira_P9-z*m2)/2",
        ],
        "important": (
            "The Kira family spans the same loop scalar-product space but is not an "
            "index-by-index copy of QEDCalc D10-D12. Amplitude/reduction exchange must "
            "apply the manifest basis transformation."
        ),
    }


def export_q01_kira_project(
    root: str | Path,
    *,
    limits: KiraSeedLimits = KiraSeedLimits(),
    back_substitution: bool = False,
) -> Path:
    root = Path(root)
    config = root / "config"
    config.mkdir(parents=True, exist_ok=True)

    (config / "integralfamilies.yaml").write_text(
        render_q01_kira_integralfamilies_yaml(), encoding="utf-8", newline="\n"
    )
    (config / "kinematics.yaml").write_text(
        render_q01_kira_kinematics_yaml(), encoding="utf-8", newline="\n"
    )
    (root / "jobs.yaml").write_text(
        render_q01_kira_jobs_yaml(limits, back_substitution=back_substitution),
        encoding="utf-8",
        newline="\n",
    )
    (root / "qedcalc_kira_manifest.json").write_text(
        json.dumps(q01_kira_manifest(limits), indent=2),
        encoding="utf-8",
        newline="\n",
    )
    return root


def kira_integral_text(indices: Iterable[int], *, family: str = Q01_KIRA_NAME) -> str:
    values = ",".join(str(int(v)) for v in indices)
    return f"{family}[{values}]"
