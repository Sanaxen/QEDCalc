"""Generate a back-substitution-only Kira job for the Q01 910-integral demand.

This script does not run Kira. It validates the existing full-demand project
and writes jobs_backsub.yaml so the already completed triangular system can be
reused. Symmetry search, initiate, and triangular reduction are disabled;
back substitution alone is enabled.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
MANIFEST = PROJECT / "qedcalc_kira_manifest.json"
BACKSUB_JOB = PROJECT / "jobs_backsub.yaml"
FAMILY = "Q01_full"
EXPECTED_TOP = [511]
EXPECTED_DEMAND = 944
EXPECTED_BOUNDS = {"r": 9, "s": 3, "d": 0}


def _load_manifest() -> dict[str, object]:
    if not MANIFEST.exists():
        raise SystemExit(
            "ERROR: full-demand Kira manifest not found: " + str(MANIFEST) + "\n"
            "Run run_three_loop_q01_kira_910_project_generate.bat first."
        )
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: cannot read Kira manifest: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit("ERROR: malformed Kira manifest")
    return data


def _validate_manifest(data: dict[str, object]) -> None:
    if data.get("family") != FAMILY:
        raise SystemExit(f"ERROR: unexpected Kira family: {data.get('family')!r}")
    top = [int(v) for v in data.get("top_level_sectors", [])]
    if top != EXPECTED_TOP:
        raise SystemExit(f"ERROR: unexpected top sector set: {top}; expected {EXPECTED_TOP}")
    if int(data.get("unique_demanded_kira_integral_count", -1)) != EXPECTED_DEMAND:
        raise SystemExit("ERROR: manifest does not describe the expected 944-integral demand")
    bounds = data.get("demand_seed_bounds")
    if not isinstance(bounds, dict):
        raise SystemExit("ERROR: manifest demand_seed_bounds is malformed")
    normalized = {key: int(bounds.get(key, -1)) for key in ("r", "s", "d")}
    if normalized != EXPECTED_BOUNDS:
        raise SystemExit(
            f"ERROR: unexpected demand seed bounds: {normalized}; expected {EXPECTED_BOUNDS}"
        )


def _require_triangular_system() -> None:
    verconfig = PROJECT / "tmp" / FAMILY / "VERconfig"
    if not verconfig.exists():
        raise SystemExit(
            "ERROR: completed triangular-system marker was not found: " + str(verconfig) + "\n"
            "Run run_three_loop_q01_kira_910_triangular.bat first."
        )


def _render_backsub_job() -> str:
    return f'''jobs:
  - reduce_sectors:
      reduce:
        - {{topologies: [{FAMILY}], sectors: [511], r: 9, s: 3, d: 0}}
      select_integrals:
        select_mandatory_recursively:
          - {{topologies: [{FAMILY}], sectors: [511], r: 9, s: 3, d: 0}}
      run_symmetries: false
      run_initiate: false
      run_triangular: false
      run_back_substitution: true
      conditional: true
'''


def main() -> None:
    print("QEDCalc Q01 full-demand Kira back-substitution job generator")
    print("mode: CONFIG ONLY; Kira is NOT run by this Python script")
    print("project:", PROJECT)

    manifest = _load_manifest()
    _validate_manifest(manifest)
    _require_triangular_system()

    BACKSUB_JOB.write_text(_render_backsub_job(), encoding="utf-8", newline="\n")
    text = BACKSUB_JOB.read_text(encoding="utf-8")
    required_tokens = [
        "topologies: [Q01_full]",
        "sectors: [511]",
        "r: 9",
        "s: 3",
        "d: 0",
        "run_symmetries: false",
        "run_initiate: false",
        "run_triangular: false",
        "run_back_substitution: true",
        "conditional: true",
    ]
    missing = [token for token in required_tokens if token not in text]
    if missing:
        raise SystemExit(f"ERROR: generated back-substitution job audit failed: {missing}")

    print("family:", FAMILY)
    print("top sector: 511")
    print("demand baseline: r=9 s=3 d=0")
    print("triangular system marker:", PROJECT / "tmp" / FAMILY / "VERconfig")
    print("generated:", BACKSUB_JOB)
    print("NOTE: existing triangular system will be reused; only back substitution is enabled.")
    print("Q01 full-demand Kira back-substitution job generation PASS")


if __name__ == "__main__":
    main()
