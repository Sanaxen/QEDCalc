"""Audit whether the final Q01 60 master forms coexist in one exact944 Kira context.

Saved-artifact only. No Kira, FireFly, Fermat, or projected-trace recomputation.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import FAMILY, PROJECT

FINAL_BASIS_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
EXACT944_MASTERS = PROJECT / "exact944" / "results" / FAMILY / "masters.final"
OUTPUT_JSON = PROJECT / "q01_kira_exact944_same_context_audit.json"
OUTPUT_TXT = PROJECT / "q01_kira_exact944_same_context_audit.txt"

IndexTuple = tuple[int, ...]
_FAMILY_RE = re.compile(rf"{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]")
_LIST_RE = re.compile(rf"\[\s*{re.escape(FAMILY)}\s*,\s*([^\]\s]+)\s*\]")
_ALT_EXACT944_RE = re.compile(r"\balt_dir\s*:\s*exact944(?:\s|$)")
_UNREDUCED_ZERO_RE = re.compile(r"unreduced integrals:\s*0\s*\.")


def _indices(text: str) -> IndexTuple:
    vals = tuple(int(x.strip()) for x in text.split(","))
    if len(vals) != 12:
        raise ValueError(f"expected 12 indices, got {len(vals)}")
    return vals


def _read_integrals(path: Path) -> set[IndexTuple]:
    if not path.exists():
        raise SystemExit(f"ERROR: required artifact not found: {path}")
    text = path.read_text(encoding="utf-8", errors="strict")
    return {_indices(m.group("args")) for m in _FAMILY_RE.finditer(text)}


def _load_final60() -> set[IndexTuple]:
    if not FINAL_BASIS_JSON.exists():
        raise SystemExit(f"ERROR: final basis JSON not found: {FINAL_BASIS_JSON}")
    data = json.loads(FINAL_BASIS_JSON.read_text(encoding="utf-8"))
    rows = data.get("basis_terms", [])
    out: set[IndexTuple] = set()
    for row in rows:
        raw = row.get("indices") if isinstance(row, dict) else None
        if isinstance(raw, list) and len(raw) == 12:
            out.add(tuple(int(v) for v in raw))
    if len(out) != 60:
        raise SystemExit(f"ERROR: expected final 60 forms, got {len(out)}")
    return out


def _resolve_target(name: str, yaml_path: Path) -> Path | None:
    for candidate in (PROJECT / name, yaml_path.parent / name):
        if candidate.is_file():
            return candidate
    matches = list(PROJECT.rglob(Path(name).name))
    return matches[0] if len(matches) == 1 else None


def main() -> None:
    print("QEDCalc Q01 exact944 same-context master audit")
    print("mode: saved artifacts only; no recomputation")

    final60 = _load_final60()
    exact_masters = _read_integrals(EXACT944_MASTERS)
    overlap = final60 & exact_masters
    missing = final60 - exact_masters

    job_rows = []
    target_union: set[IndexTuple] = set()
    preferred_lines: list[str] = []
    for path in sorted(PROJECT.rglob("*.yaml")):
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError):
            continue
        if not _ALT_EXACT944_RE.search(text):
            continue
        refs = sorted(set(_LIST_RE.findall(text)))
        resolved_rows = []
        for name in refs:
            resolved = _resolve_target(name, path)
            forms = _read_integrals(resolved) if resolved else set()
            target_union |= forms
            resolved_rows.append({
                "name": name,
                "path": str(resolved.relative_to(PROJECT)) if resolved else None,
                "forms": len(forms),
                "final60_overlap": len(forms & final60),
            })
        local_preferred = [line.strip() for line in text.splitlines() if "preferred" in line.lower()]
        preferred_lines.extend(f"{path.relative_to(PROJECT)}: {line}" for line in local_preferred)
        job_rows.append({
            "path": str(path.relative_to(PROJECT)),
            "targets": resolved_rows,
            "preferred_lines": local_preferred,
        })

    log_rows = []
    logs_with_unreduced_zero = 0
    for path in sorted(PROJECT.rglob("*.log")):
        name = path.name.lower()
        if "exact944" not in name or "closure1" in name:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError):
            continue
        zero = bool(_UNREDUCED_ZERO_RE.search(text))
        if zero:
            logs_with_unreduced_zero += 1
        log_rows.append({"path": str(path.relative_to(PROJECT)), "unreduced_zero": zero})

    same_context = len(exact_masters) > 0 and not missing
    summary = {
        "mode": "saved-artifact exact944 same-context master audit",
        "final_basis_forms": len(final60),
        "exact944_masters_final_forms": len(exact_masters),
        "final60_in_exact944_masters_final": len(overlap),
        "final60_missing_from_exact944_masters_final": len(missing),
        "all_final60_coexist_in_exact944_masters_final": same_context,
        "matching_exact944_job_yaml_files": len(job_rows),
        "job_rows": job_rows,
        "union_exact944_job_target_forms": len(target_union),
        "union_exact944_job_target_overlap_final60": len(target_union & final60),
        "preferred_master_directive_lines": preferred_lines,
        "preferred_master_directives_found": bool(preferred_lines),
        "candidate_exact944_logs": log_rows,
        "candidate_exact944_logs_with_unreduced_zero": logs_with_unreduced_zero,
        "interpretation": (
            "All 60 projected-amplitude master forms coexist in the same exact944 masters.final "
            "when all_final60_coexist_in_exact944_masters_final is true. This is stronger than a "
            "union-over-runs statement. It establishes a common Kira reduction context, but does "
            "not by itself prove global minimality beyond the generated IBP/reduction scope."
        ),
        "pass": same_context and len(exact_masters) == 117,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 exact944 same-context master audit",
        "",
        f"final basis forms: {len(final60)}",
        f"exact944 masters.final forms: {len(exact_masters)}",
        f"final60 in exact944 masters.final: {len(overlap)}",
        f"final60 missing from exact944 masters.final: {len(missing)}",
        f"all final60 coexist in one exact944 masters.final: {same_context}",
        f"matching exact944 job YAML files: {len(job_rows)}",
        f"union job target forms: {len(target_union)}",
        f"union job target overlap final60: {len(target_union & final60)}",
        f"preferred-master directive lines: {len(preferred_lines)}",
        f"candidate exact944 logs with unreduced integrals = 0: {logs_with_unreduced_zero}",
        "",
        summary["interpretation"],
    ]
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("final basis forms:", len(final60))
    print("exact944 masters.final forms:", len(exact_masters))
    print("final60 in exact944 masters.final:", len(overlap))
    print("final60 missing from exact944 masters.final:", len(missing))
    print("all final60 coexist in one exact944 masters.final:", same_context)
    print("matching exact944 job YAML files:", len(job_rows))
    print("union exact944 job target forms:", len(target_union))
    print("union target overlap with final60:", len(target_union & final60))
    print("preferred-master directive lines:", len(preferred_lines))
    print("candidate exact944 logs with unreduced integrals = 0:", logs_with_unreduced_zero)
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)

    if not summary["pass"]:
        raise SystemExit("Q01 exact944 same-context master audit FAIL")
    print("Q01 exact944 same-context master audit PASS")


if __name__ == "__main__":
    main()
