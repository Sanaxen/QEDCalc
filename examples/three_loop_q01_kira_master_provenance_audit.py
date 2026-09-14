"""Audit Q01 master provenance across every saved Kira alt_dir.

This is a saved-artifact-only diagnostic.  It performs no Kira, FireFly,
Fermat, or projected-trace recomputation.  The purpose is to explain the
apparent mismatch between the four forms in one ``masters.final`` and the
60 forms used by the finalized projected amplitude.

The audit recursively scans the Q01 project tree for:

* every ``masters.final`` and other master-like text artifact;
* every saved Kira log containing ``This requested integral is a master integral``;
* every finalized 60-form amplitude-basis entry.

For each reported ``# N`` master tag it also compares N with the positive-index
sector bitmask.  This tests the long-standing hypothesis that the report tag is
a sector number/classification tag rather than a canonical master identifier.
"""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import FAMILY, PROJECT

FINAL_BASIS_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
OUTPUT_JSON = PROJECT / "q01_kira_master_provenance_audit.json"
OUTPUT_TXT = PROJECT / "q01_kira_master_provenance_audit.txt"

IndexTuple = tuple[int, ...]

_FAMILY_RE = re.compile(
    rf"{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]"
)
_MASTER_REPORT_RE = re.compile(
    rf"This requested integral is a master integral:\s*{re.escape(FAMILY)}\["
    r"(?P<args>-?\d+(?:\s*,\s*-?\d+){11})\]\s*#\s*(?P<tag>\d+)"
)


def _indices(text: str) -> IndexTuple:
    values = tuple(int(x.strip()) for x in text.split(","))
    if len(values) != 12:
        raise ValueError(f"expected 12 indices, got {len(values)}")
    return values


def _fmt(values: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in values)}]"


def _sector(values: IndexTuple) -> int:
    result = 0
    for i, exponent in enumerate(values):
        if exponent > 0:
            result |= 1 << i
    return result


def _read_integrals(path: Path) -> set[IndexTuple]:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError):
        return set()
    return {_indices(m.group("args")) for m in _FAMILY_RE.finditer(text)}


def _read_reports(path: Path) -> list[tuple[IndexTuple, int]]:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError):
        return []
    return [(_indices(m.group("args")), int(m.group("tag"))) for m in _MASTER_REPORT_RE.finditer(text)]


def _load_basis() -> dict[IndexTuple, dict[str, object]]:
    if not FINAL_BASIS_JSON.exists():
        raise SystemExit(f"ERROR: final basis JSON not found: {FINAL_BASIS_JSON}")
    data = json.loads(FINAL_BASIS_JSON.read_text(encoding="utf-8"))
    rows = data.get("basis_terms")
    if not isinstance(rows, list) or not rows:
        raise SystemExit("ERROR: final basis JSON has no basis_terms")
    result: dict[IndexTuple, dict[str, object]] = {}
    for row in rows:
        raw = row.get("indices")
        if not isinstance(raw, list) or len(raw) != 12:
            raise SystemExit(f"ERROR: malformed basis row: {row!r}")
        key = tuple(int(v) for v in raw)
        result[key] = dict(row)
    return result


def _candidate_master_files() -> list[Path]:
    candidates: set[Path] = set()
    for path in PROJECT.rglob("*"):
        if not path.is_file():
            continue
        name = path.name.lower()
        if (
            name == "masters.final"
            or "master" in name
            or "preferred" in name
        ):
            # Keep text-sized Kira metadata only.  Ignore our own audit outputs.
            if path.name in {OUTPUT_JSON.name, OUTPUT_TXT.name, FINAL_BASIS_JSON.name}:
                continue
            try:
                if path.stat().st_size <= 10_000_000:
                    candidates.add(path)
            except OSError:
                pass
    return sorted(candidates, key=lambda p: str(p).lower())


def _candidate_logs() -> list[Path]:
    logs: list[Path] = []
    for path in PROJECT.rglob("*.log"):
        try:
            if path.stat().st_size <= 50_000_000:
                logs.append(path)
        except OSError:
            pass
    return sorted(logs, key=lambda p: str(p).lower())


def main() -> None:
    print("QEDCalc Q01 Kira master provenance audit")
    print("mode: saved artifacts only; no Kira/FireFly/Fermat/projected-trace recomputation")
    print("project:", PROJECT)

    basis_rows = _load_basis()
    basis = set(basis_rows)
    print("final amplitude basis forms:", len(basis))

    master_files = _candidate_master_files()
    master_file_rows: list[dict[str, object]] = []
    master_membership: dict[IndexTuple, list[str]] = defaultdict(list)
    masters_final_union: set[IndexTuple] = set()
    masters_final_files = 0

    for path in master_files:
        forms = _read_integrals(path)
        if not forms and path.name != "masters.final":
            continue
        rel = str(path.relative_to(PROJECT))
        is_final = path.name == "masters.final"
        if is_final:
            masters_final_files += 1
            masters_final_union |= forms
        for key in forms:
            master_membership[key].append(rel)
        row = {
            "path": rel,
            "name": path.name,
            "is_masters_final": is_final,
            "integral_forms": len(forms),
            "basis_overlap": len(forms & basis),
            "basis_missing_from_file": len(basis - forms),
            "forms_not_in_final_basis": len(forms - basis),
        }
        master_file_rows.append(row)
        print(
            f"master artifact: {rel}: forms={len(forms)} "
            f"basis_overlap={len(forms & basis)}"
        )

    reports_by_form: dict[IndexTuple, list[dict[str, object]]] = defaultdict(list)
    all_report_pairs = 0
    tag_equals_sector = 0
    tag_not_sector = 0
    logs_with_reports = 0
    for path in _candidate_logs():
        reports = _read_reports(path)
        if not reports:
            continue
        logs_with_reports += 1
        rel = str(path.relative_to(PROJECT))
        print(f"Kira master-report log: {rel}: reports={len(reports)}")
        for key, tag in reports:
            all_report_pairs += 1
            sector = _sector(key)
            is_sector = tag == sector
            if is_sector:
                tag_equals_sector += 1
            else:
                tag_not_sector += 1
            reports_by_form[key].append(
                {
                    "log": rel,
                    "tag": tag,
                    "sector": sector,
                    "tag_equals_sector": is_sector,
                }
            )

    basis_in_any_masters_final = basis & masters_final_union
    basis_reported_master = basis & set(reports_by_form)
    basis_supported = basis & (masters_final_union | set(reports_by_form))
    basis_only_reported = basis_reported_master - basis_in_any_masters_final
    unsupported = basis - basis_supported

    provenance_rows = []
    for key in sorted(basis):
        row = basis_rows[key]
        provenance_rows.append(
            {
                "integral": _fmt(key),
                "indices": list(key),
                "basis_kind": row.get("kind"),
                "sector": _sector(key),
                "masters_final_files": sorted(
                    p for p in master_membership.get(key, [])
                    if Path(p).name == "masters.final"
                ),
                "other_master_artifacts": sorted(
                    p for p in master_membership.get(key, [])
                    if Path(p).name != "masters.final"
                ),
                "kira_master_reports": reports_by_form.get(key, []),
            }
        )

    summary = {
        "mode": "saved-artifact Q01 Kira master provenance audit",
        "final_basis_forms": len(basis),
        "master_artifacts_scanned": len(master_file_rows),
        "masters_final_files": masters_final_files,
        "union_forms_in_all_masters_final": len(masters_final_union),
        "final_basis_forms_in_any_masters_final": len(basis_in_any_masters_final),
        "final_basis_forms_reported_as_master_by_kira": len(basis_reported_master),
        "final_basis_forms_only_supported_by_kira_report": len(basis_only_reported),
        "final_basis_forms_supported_by_any_master_evidence": len(basis_supported),
        "final_basis_forms_without_master_evidence": [_fmt(v) for v in sorted(unsupported)],
        "logs_with_master_reports": logs_with_reports,
        "master_report_occurrences": all_report_pairs,
        "report_tag_equals_positive_sector": tag_equals_sector,
        "report_tag_differs_from_positive_sector": tag_not_sector,
        "report_tag_is_sector_for_all_reports": all_report_pairs > 0 and tag_not_sector == 0,
        "master_artifacts": master_file_rows,
        "basis_provenance": provenance_rows,
        "interpretation": {
            "masters_final_is_global_60_basis": len(basis_in_any_masters_final) == len(basis),
            "kira_report_tag_behaves_as_sector_number": all_report_pairs > 0 and tag_not_sector == 0,
            "note": (
                "A Kira 'master integral' report for a requested integral is recorded as evidence "
                "that the integral is terminal/master in that saved reduction context. It is not "
                "treated as proof that different forms sharing a tag are equivalent."
            ),
        },
        "pass": not unsupported and all_report_pairs > 0,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 Kira master provenance audit",
        "",
        f"final basis forms: {len(basis)}",
        f"masters.final files found: {masters_final_files}",
        f"union forms across all masters.final files: {len(masters_final_union)}",
        f"final-basis forms in any masters.final: {len(basis_in_any_masters_final)}",
        f"final-basis forms reported master by Kira: {len(basis_reported_master)}",
        f"final-basis forms only supported by Kira reports: {len(basis_only_reported)}",
        f"unsupported final-basis forms: {len(unsupported)}",
        "",
        f"master report occurrences: {all_report_pairs}",
        f"tag == positive-sector bitmask: {tag_equals_sector}",
        f"tag != positive-sector bitmask: {tag_not_sector}",
        "",
        "masters.final files:",
    ]
    for row in master_file_rows:
        if row["is_masters_final"]:
            lines.append(
                f"  {row['path']}: forms={row['integral_forms']} "
                f"basis_overlap={row['basis_overlap']}"
            )
    lines.extend(["", "Final-basis provenance:"])
    for row in provenance_rows:
        lines.append(
            f"  {row['integral']} sector={row['sector']} kind={row['basis_kind']} "
            f"masters.final={len(row['masters_final_files'])} "
            f"KiraReports={len(row['kira_master_reports'])}"
        )
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("masters.final files found:", masters_final_files)
    print("union forms across all masters.final files:", len(masters_final_union))
    print("final-basis forms in any masters.final:", len(basis_in_any_masters_final))
    print("final-basis forms reported master by Kira:", len(basis_reported_master))
    print("final-basis forms only supported by Kira reports:", len(basis_only_reported))
    print("final-basis forms without any master evidence:", len(unsupported))
    print("master report occurrences:", all_report_pairs)
    print("report tag == positive-sector bitmask:", tag_equals_sector)
    print("report tag != positive-sector bitmask:", tag_not_sector)
    print("report tag is sector number for all saved reports:", all_report_pairs > 0 and tag_not_sector == 0)
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)

    if unsupported:
        for key in sorted(unsupported)[:10]:
            print("  unsupported:", _fmt(key))
        raise SystemExit("Q01 Kira master provenance audit FAIL")
    if not all_report_pairs:
        raise SystemExit("Q01 Kira master provenance audit FAIL: no Kira master reports found")
    print("Q01 Kira master provenance audit PASS")


if __name__ == "__main__":
    main()
