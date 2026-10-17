"""Extract sampled sector203 candidate-4 reductions from saved Kira l2 SYSTEM equations.

Read-only, finite-field *samples*, not exact symbolic IBP coefficients.
The ten short weight aliases are verified against the preferredMasters file
using the positional mapping found in PyRed source. Never invokes Kira.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from examples.three_loop_sector203_ffrank_audit import equations
from examples.three_loop_sector203_weight_audit import ROOT, parse_file_integrals

DEFAULT = ROOT / "output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734"
POINTS = ((17, 7), (29, 11), (37, 13))
PRIME = 1000003


def sector(indices):
    return sum(1 << i for i, a in enumerate(indices) if a > 0)


def insert_reduced(row, pivots, p, masters):
    """Eliminate all nonmaster pivot columns first, preserving master variables."""
    v = {k: x % p for k, x in row.items() if x % p}
    order = lambda k: (k in masters, k[0], k[1])
    while v:
        lead = min(v, key=order)
        existing = pivots.get(lead)
        if existing is None:
            inv = pow(v[lead], -1, p)
            pivots[lead] = {k: x * inv % p for k, x in v.items()}
            return True
        factor = v[lead]
        for k, x in existing.items():
            value = (v.get(k, 0) - factor * x) % p
            if value:
                v[k] = value
            else:
                v.pop(k, None)
        if len(v) > 25000:
            raise RuntimeError("Sparse fill too large; stopped without result")
    return False


def reduce_vector(row, pivots, p, masters):
    v = {k: x % p for k, x in row.items() if x % p}
    order = lambda k: (k in masters, k[0], k[1])
    while v:
        lead = min(v, key=order)
        if lead not in pivots:
            break
        factor = v[lead]
        for k, x in pivots[lead].items():
            value = (v.get(k, 0) - factor * x) % p
            if value:
                v[k] = value
            else:
                v.pop(k, None)
    return v


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=DEFAULT)
    parser.add_argument("--points", type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args()
    project = args.project.resolve()
    preferred = parse_file_integrals(project / "results/preferredMasters")
    selected = parse_file_integrals(project / "results/VP05_full/masters")
    if len(preferred) != 10 or len(selected) != 5 or len(set(preferred)) != 10:
        parser.error("Unexpected preferred/selected masters; cannot use short ID mapping")
    by_id = {integral: (i + 1, sector(integral)) for i, integral in enumerate(preferred)}
    try:
        master_keys = {by_id[i] for i in selected}
    except KeyError:
        parser.error("A selected master was not in preferredMasters")
    if len(master_keys) != 5 or sorted(k[0] for k in master_keys) != [5, 6, 7, 8, 9]:
        parser.error("Unexpected preferred aliases for the five selected masters")
    target = preferred[9]
    target_key = by_id[target]
    assert target_key == (10, 203)
    files = sorted((project / "tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    if len(files) != 14:
        parser.error("Expected 14 saved SYSTEM files")
    print("ALIASES " + json.dumps({
        "target": "VP05_full[" + ",".join(map(str, target)) + "]",
        "target_key": target_key,
        "masters": [
            {"key": by_id[x], "integral": "VP05_full[" + ",".join(map(str, x)) + "]"}
            for x in selected
        ]}, ensure_ascii=False), flush=True)
    for z, d in POINTS[:args.points]:
        pivots = {}
        rowcount = 0
        for file in files:
            for row in equations(file, PRIME, z, d):
                rowcount += 1
                insert_reduced(row, pivots, PRIME, master_keys)
        if rowcount != 2678 or len(pivots) != 2678:
            raise RuntimeError(f"Unexpected equation count/rank {rowcount}/{len(pivots)}")
        if any(k in pivots for k in master_keys):
            raise RuntimeError("A selected master became a pivot: cannot extract coefficients")
        remainder = reduce_vector({target_key: 1}, pivots, PRIME, master_keys)
        if any(k not in master_keys for k in remainder):
            raise RuntimeError(f"Target has nonmaster residual terms: {len(remainder)}")
        data = {
            "prime": PRIME, "z": z, "d": d,
            "equations": rowcount, "rank": len(pivots),
            "candidate4_reducible": True,
            "coefficients_mod_p": [
                {"master_key": by_id[x],
                 "coefficient_mod_p": (-remainder.get(by_id[x], 0)) % PRIME,
                 "coefficient_symmetric": (
                     ((-remainder.get(by_id[x], 0)) % PRIME + PRIME // 2) % PRIME - PRIME // 2
                 )}
                for x in selected
            ],
            "limitation": "Numeric finite-field evaluation only, not a symbolic identity or global master basis proof."
        }
        print("REDUCTION_POINT " + json.dumps(data, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
