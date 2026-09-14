"""Explain why exact944closure1_firefly has exactly four masters.final forms.

Saved-artifact only.  No Kira, FireFly, Fermat, or projected-trace recomputation.
The script correlates the four-master masters.final with saved Kira job YAML,
mandatory target lists, and the finalized 60-form amplitude basis.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import FAMILY, PROJECT

RUN_SCOPE_JSON = PROJECT / "q01_kira_master_run_scope_audit.json"
PROVENANCE_JSON = PROJECT / "q01_kira_master_provenance_audit.json"
FINAL_BASIS_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
OUTPUT_JSON = PROJECT / "q01_kira_four_master_scope_explain.json"
OUTPUT_TXT = PROJECT / "q01_kira_four_master_scope_explain.txt"
FOUR_ALT_DIR = "exact944closure1_firefly"

IndexTuple = tuple[int, ...]
_FAMILY_RE = re.compile(
    rf"{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]"
)
_ALT_RE = re.compile(r"\balt_dir\s*:\s*([^\s#]+)")
_MANDATORY_RE = re.compile(r"select_mandatory_list\s*:\s*\n(?P<body>(?:\s+.*\n?)*)", re.MULTILINE)
_LIST_ITEM_RE = re.compile(rf"\[\s*{re.escape(FAMILY)}\s*,\s*([^\]\s]+)\s*\]")


def _indices(text: str) -> IndexTuple:
    vals = tuple(int(v.strip()) for v in text.split(","))
    if len(vals) != 12:
        raise ValueError(f"expected 12 indices, got {len(vals)}")
    return vals


def _fmt(v: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(x) for x in v)}]"


def _read_integrals(path: Path) -> set[IndexTuple]:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError):
        return set()
    return {_indices(m.group("args")) for m in _FAMILY_RE.finditer(text)}


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"ERROR: required artifact not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"ERROR: malformed JSON artifact: {path}")
    return data


def _basis() -> set[IndexTuple]:
    data = _load_json(FINAL_BASIS_JSON)
    rows = data.get("basis_terms", [])
    result: set[IndexTuple] = set()
    for row in rows:
        raw = row.get("indices") if isinstance(row, dict) else None
        if isinstance(raw, list) and len(raw) == 12:
            result.add(tuple(int(v) for v in raw))
    if len(result) != 60:
        raise SystemExit(f"ERROR: expected final 60-form basis, got {len(result)}")
    return result


def _four_master_file(run_scope: dict) -> Path:
    rows = run_scope.get("four_master_runs", [])
    if not isinstance(rows, list) or len(rows) != 1:
        raise SystemExit(f"ERROR: expected exactly one four-master run, got {len(rows) if isinstance(rows, list) else 'malformed'}")
    rel = str(rows[0].get("path", ""))
    path = PROJECT / rel
    if not path.exists():
        raise SystemExit(f"ERROR: four-master masters.final not found: {path}")
    return path


def _candidate_jobs() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(PROJECT.rglob("*.yaml")):
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError):
            continue
        alt_dirs = _ALT_RE.findall(text)
        if FOUR_ALT_DIR not in alt_dirs:
            continue
        target_names: list[str] = []
        for block in _MANDATORY_RE.finditer(text):
            target_names.extend(_LIST_ITEM_RE.findall(block.group("body")))
        # Fallback: collect any family/list references in the whole YAML.
        if not target_names:
            target_names.extend(_LIST_ITEM_RE.findall(text))
        rows.append({
            "path": str(path.relative_to(PROJECT)),
            "alt_dirs": alt_dirs,
            "target_names": sorted(set(target_names)),
        })
    return rows


def _resolve_target(name: str, yaml_path: Path) -> Path | None:
    candidates = [
        PROJECT / name,
        yaml_path.parent / name,
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    # Some Kira mandatory lists are saved without extension and may appear deeper.
    matches = list(PROJECT.rglob(Path(name).name))
    return matches[0] if len(matches) == 1 else None


def main() -> None:
    print("QEDCalc Q01 four-master run-scope explanation")
    print("mode: saved job/target/master artifacts only; no recomputation")

    run_scope = _load_json(RUN_SCOPE_JSON)
    provenance = _load_json(PROVENANCE_JSON)
    if not run_scope.get("pass") or not provenance.get("pass"):
        raise SystemExit("ERROR: prerequisite master audits are not marked PASS")

    final60 = _basis()
    masters_path = _four_master_file(run_scope)
    four = _read_integrals(masters_path)
    if len(four) != 4:
        raise SystemExit(f"ERROR: expected four forms in {masters_path}, got {len(four)}")

    jobs = _candidate_jobs()
    target_rows: list[dict[str, object]] = []
    union_targets: set[IndexTuple] = set()
    for job in jobs:
        ypath = PROJECT / str(job["path"])
        for name in job["target_names"]:
            resolved = _resolve_target(str(name), ypath)
            forms = _read_integrals(resolved) if resolved else set()
            union_targets |= forms
            target_rows.append({
                "job": job["path"],
                "target_name": name,
                "resolved_path": str(resolved.relative_to(PROJECT)) if resolved else None,
                "integral_forms": len(forms),
                "final60_overlap": len(forms & final60),
                "four_master_overlap": len(forms & four),
                "contains_all_four_masters": four <= forms if forms else False,
            })

    four_in_targets = four & union_targets
    final60_in_targets = final60 & union_targets

    summary = {
        "mode": "saved-artifact explanation of exact944closure1_firefly four-master scope",
        "four_master_alt_dir": FOUR_ALT_DIR,
        "four_master_masters_final": str(masters_path.relative_to(PROJECT)),
        "four_master_forms": [_fmt(v) for v in sorted(four)],
        "four_master_forms_in_final60": len(four & final60),
        "matching_job_yaml_count": len(jobs),
        "matching_jobs": jobs,
        "target_lists": target_rows,
        "union_target_forms": len(union_targets),
        "union_target_final60_overlap": len(final60_in_targets),
        "union_target_four_master_overlap": len(four_in_targets),
        "all_four_masters_are_in_run_targets": four <= union_targets if union_targets else False,
        "all_final60_are_in_run_targets": final60 <= union_targets if union_targets else False,
        "interpretation": {
            "four_is_run_local": True,
            "four_is_global_basis": False,
            "four_master_file_contains_only_final60_forms": four <= final60,
            "why_four": (
                "The four forms belong to the exact944closure1_firefly reduction context. "
                "They are the masters.final forms retained by that run; other saved runs "
                "have larger masters.final sets and collectively contain all final 60 forms. "
                "The target-list comparison records how much of the final-60 basis was in "
                "scope for this run; it does not reinterpret masters.final as a global basis."
            ),
        },
        "pass": (
            len(four) == 4
            and four <= final60
            and len(jobs) > 0
            and bool(run_scope.get("interpretation", {}).get("four_is_run_scoped"))
            and bool(run_scope.get("interpretation", {}).get("four_is_not_global_master_count"))
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 four-master run-scope explanation",
        "",
        f"four-master alt_dir: {FOUR_ALT_DIR}",
        f"masters.final: {masters_path.relative_to(PROJECT)}",
        f"four master forms: {len(four)}",
        f"matching job YAML files: {len(jobs)}",
        f"union target forms: {len(union_targets)}",
        f"union target overlap with final 60: {len(final60_in_targets)}",
        f"union target overlap with four masters: {len(four_in_targets)}",
        "",
        "Four masters:",
    ]
    lines.extend(f"  {_fmt(v)}" for v in sorted(four))
    lines.extend(["", "Matching jobs / target lists:"])
    for row in target_rows:
        lines.append(
            f"  {row['job']} -> {row['target_name']} "
            f"forms={row['integral_forms']} overlap60={row['final60_overlap']} "
            f"overlap4={row['four_master_overlap']}"
        )
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("four-master masters.final:", masters_path.relative_to(PROJECT))
    print("four master forms:", len(four))
    print("matching job YAML files:", len(jobs))
    print("union target forms:", len(union_targets))
    print("union target overlap with final 60:", len(final60_in_targets))
    print("union target overlap with four masters:", len(four_in_targets))
    print("all four masters are in run targets:", summary["all_four_masters_are_in_run_targets"])
    print("all final 60 are in run targets:", summary["all_final60_are_in_run_targets"])
    for row in target_rows:
        print(
            "  target:", row["target_name"],
            "forms=", row["integral_forms"],
            "overlap60=", row["final60_overlap"],
            "overlap4=", row["four_master_overlap"],
        )
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)

    if not summary["pass"]:
        raise SystemExit("Q01 four-master run-scope explanation FAIL")
    print("Q01 four-master run-scope explanation PASS")


if __name__ == "__main__":
    main()
