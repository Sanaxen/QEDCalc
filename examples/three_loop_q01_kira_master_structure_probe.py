"""Inspect saved Q01 Kira master metadata without recomputation.

The goal is to resolve the apparent mismatch between ``masters.final`` and
master forms reported by ``kira2form``.  This script performs no Kira, FireFly,
or projected-trace execution.  It compares all saved master-list artifacts,
wave-1/wave-2 kira2form master reports, and the finalized projected-amplitude
basis.  Kira ``# N`` report tags are treated only as sector/classification tags;
they are not assumed to prove integral equivalence.
"""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    ALT_ROOT,
    FAMILY,
    PROJECT,
)

RESULT_DIR = ALT_ROOT / "results" / FAMILY
FINAL_BASIS_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
WAVE1_LOG = PROJECT / "q01_exact944_closure1_firefly_export.log"
WAVE2_LOG = PROJECT / "q01_terminal_wave2_firefly_export.log"
OUTPUT_JSON = PROJECT / "q01_kira_master_structure_probe.json"
OUTPUT_TXT = PROJECT / "q01_kira_master_structure_probe.txt"

IndexTuple = tuple[int, ...]

_FAMILY_RE = re.compile(
    rf"{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]"
)
_MASTER_REPORT_RE = re.compile(
    rf"This requested integral is a master integral:\s*{re.escape(FAMILY)}\["
    r"(?P<args>-?\d+(?:\s*,\s*-?\d+){11})\]\s*#\s*(?P<tag>\d+)"
)


def _indices(text: str) -> IndexTuple:
    result = tuple(int(v.strip()) for v in text.split(","))
    if len(result) != 12:
        raise ValueError(f"expected 12 indices, got {len(result)}")
    return result


def _integral_text(values: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in values)}]"


def _parse_integrals_from_text(path: Path) -> set[IndexTuple]:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError):
        return set()
    return {_indices(m.group("args")) for m in _FAMILY_RE.finditer(text)}


def _parse_master_reports(path: Path) -> dict[IndexTuple, int]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="strict")
    reports: dict[IndexTuple, int] = {}
    for match in _MASTER_REPORT_RE.finditer(text):
        key = _indices(match.group("args"))
        tag = int(match.group("tag"))
        old = reports.get(key)
        if old is not None and old != tag:
            raise SystemExit(
                f"ERROR: conflicting Kira report tags for {_integral_text(key)}: {old} vs {tag}"
            )
        reports[key] = tag
    return reports


def _candidate_master_files() -> list[Path]:
    if not RESULT_DIR.exists():
        raise SystemExit(f"ERROR: Q01 FireFly result directory not found: {RESULT_DIR}")
    candidates: set[Path] = set()
    for pattern in ("masters*", "*master*", "*preferred*"):
        candidates.update(p for p in RESULT_DIR.glob(pattern) if p.is_file())
    return sorted(candidates, key=lambda p: p.name.lower())


def _load_final_basis() -> list[dict[str, object]]:
    if not FINAL_BASIS_JSON.exists():
        raise SystemExit(f"ERROR: finalized Q01 master-basis JSON not found: {FINAL_BASIS_JSON}")
    data = json.loads(FINAL_BASIS_JSON.read_text(encoding="utf-8"))
    if not data.get("pass"):
        raise SystemExit("ERROR: finalized Q01 master-basis JSON is not marked PASS")
    rows = data.get("basis_terms")
    if not isinstance(rows, list) or not rows:
        raise SystemExit("ERROR: finalized Q01 master-basis JSON has no basis_terms")
    return rows


def main() -> None:
    print("QEDCalc Q01 Kira master-structure probe")
    print("mode: saved artifacts only; no Kira/FireFly/projected-trace recomputation")
    print("result directory:", RESULT_DIR)

    master_files = _candidate_master_files()
    file_sets: dict[str, set[IndexTuple]] = {}
    for path in master_files:
        values = _parse_integrals_from_text(path)
        file_sets[path.name] = values
        print(f"master metadata file: {path.name}: {len(values)} Q01 integral form(s)")

    masters_final = file_sets.get("masters.final", set())
    wave1_reports = _parse_master_reports(WAVE1_LOG)
    wave2_reports = _parse_master_reports(WAVE2_LOG)
    all_reports = dict(wave1_reports)
    for key, tag in wave2_reports.items():
        old = all_reports.get(key)
        if old is not None and old != tag:
            raise SystemExit(
                f"ERROR: wave-1/wave-2 Kira report tags disagree for {_integral_text(key)}"
            )
        all_reports[key] = tag

    rows = _load_final_basis()
    basis_keys: set[IndexTuple] = set()
    basis_kind_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        raw = row.get("indices")
        if not isinstance(raw, list) or len(raw) != 12:
            raise SystemExit(f"ERROR: malformed finalized basis row: {row!r}")
        key = tuple(int(v) for v in raw)
        basis_keys.add(key)
        basis_kind_counts[str(row.get("kind", ""))] += 1

    basis_missing_from_all_kira_evidence = sorted(
        basis_keys - masters_final - set(all_reports)
    )

    tag_groups: dict[int, list[IndexTuple]] = defaultdict(list)
    basis_without_report_tag: list[IndexTuple] = []
    for key in sorted(basis_keys):
        tag = all_reports.get(key)
        if tag is None:
            basis_without_report_tag.append(key)
        else:
            tag_groups[tag].append(key)

    multi_form_tags = {tag: vals for tag, vals in tag_groups.items() if len(vals) > 1}

    # Compare each saved master-like file with the finalized amplitude basis.
    file_comparisons = {}
    for name, values in file_sets.items():
        file_comparisons[name] = {
            "count": len(values),
            "basis_overlap": len(values & basis_keys),
            "basis_missing_from_file": len(basis_keys - values),
            "file_not_used_by_basis": len(values - basis_keys),
        }

    summary = {
        "mode": "saved-artifact Q01 Kira master metadata probe; no recomputation",
        "result_dir": str(RESULT_DIR),
        "final_basis_json": str(FINAL_BASIS_JSON),
        "final_basis_terms": len(basis_keys),
        "final_basis_kind_counts": dict(sorted(basis_kind_counts.items())),
        "masters_final_count": len(masters_final),
        "wave1_kira_master_reports": len(wave1_reports),
        "wave2_kira_master_reports": len(wave2_reports),
        "union_kira_master_reports": len(all_reports),
        "saved_master_files": file_comparisons,
        "basis_forms_supported_by_masters_final_or_kira_log": len(
            basis_keys & (masters_final | set(all_reports))
        ),
        "basis_forms_missing_from_all_kira_evidence": [
            _integral_text(v) for v in basis_missing_from_all_kira_evidence
        ],
        "basis_forms_with_kira_report_tag": len(basis_keys) - len(basis_without_report_tag),
        "basis_forms_without_kira_report_tag": [
            _integral_text(v) for v in basis_without_report_tag
        ],
        "distinct_report_tags_used_by_basis": len(tag_groups),
        "report_tag_groups": {
            str(tag): [_integral_text(v) for v in vals]
            for tag, vals in sorted(tag_groups.items())
        },
        "multi_form_report_tag_groups": {
            str(tag): [_integral_text(v) for v in vals]
            for tag, vals in sorted(multi_form_tags.items())
        },
        "important_note": (
            "Kira '# N' values are retained as classification/sector tags only. "
            "Multiple master forms sharing one tag are not automatically treated as equivalent."
        ),
        "pass": not basis_missing_from_all_kira_evidence,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 Kira master-structure probe",
        "",
        "No Kira/FireFly/projected-trace recomputation was performed.",
        "",
        f"final amplitude basis forms: {len(basis_keys)}",
        f"masters.final forms: {len(masters_final)}",
        f"wave-1 Kira master reports: {len(wave1_reports)}",
        f"wave-2 Kira master reports: {len(wave2_reports)}",
        f"union Kira master reports: {len(all_reports)}",
        f"distinct Kira report tags used by final basis: {len(tag_groups)}",
        f"multi-form report-tag groups: {len(multi_form_tags)}",
        "",
        "Saved master metadata files:",
    ]
    for name, info in sorted(file_comparisons.items()):
        lines.append(
            f"  {name}: count={info['count']} basis_overlap={info['basis_overlap']} "
            f"basis_missing={info['basis_missing_from_file']}"
        )
    lines.extend([
        "",
        "Report-tag groups with multiple final-basis forms (classification only; not equivalence proof):",
    ])
    for tag, vals in sorted(multi_form_tags.items()):
        lines.append(f"  # {tag}: {len(vals)} form(s)")
        for value in vals:
            lines.append(f"    {_integral_text(value)}")
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("final amplitude basis forms:", len(basis_keys))
    print("masters.final forms:", len(masters_final))
    print("wave-1 Kira master reports:", len(wave1_reports))
    print("wave-2 Kira master reports:", len(wave2_reports))
    print("union Kira master reports:", len(all_reports))
    print("distinct Kira report tags used by final basis:", len(tag_groups))
    print("multi-form report-tag groups:", len(multi_form_tags))
    print("basis forms missing from all Kira evidence:", len(basis_missing_from_all_kira_evidence))
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)

    if basis_missing_from_all_kira_evidence:
        print("first unsupported basis forms:")
        for value in basis_missing_from_all_kira_evidence[:8]:
            print("  ", _integral_text(value))
        raise SystemExit("Q01 Kira master-structure probe FAIL")

    print("Q01 Kira master-structure probe PASS")


if __name__ == "__main__":
    main()
