"""Restricted FireFly rescue probe for refined candidates in one exact sector.

This is intentionally much smaller than the earlier full r8s6d2
direct-reducibility project.  All refined candidates in the selected exact
sector are mandatory and are also supplied as preferred masters, together with
known refined candidates from proper subsectors.  This avoids an arbitrary
basis rotation that would otherwise force an expensive reduction merely to
recover the originally selected refined basis.

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


def _project(
    family: str,
    baseline: Seed,
    sector: int,
    seed: Seed,
    *,
    multi_target: bool = False,
) -> Path:
    mode = "preferred_masters" if multi_target else "firefly_numerator"
    return ROOT / "output" / (
        f"kira_{family.lower()}_{mode}_"
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
    if not targets:
        raise ValueError(f"sector {sector} contains no refined candidates")

    # For a fixed exact sector the positive-line count is fixed by the sector
    # bit mask, independent of how many refined candidates live in that sector.
    # With dot degree d, the largest positive-power sum that needs testing is
    # n_positive_lines + d.
    positive_count = int(sector).bit_count()
    dot_degree = int(args.max_d)
    seed = Seed(positive_count + dot_degree, int(args.max_s), dot_degree)

    proper_subsector_preferred = sorted({
        x for x in candidate
        if x not in targets
        and (_sector(x) & sector) == _sector(x)
        and _sector(x) != sector
    })
    # Prefer the refined candidates from this exact sector themselves.  With
    # multiple mandatory targets Kira may otherwise choose a different but
    # equivalent sector basis, forcing an expensive reduction merely to prove
    # that the original candidates span the same master space.
    preferred = sorted(set(targets) | set(proper_subsector_preferred))

    return (
        spec,
        baseline,
        union_audit_path,
        envelope,
        candidate_file,
        candidate,
        sector,
        targets,
        seed,
        preferred,
        proper_subsector_preferred,
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
        targets,
        seed,
        preferred,
        proper_subsector_preferred,
    ) = _context(args)

    project = _project(
        spec.family_id,
        baseline,
        sector,
        seed,
        multi_target=len(targets) > 1,
    )

    # A single target can use the original FireFly path because Kira commonly
    # concludes immediately that there is nothing to reduce.  For multiple
    # targets the scientific question here is only whether the requested
    # refined candidates can be selected as masters at this restricted
    # boundary.  Use initiate-only masters mode so Kira does not launch the
    # expensive downstream reduction merely to rotate between equivalent bases.
    solver = "masters" if len(targets) > 1 else "firefly"
    export_kira_project(
        spec,
        project,
        seed=seed,
        solver=solver,
        mandatory_file=MANDATORY_NAME,
        reduce_sectors=[sector],
        top_level_sectors=[sector],
        preferred_masters_file=PREFERRED_NAME if preferred else None,
        clean=True,
    )

    mandatory = project / MANDATORY_NAME
    mandatory.write_text("\n".join(targets) + "\n", encoding="utf-8", newline="\n")
    preferred_path = project / PREFERRED_NAME
    if preferred:
        preferred_path.write_text("\n".join(preferred) + "\n", encoding="utf-8", newline="\n")
    elif preferred_path.exists():
        preferred_path.unlink()

    manifest = {
        "schema_version": 1,
        "stage": "master_basis_candidate_restricted_sector_probe",
        "family": spec.family_id,
        "baseline_seed": baseline.tag,
        "candidate_envelope": envelope.tag,
        "firefly_seed": seed.tag,
        "solver": solver,
        "sector": sector,
        "targets": targets,
        "target_count": len(targets),
        "candidate_master_file": str(candidate_file),
        "candidate_master_count": len(candidate),
        "preferred_master_count": len(preferred),
        "preferred_masters": preferred,
        "preferred_proper_subsector_master_count": len(proper_subsector_preferred),
        "preferred_proper_subsector_masters": proper_subsector_preferred,
        "union_reduction_audit": str(union_audit_path),
        "project": str(project),
        "restriction": {
            "positive_power_sum_r": seed.r,
            "numerator_sum_s": seed.s,
            "dot_degree_d": seed.d,
            "top_level_sector": sector,
            "mandatory_target_count": len(targets),
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
    print(f"solver: {solver}")
    print(f"sector: {sector}")
    print(f"targets: {len(targets)}")
    for target in targets:
        print(f"  {target}")
    print(f"preferred masters total: {len(preferred)}")
    print(f"preferred exact-sector targets: {len(targets)}")
    print(f"preferred proper-subsector masters: {len(proper_subsector_preferred)}")
    print(f"project: {project}")
    print(f"manifest: {manifest_path}")
    print("QEDCalc FireFly fixed-sector numerator prepare PASS")


def print_project(args: argparse.Namespace) -> None:
    spec, baseline, _, _, _, _, sector, targets, seed, _, _ = _context(args)
    print(_project(
        spec.family_id,
        baseline,
        sector,
        seed,
        multi_target=len(targets) > 1,
    ))


def finalize(args: argparse.Namespace) -> None:
    (
        spec,
        baseline,
        union_audit_path,
        envelope,
        candidate_file,
        candidate,
        sector,
        targets,
        seed,
        preferred,
        proper_subsector_preferred,
    ) = _context(args)
    project = _project(
        spec.family_id,
        baseline,
        sector,
        seed,
        multi_target=len(targets) > 1,
    )

    try:
        masters_path, masters, source_mode = find_or_infer_masters(
            project,
            spec.family_id,
            mandatory_targets=targets,
        )
    except ValueError:
        # Multi-target preferred-master experiments use a fresh project
        # namespace.  If that experiment fails before master identification,
        # salvage the earlier restricted FireFly project when it already
        # completed Kira's initiate/master-selection stage for the exact same
        # mandatory target set.
        if len(targets) <= 1:
            raise
        legacy_project = _project(
            spec.family_id,
            baseline,
            sector,
            seed,
            multi_target=False,
        )
        masters_path, masters, source_mode = find_or_infer_masters(
            legacy_project,
            spec.family_id,
            mandatory_targets=targets,
        )
        project = legacy_project
        source_mode = f"legacy-restricted-project:{source_mode}"
    status = _classify_targets(project, spec.family_id, targets, masters)
    counts = status["counts"]
    master_set = set(masters)
    retained_targets = [x for x in targets if x in master_set]

    # Kira's initiate/master-identification stage has a useful stronger
    # semantics for mandatory targets: after equation selection, any mandatory
    # integral for which no reduction formula was found is itself reported as a
    # master.  Therefore, once a valid master list has been emitted for this
    # exact mandatory set, a mandatory target absent from that list is evidence
    # that an initiate-stage reduction relation was found, even if the later
    # triangular/FireFly export failed before writing text reduction tables.
    #
    # Apply this only when every unresolved item belongs to the exact mandatory
    # set of this project and a non-empty master list was recovered.
    initiate_reduced = []
    if masters and counts["unresolved"]:
        unresolved = list(status["items"]["unresolved"])
        initiate_reduced = [x for x in unresolved if x in set(targets)]
        if len(initiate_reduced) == len(unresolved):
            status["items"]["reduced"].extend(initiate_reduced)
            status["items"]["unresolved"] = []
            status["counts"]["reduced"] += len(initiate_reduced)
            status["counts"]["unresolved"] = 0
            status["classification_basis"] = (
                "kira-initiate-master-list: mandatory target absent from the "
                "reported master list implies a reduction relation was found "
                "during equation selection"
            )
            counts = status["counts"]

    # A restricted probe is considered successful when every mandatory target
    # has a definite classification: reduced, zero, or retained as a master.
    classified = (
        counts["master"] + counts["reduced"] + counts["zero"]
    )
    audit_pass = counts["unresolved"] == 0 and classified == len(targets)
    if audit_pass and counts["master"] == len(targets):
        conclusion = f"all-targets-retained-master-in-restricted-{seed.tag}-probe"
    elif audit_pass:
        conclusion = f"all-targets-classified-in-restricted-{seed.tag}-probe"
    else:
        conclusion = "unresolved"

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
        "targets": targets,
        "target_count": len(targets),
        "candidate_master_file": str(candidate_file),
        "candidate_master_count": len(candidate),
        "preferred_master_count": len(preferred),
        "preferred_masters": preferred,
        "preferred_proper_subsector_master_count": len(proper_subsector_preferred),
        "preferred_proper_subsector_masters": proper_subsector_preferred,
        "union_reduction_audit": str(union_audit_path),
        "project": str(project),
        "masters_path": str(masters_path),
        "master_source_mode": source_mode,
        "master_count": len(masters),
        "target_status": status,
        "initiate_stage_reduced_targets": initiate_reduced,
        "conclusion": conclusion,
        "audit_pass": audit_pass,
        "interpretation": (
            f"This is a restricted exact-sector {seed.tag} probe. "
            "A reduction/zero classification is a positive reducibility witness; "
            "for mandatory targets, absence from a valid Kira initiate-stage "
            "master list is also treated as a reduction witness. Retention is "
            "evidence within the tested exact-sector boundary. "
            "The audit covers all refined candidates in this sector."
        ),
    }
    audit_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")

    lines = [
        "QEDCalc FireFly fixed-sector numerator audit",
        f"family: {spec.family_id}",
        f"baseline seed: {baseline.tag}",
        f"FireFly seed: {seed.tag}",
        f"sector: {sector}",
        f"targets: {len(targets)}",
        *[f"  {target}" for target in targets],
        f"preferred masters total: {len(preferred)}",
        f"preferred exact-sector targets: {len(targets)}",
        f"preferred proper-subsector masters: {len(proper_subsector_preferred)}",
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
