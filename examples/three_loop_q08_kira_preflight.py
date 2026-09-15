"""Validate and export the first non-Q01 Kira family project: Q08/Q48."""
from __future__ import annotations

import json

from three_loop.integral_family_classification import ROOT
from three_loop.q08_kira_backend import (
    Q08SeedLimits,
    export_q08_kira_project,
    q08_kira_manifest,
    validate_q08_kira_basis,
)

OUTPUT_DIR = ROOT / "output" / "kira_q08_full_r7s3d0"
AUDIT_JSON = OUTPUT_DIR / "q08_kira_preflight_audit.json"
AUDIT_TXT = OUTPUT_DIR / "q08_kira_preflight_audit.txt"


def main() -> None:
    limits = Q08SeedLimits(r=7, s=3, d=0)
    basis = validate_q08_kira_basis()
    project = export_q08_kira_project(OUTPUT_DIR, limits=limits, back_substitution=False)
    manifest = q08_kira_manifest(limits)

    errors: list[str] = []
    if basis.get("inverse_propagator_count") != 12:
        errors.append("Q08 Kira family does not contain 12 inverse propagators")
    if basis.get("coefficient_matrix_rank") != 12 or not basis.get("full_rank"):
        errors.append(f"Q08 Kira basis is not rank 12: {basis}")
    if basis.get("unique_physical_count") != 7 or basis.get("auxiliary_count") != 5:
        errors.append(f"unexpected Q08 7+5 split: {basis}")
    if basis.get("top_sector") != 127:
        errors.append(f"unexpected Q08 top sector: {basis.get('top_sector')}")
    if manifest.get("raw_physical_to_unique_mapping") != [1, 2, 3, 2, 4, 2, 5, 6, 7]:
        errors.append("Q08 raw physical mapping changed")
    if manifest.get("duplicate_physical_groups") != [[2, 4, 6]]:
        errors.append("Q08 duplicate group changed")

    audit = {
        "canonical_family": "Q08_full",
        "covered_diagrams": ["Q08", "Q48"],
        "project_dir": str(project),
        "seed": {"r": 7, "s": 3, "d": 0},
        "basis": basis,
        "top_sector": 127,
        "raw_physical_to_unique_mapping": manifest["raw_physical_to_unique_mapping"],
        "duplicate_physical_groups": manifest["duplicate_physical_groups"],
        "auxiliary_names": manifest["auxiliary_names"],
        "generated_files": [
            str(project / "config" / "integralfamilies.yaml"),
            str(project / "config" / "kinematics.yaml"),
            str(project / "jobs.yaml"),
            str(project / "qedcalc_kira_manifest.json"),
        ],
        "next_step": "run local Kira baseline r7s3d0; do not mark master basis complete before boundary audits",
        "errors": errors,
        "audit_pass": not errors,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q08 Kira preflight",
        f"canonical family: {audit['canonical_family']}",
        f"covered diagrams: {audit['covered_diagrams']}",
        f"unique physical + auxiliary: {basis['unique_physical_count']} + {basis['auxiliary_count']}",
        f"canonical inverse propagators: {basis['inverse_propagator_count']}",
        f"scalar-product rank: {basis['coefficient_matrix_rank']}/12",
        f"top sector: {audit['top_sector']}",
        f"seed: r{limits.r}s{limits.s}d{limits.d}",
        f"raw->unique: {audit['raw_physical_to_unique_mapping']}",
        f"duplicates: {audit['duplicate_physical_groups']}",
        f"auxiliaries: {audit['auxiliary_names']}",
        f"project: {project}",
        f"internal audit errors: {len(errors)}",
        "QEDCalc Q08 Kira preflight " + ("PASS" if not errors else "FAIL"),
    ]
    AUDIT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc Q08 Kira preflight FAIL")


if __name__ == "__main__":
    main()
