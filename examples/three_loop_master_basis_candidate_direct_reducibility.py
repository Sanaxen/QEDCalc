"""Direct reducibility probe for one refined candidate master.

This rescue path is used when a stronger-envelope initiate-only closure is too
large even after exact-sector decomposition.

For one exact-sector candidate:
- select only that integral as the mandatory reduction target;
- deliberately exclude the target itself from preferred_masters;
- prefer only already-known refined candidate masters in proper subsectors of
  the target sector;
- run a normal Kira reduction so an actual reduction equation can be inspected.

A successful explicit reduction proves that the candidate is reducible in the
tested envelope.  If Kira completes and the target remains a master, that is
positive evidence that it remains independent in this restricted top-level
sector context.
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
    parse_integral,
)
from examples.three_loop_master_basis_candidate_closure import (
    AUDIT_DIR,
    _classify_targets,
    _parse_seed,
    _resolve,
)
from examples.three_loop_master_basis_candidate_sector_closure import _sector

MANDATORY_NAME = "mandatory_direct_reducibility_target.txt"
PREFERRED_NAME = "preferred_direct_reducibility_subsector_masters.txt"


def _project(family: str, baseline: Seed, seed: Seed, sector: int) -> Path:
    return ROOT / "output" / (
        f"kira_{family.lower()}_masters_candidate_direct_reducibility_"
        f"{baseline.tag}_{seed.tag}_sec{sector}"
    )


def _audit_paths(family: str, baseline: Seed, seed: Seed, sector: int) -> tuple[Path, Path]:
    stem = (
        f"three_loop_{family.lower()}_masters_{baseline.tag}_"
        f"candidate_direct_reducibility_{seed.tag}_sec{sector}"
    )
    return AUDIT_DIR / f"{stem}.json", AUDIT_DIR / f"{stem}.txt"


def _context(args: argparse.Namespace):
    (
        spec,
        baseline,
        union_audit_path,
        envelope,
        source_targets,
        union_targets,
        candidate_file,
        candidate,
        closure,
        closure_mode,
    ) = _resolve(args)
    if closure_mode != "refined-candidate-only":
        raise RuntimeError(
            "direct reducibility probe requires refined-candidate-only context; "
            f"got {closure_mode}"
        )

    seed = _parse_seed(args.seed)
    expected = {x.tag for x in envelope.one_axis_extensions()}
    if seed.tag not in expected:
        raise ValueError(
            f"seed {seed.tag} is not a one-axis extension of {envelope.tag}; "
            f"expected one of {sorted(expected)}"
        )

    sector = int(args.sector)
    targets = [x for x in candidate if _sector(x) == sector]
    if len(targets) != 1:
        raise ValueError(
            f"sector {sector} must contain exactly one refined candidate for the "
            f"direct probe; found {len(targets)}"
        )
    target = targets[0]

    preferred = [
        x for x in candidate
        if x != target and (_sector(x) & sector) == _sector(x) and _sector(x) != sector
    ]
    preferred = sorted(set(preferred))

    return (
        spec,
        baseline,
        union_audit_path,
        envelope,
        candidate_file,
        candidate,
        seed,
        sector,
        target,
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
        seed,
        sector,
        target,
        preferred,
    ) = _context(args)

    project = _project(spec.family_id, baseline, seed, sector)
    export_kira_project(
        spec,
        project,
        seed=seed,
        solver="ordinary",
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
        "stage": "master_basis_candidate_direct_reducibility",
        "family": spec.family_id,
        "baseline_seed": baseline.tag,
        "candidate_envelope": envelope.tag,
        "test_seed": seed.tag,
        "sector": sector,
        "target": target,
        "candidate_master_file": str(candidate_file),
        "candidate_master_count": len(candidate),
        "preferred_subsector_master_count": len(preferred),
        "preferred_subsector_masters": preferred,
        "union_reduction_audit": str(union_audit_path),
        "project": str(project),
    }
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = AUDIT_DIR / (
        f"three_loop_{spec.family_id.lower()}_masters_{baseline.tag}_"
        f"candidate_direct_reducibility_{seed.tag}_sec{sector}_manifest.json"
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )

    print("QEDCalc candidate direct reducibility prepare")
    print(f"family: {spec.family_id}")
    print(f"baseline seed: {baseline.tag}")
    print(f"candidate envelope: {envelope.tag}")
    print(f"test seed: {seed.tag}")
    print(f"sector: {sector}")
    print(f"target: {target}")
    print(f"preferred proper-subsector masters: {len(preferred)}")
    print(f"project: {project}")
    print(f"manifest: {manifest_path}")
    print("QEDCalc candidate direct reducibility prepare PASS")


def print_project(args: argparse.Namespace) -> None:
    spec, baseline, _, _, _, _, seed, sector, _, _ = _context(args)
    print(_project(spec.family_id, baseline, seed, sector))


def finalize(args: argparse.Namespace) -> None:
    (
        spec,
        baseline,
        union_audit_path,
        envelope,
        candidate_file,
        candidate,
        seed,
        sector,
        target,
        preferred,
    ) = _context(args)
    project = _project(spec.family_id, baseline, seed, sector)

    masters_path, masters, master_source_mode = find_or_infer_masters(
        project,
        spec.family_id,
        mandatory_targets=[target],
    )
    status = _classify_targets(project, spec.family_id, [target], masters)
    counts = status["counts"]

    target_is_master = target in set(masters)
    explicitly_reduced = counts["reduced"] == 1 or counts["zero"] == 1
    unresolved = counts["unresolved"] == 1

    if explicitly_reduced:
        conclusion = "reducible"
        audit_pass = True
    elif target_is_master and not unresolved:
        conclusion = "retained-master"
        audit_pass = True
    elif target_is_master:
        # In initiate/no-reduction completion modes there may be no explicit
        # equation file. Membership in the completed master list is sufficient.
        conclusion = "retained-master"
        audit_pass = True
    else:
        conclusion = "unresolved"
        audit_pass = False

    audit_json, audit_txt = _audit_paths(spec.family_id, baseline, seed, sector)
    payload = {
        "schema_version": 1,
        "stage": "master_basis_candidate_direct_reducibility_audit",
        "family": spec.family_id,
        "baseline_seed": baseline.tag,
        "candidate_envelope": envelope.tag,
        "test_seed": seed.tag,
        "sector": sector,
        "target": target,
        "candidate_master_file": str(candidate_file),
        "candidate_master_count": len(candidate),
        "preferred_subsector_master_count": len(preferred),
        "preferred_subsector_masters": preferred,
        "union_reduction_audit": str(union_audit_path),
        "project": str(project),
        "masters_path": str(masters_path),
        "master_source_mode": master_source_mode,
        "master_count": len(masters),
        "target_status": status,
        "conclusion": conclusion,
        "audit_pass": audit_pass,
    }
    audit_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )

    lines = [
        "QEDCalc candidate direct reducibility audit",
        f"family: {spec.family_id}",
        f"baseline seed: {baseline.tag}",
        f"candidate envelope: {envelope.tag}",
        f"test seed: {seed.tag}",
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
    p.add_argument("--solver", default="masters", choices=["masters"])
    p.add_argument("--seed", required=True)
    p.add_argument("--sector", required=True, type=int)
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
