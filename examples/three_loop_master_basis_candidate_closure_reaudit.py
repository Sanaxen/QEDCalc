"""Re-audit completed candidate-closure Kira runs without recomputation.

This helper exists because a completed Kira ``select_mandatory_list`` reduction
need not emit a human-readable equation file for every non-master target.  The
closure proof only needs to establish that:

1. the exact closure mandatory list was selected;
2. Kira completed successfully for the boundary project;
3. ``masters.final`` is exactly the proposed candidate basis.

Under Kira's mandatory-selection contract, every selected target that is not a
master is resolved by the completed reduction (possibly to zero).  We therefore
report those targets as ``resolved_nonmaster`` rather than pretending to know
whether they are an explicit nonzero reduction or a zero relation.

No project preparation or cleanup is performed here.  Existing expensive Kira
results are read in place.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from examples.three_loop_master_basis_candidate_closure import (
    AUDIT_DIR,
    MANDATORY_NAME,
    _parse_seed,
    _project,
    _read_integrals,
    _resolve,
    _stem,
)
from three_loop.master_basis_api import find_single_masters_final


def _completed_kira_log(project: Path) -> tuple[Path | None, bool, str]:
    logs = sorted(project.glob("kira_*_candidate_closure.log"))
    if not logs:
        return None, False, "candidate-closure Kira log not found"
    # Normally there is exactly one such log.  Accept the newest completed one
    # so a harmless older log does not mask a valid rerun.
    for path in reversed(logs):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "Total time:" in text:
            fatal_markers = (
                "Validation failed:",
                "terminate called",
                "Segmentation fault",
                "Traceback (most recent call last)",
            )
            hit = next((item for item in fatal_markers if item in text), None)
            if hit is None:
                return path, True, "completed Kira log"
            return path, False, f"fatal marker in Kira log: {hit}"
    return logs[-1], False, "Kira completion marker 'Total time:' not found"


def reaudit(args: argparse.Namespace) -> None:
    (
        spec,
        baseline_seed,
        union_audit_path,
        envelope,
        source_targets,
        union_targets,
        candidate_file,
        candidate,
        closure,
    ) = _resolve(args)

    candidate_set = set(candidate)
    closure_set = set(closure)
    rows: list[dict] = []
    errors: list[str] = []

    for seed in envelope.one_axis_extensions():
        project = _project(spec.family_id, args.solver, baseline_seed, seed)
        mandatory_path = project / MANDATORY_NAME
        try:
            mandatory = _read_integrals(mandatory_path, spec.family_id)
            masters_path, masters = find_single_masters_final(project, spec.family_id)
        except Exception as exc:
            errors.append(f"{seed.tag}: {exc}")
            rows.append({
                "seed": seed.tag,
                "project": str(project),
                "stable": False,
                "error": str(exc),
            })
            continue

        master_set = set(masters)
        mandatory_set = set(mandatory)
        log_path, kira_completed, completion_note = _completed_kira_log(project)

        missing_candidate_masters = sorted(candidate_set - master_set)
        extra_masters = sorted(master_set - candidate_set)
        missing_mandatory_targets = sorted(closure_set - mandatory_set)
        extra_mandatory_targets = sorted(mandatory_set - closure_set)
        resolved_nonmaster = sorted(closure_set - master_set) if kira_completed else []

        stable = (
            kira_completed
            and not missing_candidate_masters
            and not extra_masters
            and not missing_mandatory_targets
            and not extra_mandatory_targets
        )
        if not stable:
            errors.append(
                f"{seed.tag}: closure proof failed; kira_completed={kira_completed}, "
                f"missing_candidate={len(missing_candidate_masters)}, "
                f"extra_masters={len(extra_masters)}, "
                f"missing_mandatory={len(missing_mandatory_targets)}, "
                f"extra_mandatory={len(extra_mandatory_targets)}"
            )

        rows.append({
            "seed": seed.tag,
            "project": str(project),
            "masters_final": str(masters_path),
            "master_count": len(masters),
            "mandatory_file": str(mandatory_path),
            "mandatory_count": len(mandatory),
            "kira_log": str(log_path) if log_path else None,
            "kira_completed": kira_completed,
            "completion_note": completion_note,
            "candidate_master_count": len(candidate_set & master_set),
            "resolved_nonmaster_count": len(resolved_nonmaster),
            "resolved_nonmaster": resolved_nonmaster,
            "missing_candidate_masters": missing_candidate_masters,
            "extra_masters": extra_masters,
            "missing_mandatory_targets": missing_mandatory_targets,
            "extra_mandatory_targets": extra_mandatory_targets,
            "stable": stable,
        })

    stable_all = len(rows) == 3 and not errors and all(row.get("stable") for row in rows)
    stem = _stem(spec.family_id, args.solver, baseline_seed, envelope)
    audit_json = AUDIT_DIR / f"{stem}_reaudit.json"
    audit_txt = AUDIT_DIR / f"{stem}_reaudit.txt"

    audit = {
        "schema_version": 1,
        "stage": "master_basis_candidate_closure_reaudit",
        "classification_semantics": {
            "master": "literal member of masters.final",
            "resolved_nonmaster": (
                "selected by the exact mandatory list and not a master after a completed "
                "Kira reduction; may be a nonzero reduction or zero"
            ),
        },
        "family": spec.family_id,
        "representative": spec.representative,
        "diagrams": list(spec.diagrams),
        "baseline_seed": baseline_seed.tag,
        "solver": args.solver,
        "union_reduction_audit": str(union_audit_path),
        "source_union_target_file": str(source_targets),
        "union_target_count": len(union_targets),
        "candidate_envelope": envelope.tag,
        "candidate_master_file": str(candidate_file),
        "candidate_master_count": len(candidate),
        "closure_target_count": len(closure),
        "boundary_rows": rows,
        "stable_under_one_axis_extensions": stable_all,
        "errors": errors,
        "audit_pass": stable_all,
    }
    audit_json.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")

    lines = [
        "QEDCalc generic candidate master closure no-rerun re-audit",
        f"family: {spec.family_id}",
        f"diagrams: {list(spec.diagrams)}",
        f"baseline seed: {baseline_seed.tag}",
        f"solver: {args.solver}",
        f"candidate envelope: {envelope.tag}",
        f"union targets: {len(union_targets)}",
        f"candidate masters: {len(candidate)}",
        f"closure targets: {len(closure)}",
    ]
    for row in rows:
        if "error" in row:
            lines.append(f"{row['seed']}: ERROR {row['error']}")
            continue
        lines.extend([
            f"{row['seed']}: masters.final={row['master_count']} stable={row['stable']}",
            f"  Kira completed: {row['kira_completed']} ({row['completion_note']})",
            f"  mandatory targets: {row['mandatory_count']}",
            f"  candidate masters retained: {row['candidate_master_count']}/{len(candidate)}",
            f"  resolved non-masters: {row['resolved_nonmaster_count']}",
            f"  extra masters: {len(row['extra_masters'])}",
            f"  mandatory mismatches: missing={len(row['missing_mandatory_targets'])}, "
            f"extra={len(row['extra_mandatory_targets'])}",
        ])
    lines.extend([
        f"stable under tested one-axis extensions: {stable_all}",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {audit_json}",
        f"audit TXT: {audit_txt}",
        "QEDCalc generic candidate master closure no-rerun re-audit " + ("PASS" if stable_all else "FAIL"),
    ])
    audit_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    for line in lines:
        print(line)
    if not stable_all:
        for item in errors:
            print("ERROR:", item)
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True)
    parser.add_argument("--baseline-seed", type=_parse_seed)
    parser.add_argument("--solver", choices=("ordinary", "firefly"), default="firefly")
    args = parser.parse_args()
    reaudit(args)


if __name__ == "__main__":
    main()
