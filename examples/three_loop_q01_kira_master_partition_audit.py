"""Audit the exact 4 + 29 + 27 provenance of the final Q01 60 master forms.

Saved-artifact only.  No Kira, FireFly, Fermat, or projected-trace recomputation
is performed.

The final projected-amplitude basis contains 60 forms.  This audit checks that
those 60 forms split exactly into:

* 4 forms written to exact944closure1_firefly/results/Q01_full/masters.final;
* 29 additional Kira-master forms already present in the closure-wave-1 target
  list but not written to that run's masters.final;
* 27 further Kira-master forms which occur in the saved terminal-wave-2 list
  but were not themselves closure-wave-1 targets, i.e. they entered the saved
  reduction graph as terminal RHS leaves.

The purpose is to explain why one run has masters.final size 4 without treating
that file as a global four-master basis.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import FAMILY, PROJECT

FINAL_BASIS_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
FOUR_MASTER_FILE = PROJECT / "exact944closure1_firefly" / "results" / FAMILY / "masters.final"
CLOSURE1_TARGETS = PROJECT / "q01_exact944_closure1_targets"
TERMINAL56_TARGETS = PROJECT / "q01_terminal_wave2_targets"
OUTPUT_JSON = PROJECT / "q01_kira_master_partition_audit.json"
OUTPUT_TXT = PROJECT / "q01_kira_master_partition_audit.txt"

IndexTuple = tuple[int, ...]

_FAMILY_RE = re.compile(
    rf"{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]"
)


def _indices(text: str) -> IndexTuple:
    values = tuple(int(x.strip()) for x in text.split(","))
    if len(values) != 12:
        raise ValueError(f"expected 12 indices, got {len(values)}")
    return values


def _fmt(values: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in values)}]"


def _read_integrals(path: Path) -> set[IndexTuple]:
    if not path.exists():
        raise SystemExit(f"ERROR: required artifact not found: {path}")
    text = path.read_text(encoding="utf-8", errors="strict")
    return {_indices(m.group("args")) for m in _FAMILY_RE.finditer(text)}


def _load_final_basis() -> set[IndexTuple]:
    if not FINAL_BASIS_JSON.exists():
        raise SystemExit(f"ERROR: final basis JSON not found: {FINAL_BASIS_JSON}")
    data = json.loads(FINAL_BASIS_JSON.read_text(encoding="utf-8"))
    if not data.get("pass"):
        raise SystemExit("ERROR: final basis JSON is not marked PASS")
    rows = data.get("basis_terms")
    if not isinstance(rows, list) or not rows:
        raise SystemExit("ERROR: final basis JSON has no basis_terms")
    out: set[IndexTuple] = set()
    for row in rows:
        raw = row.get("indices")
        if not isinstance(raw, list) or len(raw) != 12:
            raise SystemExit(f"ERROR: malformed basis row: {row!r}")
        out.add(tuple(int(v) for v in raw))
    return out


def main() -> None:
    print("QEDCalc Q01 master-form partition audit")
    print("mode: saved artifacts only; no recomputation")

    final60 = _load_final_basis()
    explicit4 = _read_integrals(FOUR_MASTER_FILE)
    closure1 = _read_integrals(CLOSURE1_TARGETS)
    terminal56 = _read_integrals(TERMINAL56_TARGETS)

    explicit4_in_final = explicit4 & final60
    terminal56_in_final = terminal56 & final60
    direct_terminal29 = terminal56_in_final & closure1
    rhs_only_terminal27 = terminal56_in_final - closure1

    partition_union = explicit4_in_final | direct_terminal29 | rhs_only_terminal27
    partition_pairwise_disjoint = (
        not (explicit4_in_final & direct_terminal29)
        and not (explicit4_in_final & rhs_only_terminal27)
        and not (direct_terminal29 & rhs_only_terminal27)
    )

    closure1_final_overlap = closure1 & final60
    expected_closure1_overlap = explicit4_in_final | direct_terminal29

    summary = {
        "mode": "saved-artifact Q01 final master-form partition audit",
        "final_basis_forms": len(final60),
        "four_master_file": str(FOUR_MASTER_FILE),
        "four_master_forms": len(explicit4),
        "four_master_forms_in_final_basis": len(explicit4_in_final),
        "terminal_wave2_forms": len(terminal56),
        "terminal_wave2_forms_in_final_basis": len(terminal56_in_final),
        "closure1_target_forms": len(closure1),
        "closure1_final_basis_overlap": len(closure1_final_overlap),
        "direct_terminal_forms_in_closure1_targets": len(direct_terminal29),
        "rhs_only_terminal_forms_not_in_closure1_targets": len(rhs_only_terminal27),
        "partition_union_forms": len(partition_union),
        "partition_pairwise_disjoint": partition_pairwise_disjoint,
        "partition_equals_final_basis": partition_union == final60,
        "closure1_overlap_equals_four_plus_direct_terminal": closure1_final_overlap == expected_closure1_overlap,
        "four_plus_terminal56_equals_final_basis": (explicit4_in_final | terminal56_in_final) == final60,
        "four_and_terminal56_disjoint": not (explicit4_in_final & terminal56_in_final),
        "groups": {
            "explicit_four": [_fmt(v) for v in sorted(explicit4_in_final)],
            "direct_terminal_29": [_fmt(v) for v in sorted(direct_terminal29)],
            "rhs_only_terminal_27": [_fmt(v) for v in sorted(rhs_only_terminal27)],
        },
        "interpretation": (
            "The exact944closure1_firefly masters.final file is run-scoped. Its four forms are "
            "the explicit masters written by that run. The other 56 final forms are independently "
            "Kira-confirmed master forms: 29 were already closure-wave-1 targets, while 27 entered "
            "the reduction graph only as terminal RHS leaves and were subsequently queried in the "
            "terminal wave-2 export. Therefore 4 is not the global Q01 master count."
        ),
    }

    summary["pass"] = (
        len(final60) == 60
        and len(explicit4_in_final) == 4
        and len(terminal56_in_final) == 56
        and len(direct_terminal29) == 29
        and len(rhs_only_terminal27) == 27
        and partition_pairwise_disjoint
        and partition_union == final60
        and closure1_final_overlap == expected_closure1_overlap
        and not (explicit4_in_final & terminal56_in_final)
    )

    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 master-form partition audit",
        "",
        f"final basis forms: {len(final60)}",
        f"explicit masters.final forms: {len(explicit4_in_final)}",
        f"terminal wave-2 final forms: {len(terminal56_in_final)}",
        f"  terminal forms already in closure1 target list: {len(direct_terminal29)}",
        f"  terminal RHS-only forms outside closure1 target list: {len(rhs_only_terminal27)}",
        "",
        f"partition: {len(explicit4_in_final)} + {len(direct_terminal29)} + {len(rhs_only_terminal27)} = {len(partition_union)}",
        f"partition equals final 60: {partition_union == final60}",
        f"partition pairwise disjoint: {partition_pairwise_disjoint}",
        f"closure1 final-60 overlap: {len(closure1_final_overlap)}",
        f"closure1 overlap = 4 + 29: {closure1_final_overlap == expected_closure1_overlap}",
        "",
        "Interpretation:",
        summary["interpretation"],
    ]
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("final basis forms:", len(final60))
    print("explicit masters.final forms:", len(explicit4_in_final))
    print("terminal wave-2 final forms:", len(terminal56_in_final))
    print("terminal forms already in closure1 targets:", len(direct_terminal29))
    print("terminal RHS-only forms outside closure1 targets:", len(rhs_only_terminal27))
    print("partition:", f"{len(explicit4_in_final)} + {len(direct_terminal29)} + {len(rhs_only_terminal27)} = {len(partition_union)}")
    print("partition equals final 60:", partition_union == final60)
    print("partition pairwise disjoint:", partition_pairwise_disjoint)
    print("closure1 final-60 overlap:", len(closure1_final_overlap))
    print("closure1 overlap = 4 + 29:", closure1_final_overlap == expected_closure1_overlap)
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)

    if not summary["pass"]:
        raise SystemExit("Q01 master-form partition audit FAIL")
    print("Q01 master-form partition audit PASS")


if __name__ == "__main__":
    main()
