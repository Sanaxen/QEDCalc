"""Prepare/finalize sparse mandatory-target master discovery jobs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.master_basis_api import (
    build_family_spec,
    export_kira_project,
    find_or_infer_masters,
)
from three_loop.master_basis_sparse_discovery import (
    build_sparse_target_plan,
    render_mandatory_targets,
)

AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
MANDATORY_NAME = "mandatory_sparse_targets.txt"


def project_path(family: str, level: int) -> Path:
    return ROOT / "output" / f"kira_{family.lower()}_firefly_sparse_l{level}"


def _resolve(args: argparse.Namespace):
    spec = build_family_spec(args.family)
    plan = build_sparse_target_plan(spec, level=args.level)
    project = project_path(spec.family_id, args.level)
    return spec, plan, project


def prepare(args: argparse.Namespace) -> None:
    spec, plan, project = _resolve(args)
    mandatory = project / MANDATORY_NAME
    expected = render_mandatory_targets(plan)

    if not args.fresh and mandatory.exists():
        current = mandatory.read_text(encoding="utf-8", errors="replace")
        if current != expected:
            raise RuntimeError(
                "resume-safe sparse prepare refused because target list changed; "
                "use --fresh to discard old runtime state intentionally"
            )

    export_kira_project(
        spec,
        project,
        seed=plan.envelope,
        solver="firefly",
        mandatory_file=MANDATORY_NAME,
        reduce_sectors=[spec.top_sector],
        top_level_sectors=[spec.top_sector],
        clean=args.fresh,
    )
    mandatory.write_text(expected, encoding="utf-8", newline="\n")

    manifest = {
        "schema_version": 1,
        "stage": "master_basis_sparse_discovery",
        "family": spec.family_id,
        "representative": spec.representative,
        "diagrams": list(spec.diagrams),
        "level": plan.level,
        "target_count": plan.target_count,
        "sector_count": plan.sector_count,
        "physical_count": plan.physical_count,
        "auxiliary_count": plan.auxiliary_count,
        "envelope": {
            "r": plan.envelope.r,
            "s": plan.envelope.s,
            "d": plan.envelope.d,
            "tag": plan.envelope.tag,
        },
        "project": str(project),
        "mandatory_file": str(mandatory),
        "note": (
            "Sparse discovery only. Candidate masters must pass the existing "
            "closure validation before promotion."
        ),
    }
    (project / "qedcalc_sparse_discovery_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )

    print("QEDCalc sparse master-basis discovery prepare")
    print(f"family: {spec.family_id}")
    print(f"representative: {spec.representative}")
    print(f"level: {plan.level}")
    print(f"physical / auxiliary: {plan.physical_count} / {plan.auxiliary_count}")
    print(f"covered physical sectors: {plan.sector_count}")
    print(f"mandatory targets: {plan.target_count}")
    print(f"required envelope: {plan.envelope.tag}")
    print(f"project: {project}")
    print(f"prepare mode: {'fresh' if args.fresh else 'resume-safe'}")
    print("IMPORTANT: this is discovery only; promotion still requires closure validation.")
    print("QEDCalc sparse master-basis discovery prepare PASS")


def finalize(args: argparse.Namespace) -> None:
    spec, plan, project = _resolve(args)
    mandatory = [line.strip() for line in (project / MANDATORY_NAME).read_text(
        encoding="utf-8", errors="replace"
    ).splitlines() if line.strip()]

    masters_path, masters, source_mode = find_or_infer_masters(
        project,
        spec.family_id,
        mandatory_targets=mandatory,
    )

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"three_loop_{spec.family_id.lower()}_firefly_sparse_l{plan.level}"
    master_copy = AUDIT_DIR / f"{stem}_masters.txt"
    audit_json = AUDIT_DIR / f"{stem}_audit.json"
    audit_txt = AUDIT_DIR / f"{stem}_audit.txt"
    master_copy.write_text("\n".join(masters) + "\n", encoding="utf-8", newline="\n")

    audit = {
        "schema_version": 1,
        "stage": "master_basis_sparse_discovery",
        "family": spec.family_id,
        "representative": spec.representative,
        "diagrams": list(spec.diagrams),
        "level": plan.level,
        "target_count": plan.target_count,
        "sector_count": plan.sector_count,
        "envelope": {
            "r": plan.envelope.r,
            "s": plan.envelope.s,
            "d": plan.envelope.d,
            "tag": plan.envelope.tag,
        },
        "master_count": len(masters),
        "masters": masters,
        "master_source": str(masters_path),
        "master_source_mode": source_mode,
        "master_copy": str(master_copy),
        "audit_pass": True,
        "promotion_ready": False,
        "requires_closure_validation": True,
    }
    audit_json.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )

    lines = [
        "QEDCalc sparse master-basis discovery finalize audit",
        f"family: {spec.family_id}",
        f"level: {plan.level}",
        f"mandatory targets: {plan.target_count}",
        f"covered physical sectors: {plan.sector_count}",
        f"envelope: {plan.envelope.tag}",
        f"candidate masters: {len(masters)}",
        f"master source mode: {source_mode}",
        f"master copy: {master_copy}",
        "promotion-ready: False",
        "next: validate this candidate with the existing mandatory closure path",
        f"audit JSON: {audit_json}",
        "QEDCalc sparse master-basis discovery finalize audit PASS",
    ]
    audit_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    for line in lines:
        print(line)


def show_plan(args: argparse.Namespace) -> None:
    spec, plan, project = _resolve(args)
    recursive_hint = (
        "This sparse list replaces full recursive seed selection for discovery; "
        "it does not enumerate the entire seed volume."
    )
    print("QEDCalc sparse master-basis discovery plan")
    print(f"family: {spec.family_id}")
    print(f"representative: {spec.representative}")
    print(f"level: {plan.level}")
    print(f"physical / auxiliary: {plan.physical_count} / {plan.auxiliary_count}")
    print(f"covered physical sectors: {plan.sector_count}")
    print(f"mandatory targets: {plan.target_count}")
    print(f"required envelope: {plan.envelope.tag}")
    print(f"project: {project}")
    print(recursive_hint)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True)
    parser.add_argument("--level", type=int, choices=(0, 1, 2), default=1)
    parser.add_argument("--fresh", action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--finalize", action="store_true")
    group.add_argument("--show-plan", action="store_true")
    args = parser.parse_args()

    if args.prepare:
        prepare(args)
    elif args.finalize:
        finalize(args)
    else:
        show_plan(args)


if __name__ == "__main__":
    main()
