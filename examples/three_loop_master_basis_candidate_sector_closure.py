"""Targeted sector-local closure for refined three-loop master candidates.

This is a validation/rescue path for refinement-stage candidate closures that are
too large when all candidate sectors are generated together.

For one requested stronger seed, refined candidate masters are grouped by their
exact sector.  Each group is tested in its own Kira initiate-only project with
that exact sector as the family's top-level sector and with only the candidate
integrals from that sector as mandatory targets.

Scientific use:
1. First validate this sector-local method on a stronger seed whose full closure
   already completed and is known stable.
2. Only after that consistency check passes, use it for resource-blocked stronger
   seeds.
3. A candidate is retained only when it appears in the initiate-only master list
   of its exact-sector project.  Missing candidates are refinement signals.
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
    integral_complexity,
    parse_integral,
)
from examples.three_loop_master_basis_candidate_closure import (
    AUDIT_DIR,
    _parse_seed,
    _read_integrals,
    _resolve,
)

MANDATORY_NAME = "mandatory_candidate_sector_closure_targets.txt"
PREFERRED_NAME = "preferred_candidate_sector_masters.txt"


def _sector(target: str) -> int:
    _, indices = parse_integral(target)
    return sum(1 << i for i, power in enumerate(indices) if int(power) > 0)


def _groups(candidate: list[str]) -> dict[int, list[str]]:
    out: dict[int, list[str]] = {}
    for target in candidate:
        out.setdefault(_sector(target), []).append(target)
    return dict(sorted(out.items()))


def _project(family: str, baseline: Seed, seed: Seed, sector: int) -> Path:
    return ROOT / "output" / (
        f"kira_{family.lower()}_masters_candidate_sector_closure_"
        f"{baseline.tag}_{seed.tag}_sec{sector}"
    )


def _manifest_path(family: str, baseline: Seed, seed: Seed) -> Path:
    return AUDIT_DIR / (
        f"three_loop_{family.lower()}_masters_{baseline.tag}_"
        f"candidate_sector_closure_{seed.tag}_manifest.json"
    )


def _audit_path(family: str, baseline: Seed, seed: Seed) -> tuple[Path, Path]:
    stem = (
        f"three_loop_{family.lower()}_masters_{baseline.tag}_"
        f"candidate_sector_closure_{seed.tag}_audit"
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
            "sector-local closure is only valid after a strict-subset refinement; "
            f"closure_mode={closure_mode}"
        )
    seed = _parse_seed(args.seed)
    expected = {x.tag for x in envelope.one_axis_extensions()}
    if seed.tag not in expected:
        raise ValueError(
            f"seed {seed.tag} is not a one-axis extension of {envelope.tag}; "
            f"expected one of {sorted(expected)}"
        )
    return (
        spec,
        baseline,
        union_audit_path,
        envelope,
        source_targets,
        union_targets,
        candidate_file,
        candidate,
        seed,
    )


def _restricted_equivalent_audit(
    family_id: str,
    baseline: Seed,
    seed: Seed,
    sector: int,
    targets: list[str],
) -> tuple[bool, str]:
    """Accept a passing restricted exact-sector audit when it covers the seed envelope.

    For a fixed sector, r and d are not independent:
        r = n_positive_lines + d.
    Therefore, if the requested seed's r ceiling exceeds the maximum allowed by
    its d ceiling, the effective r ceiling is n_positive_lines + d.  A passing
    restricted FireFly audit at that effective (r,s,d) envelope is equivalent
    for this exact-sector target check.
    """
    if len(targets) != 1:
        return False, "restricted-equivalent audit requires exactly one target"

    family, indices = parse_integral(targets[0])
    if family != family_id:
        return False, "target family mismatch"

    positive_lines = sum(1 for a in indices if int(a) > 0)
    effective_r = min(seed.r, positive_lines + seed.d)
    effective = Seed(effective_r, seed.s, seed.d)

    pattern = (
        f"three_loop_{family_id.lower()}_firefly_numerator_"
        f"{baseline.tag}_{effective.tag}_sec{sector}_audit.json"
    )
    hits = sorted(AUDIT_DIR.glob(pattern))
    if len(hits) != 1:
        return False, (
            f"no unique restricted-equivalent audit for {effective.tag}; "
            f"hits={len(hits)}"
        )

    try:
        data = json.loads(hits[0].read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"cannot read restricted audit: {exc}"

    if not data.get("audit_pass"):
        return False, f"restricted audit did not pass: {hits[0]}"
    if int(data.get("sector", -1)) != sector:
        return False, "restricted audit sector mismatch"
    if str(data.get("target", "")).replace(" ", "") != targets[0].replace(" ", ""):
        return False, "restricted audit target mismatch"
    if str(data.get("firefly_seed", "")) != effective.tag:
        return False, "restricted audit seed mismatch"

    conclusion = str(data.get("conclusion", ""))
    if not conclusion.startswith("retained-master-in-restricted-"):
        return False, f"restricted audit conclusion is not retained-master: {conclusion}"

    return True, (
        f"restricted-equivalent exact-sector audit {effective.tag} "
        f"(requested {seed.tag}; positive_lines={positive_lines}, "
        f"effective_r=min({seed.r},{positive_lines}+{seed.d})={effective_r}) "
        f"from {hits[0]}"
    )


def _reusable_project(project: Path, family_id: str, targets: list[str]) -> tuple[bool, str]:
    """Reuse a completed exact-sector initiate-only result safely."""
    mandatory = project / MANDATORY_NAME
    preferred = project / PREFERRED_NAME
    if not mandatory.exists() or not preferred.exists():
        return False, "mandatory/preferred input copy missing"
    try:
        if _read_integrals(mandatory, family_id) != targets:
            return False, "mandatory target copy differs"
        if _read_integrals(preferred, family_id) != targets:
            return False, "preferred master copy differs"
        masters_path, masters, source_mode = find_or_infer_masters(
            project,
            family_id,
            mandatory_targets=targets,
        )
    except Exception as exc:
        return False, f"master result unavailable: {exc}"
    if not masters:
        return False, "master list is empty"
    return True, f"{len(masters)} masters via {source_mode} from {masters_path}"


def prepare(args: argparse.Namespace) -> None:
    (
        spec,
        baseline,
        union_audit_path,
        envelope,
        source_targets,
        union_targets,
        candidate_file,
        candidate,
        seed,
    ) = _context(args)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    groups = _groups(candidate)
    rows = []
    for sector, targets in groups.items():
        project = _project(spec.family_id, baseline, seed, sector)
        reusable, reuse_note = _reusable_project(
            project, spec.family_id, targets
        ) if project.exists() else (False, "project missing")
        if not reusable:
            restricted_ok, restricted_note = _restricted_equivalent_audit(
                spec.family_id, baseline, seed, sector, targets
            )
            if restricted_ok:
                reusable, reuse_note = True, restricted_note
        if not reusable:
            export_kira_project(
                spec,
                project,
                seed=seed,
                solver="masters",
                mandatory_file=MANDATORY_NAME,
                reduce_sectors=[sector],
                top_level_sectors=[sector],
                preferred_masters_file=PREFERRED_NAME,
                clean=True,
            )
            mandatory = project / MANDATORY_NAME
            mandatory.write_text("\n".join(targets) + "\n", encoding="utf-8", newline="\n")
            preferred = project / PREFERRED_NAME
            preferred.write_text("\n".join(targets) + "\n", encoding="utf-8", newline="\n")
        else:
            mandatory = project / MANDATORY_NAME
            preferred = project / PREFERRED_NAME
            print(f"REUSE sector {sector}: {reuse_note}", flush=True)
        rows.append({
            "sector": sector,
            "target_count": len(targets),
            "targets": targets,
            "project": str(project),
            "mandatory_file": str(mandatory),
            "preferred_masters_file": str(preferred),
            "reused_master_result": reusable,
            "reuse_note": reuse_note,
        })

    manifest = {
        "schema_version": 1,
        "stage": "master_basis_candidate_sector_closure",
        "family": spec.family_id,
        "baseline_seed": baseline.tag,
        "candidate_envelope": envelope.tag,
        "test_seed": seed.tag,
        "union_reduction_audit": str(union_audit_path),
        "source_union_target_file": str(source_targets),
        "union_target_count": len(union_targets),
        "candidate_master_file": str(candidate_file),
        "candidate_master_count": len(candidate),
        "basis_selection": "preferred_masters",
        "sector_count": len(groups),
        "sectors": rows,
    }
    path = _manifest_path(spec.family_id, baseline, seed)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")

    print("QEDCalc refined candidate sector-local closure prepare")
    print(f"family: {spec.family_id}")
    print(f"baseline seed: {baseline.tag}")
    print(f"candidate envelope: {envelope.tag}")
    print(f"test seed: {seed.tag}")
    print(f"candidate masters: {len(candidate)}")
    print("basis selection: preferred_masters")
    print(f"candidate sectors: {len(groups)}")
    for sector, targets in groups.items():
        print(f"sector {sector}: targets={len(targets)} project={_project(spec.family_id, baseline, seed, sector)}")
    print(f"manifest: {path}")
    print("QEDCalc refined candidate sector-local closure prepare PASS")


def print_projects(args: argparse.Namespace) -> None:
    spec, baseline, _, _, _, _, _, candidate, seed = _context(args)
    groups = list(_groups(candidate).items())
    total = len(groups)
    for index, (sector, targets) in enumerate(groups, start=1):
        project = _project(spec.family_id, baseline, seed, sector)
        reusable, _ = _reusable_project(
            project, spec.family_id, targets
        ) if project.exists() else (False, "")
        if not reusable:
            reusable, _ = _restricted_equivalent_audit(
                spec.family_id, baseline, seed, sector, targets
            )
        if reusable:
            continue
        print(f"{index}|{total}|{project}")


def finalize(args: argparse.Namespace) -> None:
    spec, baseline, _, envelope, _, _, candidate_file, candidate, seed = _context(args)
    groups = _groups(candidate)
    rows = []
    errors: list[str] = []
    retained_all: set[str] = set()

    for sector, targets in groups.items():
        project = _project(spec.family_id, baseline, seed, sector)
        restricted_ok, restricted_note = _restricted_equivalent_audit(
            spec.family_id, baseline, seed, sector, targets
        )
        if restricted_ok:
            retained = sorted(set(targets))
            retained_all.update(retained)
            rows.append({
                "sector": sector,
                "target_count": len(targets),
                "project": str(project),
                "masters_final": None,
                "master_source_mode": "restricted-equivalent-firefly-audit",
                "master_count": len(targets),
                "retained_candidate_count": len(retained),
                "missing_candidate_masters": [],
                "stable": True,
                "reuse_note": restricted_note,
            })
            continue

        try:
            masters_path, masters, source_mode = find_or_infer_masters(
                project,
                spec.family_id,
                mandatory_targets=targets,
            )
        except Exception as exc:
            errors.append(f"sector {sector}: {exc}")
            rows.append({
                "sector": sector,
                "target_count": len(targets),
                "stable": False,
                "error": str(exc),
                "project": str(project),
            })
            continue

        master_set = set(masters)
        missing = sorted(set(targets) - master_set)
        retained = sorted(set(targets) & master_set)
        retained_all.update(retained)
        stable = not missing
        if not stable:
            errors.append(
                f"sector {sector}: missing candidate masters={len(missing)}"
            )
        rows.append({
            "sector": sector,
            "target_count": len(targets),
            "project": str(project),
            "masters_final": str(masters_path),
            "master_source_mode": source_mode,
            "master_count": len(masters),
            "retained_candidate_count": len(retained),
            "missing_candidate_masters": missing,
            "stable": stable,
        })

    missing_global = sorted(set(candidate) - retained_all)
    stable_all = (
        not errors
        and len(rows) == len(groups)
        and not missing_global
        and all(row.get("stable") for row in rows)
    )

    audit_json, audit_txt = _audit_path(spec.family_id, baseline, seed)
    payload = {
        "schema_version": 1,
        "stage": "master_basis_candidate_sector_closure_audit",
        "family": spec.family_id,
        "baseline_seed": baseline.tag,
        "candidate_envelope": envelope.tag,
        "test_seed": seed.tag,
        "candidate_master_file": str(candidate_file),
        "candidate_master_count": len(candidate),
        "sector_count": len(groups),
        "retained_candidate_count": len(retained_all),
        "missing_candidate_masters": missing_global,
        "sector_rows": rows,
        "stable_under_sector_local_closure": stable_all,
        "errors": errors,
        "audit_pass": stable_all,
    }
    audit_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")

    lines = [
        "QEDCalc refined candidate sector-local closure audit",
        f"family: {spec.family_id}",
        f"baseline seed: {baseline.tag}",
        f"candidate envelope: {envelope.tag}",
        f"test seed: {seed.tag}",
        f"candidate masters: {len(candidate)}",
        f"candidate sectors: {len(groups)}",
    ]
    for row in rows:
        if "error" in row:
            lines.append(f"sector {row['sector']}: ERROR {row['error']}")
        else:
            lines.append(
                f"sector {row['sector']}: targets={row['target_count']} "
                f"retained={row['retained_candidate_count']}/{row['target_count']} "
                f"masters={row['master_count']} stable={row['stable']}"
            )
    lines.extend([
        f"retained candidate total: {len(retained_all)}/{len(candidate)}",
        f"missing candidate masters: {len(missing_global)}",
        f"stable under sector-local closure: {stable_all}",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {audit_json}",
        f"audit TXT: {audit_txt}",
    ])
    audit_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    if not stable_all:
        raise SystemExit(1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--baseline-seed", type=_parse_seed)
    p.add_argument("--solver", default="masters", choices=["masters"])
    p.add_argument("--seed", required=True)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--print-projects", action="store_true")
    mode.add_argument("--finalize", action="store_true")
    args = p.parse_args()

    if args.prepare:
        prepare(args)
    elif args.print_projects:
        print_projects(args)
    else:
        finalize(args)


if __name__ == "__main__":
    main()
