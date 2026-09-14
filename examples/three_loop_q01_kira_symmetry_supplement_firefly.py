"""Run a small isolated FireFly reduction for Q01 symmetry-expansion gaps.

The previous saved-result-only closure export proved that 146 symmetry-derived
integrals are not present in the existing exact944closure1_firefly database.
This helper therefore creates a *separate* supplemental FireFly job containing
only those unresolved targets.  The validated original FireFly alt_dir is never
modified.

The supplemental alt_dir is versioned so a failed FireFly reconstruction state
is never reused after changing job bounds or target-generation logic.

Modes:
  generate  read the saved closure-audit JSON and create the target/job files;
  audit     inspect the supplemental kira2form export and classify all targets.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Iterable

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    FAMILY,
    PROJECT,
)
from three_loop.kira_form_parser import iter_kira_form_rules

IndexTuple = tuple[int, ...]

SOURCE_AUDIT = PROJECT / "q01_symmetry_closure_firefly_export_audit.json"
TARGET_FILE = PROJECT / "q01_symmetry_supplement_targets"
JOB_FILE = PROJECT / "jobs_q01_symmetry_supplement_firefly.yaml"
LOG_FILE = PROJECT / "q01_symmetry_supplement_firefly.log"
# v1 may contain an incompatible FireFly saved state from an earlier aborted
# run.  Never reuse it after the r-bound fix; start a fresh isolated state.
ALT_DIR_NAME = "symmetry_supplement_firefly_v2"
ALT_ROOT = PROJECT / ALT_DIR_NAME
OUTPUT_JSON = PROJECT / "q01_symmetry_supplement_firefly_audit.json"
TOP_SECTOR = 511

_TARGET_RE = re.compile(
    rf"^{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]$"
)
_MASTER_RE = re.compile(
    rf"This requested integral is a master integral:\s*{re.escape(FAMILY)}\["
    r"(?P<args>-?\d+(?:\s*,\s*-?\d+){11})\]"
)


def _indices(text: str) -> IndexTuple:
    values = tuple(int(v.strip()) for v in text.split(","))
    if len(values) != 12:
        raise ValueError(f"expected 12 indices, got {len(values)}")
    return values


def _parse_integral(text: str) -> IndexTuple:
    match = _TARGET_RE.match(text.strip())
    if not match:
        raise ValueError(f"unexpected integral syntax: {text!r}")
    return _indices(match.group("args"))


def _integral_text(values: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in values)}]"


def _bounds(indices: IndexTuple) -> tuple[int, int, int]:
    r = sum(v for v in indices if v > 0)
    s = sum(-v for v in indices if v < 0)
    d = sum(max(v - 1, 0) for v in indices if v > 0)
    return r, s, d


def _load_source_unresolved() -> tuple[IndexTuple, ...]:
    if not SOURCE_AUDIT.exists():
        raise SystemExit(f"ERROR: source closure audit not found: {SOURCE_AUDIT}")
    data = json.loads(SOURCE_AUDIT.read_text(encoding="utf-8"))
    raw = data.get("unresolved_targets")
    if not isinstance(raw, list) or not raw:
        raise SystemExit("ERROR: source closure audit has no unresolved_targets")
    values = tuple(sorted({_parse_integral(str(item)) for item in raw}))
    return values


def generate() -> None:
    targets = _load_source_unresolved()
    maxima = [0, 0, 0]
    for target in targets:
        r, s, d = _bounds(target)
        maxima[0] = max(maxima[0], r)
        maxima[1] = max(maxima[1], s)
        maxima[2] = max(maxima[2], d)
    target_rmax, smax, dmax = maxima

    # Kira also requires r to be large enough to represent the selected top
    # sector itself.  Sector 511 has nine active denominator lines, hence r>=9
    # regardless of the maximum r of the selected mandatory targets.
    sector_min_r = TOP_SECTOR.bit_count()
    rmax = max(target_rmax, sector_min_r)

    TARGET_FILE.write_text(
        "\n".join(_integral_text(v) for v in targets) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    text = f'''jobs:\n  - reduce_sectors:\n      reduce:\n        - {{topologies: [{FAMILY}], sectors: [{TOP_SECTOR}], r: {rmax}, s: {smax}, d: {dmax}}}\n      select_integrals:\n        select_mandatory_list:\n          - [{FAMILY},{TARGET_FILE.name}]\n      run_symmetries: true\n      run_initiate: true\n      run_triangular: false\n      run_back_substitution: false\n      run_firefly: true\n      iterative_reduction: sectorwise\n      alt_dir: {ALT_DIR_NAME}\n  - kira2form:\n      target:\n        - [{FAMILY},{TARGET_FILE.name}]\n      alt_dir: {ALT_DIR_NAME}\n'''
    JOB_FILE.write_text(text, encoding="utf-8", newline="\n")

    print("QEDCalc Q01 symmetry supplemental FireFly generator")
    print("mode: isolated supplemental reduction; original FireFly alt_dir is untouched")
    print("supplement targets:", len(targets))
    print("target-derived r max:", target_rmax)
    print(f"top sector: {TOP_SECTOR}; active lines / minimum r: {sector_min_r}")
    print(f"effective seed bounds: r={rmax} s={smax} d={dmax}")
    print("alt_dir:", ALT_DIR_NAME)
    print("generated target list:", TARGET_FILE)
    print("generated job:", JOB_FILE)
    print("Q01 symmetry supplemental FireFly generation PASS")


def _load_targets() -> set[IndexTuple]:
    if not TARGET_FILE.exists():
        raise SystemExit(f"ERROR: target list not found: {TARGET_FILE}")
    return {
        _parse_integral(line.strip())
        for line in TARGET_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def _find_form_export() -> Path:
    result_dir = ALT_ROOT / "results" / FAMILY
    preferred = result_dir / "kira_q01_symmetry_supplement_targets.inc"
    if preferred.is_file():
        return preferred
    candidates = sorted(
        (p for p in result_dir.glob("*.inc") if "symmetry_supplement" in p.name),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    raise SystemExit(f"ERROR: supplemental FORM export not found under {result_dir}")


def audit() -> None:
    targets = _load_targets()
    form_path = _find_form_export()

    rules: set[IndexTuple] = set()
    zeros: set[IndexTuple] = set()
    rhs: set[IndexTuple] = set()
    for rule in iter_kira_form_rules(form_path, family=FAMILY):
        lhs = tuple(int(v) for v in rule.lhs.indices)
        if rule.terms:
            rules.add(lhs)
            rhs.update(tuple(int(v) for v in term.integral.indices) for term in rule.terms)
        elif rule.is_zero:
            zeros.add(lhs)

    log_text = LOG_FILE.read_text(encoding="utf-8", errors="strict") if LOG_FILE.exists() else ""
    master_reports = {
        _indices(match.group("args"))
        for match in _MASTER_RE.finditer(log_text)
    }
    unresolved = sorted(targets - rules - zeros - master_reports)
    unreduced_zero = bool(re.search(r"unreduced integrals:\s*0\s*\.", log_text))

    status = {
        "rule": len(targets & rules),
        "zero": len(targets & zeros),
        "kira_master": len(targets & master_reports),
        "still_unresolved": len(unresolved),
    }
    summary = {
        "mode": "isolated supplemental FireFly reduction for symmetry-expansion targets",
        "alt_dir": ALT_DIR_NAME,
        "targets": len(targets),
        "form_export": str(form_path),
        "target_status": status,
        "rhs_integrals": len(rhs),
        "kira_unreduced_integrals_zero": unreduced_zero,
        "unresolved_targets": [_integral_text(v) for v in unresolved],
        "pass": not unresolved and unreduced_zero,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("QEDCalc Q01 symmetry supplemental FireFly audit")
    print("alt_dir:", ALT_DIR_NAME)
    print("requested targets:", len(targets))
    print("exported reduction rules:", len(rules))
    print("exported zero rules:", len(zeros))
    print("Kira-reported masters:", len(master_reports))
    print("target status:", status)
    print("unique RHS integrals:", len(rhs))
    print("Kira unreduced integrals = 0:", unreduced_zero)
    print("audit JSON:", OUTPUT_JSON)
    if unresolved:
        print("unresolved target samples:")
        for value in unresolved[:12]:
            print("  ", _integral_text(value))
        raise SystemExit(3)
    if not unreduced_zero:
        raise SystemExit(1)
    print("Q01 symmetry supplemental FireFly audit PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("generate", "audit"))
    args = parser.parse_args()
    if args.mode == "generate":
        generate()
    else:
        audit()


if __name__ == "__main__":
    main()
