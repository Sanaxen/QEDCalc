"""Prepare/finalize the Q02/Q45 r8s3d0 Kira+FireFly baseline run.

This is intentionally isolated from the ordinary Kira/Fermat baseline project.
FireFly performs the full finite-field reduction; no previously known Q02
master basis is assumed.
"""
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

PROJECT = ROOT / "output" / "kira_q02_full_firefly_r8s3d0"
AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
AUDIT_JSON = AUDIT_DIR / "three_loop_q02_kira_firefly_r8s3d0_audit.json"
AUDIT_TXT = AUDIT_DIR / "three_loop_q02_kira_firefly_r8s3d0_audit.txt"
MASTER_COPY = AUDIT_DIR / "q02_firefly_r8s3d0_masters.txt"
LIMITS = Q02SeedLimits(8, 3, 0)
BOUNDARY_SEEDS = ["r9s3d0", "r8s4d0", "r8s3d1"]
RUNTIME_NAMES = (
    "results", "sectormappings", "tmp", "firefly_saves", "ff_save",
    "firefly_saves_alt", "pyred",
)


def _clean_runtime_outputs() -> list[str]:
    removed: list[str] = []
    for name in RUNTIME_NAMES:
        path = PROJECT / name
        if path.is_dir():
            shutil.rmtree(path)
            removed.append(str(path))
        elif path.exists():
            path.unlink()
            removed.append(str(path))
    for pattern in ("*.log", "*.log.gz"):
        for path in PROJECT.glob(pattern):
            path.unlink()
            removed.append(str(path))
    return removed


def _render_firefly_jobs() -> str:
    return """jobs:
  - reduce_sectors:
      reduce:
        - {topologies: [Q02_full], sectors: [255], r: 8, s: 3, d: 0}
      select_integrals:
        select_mandatory_recursively:
          - {topologies: [Q02_full], sectors: [255], r: 8, s: 3, d: 0}
      run_symmetries: true
      run_initiate: true
      run_triangular: false
      run_back_substitution: false
      run_firefly: true
"""


def prepare() -> None:
    basis = validate_q02_kira_basis()
    manifest = q02_kira_manifest(LIMITS)
    errors: list[str] = []
    if basis.get("coefficient_matrix_rank") != 12 or not basis.get("full_rank"):
        errors.append(f"Q02 basis is not full rank: {basis}")
    if manifest.get("top_sector") != Q02_KIRA_TOP_SECTOR:
        errors.append(f"Q02 top sector changed: {manifest.get('top_sector')}")
    if manifest.get("seed_limits") != {"r": 8, "s": 3, "d": 0}:
        errors.append(f"Q02 baseline seed changed: {manifest.get('seed_limits')}")
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc Q02 FireFly r8s3d0 baseline prepare FAIL")

    PROJECT.mkdir(parents=True, exist_ok=True)
    removed = _clean_runtime_outputs()
    export_q02_kira_project(PROJECT, limits=LIMITS, back_substitution=False)
    (PROJECT / "jobs.yaml").write_text(_render_firefly_jobs(), encoding="utf-8", newline="\n")

    manifest_path = PROJECT / "qedcalc_kira_manifest.json"
    exported = json.loads(manifest_path.read_text(encoding="utf-8"))
    exported.update({
        "solver_backend": "firefly",
        "firefly_enabled": True,
        "ordinary_triangular_enabled": False,
        "ordinary_back_substitution_enabled": False,
        "baseline_master_basis_assumed": False,
        "status": "fresh_firefly_baseline_master_discovery",
    })
    manifest_path.write_text(json.dumps(exported, indent=2), encoding="utf-8", newline="\n")

    print("QEDCalc Q02 FireFly r8s3d0 baseline prepare")
    print(f"canonical family: {Q02_KIRA_NAME}")
    print("covered diagrams: ['Q02', 'Q45']")
    print(f"top sector: {Q02_KIRA_TOP_SECTOR}")
    print("seed: r8s3d0")
    print(f"project: {PROJECT}")
    print(f"stale runtime entries removed: {len(removed)}")
    print("solver: Kira full reduction with FireFly")
    print("known Q02 master basis required: False")
    print("QEDCalc Q02 FireFly r8s3d0 baseline prepare PASS")


def _parse(path: Path) -> list[str]:
    pattern = re.compile(rf"{re.escape(Q02_KIRA_NAME)}\s*\[[^\]]+\]")
    out: list[str] = []
    seen: set[str] = set()
    for item in pattern.findall(path.read_text(encoding="utf-8", errors="replace")):
        item = re.sub(r"\s+", "", item)
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def finalize() -> None:
    errors: list[str] = []
    candidates = sorted(PROJECT.rglob("masters.final"), key=lambda p: str(p))
    if not candidates:
        masters_path = None
        masters: list[str] = []
        errors.append(f"no masters.final found under {PROJECT}")
    else:
        if len(candidates) != 1:
            errors.append("multiple masters.final files found: " + ", ".join(str(p) for p in candidates))
        masters_path = candidates[0]
        masters = _parse(masters_path)
        if not masters:
            errors.append(f"no {Q02_KIRA_NAME}[...] masters parsed from {masters_path}")

    stale_save_dirs = [name for name in ("ff_save", "firefly_saves_alt") if (PROJECT / name).exists()]
    if stale_save_dirs:
        errors.append("unexpected alternate FireFly save directories after run: " + ", ".join(stale_save_dirs))

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    if masters:
        MASTER_COPY.write_text("\n".join(masters) + "\n", encoding="utf-8")

    audit = {
        "canonical_family": Q02_KIRA_NAME,
        "covered_diagrams": ["Q02", "Q45"],
        "project_dir": str(PROJECT),
        "solver_backend": "firefly",
        "seed": {"r": 8, "s": 3, "d": 0},
        "top_sector": Q02_KIRA_TOP_SECTOR,
        "masters_final": str(masters_path) if masters_path else None,
        "masters_final_candidate_count": len(candidates),
        "master_count": len(masters),
        "masters": masters,
        "stable_master_copy": str(MASTER_COPY) if masters else None,
        "master_basis_status": "firefly_baseline_candidate_boundary_audits_pending",
        "required_boundary_seeds": BOUNDARY_SEEDS,
        "errors": errors,
        "audit_pass": not errors,
    }
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "QEDCalc Q02 FireFly r8s3d0 baseline Kira audit",
        f"canonical family: {Q02_KIRA_NAME}",
        "covered diagrams: ['Q02', 'Q45']",
        "solver backend: firefly",
        "seed: r8s3d0",
        f"top sector: {Q02_KIRA_TOP_SECTOR}",
        f"masters.final: {audit['masters_final']}",
        f"master count: {audit['master_count']}",
        "master-basis status: FireFly baseline candidate; boundary audits pending",
        "required boundary seeds: " + ", ".join(BOUNDARY_SEEDS),
        f"master copy: {audit['stable_master_copy']}",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {AUDIT_JSON}",
        f"audit TXT: {AUDIT_TXT}",
        "QEDCalc Q02 FireFly r8s3d0 baseline Kira audit " + ("PASS" if not errors else "FAIL"),
    ]
    AUDIT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc Q02 FireFly r8s3d0 baseline Kira audit FAIL")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--finalize", action="store_true")
    args = parser.parse_args()
    prepare() if args.prepare else finalize()


if __name__ == "__main__":
    main()
