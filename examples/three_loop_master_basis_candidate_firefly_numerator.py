"""FireFly rescue probe for one refined candidate on the fixed-sector s=6 boundary.

This is intentionally much smaller than the earlier r8s6d2 direct-reducibility
project.  For the sector-199 target we use the minimal positive-power envelope
r=5, the required numerator boundary s=6, and d=0.  Only the target integral is
mandatory; known proper-subsector refined candidates are supplied as preferred
masters.

The purpose is to let Kira generate the exact IBP system for this restricted
boundary while FireFly performs finite-field reconstruction, avoiding the
weeks-scale Python sparse-pivot accumulation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.master_basis_api import (
    Seed,
    export_kira_project,
    find_or_infer_masters,
)
from examples.three_loop_master_basis_candidate_closure import (
    AUDIT_DIR,
    _classify_targets,
    _parse_seed,
    _resolve,
)
from examples.three_loop_master_basis_candidate_sector_closure import _sector

MANDATORY_NAME = "mandatory_firefly_numerator_target.txt"
PREFERRED_NAME = "preferred_firefly_numerator_subsector_masters.txt"


def _project(family: str, baseline: Seed, sector: int, seed: Seed) -> Path:
    return ROOT / "output" / (
        f"kira_{family.lower()}_firefly_numerator_"
        f"{baseline.tag}_{seed.tag}_sec{sector}"
    )


def _context(args: argparse.Namespace):
    (
        spec,
        baseline,
        union_audit_path,
        envelope,
        _,
        _,
        candidate_file,
        candidate,
        _,
        closure_mode,
    ) = _resolve(
        argparse.Namespace(
            family=args.family,
            baseline_seed=args.baseline_seed,
            solver="masters",
        )
    )
    if closure_mode != "refined-candidate-only":
        raise RuntimeError(
            f"FireFly numerator probe requires refined-candidate-only context; got {closure_mode}"
        )

    sector = int(args.sector)
    targets = [x for x in candidate if _sector(x) == sector]
    if len(targets) != 1:
        raise ValueError(
            f"sector {sector} must contain exactly one refined candidate; found {len(targets)}"
        )
    target = targets[0]

    # For the current target every positive index equals one.  Increasing dot
    # degree by d raises the positive-power sum r from the positive-line count
    # to positive_count + d.  This lets us test the restricted boundary in the
    # sequence r5s6d0 -> r6s6d1 -> r7s6d2 without reopening the full family.
    positive_count = sum(
        1
        for x in target.split("[", 1)[1].rstrip("]").split(",")
        if int(x) > 0
    )
    dot_degree = int(args.max_d)
    seed = Seed(positive_count + dot_degree, int(args.max_s), dot_degree)

    preferred = sorted({
        x for x in candidate
        if x != target
        and (_sector(x) & sector) == _sector(x)
        and _sector(x) != sector
    })

    return (
        spec,
        baseline,
        union_audit_path,
        envelope,
        candidate_file,
        candidate,
        sector,
        target,
        seed,
        preferred,
    )


def prepare(args: argparse.Namespace) -> None:
    (
        spec,
        baseline,
        union_audit_path,
        envelope,
        candidate_file,
        candidate,
        sector,
        target,
        seed,
        preferred,
    ) = _context(args)

    project = _project(spec.family_id, baseline, sector, seed)
    export_kira_project(
        spec,
        project,
        seed=seed,
        solver="firefly",
        mandatory_file=MANDATORY_NAME,
        reduce_sectors=[sector],
        top_level_sectors=[sector],
        preferred_masters_file=PREFERRED_NAME if preferred else None,
        clean=True,
    )

    mandatory = project / MANDATORY_NAME
    mandatory.write_text(target + "\n", encoding="utf-8", newline="\n")
    preferred_path = project / PREFERRED_NAME
    if preferred:
        preferred_path.write_text("\n".join(preferred) + "\n", encoding="utf-8", newline="\n")
    elif preferred_path.exists():
        preferred_path.unlink()

    manifest = {
        "schema_version": 1,
        "stage": "master_basis_candidate_firefly_numerator_probe",
        "family": spec.family_id,
        "baseline_seed": baseline.tag,
        "candidate_envelope": envelope.tag,
        "firefly_seed": seed.tag,
        "sector": sector,
        "target": target,
        "candidate_master_file": str(candidate_file),
        "candidate_master_count": len(candidate),
        "preferred_subsector_master_count": len(preferred),
        "preferred_subsector_masters": preferred,
        "union_reduction_audit": str(union_audit_path),
        "project": str(project),
        "restriction": {
            "positive_power_sum_r": seed.r,
            "numerator_sum_s": seed.s,
            "dot_degree_d": seed.d,
            "top_level_sector": sector,
            "mandatory_target_count": 1,
        },
    }
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = AUDIT_DIR / (
        f"three_loop_{spec.family_id.lower()}_firefly_numerator_"
        f"{baseline.tag}_{seed.tag}_sec{sector}_manifest.json"
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )

    print("QEDCalc FireFly fixed-sector numerator prepare")
    print(f"family: {spec.family_id}")
    print(f"baseline seed: {baseline.tag}")
    print(f"candidate envelope: {envelope.tag}")
    print(f"FireFly seed: {seed.tag}")
    print(f"sector: {sector}")
    print(f"target: {target}")
    print(f"preferred proper-subsector masters: {len(preferred)}")
    print(f"project: {project}")
    print(f"manifest: {manifest_path}")
    print("QEDCalc FireFly fixed-sector numerator prepare PASS")


def print_project(args: argparse.Namespace) -> None:
    spec, baseline, _, _, _, _, sector, _, seed, _ = _context(args)
    print(_project(spec.family_id, baseline, sector, seed))


def finalize(args: argparse.Namespace) -> None:
    (
        spec,
        baseline,
        union_audit_path,
        envelope,
        candidate_file,
        candidate,
        sector,
        target,
        seed,
        preferred,
    ) = _context(args)
    project = _project(spec.family_id, baseline, sector, seed)

    masters_path, masters, source_mode = find_or_infer_masters(
        project,
        spec.family_id,
        mandatory_targets=[target],
    )
    status = _classify_targets(project, spec.family_id, [target], masters)
    counts = status["counts"]
    target_is_master = target in set(masters)

    if counts["reduced"] == 1 or counts["zero"] == 1:
        conclusion = "reducible"
        audit_pass = True
    elif target_is_master and counts["unresolved"] == 0:
        conclusion = "retained-master-in-restricted-r5s6d0-probe"
        audit_pass = True
    elif target_is_master:
        conclusion = "retained-master-in-restricted-r5s6d0-probe"
        audit_pass = True
    else:
        conclusion = "unresolved"
        audit_pass = False

    stem = (
        f"three_loop_{spec.family_id.lower()}_firefly_numerator_"
        f"{baseline.tag}_{seed.tag}_sec{sector}_audit"
    )
    audit_json = AUDIT_DIR / f"{stem}.json"
    audit_txt = AUDIT_DIR / f"{stem}.txt"
    payload = {
        "schema_version": 1,
        "stage": "master_basis_candidate_firefly_numerator_audit",
        "family": spec.family_id,
        "baseline_seed": baseline.tag,
        "candidate_envelope": envelope.tag,
        "firefly_seed": seed.tag,
        "sector": sector,
        "target": target,
        "candidate_master_file": str(candidate_file),
        "candidate_master_count": len(candidate),
        "preferred_subsector_master_count": len(preferred),
        "preferred_subsector_masters": preferred,
        "union_reduction_audit": str(union_audit_path),
        "project": str(project),
        "masters_path": str(masters_path),
        "master_source_mode": source_mode,
        "master_count": len(masters),
        "target_status": status,
        "conclusion": conclusion,
        "audit_pass": audit_pass,
        "interpretation": (
            "This is a restricted r=positive-line-count, s=6, d=0 sector probe. "
            "A reduction is a positive reducibility witness. Retention as a master "
            "is evidence only within this restricted no-dot numerator boundary and "
            "does not by itself prove full r8s6d2 stability."
        ),
    }
    audit_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")

    lines = [
        "QEDCalc FireFly fixed-sector numerator audit",
        f"family: {spec.family_id}",
        f"baseline seed: {baseline.tag}",
        f"FireFly seed: {seed.tag}",
        f"sector: {sector}",
        f"target: {target}",
        f"preferred proper-subsector masters: {len(preferred)}",
        f"master count: {len(masters)}",
        f"target classification: {counts}",
        f"conclusion: {conclusion}",
        f"audit pass: {audit_pass}",
        f"audit JSON: {audit_json}",
        f"audit TXT: {audit_txt}",
    ]
    audit_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    if not audit_pass:
        raise SystemExit(1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--baseline-seed", type=_parse_seed)
    p.add_argument("--sector", required=True, type=int)
    p.add_argument("--max-s", required=True, type=int)
    p.add_argument("--max-d", required=True, type=int)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--print-project", action="store_true")
    mode.add_argument("--finalize", action="store_true")
    args = p.parse_args()

    if args.prepare:
        prepare(args)
    elif args.print_project:
        print_project(args)
    else:
        finalize(args)


if __name__ == "__main__":
    main()
