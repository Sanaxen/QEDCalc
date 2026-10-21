"""Read-only audit of multi-term SYSTEM relations involving VP05 small target IDs.

This is a structural incidence audit, NOT a solved equality or exponent alias.
Exact raw coefficients and provenance are retained in JSON.
"""
from __future__ import annotations

import argparse
import gzip
import json
from collections import Counter, defaultdict, deque
from pathlib import Path

from examples.three_loop_sector203_l2_witness_subset import DEFAULT

TARGETS = ((10, 203), (6, 203), (5, 201))


def read_rows(project):
    rows = []
    for path in sorted((project / "tmp" / "VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            while marker := stream.readline():
                if marker.strip() != "Eq":
                    raise ValueError(f"Unexpected marker in {path}")
                head = stream.readline().strip()
                n = int(stream.readline().strip())
                terms = []
                for _ in range(n):
                    fields = stream.readline().split()
                    if len(fields) < 4:
                        raise ValueError(f"Malformed term in {path}, head {head}")
                    terms.append({"key": [int(fields[2]), int(fields[3])], "coefficient": fields[1]})
                rows.append({"file": path.name, "equation_id": head, "term_count": n, "terms": terms})
    if len(rows) != 2678:
        raise ValueError(f"Expected 2678 SYSTEM rows, got {len(rows)}")
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=DEFAULT)
    parser.add_argument("--output", type=Path, default=Path(
        "output/three_loop_integral_family_audit/vp05_small_id_multiterm_scope.json"))
    args = parser.parse_args()
    rows = read_rows(args.project)
    incidence = defaultdict(list)
    for i, row in enumerate(rows):
        for key in {tuple(t["key"]) for t in row["terms"]}:
            incidence[key].append(i)

    targets = []
    for target in TARGETS:
        indices = incidence.get(target, [])
        direct = [rows[i] for i in indices]
        histogram = Counter(str(r["term_count"]) for r in direct)
        small_neighbours = Counter()
        for row in direct:
            for t in row["terms"]:
                key = tuple(t["key"])
                if key != target and 1 <= key[0] <= 10:
                    small_neighbours[key] += 1
        # Traverse the variable-equation bipartite graph. Edges signify co-occurrence only.
        visited_vars = {target}
        visited_rows = set()
        queue = deque([(target, 0)])
        distance_counts = Counter()
        while queue:
            var, depth = queue.popleft()
            if depth >= 2:
                continue
            for i in incidence.get(var, []):
                if i in visited_rows:
                    continue
                visited_rows.add(i)
                distance_counts[depth + 1] += 1
                for term in rows[i]["terms"]:
                    key = tuple(term["key"])
                    if key not in visited_vars:
                        visited_vars.add(key)
                        queue.append((key, depth + 1))
        targets.append({
            "key": list(target),
            "direct_row_count": len(direct),
            "direct_term_count_histogram": dict(sorted(histogram.items(), key=lambda x: int(x[0]))),
            "direct_small_neighbours": [
                {"key": list(k), "cooccurring_rows": n}
                for k, n in sorted(small_neighbours.items())
            ],
            "direct_rows": direct,
            "connected_rows_within_two_variable_hops": len(visited_rows),
            "connected_variables_within_two_variable_hops": len(visited_vars),
            "connected_rows_by_hop": dict(sorted(distance_counts.items())),
        })
    result = {
        "project": str(args.project.resolve()),
        "system_equations": len(rows),
        "target_results": targets,
        "alias_mapping_verified": False,
        "linear_elimination_performed": False,
        "warning": "Co-occurrence, even through multiple equations, is NOT an exact alias, reduction, or proof of target row-space membership. Rows retain unparsed original coefficient strings.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("VP05_SMALL_ID_MULTITERM_SCOPE " + json.dumps({
        "system_equations": len(rows),
        "targets": [{k: v for k, v in t.items() if k != "direct_rows"} for t in targets],
        "alias_mapping_verified": False,
        "linear_elimination_performed": False,
        "output": str(args.output),
    }), flush=True)


if __name__ == "__main__":
    main()
