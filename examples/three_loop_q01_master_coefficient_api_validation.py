"""Re-run Q01 coefficient synthesis through the reusable three_loop API.

This is a saved-artifact validation only: it does not recompute the projected
trace and does not launch Kira/FireFly.  The newly produced 60 exact master
coefficients are compared algebraically with the already-PASS d+1 coefficient
artifact using Fermat, not merely by string formatting.
"""
from __future__ import annotations

import json
from pathlib import Path

import examples.three_loop_q01_projected_amplitude_master_coefficients as q01
from three_loop.kira_isp_bridge import expand_qedcalc_integral_to_kira
from three_loop.master_coefficient_api import (
    FermatExactBackend,
    MasterCoefficientConfig,
    fermat_text_is_zero,
    synthesize_master_coefficients,
)

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
REFERENCE_JSON = PROJECT / "q01_projected_amplitude_final60_coefficients.json"
OUTPUT_JSON = PROJECT / "q01_master_coefficient_api_validation.json"
OUTPUT_TXT = PROJECT / "q01_master_coefficient_api_validation.txt"


def main() -> None:
    print("QEDCalc Q01 reusable master-coefficient API validation")
    print("mode: saved artifacts only; no projected trace or Kira/FireFly run")

    if not REFERENCE_JSON.exists():
        raise SystemExit(f"ERROR: PASS reference coefficient artifact not found: {REFERENCE_JSON}")
    reference = json.loads(REFERENCE_JSON.read_text(encoding="utf-8"))
    if not reference.get("pass"):
        raise SystemExit("ERROR: reference coefficient artifact is not marked PASS")

    # Select the validated d+1 solve whose masters.final is exactly final60.
    q01.ALT_ROOT = q01.PROJECT / "exact944_r9s3d1_firefly"
    q01.RESULT_DIR = q01.ALT_ROOT / "results" / q01.FAMILY
    q01.TARGET_FILE = q01.PROJECT / "q01_exact944_r9s3d1_firefly_boundary_targets"

    projected_raw = q01._load_projected_terms()
    projected = [(native, coeff) for native, coeff, _ in projected_raw]
    final60 = frozenset(q01._load_final60())
    exact944 = frozenset(q01._load_family_file(q01.ORIGINAL_TARGET_FILE, q01.EXPECTED_ORIGINAL))
    mandatory = q01._load_family_file(q01.TARGET_FILE)
    if not final60.issubset(mandatory):
        raise SystemExit("ERROR: d+1 mandatory target set does not contain final60")

    form_export = q01._find_form_export()
    masters_file = q01.RESULT_DIR / "masters.final"
    config = MasterCoefficientConfig(
        family=q01.FAMILY,
        form_export=form_export,
        masters_file=masters_file,
        final_basis=final60,
        expected_kira_targets=exact944,
        expected_native_terms=q01.EXPECTED_NATIVE,
        fermat_group_size=128,
    )
    backend = FermatExactBackend(group_size=128)
    result = synthesize_master_coefficients(
        projected,
        expand_qedcalc_integral_to_kira,
        config,
        backend=backend,
    )

    ref_rows = {
        tuple(int(x) for x in row["indices"]): row
        for row in reference.get("basis_terms", [])
        if isinstance(row, dict) and isinstance(row.get("indices"), list)
    }
    new_rows = {row.indices: row for row in result.rows}
    missing_reference = sorted(set(new_rows) - set(ref_rows))
    missing_api = sorted(set(ref_rows) - set(new_rows))
    mismatches: list[dict[str, object]] = []

    print("comparing API coefficients with PASS reference using Fermat...")
    for pos, indices in enumerate(sorted(set(new_rows) & set(ref_rows)), 1):
        new_coeff = new_rows[indices].coefficient
        old_coeff = str(ref_rows[indices].get("coefficient", "0"))
        symbols = set(new_rows[indices].symbols)
        symbols.update(str(s) for s in ref_rows[indices].get("symbols", []))
        difference = backend._run_sum([new_coeff, f"-({old_coeff})"], symbols)
        if not fermat_text_is_zero(difference):
            mismatches.append(
                {
                    "indices": list(indices),
                    "api_coefficient": new_coeff,
                    "reference_coefficient": old_coeff,
                    "difference": difference,
                }
            )
        if pos % 10 == 0 or pos == 60:
            print(f"  compared {pos}/60; mismatches={len(mismatches)}", flush=True)

    checks = {
        "api_pipeline_pass": result.passed,
        "native_terms_910": result.native_terms == q01.EXPECTED_NATIVE,
        "bridge_unique_targets_944": result.bridge_unique_targets == q01.EXPECTED_ORIGINAL,
        "reduction_masters_60": result.reduction_masters == q01.EXPECTED_FINAL,
        "raw_master_forms_60": result.raw_master_forms == q01.EXPECTED_FINAL,
        "final_basis_rows_60": len(result.rows) == q01.EXPECTED_FINAL,
        "nonzero_final_coefficients_60": result.nonzero_final_coefficients == q01.EXPECTED_FINAL,
        "no_extra_nonzero_masters": len(result.extra_nonzero_masters) == 0,
        "reference_basis_matches": not missing_reference and not missing_api,
        "all_60_coefficients_match_reference_exactly": not mismatches,
    }
    passed = all(checks.values())

    payload = {
        "mode": "Q01 d+1 saved-artifact validation through reusable master coefficient API",
        "family": q01.FAMILY,
        "form_export": str(form_export),
        "masters_file": str(masters_file),
        "reference": str(REFERENCE_JSON),
        "native_terms": result.native_terms,
        "bridge_unique_targets": result.bridge_unique_targets,
        "reduction_masters": result.reduction_masters,
        "raw_master_forms": result.raw_master_forms,
        "nonzero_final_coefficients": result.nonzero_final_coefficients,
        "extra_nonzero_masters": len(result.extra_nonzero_masters),
        "missing_reference": [list(v) for v in missing_reference],
        "missing_api": [list(v) for v in missing_api],
        "coefficient_mismatches": mismatches,
        "checks": checks,
        "pass": passed,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "QEDCalc Q01 reusable master-coefficient API validation",
        "",
        f"native terms: {result.native_terms}",
        f"bridge unique targets: {result.bridge_unique_targets}",
        f"reduction masters: {result.reduction_masters}",
        f"raw master forms: {result.raw_master_forms}",
        f"nonzero final coefficients: {result.nonzero_final_coefficients}",
        f"extra nonzero masters: {len(result.extra_nonzero_masters)}",
        f"coefficient mismatches: {len(mismatches)}",
        "",
        "checks:",
    ]
    lines.extend(f"  {key}: {value}" for key, value in checks.items())
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("API reduction masters:", result.reduction_masters)
    print("API nonzero final coefficients:", result.nonzero_final_coefficients)
    print("API extra nonzero masters:", len(result.extra_nonzero_masters))
    print("reference coefficient mismatches:", len(mismatches))
    print("audit JSON:", OUTPUT_JSON)
    print("audit TXT:", OUTPUT_TXT)
    if not passed:
        print("Q01 reusable master-coefficient API validation FAIL")
        raise SystemExit(1)
    print("Q01 reusable master-coefficient API validation PASS")


if __name__ == "__main__":
    main()
