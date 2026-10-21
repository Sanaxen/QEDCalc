"""Finite-field target row-space membership for saved VP05 witness equations.

No Kira or Fermat execution, no symbolic proof. Integral aliases must be
verified against the actual witness column encoding before conclusions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from examples.three_loop_sector203_fermat_probe import FOLDER
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows, order

POINTS = ((1000037, 21, 15), (1000081, 25, 23), (1000117, 29, 31))
DEFAULT_TERMS = ((10, 203, "z"), (6, 203, "-2"), (5, 201, "2"))


def residue(expr, p, z, d):
    if expr == "z":
        return z % p
    if expr == "-2":
        return (-2) % p
    if expr == "2":
        return 2 % p
    raise ValueError("Only audited target coefficients z,-2,2 are supported")


def eliminate(rows, target, p):
    """Reduce target against row-echelon basis, tracking independent row IDs.

    This is finite-field row-space membership, not a rational-function proof.
    """
    basis = {}
    owners = {}
    ranks = 0
    target_appearing_rows = set()
    target_keys = set(target)
    for i, original in enumerate(rows):
        if target_keys.intersection(original):
            target_appearing_rows.add(i)
        vec = original.copy()
        combo = {i: 1}
        while vec:
            lead = min(vec, key=order)
            if lead not in basis:
                inv = pow(vec[lead], -1, p)
                basis[lead] = {k: v * inv % p for k, v in vec.items()}
                # Avoid keeping full row provenance: may explode at 528 rows.
                owners[lead] = i
                ranks += 1
                break
            fac = vec[lead]
            for k, value in basis[lead].items():
                val = (vec.get(k, 0) - fac * value) % p
                if val: vec[k] = val
                else: vec.pop(k, None)
    original_target = target.copy()
    target_ops = []
    while target:
        lead = min(target, key=order)
        if lead not in basis:
            break
        fac = target[lead]
        target_ops.append({"owner": owners[lead], "pivot": list(lead)})
        for k, v in basis[lead].items():
            val = (target.get(k, 0) - fac * v) % p
            if val: target[k] = val
            else: target.pop(k, None)
    return {"rank": ranks, "target_in_rowspace": not target,
            "target_remainder_size": len(target),
            "target_remainder_sample": [
                {"key": list(k), "coefficient": target[k]}
                for k in sorted(target, key=order)[:8]],
            "target_elimination_steps": len(target_ops),
            "target_elimination_first_owners": target_ops[:12],
            "direct_target_support_rows": len(target_appearing_rows),
            "direct_target_support_row_ids": sorted(target_appearing_rows)[:40],
            "full_target": [{"key": list(k), "coefficient": v}
                            for k, v in original_target.items()]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--equations", type=Path)
    ap.add_argument("--rows", type=int, default=528)
    ap.add_argument("--target-term", action="append", nargs=3,
                    metavar=("KEY", "SECTOR", "COEFFICIENT"),
                    help="Override default keys for I10,I6,I5; repeated triple")
    a = ap.parse_args()
    if not 1 <= a.rows <= 528:
        ap.error("rows must be 1..528")
    files = [a.equations.resolve()] if a.equations else sorted(
        FOLDER.glob("vp05_candidate4_witness_*.equations.json"))
    if not files:
        ap.error("Witness equations JSON not found")
    path = files[-1]
    rows = json.loads(path.read_text(encoding="utf-8-sig"))["rows"][:a.rows]
    columns = {tuple(t["key"]) for row in rows for t in row["terms"]}
    terms = [(int(k), int(sec), value) for k, sec, value in a.target_term] if a.target_term else DEFAULT_TERMS
    keys = {(k, sector) for k, sector, _ in terms}
    if len(keys) != len(terms):
        ap.error("Target keys must be distinct")
    absent = sorted(keys - columns)
    print("TARGET_ROWSPACE_INPUT " + json.dumps({
        "rows": len(rows), "columns": len(columns),
        "keys": [{"key": [k, sec], "coefficient": v,
                  "present_in_witness_columns": (k, sec) in columns}
                 for k, sec, v in terms],
        "source": str(path),
        "alias_mapping_verified": False,
        "proof": False}), flush=True)
    if absent:
        print("TARGET_ROWSPACE_BLOCKED " + json.dumps({
            "reason": "target aliases absent from this equation encoding",
            "missing_keys": [list(k) for k in absent],
            "next": "Resolve key mapping against witness metadata; do not interpret missing keys as independent integrals",
            "proof": False}), flush=True)
        return
    for p, z, d in POINTS:
        try:
            matrix = mod_rows(rows, p, z, d)
            target = {(k, sec): residue(v, p, z, d) for k, sec, v in terms}
            target = {k: v for k, v in target.items() if v}
            result = eliminate(matrix, target, p)
        except (ZeroDivisionError, ValueError) as exc:
            print("TARGET_ROWSPACE_POINT_ERROR " + json.dumps({
                "point": [p, z, d], "error": str(exc)}), flush=True)
            continue
        result.update({"point": [p, z, d], "proof": False})
        print("TARGET_ROWSPACE_POINT " + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
