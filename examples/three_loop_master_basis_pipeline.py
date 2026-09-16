"""Thin CLI over the reusable three-loop master-basis API.

This CLI prepares or inspects a single family/seed project.  It intentionally
leaves the actual Kira execution to the Windows/WSL BAT layer.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.master_basis_api import (
    Seed,
    build_family_spec,
    export_kira_project,
    find_single_masters_final,
)


def _parse_seed(text: str) -> Seed:
    import re

    match = re.fullmatch(r"r(\d+)s(\d+)d(\d+)", text.strip())
    if not match:
        raise argparse.ArgumentTypeError("seed must look like r8s3d0")
    return Seed(*(int(x) for x in match.groups()))


def project_path(family: str, seed: Seed, solver: str) -> Path:
    suffix = "" if solver == "ordinary" else f"_{solver}"
    return ROOT / "output" / f"kira_{family.lower()}{suffix}_{seed.tag}"


def prepare(args: argparse.Namespace) -> None:
    spec = build_family_spec(args.family)
    seed = args.seed or spec.baseline_seed
    project = project_path(spec.family_id, seed, args.solver)
    export_kira_project(spec, project, seed=seed, solver=args.solver)
    print("QEDCalc generic master-basis prepare")
    print(f"family: {spec.family_id}")
    print(f"representative: {spec.representative}")
    print(f"diagrams: {list(spec.diagrams)}")
    print(f"unique physical: {spec.unique_physical_count}")
    print(f"auxiliary count: {spec.auxiliary_count}")
    print(f"top sector: {spec.top_sector}")
    print(f"seed: {seed.tag}")
    print(f"solver: {args.solver}")
    print(f"project: {project}")
    print("QEDCalc generic master-basis prepare PASS")


def finalize(args: argparse.Namespace) -> None:
    spec = build_family_spec(args.family)
    seed = args.seed or spec.baseline_seed
    project = project_path(spec.family_id, seed, args.solver)
    masters_path, masters = find_single_masters_final(project, spec.family_id)
    audit_dir = ROOT / "output" / "three_loop_integral_family_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    stem = f"three_loop_{spec.family_id.lower()}_{args.solver}_{seed.tag}_generic_audit"
    audit_json = audit_dir / f"{stem}.json"
    audit_txt = audit_dir / f"{stem}.txt"
    master_copy = audit_dir / f"{spec.family_id.lower()}_{args.solver}_{seed.tag}_masters.txt"
    master_copy.write_text("\n".join(masters) + "\n", encoding="utf-8")
    audit = {
        "schema_version": 1,
        "family": spec.family_id,
        "representative": spec.representative,
        "diagrams": list(spec.diagrams),
        "seed": {"r": seed.r, "s": seed.s, "d": seed.d},
        "solver": args.solver,
        "project": str(project),
        "masters_final": str(masters_path),
        "master_count": len(masters),
        "masters": masters,
        "master_copy": str(master_copy),
        "audit_pass": True,
    }
    audit_json.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "QEDCalc generic master-basis finalize audit",
        f"family: {spec.family_id}",
        f"diagrams: {list(spec.diagrams)}",
        f"seed: {seed.tag}",
        f"solver: {args.solver}",
        f"masters.final: {masters_path}",
        f"master count: {len(masters)}",
        f"master copy: {master_copy}",
        f"audit JSON: {audit_json}",
        f"audit TXT: {audit_txt}",
        "QEDCalc generic master-basis finalize audit PASS",
    ]
    audit_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)


def show_spec(args: argparse.Namespace) -> None:
    spec = build_family_spec(args.family)
    print(json.dumps(spec.to_dict(), indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True)
    parser.add_argument("--seed", type=_parse_seed)
    parser.add_argument("--solver", choices=("ordinary", "firefly"), default="ordinary")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--finalize", action="store_true")
    group.add_argument("--show-spec", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare(args)
    elif args.finalize:
        finalize(args)
    else:
        show_spec(args)


if __name__ == "__main__":
    main()
