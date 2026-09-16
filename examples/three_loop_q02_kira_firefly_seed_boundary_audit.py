"""Run Q02/Q45 one-axis Kira+FireFly seed-boundary master-basis audits."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.q02_kira_backend import (
    Q02_KIRA_NAME,
    Q02_KIRA_TOP_SECTOR,
    Q02SeedLimits,
    export_q02_kira_project,
    q02_kira_manifest,
    validate_q02_kira_basis,
)

AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
BASELINE_MASTER_COPY = AUDIT_DIR / "q02_firefly_r8s3d0_masters.txt"
BASELINE_AUDIT_JSON = AUDIT_DIR / "three_loop_q02_kira_firefly_r8s3d0_audit.json"
SEEDS = {
    "r9s3d0": Q02SeedLimits(9, 3, 0),
    "r8s4d0": Q02SeedLimits(8, 4, 0),
    "r8s3d1": Q02SeedLimits(8, 3, 1),
}
RUNTIME_NAMES = (
    "results", "sectormappings", "tmp", "firefly_saves", "ff_save",
    "firefly_saves_alt", "pyred",
)


def _project(seed: str) -> Path:
    return ROOT / "output" / f"kira_q02_full_firefly_{seed}"


def _audit_json(seed: str) -> Path:
    return AUDIT_DIR / f"three_loop_q02_kira_firefly_{seed}_boundary_audit.json"


def _audit_txt(seed: str) -> Path:
    return AUDIT_DIR / f"three_loop_q02_kira_firefly_{seed}_boundary_audit.txt"


def _parse_text(text: str) -> list[str]:
    pattern = re.compile(rf"{re.escape(Q02_KIRA_NAME)}\s*\[[^\]]+\]")
    out: list[str] = []
    seen: set[str] = set()
    for item in pattern.findall(text):
        item = re.sub(r"\s+", "", item)
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _load_baseline() -> list[str]:
    if not BASELINE_MASTER_COPY.is_file():
        raise FileNotFoundError(
            f"FireFly baseline master copy not found: {BASELINE_MASTER_COPY}; "
            "run run_three_loop_q02_kira_firefly_r8s3d0.bat first"
        )
    masters = _parse_text(BASELINE_MASTER_COPY.read_text(encoding="utf-8", errors="replace"))
    if not masters:
        raise ValueError("Q02 FireFly baseline master copy contains no parseable masters")
    if not BASELINE_AUDIT_JSON.is_file():
        raise FileNotFoundError(f"FireFly baseline audit JSON not found: {BASELINE_AUDIT_JSON}")
    audit = json.loads(BASELINE_AUDIT_JSON.read_text(encoding="utf-8"))
    if not audit.get("audit_pass"):
        raise ValueError("Q02 FireFly baseline audit JSON is not PASS")
    if audit.get("solver_backend") != "firefly":
        raise ValueError("Q02 baseline audit is not a FireFly baseline")
    if audit.get("master_count") != len(masters):
        raise ValueError(
            f"Q02 FireFly baseline count mismatch: audit={audit.get('master_count')} parsed={len(masters)}"
        )
    return masters


def _clean(project: Path) -> list[str]:
    removed: list[str] = []
    for name in RUNTIME_NAMES:
        path = project / name
        if path.is_dir():
            shutil.rmtree(path)
            removed.append(str(path))
        elif path.exists():
            path.unlink()
            removed.append(str(path))
    for pattern in ("*.log", "*.log.gz"):
        for path in project.glob(pattern):
            path.unlink()
            removed.append(str(path))
    return removed


def _render_firefly_jobs(seed: str) -> str:
    limits = SEEDS[seed]
    return f"""jobs:
  - reduce_sectors:
      reduce:
        - {{topologies: [Q02_full], sectors: [255], r: {limits.r}, s: {limits.s}, d: {limits.d}}}
      select_integrals:
        select_mandatory_recursively:
          - {{topologies: [Q02_full], sectors: [255], r: {limits.r}, s: {limits.s}, d: {limits.d}}}
      run_symmetries: true
      run_initiate: true
      run_triangular: false
      run_back_substitution: false
      run_firefly: true
"""


def prepare(seed: str) -> None:
    limits = SEEDS[seed]
    baseline = _load_baseline()
    basis = validate_q02_kira_basis()
    manifest = q02_kira_manifest(limits)
    errors: list[str] = []
    if basis.get("coefficient_matrix_rank") != 12 or not basis.get("full_rank"):
        errors.append(f"Q02 basis is not full rank: {basis}")
    if manifest.get("top_sector") != Q02_KIRA_TOP_SECTOR:
        errors.append(f"Q02 top sector changed: {manifest.get('top_sector')}")
    expected = {"r": limits.r, "s": limits.s, "d": limits.d}
    if manifest.get("seed_limits") != expected:
        errors.append(f"Q02 {seed} seed manifest mismatch: {manifest.get('seed_limits')} != {expected}")
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(f"QEDCalc Q02 FireFly {seed} boundary prepare FAIL")

    project = _project(seed)
    project.mkdir(parents=True, exist_ok=True)
    removed = _clean(project)
    export_q02_kira_project(project, limits=limits, back_substitution=False)
    (project / "jobs.yaml").write_text(_render_firefly_jobs(seed), encoding="utf-8", newline="\n")
    manifest_path = project / "qedcalc_kira_manifest.json"
    exported = json.loads(manifest_path.read_text(encoding="utf-8"))
    exported.update({
        "solver_backend": "firefly",
        "firefly_enabled": True,
        "ordinary_triangular_enabled": False,
        "ordinary_back_substitution_enabled": False,
        "baseline_master_count": len(baseline),
        "status": "firefly_one_axis_seed_boundary_test",
    })
    manifest_path.write_text(json.dumps(exported, indent=2), encoding="utf-8", newline="\n")

    print(f"QEDCalc Q02 FireFly {seed} boundary prepare")
    print(f"canonical family: {Q02_KIRA_NAME}")
    print("covered diagrams: ['Q02', 'Q45']")
    print(f"top sector: {Q02_KIRA_TOP_SECTOR}")
    print(f"seed: {seed}")
    print(f"baseline masters: {len(baseline)}")
    print(f"project: {project}")
    print(f"stale runtime entries removed: {len(removed)}")
    print("solver: Kira full reduction with FireFly")
    print(f"QEDCalc Q02 FireFly {seed} boundary prepare PASS")


def finalize(seed: str) -> None:
    baseline = _load_baseline()
    project = _project(seed)
    errors: list[str] = []
    candidates = sorted(project.rglob("masters.final"), key=lambda p: str(p))
    if not candidates:
        masters_path = None
        masters: list[str] = []
        errors.append(f"no masters.final found under {project}")
    else:
        if len(candidates) != 1:
            errors.append("multiple masters.final files found: " + ", ".join(str(p) for p in candidates))
        masters_path = candidates[0]
        masters = _parse_text(masters_path.read_text(encoding="utf-8", errors="replace"))
        if not masters:
            errors.append(f"no {Q02_KIRA_NAME}[...] masters parsed from {masters_path}")

    boundary_set = set(masters)
    missing = [master for master in baseline if master not in boundary_set]
    retained = len(baseline) - len(missing)
    subset = not missing
    if not subset:
        errors.append(
            f"FireFly baseline master set is not contained in {seed}: "
            f"{len(missing)} of {len(baseline)} baseline masters missing"
        )

    unexpected_save_dirs = [name for name in ("ff_save", "firefly_saves_alt") if (project / name).exists()]
    if unexpected_save_dirs:
        errors.append("unexpected alternate FireFly save directories: " + ", ".join(unexpected_save_dirs))

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    audit = {
        "canonical_family": Q02_KIRA_NAME,
        "covered_diagrams": ["Q02", "Q45"],
        "solver_backend": "firefly",
        "baseline_seed": {"r": 8, "s": 3, "d": 0},
        "boundary_seed_name": seed,
        "boundary_seed": {"r": SEEDS[seed].r, "s": SEEDS[seed].s, "d": SEEDS[seed].d},
        "top_sector": Q02_KIRA_TOP_SECTOR,
        "project_dir": str(project),
        "masters_final": str(masters_path) if masters_path else None,
        "baseline_master_count": len(baseline),
        "boundary_master_count": len(masters),
        "retained_baseline_master_count": retained,
        "missing_baseline_masters": missing,
        "baseline_subset_of_boundary": subset,
        "errors": errors,
        "audit_pass": not errors,
    }
    _audit_json(seed).write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        f"QEDCalc Q02 FireFly {seed} seed-boundary audit",
        "baseline seed: r8s3d0",
        f"boundary seed: {seed}",
        f"baseline masters: {len(baseline)}",
        f"boundary masters: {len(masters)}",
        f"retained baseline masters: {retained}/{len(baseline)}",
        f"missing baseline masters: {len(missing)}",
        f"baseline subset of boundary: {subset}",
        f"masters.final: {audit['masters_final']}",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {_audit_json(seed)}",
        f"audit TXT: {_audit_txt(seed)}",
        f"QEDCalc Q02 FireFly {seed} seed-boundary audit " + ("PASS" if not errors else "FAIL"),
    ]
    _audit_txt(seed).write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(f"QEDCalc Q02 FireFly {seed} seed-boundary audit FAIL")


def aggregate() -> None:
    baseline = _load_baseline()
    errors: list[str] = []
    summaries: dict[str, object] = {}
    for seed in SEEDS:
        path = _audit_json(seed)
        if not path.is_file():
            errors.append(f"missing FireFly boundary audit JSON for {seed}: {path}")
            continue
        audit = json.loads(path.read_text(encoding="utf-8"))
        if not audit.get("audit_pass") or not audit.get("baseline_subset_of_boundary"):
            errors.append(f"FireFly boundary audit did not pass for {seed}")
        if audit.get("baseline_master_count") != len(baseline):
            errors.append(f"FireFly baseline count mismatch for {seed}")
        summaries[seed] = {
            "master_count": audit.get("boundary_master_count"),
            "retained": audit.get("retained_baseline_master_count"),
            "missing": len(audit.get("missing_baseline_masters") or []),
            "subset": bool(audit.get("baseline_subset_of_boundary")),
        }

    stable = not errors and len(summaries) == len(SEEDS)
    out_json = AUDIT_DIR / "three_loop_q02_kira_firefly_seed_boundary_audit.json"
    out_txt = AUDIT_DIR / "three_loop_q02_kira_firefly_seed_boundary_audit.txt"
    result = {
        "canonical_family": Q02_KIRA_NAME,
        "covered_diagrams": ["Q02", "Q45"],
        "solver_backend": "firefly",
        "baseline_seed": {"r": 8, "s": 3, "d": 0},
        "baseline_master_count": len(baseline),
        "boundary_seeds": summaries,
        "stable_under_tested_one_axis_seed_extensions": stable,
        "master_basis_status": (
            "stable_under_tested_one_axis_seed_extensions" if stable else "boundary_review_required"
        ),
        "errors": errors,
        "audit_pass": stable,
    }
    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["QEDCalc Q02 FireFly seed-boundary aggregate audit", f"baseline masters: {len(baseline)}"]
    for seed in SEEDS:
        summary = summaries.get(seed)
        if summary is None:
            lines.append(f"{seed}: MISSING AUDIT")
        else:
            lines.append(
                f"{seed}: masters={summary['master_count']} retained={summary['retained']}/{len(baseline)} "
                f"missing={summary['missing']} subset={summary['subset']}"
            )
    lines += [
        f"stable under tested one-axis seed extensions: {stable}",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {out_json}",
        f"audit TXT: {out_txt}",
        "QEDCalc Q02 FireFly seed-boundary aggregate audit " + ("PASS" if stable else "FAIL"),
    ]
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc Q02 FireFly seed-boundary aggregate audit FAIL")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", choices=tuple(SEEDS))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--finalize", action="store_true")
    group.add_argument("--aggregate", action="store_true")
    args = parser.parse_args()
    if args.aggregate:
        if args.seed is not None:
            parser.error("--aggregate must not be combined with --seed")
        aggregate()
    elif args.seed is None:
        parser.error("--seed is required with --prepare/--finalize")
    elif args.prepare:
        prepare(args.seed)
    else:
        finalize(args.seed)


if __name__ == "__main__":
    main()
