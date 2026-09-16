"""Prepare/finalize Q02 FireFly reduction of the union of master candidates.

The target list is produced by three_loop_q02_firefly_master_union_audit.py.
This stage asks Kira to reduce all candidates from the four tested seed master
sets together, so a single final basis can be selected without assuming that
one seed's masters must literally survive in another seed's masters.final.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.q02_kira_backend import Q02_KIRA_NAME, Q02_KIRA_TOP_SECTOR, Q02SeedLimits, export_q02_kira_project

AUDIT_DIR = ROOT / "output" / "three_loop_integral_family_audit"
TARGET_FILE = AUDIT_DIR / "q02_firefly_master_union_targets.txt"
PROJECT = ROOT / "output" / "kira_q02_full_firefly_master_union"
AUDIT_JSON = AUDIT_DIR / "three_loop_q02_firefly_master_union_reduction_audit.json"
AUDIT_TXT = AUDIT_DIR / "three_loop_q02_firefly_master_union_reduction_audit.txt"
MASTER_COPY = AUDIT_DIR / "q02_firefly_master_union_masters.txt"
PATTERN = re.compile(r"Q02_full\s*\[[^\]]+\]")


def _targets() -> list[str]:
    if not TARGET_FILE.is_file():
        raise FileNotFoundError(f"union target file not found: {TARGET_FILE}; run run_three_loop_q02_firefly_master_union_audit.bat first")
    out: list[str] = []
    seen: set[str] = set()
    for item in PATTERN.findall(TARGET_FILE.read_text(encoding="utf-8", errors="replace")):
        item = re.sub(r"\s+", "", item)
        if item not in seen:
            seen.add(item)
            out.append(item)
    if not out:
        raise ValueError("union target file contains no Q02_full integrals")
    return out


def _indices(item: str) -> str:
    inside = item[item.index("[") + 1:item.rindex("]")]
    parts = [x.strip() for x in inside.split(",")]
    if len(parts) != 12:
        raise ValueError(f"expected 12 indices: {item}")
    return ",".join(parts)


def _render_jobs(targets: list[str]) -> str:
    integrals = "\n".join(f"          - [Q02_full, [{_indices(item)}]]" for item in targets)
    return f"""jobs:
  - reduce_sectors:
      reduce:
        - {{topologies: [Q02_full], sectors: [255], r: 9, s: 4, d: 1}}
      select_integrals:
        select_mandatory_list:
{integrals}
      run_symmetries: true
      run_initiate: true
      run_triangular: false
      run_back_substitution: false
      run_firefly: true
"""


def _clean() -> None:
    for name in ("results", "sectormappings", "tmp", "firefly_saves", "ff_save", "firefly_saves_alt", "pyred"):
        path = PROJECT / name
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    for pattern in ("*.log", "*.log.gz"):
        for path in PROJECT.glob(pattern):
            path.unlink()


def prepare() -> None:
    targets = _targets()
    PROJECT.mkdir(parents=True, exist_ok=True)
    _clean()
    # r9s4d1 bounds cover all three tested one-axis extensions simultaneously.
    export_q02_kira_project(PROJECT, limits=Q02SeedLimits(9, 4, 1), back_substitution=False)
    (PROJECT / "jobs.yaml").write_text(_render_jobs(targets), encoding="utf-8", newline="\n")
    print("QEDCalc Q02 FireFly mandatory-union reduction prepare")
    print(f"union mandatory targets: {len(targets)}")
    print("envelope seed bounds: r9s4d1")
    print(f"project: {PROJECT}")
    print("solver: FireFly")
    print("QEDCalc Q02 FireFly mandatory-union reduction prepare PASS")


def _parse(path: Path) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in PATTERN.findall(path.read_text(encoding="utf-8", errors="replace")):
        item = re.sub(r"\s+", "", item)
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def finalize() -> None:
    targets = _targets()
    candidates = sorted(PROJECT.rglob("masters.final"), key=lambda p: str(p))
    errors: list[str] = []
    if len(candidates) != 1:
        errors.append(f"expected exactly one masters.final, found {len(candidates)}")
    masters_path = candidates[0] if candidates else None
    masters = _parse(masters_path) if masters_path else []
    if not masters:
        errors.append("no Q02_full masters parsed from union reduction")

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    if masters:
        MASTER_COPY.write_text("\n".join(masters) + "\n", encoding="utf-8")

    result = {
        "canonical_family": Q02_KIRA_NAME,
        "solver_backend": "firefly",
        "top_sector": Q02_KIRA_TOP_SECTOR,
        "envelope_seed": {"r": 9, "s": 4, "d": 1},
        "mandatory_union_target_count": len(targets),
        "masters_final": str(masters_path) if masters_path else None,
        "master_count": len(masters),
        "masters": masters,
        "master_copy": str(MASTER_COPY) if masters else None,
        "errors": errors,
        "audit_pass": not errors,
    }
    AUDIT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "QEDCalc Q02 FireFly mandatory-union reduction audit",
        f"mandatory union targets: {len(targets)}",
        "envelope seed: r9s4d1",
        f"masters.final: {result['masters_final']}",
        f"master count: {len(masters)}",
        f"internal audit errors: {len(errors)}",
        f"audit JSON: {AUDIT_JSON}",
        f"audit TXT: {AUDIT_TXT}",
        "QEDCalc Q02 FireFly mandatory-union reduction audit " + ("PASS" if not errors else "FAIL"),
    ]
    AUDIT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        print(line)
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit("QEDCalc Q02 FireFly mandatory-union reduction audit FAIL")


def main() -> None:
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--prepare", action="store_true")
    g.add_argument("--finalize", action="store_true")
    args = p.parse_args()
    prepare() if args.prepare else finalize()


if __name__ == "__main__":
    main()
