"""Prepare/finalize the Q05/Q42 baseline Kira master-basis run."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.q05_kira_backend import (
    Q05_COVERED_DIAGRAMS,
    Q05_KIRA_NAME,
    Q05_KIRA_TOP_SECTOR,
    Q05SeedLimits,
    export_q05_kira_project,
    q05_kira_manifest,
    validate_q05_family_equivalence,
    validate_q05_kira_basis,
)

PROJECT = ROOT / "output" / "kira_q05_full_r8s3d0"
AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
AUDIT_JSON = AUDIT_DIR / "three_loop_q05_kira_r8s3d0_audit.json"
AUDIT_TXT = AUDIT_DIR / "three_loop_q05_kira_r8s3d0_audit.txt"
MASTER_COPY = AUDIT_DIR / "q05_r8s3d0_masters.txt"
LIMITS = Q05SeedLimits(8, 3, 0)
BOUNDARY_SEEDS = ["r9s3d0", "r8s4d0", "r8s3d1"]


def _clean_runtime_outputs() -> list[str]:
    removed: list[str] = []
    for name in (
        "results",
        "sectormappings",
        "tmp",
        "firefly_saves",
        "ff_save",
        "firefly_saves_alt",
        "pyred",
    ):
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


def prepare() -> None:
    basis = validate_q05_kira_basis()
    equivalence = validate_q05_family_equivalence()
    manifest = q05_kira_manifest(LIMITS)
    errors: list[str] = []
    if basis.get("coefficient_matrix_rank") != 12 or not basis.get("full_rank"):
        errors.append(f"Q05 basis is not full rank: {basis}")
    if not equivalence.get("all_exact"):
        errors.append(f"Q05/Q42 exact family equivalence failed: {equivalence}")
    if manifest.get("top_sector") != Q05_KIRA_TOP_SECTOR:
        errors.append(f"Q05 top sector changed: {manifest.get('top_sector')}")
    if manifest.get("seed_limits") != {"r": 8, "s": 3, "d": 0}:
        errors.append(f"Q05 baseline seed changed: {manifest.get('seed_limits')}")
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc Q05 r8s3d0 baseline prepare FAIL")

    PROJECT.mkdir(parents=True, exist_ok=True)
    removed = _clean_runtime_outputs()
    export_q05_kira_project(PROJECT, limits=LIMITS, back_substitution=True)

    print("QEDCalc Q05 r8s3d0 baseline prepare")
    print(f"canonical family: {Q05_KIRA_NAME}")
    print(f"covered diagrams: {list(Q05_COVERED_DIAGRAMS)}")
    print(f"top sector: {Q05_KIRA_TOP_SECTOR}")
    print("seed: r8s3d0")
    print(f"project: {PROJECT}")
    print(f"stale runtime entries removed: {len(removed)}")
    print("Q05/Q42 exact family equivalence: PASS")
    print("back substitution: enabled (required for masters.final audit)")
    print("QEDCalc Q05 r8s3d0 baseline prepare PASS")


def _parse(path: Path) -> list[str]:
    pattern = re.compile(rf"{re.escape(Q05_KIRA_NAME)}\s*\[[^\]]+\]")
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
            errors.append(
                "multiple masters.final files found: " + ", ".join(str(p) for p in candidates)
            )
        masters_path = candidates[0]
        masters = _parse(masters_path)
        if not masters:
            errors.append(f"no {Q05_KIRA_NAME}[...] masters parsed from {masters_path}")

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    if masters:
        MASTER_COPY.write_text("\n".join(masters) + "\n", encoding="utf-8")

    audit = {
        "canonical_family": Q05_KIRA_NAME,
        "covered_diagrams": list(Q05_COVERED_DIAGRAMS),
        "project_dir": str(PROJECT),
        "seed": {"r": 8, "s": 3, "d": 0},
        "top_sector": Q05_KIRA_TOP_SECTOR,
        "masters_final": str(masters_path) if masters_path else None,
        "masters_final_candidate_count": len(candidates),
        "master_count": len(masters),
        "masters": masters,
        "stable_master_copy": str(MASTER_COPY) if masters else None,
        "master_basis_status": "baseline_candidate_boundary_audits_pending",
        "required_boundary_seeds": BOUNDARY_SEEDS,
        "errors": errors,
        "audit_pass": not errors,
    }
    AUDIT_JSON.write_text(
        json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        "QEDCalc Q05 r8s3d0 baseline Kira audit",
        f"canonical family: {Q05_KIRA_NAME}",
        f"covered diagrams: {list(Q05_COVERED_DIAGRAMS)}",
        "seed: r8s3d0",
        f"top sector: {Q05_KIRA_TOP_SECTOR}",
        f"masters.final: {audit['masters_final']}",
        f"master count: {audit['master_count']}",
        "master-basis status: baseline candidate; boundary audits pending",
        "required boundary seeds: " + ", ".join(BOUNDARY_SEEDS),
        f"master copy: {audit['stable_master_copy']}",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {AUDIT_JSON}",
        f"audit TXT: {AUDIT_TXT}",
        "QEDCalc Q05 r8s3d0 baseline Kira audit " + ("PASS" if not errors else "FAIL"),
    ]
    AUDIT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc Q05 r8s3d0 baseline Kira audit FAIL")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--finalize", action="store_true")
    args = parser.parse_args()
    prepare() if args.prepare else finalize()


if __name__ == "__main__":
    main()
