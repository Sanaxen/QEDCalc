"""Generate a config-only Kira project for the exact Q01 910-integral demand.

This script deliberately does NOT run Kira.  It consumes the saved demand plan
produced by ``three_loop_q01_kira_910_demand_plan.py`` and creates a Kira
project whose top-level sector covers the exact expanded Q01 demand.

The r/s/d values copied from the demand plan are demand maxima only.  They are
not claimed to be sufficient Laporta/IBP closure limits; later runs may need
larger recursive seeds.
"""
from __future__ import annotations

import json
from pathlib import Path

from three_loop.kira_backend import validate_q01_kira_basis


ROOT = Path(__file__).resolve().parents[1]
PLAN_JSON = ROOT / "output" / "kira_q01_910_demand_plan.json"
FAMILY = "Q01_full"
EXPECTED_TOP_SECTORS = [511]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"


def _load_plan() -> dict[str, object]:
    if not PLAN_JSON.exists():
        raise SystemExit(
            "ERROR: demand plan not found: " + str(PLAN_JSON) + "\n"
            "Run run_three_loop_q01_kira_910_demand_plan.bat first."
        )
    try:
        plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: cannot read demand plan: {exc}") from exc

    maxima = [int(v) for v in plan.get("maximal_sectors", [])]
    if maxima != EXPECTED_TOP_SECTORS:
        raise SystemExit(
            "ERROR: unexpected maximal sector set in demand plan: "
            f"{maxima}; expected {EXPECTED_TOP_SECTORS}. Refusing to guess."
        )
    if int(plan.get("unique_demanded_kira_integral_count", -1)) != 944:
        raise SystemExit(
            "ERROR: demand plan does not contain the expected 944 unique Kira integrals."
        )
    return plan


def _render_integralfamilies() -> str:
    return f'''integralfamilies:
  - name: "{FAMILY}"
    loop_momenta: [k, l, r]
    top_level_sectors: [511]
    propagators:
      - ["k-p-q", "m2"]
      - ["k+l-p", "m2"]
      - ["l+r-p", "m2"]
      - ["r-p", "m2"]
      - ["k-p", "m2"]
      - ["l-p", "m2"]
      - ["k", 0]
      - ["l", 0]
      - ["r", 0]
      - ["k-r", 0]
      - ["l+q", 0]
      - ["r+q", 0]
'''


def _render_kinematics() -> str:
    return '''kinematics:
  outgoing_momenta: [p, q]
  kinematic_invariants:
    - [m2, 2]
    - [z, 0]
  scalarproduct_rules:
    - [[p,p], "m2"]
    - [[q,q], "z*m2"]
    - [[p,q], "-z*m2/2"]
  symbol_to_replace_by_one: m2
'''


def _render_jobs(*, r: int, s: int, d: int) -> str:
    return f'''jobs:
  - reduce_sectors:
      reduce:
        - {{topologies: [{FAMILY}], sectors: [511], r: {r}, s: {s}, d: {d}}}
      select_integrals:
        select_mandatory_recursively:
          - {{topologies: [{FAMILY}], sectors: [511], r: {r}, s: {s}, d: {d}}}
      run_symmetries: true
      run_initiate: true
      run_triangular: sectorwise
      run_back_substitution: false
'''


def main() -> None:
    print("QEDCalc Q01 full-demand Kira project generator")
    print("mode: CONFIG ONLY; Kira is NOT run")
    print("demand plan:", PLAN_JSON)

    plan = _load_plan()
    bounds = plan.get("required_seed_bounds_from_exact_demand", {})
    if not isinstance(bounds, dict):
        raise SystemExit("ERROR: malformed demand seed bounds")
    r = int(bounds.get("r_max", -1))
    s = int(bounds.get("s_max", -1))
    d = int(bounds.get("d_max", -1))
    if min(r, s, d) < 0:
        raise SystemExit(f"ERROR: invalid demand bounds r={r} s={s} d={d}")

    # Keep the output path self-describing and reject stale/mismatched plans.
    expected_name = f"kira_q01_full_demand_r{r}s{s}d{d}"
    if PROJECT.name != expected_name:
        raise SystemExit(
            f"ERROR: project path/bounds mismatch: {PROJECT.name} != {expected_name}"
        )

    basis = validate_q01_kira_basis()
    if not basis.get("full_rank"):
        raise SystemExit("ERROR: Q01 Kira basis validation failed")

    config = PROJECT / "config"
    config.mkdir(parents=True, exist_ok=True)
    (config / "integralfamilies.yaml").write_text(
        _render_integralfamilies(), encoding="utf-8", newline="\n"
    )
    (config / "kinematics.yaml").write_text(
        _render_kinematics(), encoding="utf-8", newline="\n"
    )
    (PROJECT / "jobs.yaml").write_text(
        _render_jobs(r=r, s=s, d=d), encoding="utf-8", newline="\n"
    )

    manifest = {
        "backend": "kira",
        "diagram_id": "Q01",
        "family": FAMILY,
        "purpose": "Q01 exact 910-native-integral full-demand baseline",
        "source_demand_plan": str(PLAN_JSON),
        "native_integral_count": int(plan["native_integral_count"]),
        "unique_demanded_kira_integral_count": int(
            plan["unique_demanded_kira_integral_count"]
        ),
        "distinct_demanded_sector_count": int(plan["distinct_demanded_sector_count"]),
        "top_level_sectors": EXPECTED_TOP_SECTORS,
        "demand_seed_bounds": {"r": r, "s": s, "d": d},
        "basis_validation": basis,
        "kira_index_order": [
            "QED_D1", "QED_D3", "QED_D5", "QED_D6",
            "QED_D2", "QED_D4", "QED_D7", "QED_D8", "QED_D9",
            "A10=(k-r)^2", "A11=(l+q)^2", "A12=(r+q)^2",
        ],
        "warnings": [
            "r/s/d are maxima observed in the exact 944-integral demand, not proven IBP-closure limits.",
            "A later Kira reduction may require increasing r, s, and/or d.",
            "This generator does not launch Kira.",
        ],
    }
    (PROJECT / "qedcalc_kira_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )

    # Lightweight self-audit of the generated text, before any Kira invocation.
    family_text = (config / "integralfamilies.yaml").read_text(encoding="utf-8")
    jobs_text = (PROJECT / "jobs.yaml").read_text(encoding="utf-8")
    required_tokens = [
        f'name: "{FAMILY}"',
        "top_level_sectors: [511]",
        f"topologies: [{FAMILY}]",
        "sectors: [511]",
        f"r: {r}",
        f"s: {s}",
        f"d: {d}",
    ]
    combined = family_text + "\n" + jobs_text
    missing = [token for token in required_tokens if token not in combined]
    if missing:
        raise SystemExit(f"ERROR: generated configuration audit failed: {missing}")

    print("project:", PROJECT)
    print("family:", FAMILY)
    print("top sector: 511")
    print("demanded Kira integrals:", plan["unique_demanded_kira_integral_count"])
    print("demanded sectors:", plan["distinct_demanded_sector_count"])
    print(f"demand baseline: r={r} s={s} d={d}")
    print("basis rank:", basis.get("coefficient_matrix_rank"), "/", basis.get("scalar_product_count"))
    print("generated:", config / "integralfamilies.yaml")
    print("generated:", config / "kinematics.yaml")
    print("generated:", PROJECT / "jobs.yaml")
    print("generated:", PROJECT / "qedcalc_kira_manifest.json")
    print("NOTE: Kira was NOT run; r/s/d may need enlargement for recursive IBP closure.")
    print("Q01 full-demand Kira project generation PASS")


if __name__ == "__main__":
    main()
