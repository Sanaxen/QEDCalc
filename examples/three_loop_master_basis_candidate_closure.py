"""Generic final candidate-closure audit for stage-2 three-loop master bases.

After a seed-dependent family has been reduced through a common mandatory-union
context, this helper takes the resulting candidate master basis and proves it at
the three one-axis extensions of the common r/s/d envelope.  The exact same
mandatory target set is used at every boundary: original union targets plus the
candidate master forms, deduplicated deterministically.

The companion BAT file launches Kira/FireFly.  This module only prepares the
projects and audits completed reductions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Iterable

from three_loop.integral_family_classification import ROOT
from three_loop.master_basis_api import (
    Seed,
    build_family_spec,
    export_kira_project,
    find_single_masters_final,
    find_or_infer_masters,
    parse_integral,
)

AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
MANDATORY_NAME = "mandatory_candidate_closure_targets.txt"


def _parse_seed(text: str) -> Seed:
    m = re.fullmatch(r"r(\d+)s(\d+)d(\d+)", text.strip())
    if not m:
        raise argparse.ArgumentTypeError("seed must look like r8s3d0")
    return Seed(*(int(x) for x in m.groups()))


def _normalize_integral(text: str, family_id: str) -> str:
    family, indices = parse_integral(text)
    if family != family_id:
        raise ValueError(f"integral belongs to {family!r}, expected {family_id!r}: {text}")
    if len(indices) != 12:
        raise ValueError(f"expected 12 indices: {text}")
    return f"{family}[{','.join(str(x) for x in indices)}]"


def _read_integrals(path: Path, family_id: str) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(path)
    out: list[str] = []
    seen: set[str] = set()
    pattern = re.compile(rf"{re.escape(family_id)}\s*\[[^\]]+\]")
    text = path.read_text(encoding="utf-8", errors="replace")
    for raw in pattern.findall(text):
        item = _normalize_integral(re.sub(r"\s+", "", raw), family_id)
        if item not in seen:
            seen.add(item)
            out.append(item)
    if not out:
        raise ValueError(f"no {family_id} integrals found in {path}")
    return out


def _target_sectors(targets: list[str]) -> list[int]:
    sectors: set[int] = set()
    for target in targets:
        _, indices = parse_integral(target)
        sector = sum(1 << i for i, power in enumerate(indices) if int(power) > 0)
        sectors.add(sector)
    return sorted(sectors)


def _maximal_sectors(sectors: list[int]) -> list[int]:
    unique = sorted(set(int(x) for x in sectors))
    return [
        sector for sector in unique
        if not any(sector != other and (sector & other) == sector for other in unique)
    ]


def _union_audit(family_id: str, solver: str, baseline_seed: Seed) -> tuple[Path, dict]:
    pattern = (
        f"three_loop_{family_id.lower()}_{solver}_{baseline_seed.tag}_"
        "union_*_reduction_audit.json"
    )
    hits = sorted(AUDIT_DIR.glob(pattern))
    if len(hits) != 1:
        raise FileNotFoundError(
            f"expected exactly one union-reduction audit for {family_id} {baseline_seed.tag}; "
            f"hits={hits}"
        )
    path = hits[0]
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("audit_pass"):
        raise ValueError(f"union-reduction audit is not PASS: {path}")
    return path, data


def _resolve(args: argparse.Namespace):
    spec = build_family_spec(args.family)
    baseline_seed = args.baseline_seed or spec.baseline_seed
    audit_path, audit = _union_audit(spec.family_id, args.solver, baseline_seed)
    envelope = _parse_seed(str(audit["required_envelope"]))
    source_targets = Path(str(audit["source_target_file"]))
    candidate_file = Path(str(audit["candidate_master_copy"]))
    union_targets = _read_integrals(source_targets, spec.family_id)
    candidate = _read_integrals(candidate_file, spec.family_id)

    closure: list[str] = []
    seen: set[str] = set()
    for item in [*union_targets, *candidate]:
        if item not in seen:
            seen.add(item)
            closure.append(item)
    return (
        spec,
        baseline_seed,
        audit_path,
        envelope,
        source_targets,
        union_targets,
        candidate_file,
        candidate,
        closure,
    )


def _stem(family_id: str, solver: str, baseline_seed: Seed, envelope: Seed) -> str:
    return (
        f"three_loop_{family_id.lower()}_{solver}_{baseline_seed.tag}_"
        f"candidate_{envelope.tag}_closure"
    )


def _project(family_id: str, solver: str, baseline_seed: Seed, seed: Seed) -> Path:
    return ROOT / "output" / (
        f"kira_{family_id.lower()}_{solver}_candidate_closure_"
        f"{baseline_seed.tag}_{seed.tag}"
    )


def _manifest_path(family_id: str, solver: str, baseline_seed: Seed, envelope: Seed) -> Path:
    return AUDIT_DIR / f"{_stem(family_id, solver, baseline_seed, envelope)}_manifest.json"


def prepare(args: argparse.Namespace) -> None:
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
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    projects: list[dict[str, str]] = []
    reduce_sectors = _target_sectors(closure)
    top_level_sectors = _maximal_sectors([spec.top_sector, *reduce_sectors])
    for seed in envelope.one_axis_extensions():
        project = _project(spec.family_id, args.solver, baseline_seed, seed)
        export_kira_project(
            spec,
            project,
            seed=seed,
            solver=args.solver,
            mandatory_file=MANDATORY_NAME,
            reduce_sectors=reduce_sectors,
            top_level_sectors=top_level_sectors,
            clean=True,
        )
        mandatory = project / MANDATORY_NAME
        mandatory.write_text("\n".join(closure) + "\n", encoding="utf-8", newline="\n")
        projects.append({"seed": seed.tag, "project": str(project), "mandatory_file": str(mandatory)})

    manifest = {
        "schema_version": 1,
        "stage": "master_basis_candidate_closure",
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
        "candidate_masters": candidate,
        "closure_target_count": len(closure),
        "closure_targets": closure,
        "reduce_sectors": reduce_sectors,
        "top_level_sectors": top_level_sectors,
        "boundaries": projects,
    }
    manifest_path = _manifest_path(spec.family_id, args.solver, baseline_seed, envelope)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n"
    )

    print("QEDCalc generic candidate master closure prepare")
    print(f"family: {spec.family_id}")
    print(f"diagrams: {list(spec.diagrams)}")
    print(f"baseline seed: {baseline_seed.tag}")
    print(f"solver: {args.solver}")
    print(f"candidate envelope: {envelope.tag}")
    print(f"union targets: {len(union_targets)}")
    print(f"candidate masters: {len(candidate)}")
    print(f"closure targets: {len(closure)}")
    print(f"mandatory target sectors: {reduce_sectors}")
    print(f"Kira top-level sectors: {top_level_sectors}")
    for row in projects:
        print(f"boundary {row['seed']}: {row['project']}")
    print(f"manifest: {manifest_path}")
    print("QEDCalc generic candidate master closure prepare PASS")


def print_projects(args: argparse.Namespace) -> None:
    (
        spec, baseline_seed, _, envelope, _, _, _, _, _
    ) = _resolve(args)
    for seed in envelope.one_axis_extensions():
        print(str(_project(spec.family_id, args.solver, baseline_seed, seed)))


def _reduction_files(project: Path, family_id: str) -> list[Path]:
    result_root = project / "results" / family_id
    if not result_root.exists():
        return []
    preferred = [result_root / "kira_integrals.kira"]
    hits = [p for p in preferred if p.exists()]
    for pattern in ("*.kira", "*.txt", "*.m"):
        for path in result_root.rglob(pattern):
            if path.name == "masters.final" or path in hits:
                continue
            hits.append(path)
    return hits


def _equation_lhs(text: str, family_id: str) -> dict[str, str]:
    """Best-effort parser for Kira text exports.

    Kira versions differ slightly in whitespace and line wrapping.  We only need
    a conservative answer: an explicit LHS proves that a non-master target was
    reduced (or zero); absence leaves it unresolved rather than guessing.
    """
    integral = rf"{re.escape(family_id)}\s*\[[^\]]+\]"
    eq = re.compile(rf"(?ms)^\s*({integral})\s*=\s*(.*?)(?=^\s*{integral}\s*=|\Z)")
    out: dict[str, str] = {}
    for match in eq.finditer(text):
        lhs = _normalize_integral(re.sub(r"\s+", "", match.group(1)), family_id)
        out[lhs] = match.group(2).strip()
    return out


def _classify_targets(project: Path, family_id: str, targets: Iterable[str], masters: list[str]) -> dict:
    master_set = set(masters)
    equations: dict[str, str] = {}
    files = _reduction_files(project, family_id)
    for path in files:
        try:
            equations.update(_equation_lhs(path.read_text(encoding="utf-8", errors="replace"), family_id))
        except OSError:
            pass

    buckets = {"master": [], "reduced": [], "zero": [], "unresolved": []}
    family_pattern = re.compile(rf"{re.escape(family_id)}\s*\[")
    for target in targets:
        if target in master_set:
            buckets["master"].append(target)
            continue
        rhs = equations.get(target)
        if rhs is None:
            buckets["unresolved"].append(target)
        elif family_pattern.search(rhs):
            buckets["reduced"].append(target)
        else:
            # A completed Kira equation without a family integral on the RHS is
            # a zero/scaleless result for this reduction purpose.
            buckets["zero"].append(target)
    return {
        "counts": {key: len(value) for key, value in buckets.items()},
        "items": buckets,
        "reduction_files": [str(p) for p in files],
    }


def finalize(args: argparse.Namespace) -> None:
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
    manifest_path = _manifest_path(spec.family_id, args.solver, baseline_seed, envelope)
    if not manifest_path.exists():
        raise FileNotFoundError(f"closure manifest not found; run --prepare first: {manifest_path}")

    rows: list[dict] = []
    errors: list[str] = []
    candidate_set = set(candidate)
    for seed in envelope.one_axis_extensions():
        project = _project(spec.family_id, args.solver, baseline_seed, seed)
        try:
            masters_path, masters, master_source_mode = find_or_infer_masters(
                project,
                spec.family_id,
                mandatory_targets=closure,
            )
        except Exception as exc:
            errors.append(f"{seed.tag}: {exc}")
            rows.append({"seed": seed.tag, "project": str(project), "stable": False, "error": str(exc)})
            continue

        candidate_status = _classify_targets(project, spec.family_id, candidate, masters)
        union_status = _classify_targets(project, spec.family_id, union_targets, masters)
        closure_status = _classify_targets(project, spec.family_id, closure, masters)
        current_set = set(masters)
        missing_candidate_masters = sorted(candidate_set - current_set)
        candidate_unresolved = candidate_status["counts"]["unresolved"]
        closure_unresolved = closure_status["counts"]["unresolved"]
        stable = not missing_candidate_masters and candidate_unresolved == 0 and closure_unresolved == 0
        if not stable:
            errors.append(
                f"{seed.tag}: candidate/closure unstable; missing candidate masters="
                f"{len(missing_candidate_masters)}, unresolved={closure_unresolved}"
            )
        rows.append({
            "seed": seed.tag,
            "project": str(project),
            "masters_final": str(masters_path),
            "master_source_mode": master_source_mode,
            "master_count": len(masters),
            "candidate_status": candidate_status,
            "union_target_status": union_status,
            "closure_target_status": closure_status,
            "missing_candidate_masters": missing_candidate_masters,
            "stable": stable,
        })

    stable_all = not errors and len(rows) == 3 and all(row.get("stable") for row in rows)
    stem = _stem(spec.family_id, args.solver, baseline_seed, envelope)
    audit_json = AUDIT_DIR / f"{stem}_audit.json"
    audit_txt = AUDIT_DIR / f"{stem}_audit.txt"
    audit = {
        "schema_version": 1,
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
    audit_json.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n"
    )

    lines = [
        "QEDCalc generic candidate master closure aggregate audit",
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
        cc = row["candidate_status"]["counts"]
        uc = row["union_target_status"]["counts"]
        lines.extend([
            f"{row['seed']}: masters.final={row['master_count']} stable={row['stable']}",
            f"  candidate status: {cc}",
            f"  union target status: {uc}",
            f"  missing candidate masters: {len(row['missing_candidate_masters'])}",
        ])
    lines.extend([
        f"stable under tested one-axis extensions: {stable_all}",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {audit_json}",
        f"audit TXT: {audit_txt}",
        "QEDCalc generic candidate master closure aggregate audit " + ("PASS" if stable_all else "FAIL"),
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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--finalize", action="store_true")
    group.add_argument("--print-projects", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare(args)
    elif args.finalize:
        finalize(args)
    else:
        print_projects(args)


if __name__ == "__main__":
    main()
