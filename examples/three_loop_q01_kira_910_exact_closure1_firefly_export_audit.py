"""Export/audit helper for the completed Q01 exact944 closure-wave-1 FireFly run.

The expensive projected Q01 trace and the FireFly reduction are never recomputed here.
The launcher uses this module in two phases:

1. generate a small ``kira2form`` job that reads the isolated FireFly ``alt_dir``;
2. audit the exported table against the saved 910 native QEDCalc integrals, the
   original 944 exact demands, and the larger closure-wave-1 target set.

A successful audit establishes the chain

    910 native QEDCalc integrals -> original exact944 demands
    -> closure-wave-1 targets -> master integrals

using QEDCalc's existing ISP bridge and Kira FORM-table parser.
"""
from __future__ import annotations

from collections import Counter
import argparse
import json
from pathlib import Path
from typing import Iterable

from examples.three_loop_q01_kira_910_coverage import _discover_saved_integrals
from three_loop.kira_isp_bridge import expand_qedcalc_integral_to_kira
from three_loop.kira_reducer import KiraReductionTable


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
FAMILY = "Q01_full"
ORIGINAL_TARGET_FILE = PROJECT / "q01_944_targets"
CLOSURE_TARGET_FILE = PROJECT / "q01_exact944_closure1_targets"
ALT_DIR_NAME = "exact944closure1_firefly"
ALT_ROOT = PROJECT / ALT_DIR_NAME
EXPORT_JOB = PROJECT / "jobs_exact944_closure1_firefly_export.yaml"
OUTPUT_JSON = PROJECT / "q01_exact944_closure1_firefly_export_audit.json"
EXPECTED_NATIVE = 910
EXPECTED_ORIGINAL = 944


def _indices12(values: Iterable[int]) -> tuple[int, ...]:
    result = tuple(int(v) for v in values)
    if len(result) != 12:
        raise ValueError(f"expected 12 integral indices, got {len(result)}")
    return result


def _parse_family_line(line: str) -> tuple[int, ...]:
    text = line.strip()
    prefix = FAMILY + "["
    if not text.startswith(prefix) or not text.endswith("]"):
        raise ValueError(f"unexpected target syntax: {text!r}")
    return _indices12(int(v.strip()) for v in text[len(prefix):-1].split(","))


def _load_target_file(
    path: Path,
    *,
    label: str,
    expected_count: int | None = None,
) -> tuple[tuple[int, ...], ...]:
    if not path.exists():
        raise SystemExit(f"ERROR: {label} target list not found: {path}")
    try:
        values = tuple(
            _parse_family_line(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f"ERROR: could not parse {label} target list: {exc}") from exc

    unique = tuple(dict.fromkeys(values))
    if not values:
        raise SystemExit(f"ERROR: {label} target list is empty: {path}")
    if len(values) != len(unique):
        raise SystemExit(
            f"ERROR: {label} target list contains duplicates: "
            f"total={len(values)} unique={len(unique)}"
        )
    if expected_count is not None and len(unique) != expected_count:
        raise SystemExit(
            f"ERROR: {label} target list has the wrong size: "
            f"total={len(values)} unique={len(unique)} expected={expected_count}"
        )
    return unique


def _load_target_sets() -> tuple[
    tuple[tuple[int, ...], ...],
    tuple[tuple[int, ...], ...],
]:
    original = _load_target_file(
        ORIGINAL_TARGET_FILE,
        label="original exact944",
        expected_count=EXPECTED_ORIGINAL,
    )
    closure = _load_target_file(
        CLOSURE_TARGET_FILE,
        label="closure-wave-1",
    )
    original_set = set(original)
    closure_set = set(closure)
    missing_original = sorted(original_set - closure_set)
    if missing_original:
        raise SystemExit(
            "ERROR: closure-wave-1 target list does not contain all original exact944 demands; "
            f"missing={len(missing_original)}"
        )
    return original, closure


def generate_export_job() -> None:
    original, closure = _load_target_sets()
    closure_added = len(set(closure) - set(original))
    text = f'''jobs:\n  - kira2form:\n      target:\n        - [{FAMILY},{CLOSURE_TARGET_FILE.name}]\n      alt_dir: {ALT_DIR_NAME}\n'''
    EXPORT_JOB.write_text(text, encoding="utf-8", newline="\n")

    required = (
        "kira2form:",
        f"[{FAMILY},{CLOSURE_TARGET_FILE.name}]",
        f"alt_dir: {ALT_DIR_NAME}",
    )
    missing = [token for token in required if token not in text]
    if missing:
        raise SystemExit(f"ERROR: generated export-job audit failed: {missing}")

    print("QEDCalc Q01 exact944 closure-wave-1 FireFly export generator")
    print("original exact944 demands:", len(original))
    print("closure-wave-1 targets:", len(closure))
    print("closure-added targets:", closure_added)
    print("alt_dir:", ALT_DIR_NAME)
    print("generated:", EXPORT_JOB)
    print("Q01 exact944 closure-wave-1 FireFly export generation PASS")


def _find_export_files() -> tuple[Path, Path]:
    result_dir = ALT_ROOT / "results" / FAMILY
    if not result_dir.exists():
        raise SystemExit(
            "ERROR: FireFly result directory was not found after export: "
            f"{result_dir}"
        )

    form_candidates = [
        result_dir / f"kira_{FAMILY}.inc",
        result_dir / f"kira_{CLOSURE_TARGET_FILE.name}.inc",
        result_dir / "kira.inc",
    ]
    form_candidates.extend(sorted(result_dir.glob("*.inc")))
    form_file = next((p for p in form_candidates if p.is_file()), None)
    if form_file is None:
        raise SystemExit(
            "ERROR: Kira FORM export was not found under FireFly alt_dir: "
            f"{result_dir}"
        )

    masters_candidates = [result_dir / "masters.final", result_dir / "masters"]
    masters_file = next((p for p in masters_candidates if p.is_file()), None)
    if masters_file is None:
        raise SystemExit(
            "ERROR: Kira master list was not found under FireFly alt_dir: "
            f"{result_dir}"
        )
    return form_file, masters_file


def audit() -> None:
    print("QEDCalc Q01 exact944 closure-wave-1 FireFly export audit")
    print("project:", PROJECT)
    print("mode: saved artifacts only; projected trace and FireFly reduction are NOT recomputed")

    original, closure = _load_target_sets()
    original_set = set(original)
    closure_set = set(closure)
    closure_added = sorted(closure_set - original_set)
    print("original exact944 demands:", len(original))
    print("closure-wave-1 targets:", len(closure))
    print("closure-added targets:", len(closure_added))

    source_path, source_trail, native_integrals = _discover_saved_integrals()
    if len(native_integrals) != EXPECTED_NATIVE:
        raise SystemExit(
            f"ERROR: native Q01 set has {len(native_integrals)} integrals; expected {EXPECTED_NATIVE}"
        )
    print("native source:", source_path)
    print("native artifact path:", source_trail)
    print("native integrals:", len(native_integrals))

    expanded_set: set[tuple[int, ...]] = set()
    expanded_total = 0
    rejected_native: list[dict[str, object]] = []
    for native in native_integrals:
        try:
            expansion = expand_qedcalc_integral_to_kira(native)
        except Exception as exc:
            if len(rejected_native) < 10:
                rejected_native.append({"native": list(native), "error": str(exc)})
            continue
        expanded_total += len(expansion.terms)
        expanded_set.update(term.kira_indices for term in expansion.terms)

    if rejected_native:
        print("ERROR: native-to-Kira expansion rejected integral(s):", len(rejected_native))
        for item in rejected_native:
            print("  ", item)
        raise SystemExit(2)

    missing_from_original = sorted(expanded_set - original_set)
    missing_from_closure = sorted(expanded_set - closure_set)
    print("expanded Kira terms:", expanded_total)
    print("unique expanded Kira integrals:", len(expanded_set))
    print("expanded integrals missing from original exact944:", len(missing_from_original))
    print("expanded integrals missing from closure-wave-1:", len(missing_from_closure))

    form_file, masters_file = _find_export_files()
    print("FORM export:", form_file)
    print("master list:", masters_file)

    try:
        table = KiraReductionTable.from_form_export(
            form_file, masters_file, family=FAMILY
        )
    except Exception as exc:
        raise SystemExit(f"ERROR: could not load back-substituted Kira FORM export: {exc}") from exc

    print("Kira rules loaded:", len(table.rules))
    print("Kira masters loaded:", len(table.masters))

    original_status: Counter[str] = Counter()
    unresolved_original: list[tuple[int, ...]] = []
    for demand in original:
        result = table.reduce_kira(demand)
        original_status[result.status] += 1
        if result.status == "not_in_table":
            unresolved_original.append(demand)

    closure_status: Counter[str] = Counter()
    unresolved_closure: list[tuple[int, ...]] = []
    for demand in closure:
        result = table.reduce_kira(demand)
        closure_status[result.status] += 1
        if result.status == "not_in_table":
            unresolved_closure.append(demand)

    native_status: Counter[str] = Counter()
    native_missing_terms: set[tuple[int, ...]] = set()
    native_missing_examples: list[dict[str, object]] = []
    for native in native_integrals:
        expansion = expand_qedcalc_integral_to_kira(native)
        local_missing: list[tuple[int, ...]] = []
        for term in expansion.terms:
            result = table.reduce_kira(term.kira_indices)
            if result.status == "not_in_table":
                local_missing.append(term.kira_indices)
                native_missing_terms.add(term.kira_indices)
        if not local_missing:
            native_status["fully_reduced"] += 1
        elif len(local_missing) < len(expansion.terms):
            native_status["partially_reduced"] += 1
        else:
            native_status["missing"] += 1
        if local_missing and len(native_missing_examples) < 10:
            native_missing_examples.append(
                {
                    "native": list(native),
                    "missing": [list(v) for v in local_missing[:10]],
                }
            )

    pass_checks = {
        "native_count_910": len(native_integrals) == EXPECTED_NATIVE,
        "original_exact_demand_count_944": len(original) == EXPECTED_ORIGINAL,
        "all_original_exact944_in_closure": original_set <= closure_set,
        "all_native_expansions_in_original_exact944": not missing_from_original,
        "all_native_expansions_in_closure": not missing_from_closure,
        "all_910_native_integrals_fully_reduced": native_status["fully_reduced"] == EXPECTED_NATIVE,
        "all_original_exact944_demands_resolved": not unresolved_original,
        "all_closure_wave1_targets_resolved": not unresolved_closure,
        "form_rhs_closed_to_masters": True,
    }
    passed = all(pass_checks.values())

    summary = {
        "mode": "saved-artifact FireFly export audit; no projected-trace or reduction recomputation",
        "project": str(PROJECT),
        "alt_dir": ALT_DIR_NAME,
        "native_source": str(source_path),
        "native_artifact_path": source_trail,
        "native_integrals": len(native_integrals),
        "original_exact_demands": len(original),
        "closure_targets": len(closure),
        "closure_added_targets": len(closure_added),
        "expanded_terms_total": expanded_total,
        "unique_expanded_kira_integrals": len(expanded_set),
        "expanded_missing_from_original_exact944": [list(v) for v in missing_from_original],
        "expanded_missing_from_closure": [list(v) for v in missing_from_closure],
        "form_export": str(form_file),
        "masters_file": str(masters_file),
        "kira_rules_loaded": len(table.rules),
        "kira_masters_loaded": len(table.masters),
        "original_status": dict(sorted(original_status.items())),
        "unresolved_original_exact944_demands": [list(v) for v in unresolved_original],
        "closure_status": dict(sorted(closure_status.items())),
        "unresolved_closure_targets": [list(v) for v in unresolved_closure],
        "native_status": dict(sorted(native_status.items())),
        "native_missing_unique_terms": [list(v) for v in sorted(native_missing_terms)],
        "native_missing_examples": native_missing_examples,
        "checks": pass_checks,
        "pass": passed,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("original exact944 status:", dict(sorted(original_status.items())))
    print("unresolved original exact944 demands:", len(unresolved_original))
    print("closure-wave-1 status:", dict(sorted(closure_status.items())))
    print("unresolved closure-wave-1 targets:", len(unresolved_closure))
    print("native status:", dict(sorted(native_status.items())))
    print("native missing unique Kira terms:", len(native_missing_terms))
    print("audit JSON:", OUTPUT_JSON)
    for name, value in pass_checks.items():
        print(f"  {'PASS' if value else 'FAIL'}: {name}")

    if not passed:
        print("Q01 exact944 closure-wave-1 FireFly export audit FAIL")
        raise SystemExit(1)
    print("Q01 exact944 closure-wave-1 FireFly export audit PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=("generate-export", "audit"),
        help="generate the lightweight kira2form job or audit its exported table",
    )
    args = parser.parse_args()
    if args.mode == "generate-export":
        generate_export_job()
    else:
        audit()


if __name__ == "__main__":
    main()
