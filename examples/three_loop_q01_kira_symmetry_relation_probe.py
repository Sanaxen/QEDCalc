"""Probe saved Kira symmetry/relation FORM files for Q01 master-form mappings.

This helper performs no Kira, FireFly, or projected-trace computation.  It reads
saved ``sectormappings/Q01_full`` metadata and the finalized projected-amplitude
master-form basis, then extracts FORM statements that mention one or more final
master forms.  Statements mentioning two or more final forms are reported as
candidate symmetry/canonicalization relations.

The probe is deliberately conservative: it does not yet merge basis forms.  It
only records exact saved statements that can justify a later canonicalization
step.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    FAMILY,
    PROJECT,
)

FINAL_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
OUTPUT_JSON = PROJECT / "q01_kira_symmetry_relation_probe.json"

# Prefer the completed FireFly tree, then fall back to the earlier exact944 tree.
MAPPING_ROOTS = (
    PROJECT / "exact944closure1_firefly" / "sectormappings" / FAMILY,
    PROJECT / "exact944closure1" / "sectormappings" / FAMILY,
    PROJECT / "exact944" / "sectormappings" / FAMILY,
)
CANDIDATE_NAMES = (
    "relations.frm",
    "symmetries.frm",
    "relations",
    "symmetries",
    "sectorRelations",
    "sectorSymmetries",
)

# Kira metadata may use square brackets or FORM parentheses.
_INTEGRAL_ANY_RE = re.compile(
    rf"{re.escape(FAMILY)}\s*[\[(](?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})[\])]"
)

IndexTuple = tuple[int, ...]


def _indices(text: str) -> IndexTuple:
    values = tuple(int(part.strip()) for part in text.split(","))
    if len(values) != 12:
        raise ValueError(f"expected 12 indices, got {len(values)}")
    return values


def _integral_text(values: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in values)}]"


def _load_final_basis() -> set[IndexTuple]:
    if not FINAL_JSON.exists():
        raise SystemExit(f"ERROR: final Q01 master-basis JSON not found: {FINAL_JSON}")
    data = json.loads(FINAL_JSON.read_text(encoding="utf-8"))
    rows = data.get("basis_terms", [])
    basis: set[IndexTuple] = set()
    for row in rows:
        raw = row.get("indices")
        if not isinstance(raw, list) or len(raw) != 12:
            raise SystemExit(f"ERROR: malformed basis row: {row!r}")
        basis.add(tuple(int(v) for v in raw))
    if not basis:
        raise SystemExit("ERROR: final Q01 master basis is empty")
    return basis


def _choose_mapping_root() -> Path:
    for root in MAPPING_ROOTS:
        if root.is_dir():
            return root
    raise SystemExit(
        "ERROR: no saved Q01 sectormappings directory found; checked: "
        + ", ".join(str(v) for v in MAPPING_ROOTS)
    )


def _iter_statements(path: Path):
    """Yield semicolon statements when possible, otherwise physical lines."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if ";" in text:
        for part in text.split(";"):
            statement = part.strip()
            if statement:
                yield statement + ";"
    else:
        for raw in text.splitlines():
            line = raw.strip()
            if line:
                yield line


def main() -> None:
    print("QEDCalc Q01 Kira symmetry/relation master-form probe")
    print("mode: saved metadata only; no Kira/FireFly/projected-trace recomputation")

    basis = _load_final_basis()
    root = _choose_mapping_root()
    files = [root / name for name in CANDIDATE_NAMES if (root / name).is_file()]
    if not files:
        raise SystemExit(f"ERROR: no relation/symmetry metadata files found under {root}")

    statements_with_basis: list[dict[str, object]] = []
    multi_basis_statements: list[dict[str, object]] = []
    mentioned_basis: set[IndexTuple] = set()
    pair_edges: set[tuple[IndexTuple, IndexTuple]] = set()

    for path in files:
        for statement in _iter_statements(path):
            matches = []
            for match in _INTEGRAL_ANY_RE.finditer(statement):
                try:
                    key = _indices(match.group("args"))
                except ValueError:
                    continue
                if key in basis:
                    matches.append(key)
            unique = tuple(dict.fromkeys(matches))
            if not unique:
                continue
            mentioned_basis.update(unique)
            row = {
                "file": str(path.relative_to(PROJECT)),
                "basis_forms": [_integral_text(v) for v in unique],
                "statement": statement[:4000],
            }
            statements_with_basis.append(row)
            if len(unique) >= 2:
                multi_basis_statements.append(row)
                for i, left in enumerate(unique):
                    for right in unique[i + 1 :]:
                        edge = tuple(sorted((left, right)))
                        pair_edges.add(edge)

    missing = sorted(basis - mentioned_basis)

    # Connected components are only candidate relation clusters at this stage.
    adjacency: dict[IndexTuple, set[IndexTuple]] = {v: set() for v in basis}
    for left, right in pair_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen: set[IndexTuple] = set()
    components: list[list[IndexTuple]] = []
    for start in sorted(basis):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        component: list[IndexTuple] = []
        while stack:
            node = stack.pop()
            component.append(node)
            for child in adjacency[node]:
                if child not in seen:
                    seen.add(child)
                    stack.append(child)
        components.append(sorted(component))

    nontrivial_components = [c for c in components if len(c) > 1]
    summary = {
        "mode": "saved Kira symmetry/relation metadata probe; no recomputation",
        "mapping_root": str(root),
        "candidate_files": [str(v.relative_to(PROJECT)) for v in files],
        "final_master_forms": len(basis),
        "master_forms_mentioned_in_metadata": len(mentioned_basis),
        "master_forms_missing_from_metadata": [_integral_text(v) for v in missing],
        "statements_mentioning_final_forms": len(statements_with_basis),
        "statements_mentioning_multiple_final_forms": len(multi_basis_statements),
        "candidate_pair_edges": len(pair_edges),
        "candidate_relation_components": [
            [_integral_text(v) for v in comp] for comp in nontrivial_components
        ],
        "candidate_relation_component_count": len(nontrivial_components),
        "samples": multi_basis_statements[:30],
        "pass": len(basis) > 0 and len(files) > 0,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("mapping root:", root)
    print("final master forms:", len(basis))
    print("candidate metadata files:", len(files))
    for path in files:
        print("  ", path.relative_to(PROJECT), "size=", path.stat().st_size)
    print("master forms mentioned in metadata:", len(mentioned_basis))
    print("master forms missing from metadata:", len(missing))
    print("statements mentioning final forms:", len(statements_with_basis))
    print("relation-like statements with >=2 final forms:", len(multi_basis_statements))
    print("candidate pair edges:", len(pair_edges))
    print("candidate nontrivial relation components:", len(nontrivial_components))
    print("probe JSON:", OUTPUT_JSON)

    if nontrivial_components:
        print("candidate relation components:")
        for comp in nontrivial_components[:12]:
            print("  component size", len(comp))
            for value in comp[:12]:
                print("    ", _integral_text(value))
    if multi_basis_statements:
        print("relation-like samples:")
        for row in multi_basis_statements[:8]:
            print("  file:", row["file"])
            print("  forms:", row["basis_forms"])
            text = str(row["statement"]).replace("\n", " ")
            print("  statement:", text[:700])

    if not summary["pass"]:
        raise SystemExit("Q01 Kira symmetry/relation master-form probe FAIL")
    print("Q01 Kira symmetry/relation master-form probe PASS")


if __name__ == "__main__":
    main()
