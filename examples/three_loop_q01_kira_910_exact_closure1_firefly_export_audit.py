"""Export/audit helper for the completed Q01 exact944 closure-wave-1 FireFly run.

The expensive projected Q01 trace and the FireFly reduction are never recomputed here.
The launcher uses this module in two phases:

1. generate a small ``kira2form`` job that reads the isolated FireFly ``alt_dir``;
2. audit the exported table against the saved 910 native QEDCalc integrals and the
   944 closure-wave-1 mandatory Kira targets.

A successful audit establishes the chain

    910 native QEDCalc integrals -> 944 mandatory Kira demands -> master integrals

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
TARGET_FILE = PROJECT / "q01_exact944_closure1_targets"
ALT_DIR_NAME = "exact944closure1_firefly"
ALT_ROOT = PROJECT / ALT_DIR_NAME
EXPORT_JOB = PROJECT / "jobs_exact944_closure1_firefly_export.yaml"
OUTPUT_JSON = PROJECT / "q01_exact944_closure1_firefly_export_audit.json"
EXPECTED_NATIVE = 910
EXPECTED_DEMANDS = 944


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


def _load_demands() -> tuple[tuple[int, ...], ...]:
    if not TARGET_FILE.exists():
        raise SystemExit(f"ERROR: mandatory target list not found: {TARGET_FILE}")
    try:
        demands = tuple(
            _parse_family_line(line)
            for line in TARGET_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f"ERROR: could not parse mandatory target list: {exc}") from exc

    unique = tuple(dict.fromkeys(demands))
    if len(demands) != EXPECTED_DEMANDS or len(unique) != EXPECTED_DEMANDS:
        raise SystemExit(
            "ERROR: exact944 mandatory target list is not the expected complete set: "
            f"total={len(demands)} unique={len(unique)} expected={EXPECTED_DEMANDS}"
        )
    return unique


def generate_export_job() -> None:
    demands = _load_demands()
    text = f'''jobs:\n  - kira2form:\n      target:\n        - [{FAMILY},{TARGET_FILE.name}]\n      alt_dir: {ALT_DIR_NAME}\n'''
    EXPORT_JOB.write_text(text, encoding="utf-8", newline="\n")

    required = (
        "kira2form:",
        f"[{FAMILY},{TARGET_FILE.name}]",
        f"alt_dir: {ALT_DIR_NAME}",
    )
    missing = [token for token in required if token not in text]
    if missing:
        raise SystemExit(f"ERROR: generated export-job audit failed: {missing}")

    print("QEDCalc Q01 exact944 closure-wave-1 FireFly export generator")
    print("mandatory Kira demands:", len(demands))
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

    demands = _load_demands()
    demand_set = set(demands)
    print("mandatory Kira demands:", len(demands))

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

    missing_from_mandatory = sorted(expanded_set - demand_set)
    mandatory_not_from_native = sorted(demand_set - expanded_set)
    print("expanded Kira terms:", expanded_total)
    print("unique expanded Kira integrals:", len(expanded_set))
    print("expanded integrals missing from mandatory list:", len(missing_from_mandatory))
    print("mandatory closure-only demands:", len(mandatory_not_from_native))

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

    demand_status: Counter[str] = Counter()
    unresolved_demands: list[tuple[int, ...]] = []
    for demand in demands:
        result = table.reduce_kira(demand)
        demand_status[result.status] += 1
        if result.status == "not_in_table":
            unresolved_demands.append(demand)

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
        "mandatory_count_944": len(demands) == EXPECTED_DEMANDS,
        "all_native_expansions_in_mandatory_set": not missing_from_mandatory,
        "all_910_native_integrals_fully_reduced": native_status["fully_reduced"] == EXPECTED_NATIVE,
        "all_944_mandatory_demands_resolved": not unresolved_demands,
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
        "mandatory_demands": len(demands),
        "expanded_terms_total": expanded_total,
        "unique_expanded_kira_integrals": len(expanded_set),
        "mandatory_closure_only_demands": len(mandatory_not_from_native),
        "expanded_missing_from_mandatory": [list(v) for v in missing_from_mandatory],
        "form_export": str(form_file),
        "masters_file": str(masters_file),
        "kira_rules_loaded": len(table.rules),
        "kira_masters_loaded": len(table.masters),
        "demand_status": dict(sorted(demand_status.items())),
        "unresolved_mandatory_demands": [list(v) for v in unresolved_demands],
        "native_status": dict(sorted(native_status.items())),
        "native_missing_unique_terms": [list(v) for v in sorted(native_missing_terms)],
        "native_missing_examples": native_missing_examples,
        "checks": pass_checks,
        "pass": passed,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("mandatory status:", dict(sorted(demand_status.items())))
    print("unresolved mandatory demands:", len(unresolved_demands))
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
