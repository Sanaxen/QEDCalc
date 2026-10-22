"""Fail-closed reusable VP05 single-target exact reduction rule.

No Kira run and no generic rule inference. Loads the immutable verified
artifact and checks all anchored exponent/coefficient/identity assertions.
The artifact is a local *attestation*; primary source proof reports should
be regenerated/verified by the dedicated audit before distributing it.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import sympy as sp

FAMILY = "VP05_full"
TARGET = (1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0)
MASTER_6 = (1, 1, -1, 1, 0, 0, 1, 1, 0, 0, 0, 0)
MASTER_5 = (1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0)
DEFAULT_ARTIFACT = Path("output/three_loop_integral_family_audit/vp05_verified_reduction_artifact_v1.json")
REQUIRED = (
    "exact_400_columns", "all_166_lineage_exact", "raw_kira_system_replay",
    "hashes_match", "preferred_input_matches_saved", "target_keys_present",
    "preferred_job_reference",
)

@dataclass(frozen=True)
class ReductionRule:
    family: str
    target: tuple[int, ...]
    terms: tuple[tuple[tuple[int, ...], sp.Expr], ...]
    source: Path

def load_verified_vp05_rule(path: str | Path = DEFAULT_ARTIFACT) -> ReductionRule:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if data.get("status") != "EXACT_SAVED_KIRA_PROJECT_REDUCTION":
        raise ValueError("VP05 artifact is not verified")
    checks = data.get("checks", {})
    if any(checks.get(name) is not True for name in REQUIRED):
        raise ValueError("VP05 artifact fails evidence checks")
    if data.get("historical_kira_binary_version_verified") is not False:
        raise ValueError("Unexpected historical Kira version flag")
    if data.get("diagram_momentum_routing_independently_verified") is not False:
        raise ValueError("Unexpected independent routing flag")
    t = data.get("target", {})
    if t.get("key") != [10, 203] or tuple(t.get("exponents", ())) != TARGET:
        raise ValueError("VP05 target identity mismatch")
    terms = data.get("right_hand_side")
    expected = [
        {"key": [6, 203], "exponents": list(MASTER_6), "coefficient": "2/z"},
        {"key": [5, 201], "exponents": list(MASTER_5), "coefficient": "-2/z"},
    ]
    if terms != expected:
        raise ValueError("VP05 right-hand-side identity mismatch")
    expected_equation = (
        "z*VP05_full[1,1,0,1,0,0,1,1,0,0,0,0] - "
        "2*VP05_full[1,1,-1,1,0,0,1,1,0,0,0,0] + "
        "2*VP05_full[1,0,0,1,0,0,1,1,0,0,0,0] = 0"
    )
    if data.get("equation") != expected_equation:
        raise ValueError("VP05 exact equation mismatch")
    z = sp.Symbol("z")
    return ReductionRule(FAMILY, TARGET, ((MASTER_6, 2 / z), (MASTER_5, -2 / z)), path)

def reduce_if_verified(
    family: str,
    exponents: tuple[int, ...],
    artifact: str | Path = DEFAULT_ARTIFACT,
) -> tuple[tuple[tuple[int, ...], sp.Expr], ...] | None:
    """Only the exact declared target is eligible; other integrals are untouched."""
    if family != FAMILY or tuple(exponents) != TARGET:
        return None
    return load_verified_vp05_rule(artifact).terms
