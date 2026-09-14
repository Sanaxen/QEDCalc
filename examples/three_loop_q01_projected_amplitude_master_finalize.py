"""Finalize the saved Q01 projected amplitude on the Kira-confirmed master basis.

This stage performs no projected trace, FireFly reduction, or Kira execution.
It uses the already-saved terminal wave-2 kira2form log as an authoritative
classification artifact.  Kira explicitly reported every wave-1 terminal
leaf as ``This requested integral is a master integral`` and reported zero
unreduced integrals.  Those forms are therefore promoted from provisional
``terminal`` leaves to ``kira_master_confirmed`` forms in the saved projected-
amplitude reduction.

Important: a Kira-confirmed master *form* is not automatically claimed to be
an independent canonical master.  Symmetry-equivalent forms may still exist.
This script only certifies that no further reduction rule exists for the forms
requested from the saved FireFly database.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    FAMILY,
    PROJECT,
)

TARGET_FILE = PROJECT / "q01_terminal_wave2_targets"
WAVE2_LOG = PROJECT / "q01_terminal_wave2_firefly_export.log"
REDUCED_JSON = PROJECT / "q01_projected_amplitude_firefly_reduced.json"
OUTPUT_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
OUTPUT_TXT = PROJECT / "q01_projected_amplitude_kira_master_basis.txt"

_MASTER_RE = re.compile(
    rf"This requested integral is a master integral:\s*{re.escape(FAMILY)}\["
    r"(?P<args>-?\d+(?:\s*,\s*-?\d+){11})\]\s*#\s*(?P<tag>\d+)"
)
_TARGET_RE = re.compile(
    rf"^{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]$"
)

IndexTuple = tuple[int, ...]


def _indices(text: str) -> IndexTuple:
    values = tuple(int(part.strip()) for part in text.split(","))
    if len(values) != 12:
        raise ValueError(f"expected 12 indices, got {len(values)}")
    return values


def _integral_text(values: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in values)}]"


def _load_targets() -> tuple[IndexTuple, ...]:
    if not TARGET_FILE.exists():
        raise SystemExit(f"ERROR: wave-2 target file not found: {TARGET_FILE}")
    targets: list[IndexTuple] = []
    for line_no, raw in enumerate(TARGET_FILE.read_text(encoding="utf-8").splitlines(), 1):
        text = raw.strip()
        if not text:
            continue
        match = _TARGET_RE.match(text)
        if not match:
            raise SystemExit(f"ERROR: malformed target at line {line_no}: {text!r}")
        targets.append(_indices(match.group("args")))
    if len(targets) != len(set(targets)):
        raise SystemExit("ERROR: wave-2 target file contains duplicates")
    if not targets:
        raise SystemExit("ERROR: wave-2 target file is empty")
    return tuple(targets)


def _load_kira_master_reports() -> tuple[dict[IndexTuple, int], str]:
    if not WAVE2_LOG.exists():
        raise SystemExit(f"ERROR: saved wave-2 Kira log not found: {WAVE2_LOG}")
    text = WAVE2_LOG.read_text(encoding="utf-8", errors="strict")
    reports: dict[IndexTuple, int] = {}
    for match in _MASTER_RE.finditer(text):
        key = _indices(match.group("args"))
        tag = int(match.group("tag"))
        previous = reports.get(key)
        if previous is not None and previous != tag:
            raise SystemExit(f"ERROR: conflicting Kira master tags for {_integral_text(key)}")
        reports[key] = tag
    return reports, text


def main() -> None:
    print("QEDCalc Q01 projected-amplitude Kira-master finalization")
    print("mode: saved artifacts only; no Kira/FireFly/projected-trace recomputation")

    targets = _load_targets()
    target_set = set(targets)
    reports, log_text = _load_kira_master_reports()
    report_set = set(reports)

    missing_reports = sorted(target_set - report_set)
    unexpected_reports = sorted(report_set - target_set)
    unreduced_zero = bool(re.search(r"unreduced integrals:\s*0\s*\.", log_text))

    print("wave-2 requested terminal forms:", len(targets))
    print("Kira-reported master forms:", len(reports))
    print("missing master reports:", len(missing_reports))
    print("unexpected master reports:", len(unexpected_reports))
    print("Kira unreduced integrals = 0:", unreduced_zero)

    if missing_reports:
        raise SystemExit(
            "ERROR: not every wave-2 terminal form was confirmed as a Kira master; "
            f"missing={len(missing_reports)} first={_integral_text(missing_reports[0])}"
        )
    if unexpected_reports:
        raise SystemExit(
            "ERROR: wave-2 log contains unexpected master-form reports; "
            f"extra={len(unexpected_reports)} first={_integral_text(unexpected_reports[0])}"
        )
    if not unreduced_zero:
        raise SystemExit("ERROR: wave-2 Kira log does not report 'unreduced integrals: 0.'")

    if not REDUCED_JSON.exists():
        raise SystemExit(f"ERROR: reduced projected-amplitude JSON not found: {REDUCED_JSON}")
    data = json.loads(REDUCED_JSON.read_text(encoding="utf-8"))
    basis_terms = list(data.get("basis_terms", []))
    if not basis_terms:
        raise SystemExit("ERROR: reduced projected-amplitude JSON has no basis_terms")

    confirmed_used = 0
    explicit_used = 0
    unconfirmed_terminal: list[str] = []
    final_rows: list[dict[str, object]] = []

    for row in basis_terms:
        kind = str(row.get("kind", ""))
        indices_raw = row.get("indices")
        if not isinstance(indices_raw, list) or len(indices_raw) != 12:
            raise SystemExit(f"ERROR: malformed basis row: {row!r}")
        key = tuple(int(v) for v in indices_raw)
        updated = dict(row)
        if kind == "master":
            updated["kind"] = "explicit_master"
            updated["kira_master_confirmation"] = "masters.final"
            explicit_used += 1
        elif kind == "terminal":
            if key not in report_set:
                unconfirmed_terminal.append(_integral_text(key))
                updated["kind"] = "unconfirmed_terminal"
            else:
                updated["kind"] = "kira_master_confirmed"
                updated["kira_master_confirmation"] = "wave2_kira2form_log"
                updated["kira_report_tag"] = reports[key]
                confirmed_used += 1
        else:
            raise SystemExit(f"ERROR: unexpected basis kind {kind!r} for {_integral_text(key)}")
        final_rows.append(updated)

    if unconfirmed_terminal:
        raise SystemExit(
            "ERROR: reduced amplitude still contains terminal forms not confirmed by Kira; "
            f"count={len(unconfirmed_terminal)} first={unconfirmed_terminal[0]}"
        )

    final_summary = {
        "mode": "saved-artifact Kira master-form finalization; no recomputation",
        "source_reduced_json": str(REDUCED_JSON),
        "wave2_target_file": str(TARGET_FILE),
        "wave2_kira_log": str(WAVE2_LOG),
        "wave2_requested_forms": len(targets),
        "wave2_kira_confirmed_master_forms": len(reports),
        "kira_unreduced_integrals_zero": unreduced_zero,
        "native_projected_terms": data.get("native_projected_terms"),
        "unique_expanded_kira_integrals": data.get("unique_expanded_kira_integrals"),
        "output_nonzero_basis_terms": len(final_rows),
        "output_explicit_master_terms": explicit_used,
        "output_kira_confirmed_master_terms": confirmed_used,
        "basis_is_independence_minimized": False,
        "basis_note": (
            "All output forms are masters according to masters.final or the saved wave-2 "
            "kira2form log. Symmetry-equivalent master forms may remain; this artifact does "
            "not claim that the displayed forms are a minimal independent canonical basis."
        ),
        "basis_terms": final_rows,
        "pass": (
            not missing_reports
            and not unexpected_reports
            and unreduced_zero
            and not unconfirmed_terminal
            and data.get("native_projected_terms") == 910
            and data.get("unique_expanded_kira_integrals") == 944
            and len(final_rows) > 0
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(final_summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 projected amplitude on Kira-confirmed master-form basis",
        "",
        "This is a reduction-complete Kira master-form basis, not yet claimed to be a",
        "minimal independent canonical master basis under all symmetry identifications.",
        "",
        f"native projected terms: {final_summary['native_projected_terms']}",
        f"unique expanded Kira integrals: {final_summary['unique_expanded_kira_integrals']}",
        f"wave-2 Kira-confirmed master forms: {len(reports)}",
        f"nonzero output basis terms: {len(final_rows)}",
        f"explicit masters used: {explicit_used}",
        f"wave-2-confirmed master forms used: {confirmed_used}",
        "",
        "Reduced projected amplitude:",
    ]
    for row in final_rows:
        lines.append(f"[{row['kind']}] ({row['coefficient']}) * {row['integral']}")
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("nonzero output basis terms:", len(final_rows))
    print("  explicit masters used:", explicit_used)
    print("  Kira-confirmed master forms used:", confirmed_used)
    print("unconfirmed terminal forms in amplitude: 0")
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)

    if not final_summary["pass"]:
        raise SystemExit("Q01 projected-amplitude Kira-master finalization FAIL")
    print("Q01 projected-amplitude Kira-master finalization PASS")


if __name__ == "__main__":
    main()
