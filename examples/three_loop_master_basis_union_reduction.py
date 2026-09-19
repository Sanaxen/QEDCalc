"""Generic mandatory-union reduction for stage-2 three-loop master bases.

This is the reusable continuation of the one-axis boundary audit.  When literal
``masters.final`` representatives change with the seed, the boundary audit
writes the union of all observed master forms.  This CLI puts that union into a
single Kira reduction context, derives the minimum r/s/d envelope required by
those explicit targets, and records the resulting candidate master basis.

The actual Kira/FireFly process is intentionally launched by the companion BAT
file so long WSL calculations remain visible and restartable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from three_loop.integral_family_classification import ROOT
from three_loop.master_basis_api import (
    Seed,
    build_family_spec,
    export_kira_project,
    find_single_masters_final,
    parse_integral,
    required_envelope,
)

AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
MANDATORY_NAME = "mandatory_union_targets.txt"


def _parse_seed(text: str) -> Seed:
    match = re.fullmatch(r"r(\d+)s(\d+)d(\d+)", text.strip())
    if not match:
        raise argparse.ArgumentTypeError("seed must look like r8s3d0")
    return Seed(*(int(x) for x in match.groups()))


def _default_target_path(family_id: str, solver: str, baseline_seed: Seed) -> Path:
    return AUDIT_DIR / (
        f"{family_id.lower()}_{solver}_{baseline_seed.tag}_master_union_targets.txt"
    )


def project_path(family_id: str, solver: str, baseline_seed: Seed) -> Path:
    return ROOT / "output" / (
        f"kira_{family_id.lower()}_{solver}_union_{baseline_seed.tag}"
    )


def _read_targets(path: Path, family_id: str) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"mandatory union target file not found: {path}")

    targets: list[str] = []
    seen: set[str] = set()
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        text = raw.strip()
        if not text or text.startswith("#"):
            continue
        family, indices = parse_integral(text)
        if family != family_id:
            raise ValueError(
                f"target belongs to {family!r}, expected {family_id!r}: {text}"
            )
        if len(indices) != 12:
            raise ValueError(f"expected 12 indices in mandatory target: {text}")
        normalized = f"{family}[{','.join(str(x) for x in indices)}]"
        if normalized not in seen:
            seen.add(normalized)
            targets.append(normalized)

    if not targets:
        raise ValueError(f"no mandatory targets found in {path}")
    return targets


def _sha256_targets(targets: list[str]) -> str:
    payload = ("\n".join(targets) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _target_sectors(targets: list[str]) -> list[int]:
    sectors: set[int] = set()
    for target in targets:
        _, indices = parse_integral(target)
        sector = sum(1 << i for i, power in enumerate(indices) if int(power) > 0)
        sectors.add(sector)
    return sorted(sectors)


def _resolve(args: argparse.Namespace):
    spec = build_family_spec(args.family)
    baseline_seed = args.baseline_seed or spec.baseline_seed
    source = args.targets or _default_target_path(
        spec.family_id, args.solver, baseline_seed
    )
    source = Path(source)
    targets = _read_targets(source, spec.family_id)
    envelope = required_envelope(targets, floor=baseline_seed)
    project = project_path(spec.family_id, args.solver, baseline_seed)
    return spec, baseline_seed, source, targets, envelope, project


def prepare(args: argparse.Namespace) -> None:
    spec, baseline_seed, source, targets, envelope, project = _resolve(args)

    reduce_sectors = _target_sectors(targets)
    export_kira_project(
        spec,
        project,
        seed=envelope,
        solver=args.solver,
        mandatory_file=MANDATORY_NAME,
        reduce_sectors=reduce_sectors,
        clean=True,
    )
    mandatory = project / MANDATORY_NAME
    mandatory.write_text("\n".join(targets) + "\n", encoding="utf-8", newline="\n")

    manifest = {
        "schema_version": 1,
        "stage": "master_basis_mandatory_union_reduction",
        "family": spec.family_id,
        "representative": spec.representative,
        "diagrams": list(spec.diagrams),
        "baseline_seed": baseline_seed.tag,
        "solver": args.solver,
        "source_target_file": str(source),
        "mandatory_file": str(mandatory),
        "mandatory_target_count": len(targets),
        "mandatory_target_sha256": _sha256_targets(targets),
        "required_envelope": envelope.tag,
        "reduce_sectors": reduce_sectors,
        "project": str(project),
    }
    (project / "qedcalc_union_reduction_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n"
    )

    print("QEDCalc generic mandatory-union reduction prepare")
    print(f"family: {spec.family_id}")
    print(f"diagrams: {list(spec.diagrams)}")
    print(f"baseline seed: {baseline_seed.tag}")
    print(f"solver: {args.solver}")
    print(f"union target source: {source}")
    print(f"mandatory targets: {len(targets)}")
    print(f"required envelope: {envelope.tag}")
    print(f"mandatory target sectors: {reduce_sectors}")
    print(f"project: {project}")
    print(f"mandatory file: {mandatory}")
    print("QEDCalc generic mandatory-union reduction prepare PASS")


def finalize(args: argparse.Namespace) -> None:
    spec, baseline_seed, source, targets, envelope, project = _resolve(args)
    mandatory = project / MANDATORY_NAME
    if not mandatory.exists():
        raise FileNotFoundError(f"prepared mandatory target copy not found: {mandatory}")

    prepared_targets = _read_targets(mandatory, spec.family_id)
    source_hash = _sha256_targets(targets)
    prepared_hash = _sha256_targets(prepared_targets)
    if source_hash != prepared_hash:
        raise ValueError(
            "union target source changed after prepare; rerun the reduction from prepare"
        )

    masters_path, masters = find_single_masters_final(project, spec.family_id)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    stem = (
        f"three_loop_{spec.family_id.lower()}_{args.solver}_{baseline_seed.tag}_"
        f"union_{envelope.tag}_reduction_audit"
    )
    audit_json = AUDIT_DIR / f"{stem}.json"
    audit_txt = AUDIT_DIR / f"{stem}.txt"
    master_copy = AUDIT_DIR / (
        f"{spec.family_id.lower()}_{args.solver}_{baseline_seed.tag}_"
        f"union_{envelope.tag}_masters.txt"
    )
    master_copy.write_text("\n".join(masters) + "\n", encoding="utf-8", newline="\n")

    audit = {
        "schema_version": 1,
        "family": spec.family_id,
        "representative": spec.representative,
        "diagrams": list(spec.diagrams),
        "baseline_seed": baseline_seed.tag,
        "solver": args.solver,
        "source_target_file": str(source),
        "mandatory_target_count": len(targets),
        "mandatory_target_sha256": source_hash,
        "required_envelope": envelope.tag,
        "project": str(project),
        "masters_final": str(masters_path),
        "candidate_master_count": len(masters),
        "candidate_masters": masters,
        "candidate_master_copy": str(master_copy),
        "audit_pass": True,
    }
    audit_json.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n"
    )

    lines = [
        "QEDCalc generic mandatory-union reduction finalize audit",
        f"family: {spec.family_id}",
        f"diagrams: {list(spec.diagrams)}",
        f"baseline seed: {baseline_seed.tag}",
        f"solver: {args.solver}",
        f"mandatory targets: {len(targets)}",
        f"required envelope: {envelope.tag}",
        f"masters.final: {masters_path}",
        f"candidate master count: {len(masters)}",
        f"candidate master copy: {master_copy}",
        f"audit JSON: {audit_json}",
        f"audit TXT: {audit_txt}",
        "QEDCalc generic mandatory-union reduction finalize audit PASS",
    ]
    audit_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    for line in lines:
        print(line)


def show_plan(args: argparse.Namespace) -> None:
    spec, baseline_seed, source, targets, envelope, project = _resolve(args)
    print("QEDCalc generic mandatory-union reduction plan")
    print(f"family: {spec.family_id}")
    print(f"baseline seed: {baseline_seed.tag}")
    print(f"solver: {args.solver}")
    print(f"union target source: {source}")
    print(f"mandatory targets: {len(targets)}")
    print(f"required envelope: {envelope.tag}")
    print(f"project: {project}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True)
    parser.add_argument("--baseline-seed", type=_parse_seed)
    parser.add_argument("--solver", choices=("ordinary", "firefly"), default="firefly")
    parser.add_argument("--targets", type=Path)
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
