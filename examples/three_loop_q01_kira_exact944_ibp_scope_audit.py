"""Audit the saved Q01 exact944 Kira IBP/reduction scope.

Saved-artifact only. No Kira, FireFly, Fermat, or projected-trace recomputation.

This stage does not claim a mathematically global minimal master basis.  It checks
that the exact944 run which contains all final 60 master forms also had the
original 944 mandatory demands in scope, records the saved seed/sector settings,
checks for preferred-master directives, and records saved Kira evidence that no
requested integrals remained unreduced.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import FAMILY, PROJECT

SAME_CONTEXT_JSON = PROJECT / "q01_kira_exact944_same_context_audit.json"
ORIGINAL_TARGETS = PROJECT / "q01_944_targets"
OUTPUT_JSON = PROJECT / "q01_kira_exact944_ibp_scope_audit.json"
OUTPUT_TXT = PROJECT / "q01_kira_exact944_ibp_scope_audit.txt"

IndexTuple = tuple[int, ...]
_FAMILY_RE = re.compile(rf"{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]")
_LIST_RE = re.compile(rf"\[\s*{re.escape(FAMILY)}\s*,\s*([^\]\s]+)\s*\]")
_ALT_RE = re.compile(r"\balt_dir\s*:\s*exact944(?:\s|$)")
_UNREDUCED_ZERO_RE = re.compile(r"unreduced integrals:\s*0\s*\.")
_SETTING_KEYS = (
    "top_level_sectors",
    "top_level_sector",
    "r:",
    "s:",
    "d:",
    "select_mandatory_list",
    "select_mandatory_recursively",
    "preferred",
)


def _indices(text: str) -> IndexTuple:
    values = tuple(int(v.strip()) for v in text.split(","))
    if len(values) != 12:
        raise ValueError(f"expected 12 indices, got {len(values)}")
    return values


def _read_integrals(path: Path) -> set[IndexTuple]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="strict")
    return {_indices(m.group("args")) for m in _FAMILY_RE.finditer(text)}


def _resolve_target(name: str, yaml_path: Path) -> Path | None:
    for candidate in (PROJECT / name, yaml_path.parent / name):
        if candidate.is_file():
            return candidate
    matches = list(PROJECT.rglob(Path(name).name))
    return matches[0] if len(matches) == 1 else None


def main() -> None:
    print("QEDCalc Q01 exact944 IBP/reduction-scope audit")
    print("mode: saved artifacts only; no recomputation")

    if not SAME_CONTEXT_JSON.exists():
        raise SystemExit(f"ERROR: same-context audit JSON not found: {SAME_CONTEXT_JSON}")
    same = json.loads(SAME_CONTEXT_JSON.read_text(encoding="utf-8"))
    if not same.get("pass"):
        raise SystemExit("ERROR: exact944 same-context audit is not marked PASS")
    if not same.get("all_final60_coexist_in_exact944_masters_final"):
        raise SystemExit("ERROR: final 60 do not coexist in exact944 masters.final")

    original944 = _read_integrals(ORIGINAL_TARGETS)
    if len(original944) != 944:
        raise SystemExit(f"ERROR: expected 944 original targets, got {len(original944)}")

    yaml_rows: list[dict[str, object]] = []
    union_targets: set[IndexTuple] = set()
    preferred_lines: list[str] = []
    all_setting_lines: list[str] = []

    for path in sorted(PROJECT.rglob("*.yaml")):
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError):
            continue
        if not _ALT_RE.search(text):
            continue

        refs = sorted(set(_LIST_RE.findall(text)))
        target_rows = []
        for name in refs:
            resolved = _resolve_target(name, path)
            forms = _read_integrals(resolved) if resolved else set()
            union_targets |= forms
            target_rows.append({
                "name": name,
                "path": str(resolved.relative_to(PROJECT)) if resolved else None,
                "forms": len(forms),
                "original944_overlap": len(forms & original944),
            })

        settings = []
        for raw in text.splitlines():
            stripped = raw.strip()
            low = stripped.lower()
            if any(key.lower() in low for key in _SETTING_KEYS):
                settings.append(stripped)
                all_setting_lines.append(f"{path.relative_to(PROJECT)}: {stripped}")
                if "preferred" in low:
                    preferred_lines.append(f"{path.relative_to(PROJECT)}: {stripped}")

        yaml_rows.append({
            "path": str(path.relative_to(PROJECT)),
            "targets": target_rows,
            "scope_setting_lines": settings,
        })

    missing944 = sorted(original944 - union_targets)

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
        log_rows.append({
            "path": str(path.relative_to(PROJECT)),
            "unreduced_integrals_zero": zero,
        })

    summary = {
        "mode": "saved-artifact exact944 IBP/reduction-scope audit",
        "same_context_pass": bool(same.get("pass")),
        "final60_coexist_in_exact944": bool(same.get("all_final60_coexist_in_exact944_masters_final")),
        "exact944_masters_final_forms": int(same.get("exact944_masters_final_forms", 0)),
        "original_exact944_target_forms": len(original944),
        "matching_exact944_job_yaml_files": len(yaml_rows),
        "union_exact944_job_target_forms": len(union_targets),
        "original944_present_in_union_job_targets": len(original944 & union_targets),
        "original944_missing_from_union_job_targets": len(missing944),
        "missing_original944_samples": [list(v) for v in missing944[:12]],
        "scope_setting_lines": all_setting_lines,
        "preferred_master_directive_lines": preferred_lines,
        "preferred_master_directives_found": bool(preferred_lines),
        "candidate_exact944_logs": log_rows,
        "candidate_exact944_logs_with_unreduced_zero": logs_with_unreduced_zero,
        "job_rows": yaml_rows,
        "interpretation": (
            "PASS certifies the saved exact944 reduction scope used here: all 944 original mandatory "
            "demands are represented in the exact944 job-target union, all final 60 forms coexist in "
            "one exact944 masters.final, and at least one saved exact944 log reports unreduced "
            "integrals: 0. This is evidence of reduction completeness for the generated exact944 "
            "problem, not a proof of global IBP minimality under arbitrarily larger seed bounds."
        ),
    }
    summary["pass"] = (
        summary["same_context_pass"]
        and summary["final60_coexist_in_exact944"]
        and summary["exact944_masters_final_forms"] == 117
        and len(original944) == 944
        and not missing944
        and len(yaml_rows) > 0
        and logs_with_unreduced_zero > 0
    )

    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "QEDCalc Q01 exact944 IBP/reduction-scope audit",
        "",
        f"same-context audit PASS: {summary['same_context_pass']}",
        f"final60 coexist in exact944: {summary['final60_coexist_in_exact944']}",
        f"exact944 masters.final forms: {summary['exact944_masters_final_forms']}",
        f"original exact944 targets: {len(original944)}",
        f"matching exact944 job YAML files: {len(yaml_rows)}",
        f"union exact944 job target forms: {len(union_targets)}",
        f"original944 present in job-target union: {len(original944 & union_targets)}",
        f"original944 missing from job-target union: {len(missing944)}",
        f"preferred-master directive lines: {len(preferred_lines)}",
        f"candidate exact944 logs with unreduced integrals = 0: {logs_with_unreduced_zero}",
        "",
        "Saved scope-setting lines:",
    ]
    lines.extend(f"  {line}" for line in all_setting_lines)
    lines.extend(["", summary["interpretation"]])
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("same-context audit PASS:", summary["same_context_pass"])
    print("final60 coexist in exact944:", summary["final60_coexist_in_exact944"])
    print("exact944 masters.final forms:", summary["exact944_masters_final_forms"])
    print("original exact944 targets:", len(original944))
    print("matching exact944 job YAML files:", len(yaml_rows))
    print("union exact944 job target forms:", len(union_targets))
    print("original944 present in job-target union:", len(original944 & union_targets))
    print("original944 missing from job-target union:", len(missing944))
    print("preferred-master directive lines:", len(preferred_lines))
    print("candidate exact944 logs with unreduced integrals = 0:", logs_with_unreduced_zero)
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)

    if not summary["pass"]:
        raise SystemExit("Q01 exact944 IBP/reduction-scope audit FAIL")
    print("Q01 exact944 IBP/reduction-scope audit PASS")


if __name__ == "__main__":
    main()
