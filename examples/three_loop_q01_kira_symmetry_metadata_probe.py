"""Discover saved Kira symmetry/canonicalization metadata for Q01 masters.

This probe performs no Kira, FireFly, or projected-trace computation.  It
inspects the already-saved Q01 Kira project for text artifacts that may encode
sector mappings, symmetry relations, preferred masters, or canonicalization
metadata.  It also cross-references every master form used by the finalized
projected amplitude against those artifacts.

The purpose is deliberately diagnostic: Kira report tags (``# N``) are not
assumed to prove equivalence.  A later canonicalization step will only merge
forms when an explicit saved relation or mapping supports it.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    ALT_ROOT,
    FAMILY,
    PROJECT,
)

FINAL_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
OUTPUT_JSON = PROJECT / "q01_kira_symmetry_metadata_probe.json"
OUTPUT_TXT = PROJECT / "q01_kira_symmetry_metadata_probe.txt"

# Kira output names vary by version/configuration.  Search conservatively for
# likely metadata names rather than assuming one fixed directory layout.
NAME_KEYWORDS = (
    "symmetr",
    "mapping",
    "sector",
    "master",
    "prefer",
    "canonical",
    "relation",
    "equiv",
    "unique",
)
TEXT_SUFFIXES = {
    "",
    ".txt",
    ".log",
    ".yaml",
    ".yml",
    ".json",
    ".inc",
    ".dat",
    ".map",
    ".list",
    ".final",
}
MAX_SCAN_BYTES = 32 * 1024 * 1024
_MASTER_FORM_RE = re.compile(
    rf"{re.escape(FAMILY)}[\[(](?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})[\])]")

IndexTuple = tuple[int, ...]


def _indices(text: str) -> IndexTuple:
    values = tuple(int(part.strip()) for part in text.split(","))
    if len(values) != 12:
        raise ValueError(f"expected 12 indices, got {len(values)}")
    return values


def _integral_text(values: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in values)}]"


def _load_final_basis() -> tuple[IndexTuple, ...]:
    if not FINAL_JSON.exists():
        raise SystemExit(f"ERROR: finalized Q01 master-basis JSON not found: {FINAL_JSON}")
    data = json.loads(FINAL_JSON.read_text(encoding="utf-8"))
    rows = data.get("basis_terms", [])
    if not isinstance(rows, list) or not rows:
        raise SystemExit("ERROR: finalized Q01 master-basis JSON has no basis_terms")
    basis: list[IndexTuple] = []
    for row in rows:
        raw = row.get("indices") if isinstance(row, dict) else None
        if not isinstance(raw, list) or len(raw) != 12:
            raise SystemExit(f"ERROR: malformed finalized basis row: {row!r}")
        basis.append(tuple(int(v) for v in raw))
    if len(basis) != len(set(basis)):
        raise SystemExit("ERROR: finalized Q01 master basis contains duplicate forms")
    return tuple(basis)


def _is_candidate(path: Path) -> bool:
    name = path.name.lower()
    if any(keyword in name for keyword in NAME_KEYWORDS):
        return True
    # Kira result/config files can have generic names; include modest text files
    # under the FireFly result tree for content-level inspection.
    try:
        relative = path.relative_to(ALT_ROOT)
    except ValueError:
        return False
    return "results" in relative.parts and path.suffix.lower() in TEXT_SUFFIXES


def _read_text(path: Path) -> str | None:
    try:
        size = path.stat().st_size
    except OSError:
        return None
    if size > MAX_SCAN_BYTES:
        return None
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw[:8192]:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return raw.decode("latin-1")
        except UnicodeDecodeError:
            return None


def _sector_signature(indices: IndexTuple) -> tuple[int, ...]:
    return tuple(i + 1 for i, value in enumerate(indices) if value > 0)


def main() -> None:
    print("QEDCalc Q01 Kira symmetry/canonicalization metadata probe")
    print("mode: saved artifacts only; no Kira/FireFly/projected-trace recomputation")
    print("project:", PROJECT)

    basis = _load_final_basis()
    basis_set = set(basis)
    print("final projected-amplitude master forms:", len(basis))

    files: list[Path] = []
    if not PROJECT.exists():
        raise SystemExit(f"ERROR: Q01 Kira project not found: {PROJECT}")
    for path in PROJECT.rglob("*"):
        if path.is_file() and _is_candidate(path):
            files.append(path)
    files = sorted(set(files))

    candidate_rows: list[dict[str, object]] = []
    form_occurrences: dict[IndexTuple, list[dict[str, object]]] = defaultdict(list)
    relation_like_lines: list[dict[str, object]] = []
    keyword_hits: Counter[str] = Counter()
    scanned_text_files = 0

    for path in files:
        text = _read_text(path)
        relative = str(path.relative_to(PROJECT))
        row: dict[str, object] = {
            "path": relative,
            "size": path.stat().st_size,
            "text_scanned": text is not None,
        }
        if text is None:
            candidate_rows.append(row)
            continue
        scanned_text_files += 1
        lowered = text.lower()
        hits = [keyword for keyword in NAME_KEYWORDS if keyword in lowered]
        row["content_keywords"] = hits
        for keyword in hits:
            keyword_hits[keyword] += 1

        matched_basis: set[IndexTuple] = set()
        for match in _MASTER_FORM_RE.finditer(text):
            key = _indices(match.group("args"))
            if key in basis_set:
                matched_basis.add(key)
        row["final_basis_forms_mentioned"] = len(matched_basis)

        if matched_basis:
            # Record a bounded set of actual line contexts for each form.
            for line_no, line in enumerate(text.splitlines(), 1):
                if FAMILY not in line:
                    continue
                local_forms = {
                    _indices(match.group("args"))
                    for match in _MASTER_FORM_RE.finditer(line)
                } & basis_set
                for key in local_forms:
                    if len(form_occurrences[key]) < 12:
                        form_occurrences[key].append(
                            {"path": relative, "line": line_no, "text": line.strip()[:600]}
                        )
                # A line containing two or more final-basis forms is especially
                # interesting because it may encode a mapping/relation.
                if len(local_forms) >= 2 and len(relation_like_lines) < 200:
                    relation_like_lines.append(
                        {
                            "path": relative,
                            "line": line_no,
                            "forms": [_integral_text(v) for v in sorted(local_forms)],
                            "text": line.strip()[:1200],
                        }
                    )
        candidate_rows.append(row)

    sector_groups: dict[tuple[int, ...], list[IndexTuple]] = defaultdict(list)
    for key in basis:
        sector_groups[_sector_signature(key)].append(key)
    multi_form_sector_groups = {
        sector: forms for sector, forms in sector_groups.items() if len(forms) > 1
    }

    forms_with_evidence = {key for key, occurrences in form_occurrences.items() if occurrences}
    forms_without_evidence = sorted(basis_set - forms_with_evidence)

    likely_symmetry_files = [
        row for row in candidate_rows
        if any(
            keyword in str(row["path"]).lower()
            for keyword in ("symmetr", "mapping", "canonical", "equiv", "relation")
        )
        or any(
            keyword in row.get("content_keywords", [])
            for keyword in ("symmetr", "mapping", "canonical", "equiv", "relation")
        )
    ]

    summary = {
        "mode": "saved Kira metadata discovery; no recomputation",
        "project": str(PROJECT),
        "final_master_forms": len(basis),
        "candidate_files": len(candidate_rows),
        "scanned_text_files": scanned_text_files,
        "likely_symmetry_metadata_files": len(likely_symmetry_files),
        "content_keyword_file_counts": dict(sorted(keyword_hits.items())),
        "forms_mentioned_in_candidate_metadata": len(forms_with_evidence),
        "forms_without_candidate_metadata_mentions": [
            _integral_text(v) for v in forms_without_evidence
        ],
        "relation_like_lines_with_multiple_final_forms": len(relation_like_lines),
        "distinct_positive_sector_signatures": len(sector_groups),
        "multi_form_positive_sector_groups": len(multi_form_sector_groups),
        "sector_groups": [
            {
                "positive_indices": list(sector),
                "count": len(forms),
                "forms": [_integral_text(v) for v in sorted(forms)],
            }
            for sector, forms in sorted(sector_groups.items())
        ],
        "likely_symmetry_files": likely_symmetry_files[:100],
        "candidate_files_detail": candidate_rows[:300],
        "relation_like_lines": relation_like_lines,
        "form_occurrences": {
            _integral_text(key): occurrences
            for key, occurrences in sorted(form_occurrences.items())
        },
        "pass": bool(basis) and bool(candidate_rows),
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 Kira symmetry/canonicalization metadata probe",
        "",
        f"final master forms: {len(basis)}",
        f"candidate metadata/result files: {len(candidate_rows)}",
        f"scanned text files: {scanned_text_files}",
        f"likely symmetry/canonicalization files: {len(likely_symmetry_files)}",
        f"final forms mentioned in candidate metadata: {len(forms_with_evidence)}",
        f"relation-like lines containing >=2 final forms: {len(relation_like_lines)}",
        f"distinct positive-sector signatures: {len(sector_groups)}",
        f"multi-form positive-sector groups: {len(multi_form_sector_groups)}",
        "",
        "Likely symmetry/canonicalization files:",
    ]
    for row in likely_symmetry_files[:40]:
        lines.append(f"  {row['path']}  size={row['size']}")
    lines.extend(["", "Relation-like line samples:"])
    for row in relation_like_lines[:30]:
        lines.append(f"  {row['path']}:{row['line']}  {row['text']}")
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("candidate metadata/result files:", len(candidate_rows))
    print("scanned text files:", scanned_text_files)
    print("likely symmetry/canonicalization files:", len(likely_symmetry_files))
    print("final forms mentioned in candidate metadata:", len(forms_with_evidence))
    print("relation-like lines containing >=2 final forms:", len(relation_like_lines))
    print("distinct positive-sector signatures:", len(sector_groups))
    print("multi-form positive-sector groups:", len(multi_form_sector_groups))
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)
    if likely_symmetry_files:
        print("likely metadata files:")
        for row in likely_symmetry_files[:12]:
            print("  ", row["path"], "size=", row["size"])
    if relation_like_lines:
        print("relation-like samples:")
        for row in relation_like_lines[:8]:
            print(f"  {row['path']}:{row['line']}: {row['text']}")

    if not summary["pass"]:
        raise SystemExit("Q01 Kira symmetry/canonicalization metadata probe FAIL")
    print("Q01 Kira symmetry/canonicalization metadata probe PASS")


if __name__ == "__main__":
    main()
