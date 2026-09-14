"""Conservatively prove Q01 master-form equivalences from Kira sector mappings.

This helper reads the saved ``sectorRelations`` and ``sectorSymmetries`` files
from the completed FireFly Kira project and applies only the explicit propagator
index maps encoded after Kira's two ``{place==holder}`` tokens.

It deliberately ignores FORM ``Fac(...)`` relations and refuses any mapping for
which a non-zero source exponent has no explicit target propagator or for which
multiple source propagators collide on one target.  Therefore every reported
edge is a conservative pure index-permutation equivalence candidate suitable
for subsequent coefficient-combination checks; absence of an edge does not
mean two forms are inequivalent.
"""
from __future__ import annotations

from collections import defaultdict, deque
import json
from pathlib import Path

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    ALT_ROOT,
    FAMILY,
    PROJECT,
)

MASTER_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
OUTPUT_JSON = PROJECT / "q01_kira_sector_permutation_equivalence_probe.json"
SECTOR_DIR = ALT_ROOT / "sectormappings" / FAMILY
FILES = (SECTOR_DIR / "sectorRelations", SECTOR_DIR / "sectorSymmetries")

IndexTuple = tuple[int, ...]


def _sector(indices: IndexTuple) -> int:
    value = 0
    for i, exponent in enumerate(indices):
        if exponent > 0:
            value |= 1 << i
    return value


def _integral_text(values: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in values)}]"


def _load_final_forms() -> set[IndexTuple]:
    if not MASTER_JSON.exists():
        raise SystemExit(f"ERROR: master-basis JSON not found: {MASTER_JSON}")
    data = json.loads(MASTER_JSON.read_text(encoding="utf-8"))
    forms: set[IndexTuple] = set()
    for row in data.get("basis_terms", []):
        raw = row.get("indices")
        if not isinstance(raw, list) or len(raw) != 12:
            raise SystemExit(f"ERROR: malformed basis row: {row!r}")
        forms.add(tuple(int(v) for v in raw))
    if not forms:
        raise SystemExit("ERROR: no final master forms in master-basis JSON")
    return forms


def _parse_mapping_line(line: str, *, source_file: Path, line_no: int) -> tuple[int, int, tuple[int, ...]] | None:
    text = line.strip()
    if not text:
        return None
    marker = "{place==holder} {place==holder}"
    if marker not in text:
        return None
    before, after = text.split(marker, 1)
    before_tokens = before.split()
    after_tokens = after.split()
    if len(before_tokens) < 2 or len(after_tokens) < 12:
        return None

    try:
        source_sector = int(before_tokens[0])
        # Immediately before the placeholders Kira stores: sign, target sector,
        # number-of-lines/active-count metadata, then a zero flag.  The target
        # sector is therefore the third token from the end of this prefix.
        target_sector = int(before_tokens[-3])
        mapping = tuple(int(token) for token in after_tokens[:12])
    except ValueError:
        return None

    if any(value < -1 or value >= 12 for value in mapping):
        raise SystemExit(
            f"ERROR: invalid propagator map in {source_file} line {line_no}: {mapping}"
        )
    return source_sector, target_sector, mapping


def _apply_pure_map(indices: IndexTuple, mapping: tuple[int, ...]) -> IndexTuple | None:
    out = [0] * 12
    used: set[int] = set()
    for source_pos, exponent in enumerate(indices):
        if exponent == 0:
            continue
        target_pos = mapping[source_pos]
        if target_pos < 0:
            return None
        if target_pos in used:
            return None
        used.add(target_pos)
        out[target_pos] = exponent
    return tuple(out)


def main() -> None:
    print("QEDCalc Q01 Kira sector-permutation master-form equivalence probe")
    print("mode: saved sectormapping metadata only; no Kira/FireFly recomputation")

    forms = _load_final_forms()
    print("final master forms:", len(forms))

    mappings_by_sector: dict[int, list[tuple[str, int, tuple[int, ...], int]]] = defaultdict(list)
    parsed_lines = 0
    for path in FILES:
        if not path.exists():
            raise SystemExit(f"ERROR: Kira sectormapping file not found: {path}")
        local = 0
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="strict").splitlines(), 1):
            parsed = _parse_mapping_line(line, source_file=path, line_no=line_no)
            if parsed is None:
                continue
            source_sector, target_sector, mapping = parsed
            mappings_by_sector[source_sector].append((path.name, target_sector, mapping, line_no))
            parsed_lines += 1
            local += 1
        print(f"parsed {path.name} mappings:", local)

    edges: set[tuple[IndexTuple, IndexTuple]] = set()
    edge_rows: list[dict[str, object]] = []
    rejected_no_direct_map = 0
    sector_mismatch = 0

    for source in sorted(forms):
        source_sector = _sector(source)
        for file_name, target_sector, mapping, line_no in mappings_by_sector.get(source_sector, []):
            mapped = _apply_pure_map(source, mapping)
            if mapped is None:
                rejected_no_direct_map += 1
                continue
            if _sector(mapped) != target_sector:
                sector_mismatch += 1
                continue
            if mapped not in forms or mapped == source:
                continue
            edge = tuple(sorted((source, mapped)))
            if edge in edges:
                continue
            edges.add(edge)
            edge_rows.append(
                {
                    "source": _integral_text(source),
                    "target": _integral_text(mapped),
                    "source_indices": list(source),
                    "target_indices": list(mapped),
                    "source_sector": source_sector,
                    "target_sector": target_sector,
                    "mapping_file": file_name,
                    "mapping_line": line_no,
                    "propagator_map_zero_based": list(mapping),
                }
            )

    adjacency: dict[IndexTuple, set[IndexTuple]] = defaultdict(set)
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)

    components: list[list[IndexTuple]] = []
    seen: set[IndexTuple] = set()
    for start in sorted(forms):
        if start in seen or start not in adjacency:
            continue
        queue = deque([start])
        seen.add(start)
        component: list[IndexTuple] = []
        while queue:
            node = queue.popleft()
            component.append(node)
            for nxt in sorted(adjacency[node]):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        if len(component) > 1:
            components.append(sorted(component))

    covered = set().union(*(set(c) for c in components)) if components else set()
    canonical_count_if_merged = len(forms) - sum(len(c) - 1 for c in components)

    summary = {
        "mode": "conservative pure propagator-index permutation audit from saved Kira sectormappings",
        "final_master_forms": len(forms),
        "parsed_mapping_lines": parsed_lines,
        "candidate_equivalence_edges": len(edges),
        "nontrivial_equivalence_components": len(components),
        "forms_in_nontrivial_components": len(covered),
        "canonical_form_count_if_only_proven_edges_are_merged": canonical_count_if_merged,
        "rejected_mappings_without_direct_nonzero_index_map": rejected_no_direct_map,
        "sector_mismatch_after_mapping": sector_mismatch,
        "edges": edge_rows,
        "components": [
            [_integral_text(value) for value in component]
            for component in components
        ],
        "pass": parsed_lines > 0 and sector_mismatch == 0,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("parsed mapping lines:", parsed_lines)
    print("candidate proven permutation edges:", len(edges))
    print("nontrivial equivalence components:", len(components))
    print("forms in nontrivial components:", len(covered))
    print("canonical count if only proven edges are merged:", canonical_count_if_merged)
    print("mappings rejected because a nonzero index had no direct target:", rejected_no_direct_map)
    print("sector mismatches after mapping:", sector_mismatch)
    print("probe JSON:", OUTPUT_JSON)

    for i, component in enumerate(components[:12], 1):
        print(f"component {i} size={len(component)}")
        for value in component:
            print("  ", _integral_text(value))

    if not summary["pass"]:
        raise SystemExit("Q01 Kira sector-permutation master-form equivalence probe FAIL")
    print("Q01 Kira sector-permutation master-form equivalence probe PASS")


if __name__ == "__main__":
    main()
