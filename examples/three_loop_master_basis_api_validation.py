"""Regression audit for the reusable stage-2 master-basis API."""
from __future__ import annotations

import json
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.master_basis_api import (
    Seed,
    build_family_spec,
    render_integralfamilies_yaml,
    render_kinematics_yaml,
)
from three_loop.q02_kira_backend import (
    Q02_AUXILIARY_NAMES,
    Q02_DUPLICATE_GROUPS,
    Q02_RAW_TO_UNIQUE,
    render_q02_kira_integralfamilies_yaml,
    render_q02_kira_kinematics_yaml,
)
from three_loop.q05_kira_backend import (
    Q05_AUXILIARY_NAMES,
    Q05_DUPLICATE_GROUPS,
    Q05_RAW_TO_UNIQUE,
    render_q05_kira_integralfamilies_yaml,
    render_q05_kira_kinematics_yaml,
)

AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
AUDIT_JSON = AUDIT_DIR / "three_loop_master_basis_api_validation.json"
AUDIT_TXT = AUDIT_DIR / "three_loop_master_basis_api_validation.txt"


def _norm(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def main() -> None:
    errors: list[str] = []
    rows: list[dict[str, object]] = []

    q02 = build_family_spec("Q02_full")
    q05 = build_family_spec("Q05_full")
    q08 = build_family_spec("Q08_full")
    q10 = build_family_spec("Q10_full")
    q01 = build_family_spec("Q01_full")

    expected_master_ids = {
        "Q01_full": "Q01_final60",
        "Q02_full": "Q02_final17",
        "Q08_full": "Q08_final12",
        "Q10_full": "Q10_final13",
    }
    for spec in (q01, q02, q08, q10):
        expected = expected_master_ids[spec.family_id]
        if spec.master_basis_id != expected:
            errors.append(
                f"{spec.family_id}: master basis {spec.master_basis_id!r} != {expected!r}"
            )

    checks = [
        (
            q02,
            tuple(Q02_RAW_TO_UNIQUE),
            tuple(tuple(x) for x in Q02_DUPLICATE_GROUPS),
            tuple(Q02_AUXILIARY_NAMES),
            render_q02_kira_integralfamilies_yaml(),
            render_q02_kira_kinematics_yaml(),
        ),
        (
            q05,
            tuple(Q05_RAW_TO_UNIQUE),
            tuple(tuple(x) for x in Q05_DUPLICATE_GROUPS),
            tuple(Q05_AUXILIARY_NAMES),
            render_q05_kira_integralfamilies_yaml(),
            render_q05_kira_kinematics_yaml(),
        ),
    ]

    for spec, mapping, duplicates, auxiliaries, old_family_yaml, old_kin_yaml in checks:
        local_errors: list[str] = []
        if spec.raw_to_unique != mapping:
            local_errors.append(f"raw_to_unique={spec.raw_to_unique} expected={mapping}")
        if spec.duplicate_groups != duplicates:
            local_errors.append(f"duplicate_groups={spec.duplicate_groups} expected={duplicates}")
        if spec.auxiliary_names != auxiliaries:
            local_errors.append(f"auxiliaries={spec.auxiliary_names} expected={auxiliaries}")
        if spec.baseline_seed != Seed(spec.unique_physical_count, 3, 0):
            local_errors.append(f"baseline_seed={spec.baseline_seed}")
        if spec.top_sector != (1 << spec.unique_physical_count) - 1:
            local_errors.append(f"top_sector={spec.top_sector}")
        if _norm(render_integralfamilies_yaml(spec)) != _norm(old_family_yaml):
            local_errors.append("integralfamilies.yaml differs from dedicated backend")
        if _norm(render_kinematics_yaml()) != _norm(old_kin_yaml):
            local_errors.append("kinematics.yaml differs from dedicated backend")
        rows.append(
            {
                "family": spec.family_id,
                "diagrams": list(spec.diagrams),
                "unique_physical": spec.unique_physical_count,
                "auxiliary_count": spec.auxiliary_count,
                "top_sector": spec.top_sector,
                "baseline_seed": spec.baseline_seed.tag,
                "errors": local_errors,
                "pass": not local_errors,
            }
        )
        errors.extend(f"{spec.family_id}: {item}" for item in local_errors)

    audit = {
        "schema_version": 1,
        "api": "three_loop.master_basis_api",
        "known_completed_master_bases": expected_master_ids,
        "dedicated_backend_regressions": rows,
        "errors": errors,
        "audit_pass": not errors,
    }
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc reusable master-basis API validation",
        f"Q01 master: {q01.master_basis_id}",
        f"Q02 master: {q02.master_basis_id}",
        f"Q08 master: {q08.master_basis_id}",
        f"Q10 master: {q10.master_basis_id}",
    ]
    for row in rows:
        lines.append(
            f"{row['family']}: unique={row['unique_physical']} aux={row['auxiliary_count']} "
            f"top_sector={row['top_sector']} baseline={row['baseline_seed']} pass={row['pass']}"
        )
    lines.extend(
        [
            f"internal audit errors: {len(errors)}",
            f"audit JSON: {AUDIT_JSON}",
            f"audit TXT: {AUDIT_TXT}",
            "QEDCalc reusable master-basis API validation " + ("PASS" if not errors else "FAIL"),
        ]
    )
    AUDIT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if errors:
        for item in errors:
            print("ERROR:", item)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
