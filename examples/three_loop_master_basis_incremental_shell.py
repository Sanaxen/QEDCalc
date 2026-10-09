"""Enumerate the incremental r/s/d shell between two Kira seed envelopes.

This is a diagnostic/preparation tool for resource-blocked master-basis closure.
It does not run Kira.  It enumerates integral index tuples in selected sectors
under the same r/s/d complexity convention used by QEDCalc and reports only the
new points admitted by the stronger seed but not by the weaker seed.

For the VP05 blockage the intended comparison is:
    r8s5d2 -> r8s6d2
so the output is the newly added s=6 shell.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from three_loop.integral_family_classification import ROOT
from three_loop.master_basis_api import Seed, build_family_spec, integral_complexity
from examples.three_loop_master_basis_candidate_closure import AUDIT_DIR, _parse_seed


def _subsectors(top_sector: int) -> list[int]:
    bits = [i for i in range(12) if top_sector & (1 << i)]
    out = []
    for mask in range(1, 1 << len(bits)):
        sector = 0
        for j, bit in enumerate(bits):
            if mask & (1 << j):
                sector |= 1 << bit
        out.append(sector)
    return sorted(out)


def _positive_compositions(total: int, n: int):
    if n == 0:
        if total == 0:
            yield ()
        return
    if total < n:
        return
    for cuts in itertools.combinations(range(1, total), n - 1):
        prev = 0
        vals = []
        for c in (*cuts, total):
            vals.append(c - prev)
            prev = c
        yield tuple(vals)


def _negative_distributions(total: int, n: int):
    if n == 0:
        if total == 0:
            yield ()
        return
    # weak compositions of total into n slots
    for bars in itertools.combinations(range(total + n - 1), n - 1):
        prev = -1
        vals = []
        for b in (*bars, total + n - 1):
            vals.append(b - prev - 1)
            prev = b
        yield tuple(vals)


def _enumerate_sector(family: str, sector: int, seed: Seed):
    pos = [i for i in range(12) if sector & (1 << i)]
    neg = [i for i in range(12) if i not in pos]
    npos = len(pos)

    # Positive powers sum to r. d = sum(a_i-1) = r - npos.
    # Hence d is fixed by r and the sector line count.
    for r in range(npos, seed.r + 1):
        d = r - npos
        if d > seed.d:
            continue
        for pvals in _positive_compositions(r, npos):
            for s in range(0, seed.s + 1):
                for nvals in _negative_distributions(s, len(neg)):
                    idx = [0] * 12
                    for i, value in zip(pos, pvals):
                        idx[i] = value
                    for i, value in zip(neg, nvals):
                        idx[i] = -value
                    yield f"{family}[{','.join(str(x) for x in idx)}]"


def _new_shell(family: str, sector: int, weak: Seed, strong: Seed) -> list[str]:
    weak_set = set(_enumerate_sector(family, sector, weak))
    return sorted(set(_enumerate_sector(family, sector, strong)) - weak_set)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--from-seed", required=True, type=_parse_seed)
    p.add_argument("--to-seed", required=True, type=_parse_seed)
    p.add_argument("--top-sector", required=True, type=int)
    p.add_argument("--include-subsectors", action="store_true")
    args = p.parse_args()

    spec = build_family_spec(args.family)
    sectors = (
        _subsectors(args.top_sector)
        if args.include_subsectors
        else [args.top_sector]
    )

    rows = []
    total = 0
    for sector in sectors:
        shell = _new_shell(spec.family_id, sector, args.from_seed, args.to_seed)
        if not shell:
            continue
        rows.append({
            "sector": sector,
            "count": len(shell),
            "integrals": shell,
        })
        total += len(shell)

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    stem = (
        f"three_loop_{spec.family_id.lower()}_incremental_shell_"
        f"{args.from_seed.tag}_to_{args.to_seed.tag}_top{args.top_sector}"
    )
    out_json = AUDIT_DIR / f"{stem}.json"
    out_txt = AUDIT_DIR / f"{stem}.txt"
    payload = {
        "schema_version": 1,
        "stage": "master_basis_incremental_shell",
        "family": spec.family_id,
        "from_seed": args.from_seed.tag,
        "to_seed": args.to_seed.tag,
        "top_sector": args.top_sector,
        "include_subsectors": args.include_subsectors,
        "sector_count_with_new_integrals": len(rows),
        "new_integral_count": total,
        "rows": rows,
    }
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")

    lines = [
        "QEDCalc incremental seed-shell audit",
        f"family: {spec.family_id}",
        f"from seed: {args.from_seed.tag}",
        f"to seed: {args.to_seed.tag}",
        f"top sector: {args.top_sector}",
        f"include subsectors: {args.include_subsectors}",
        f"sectors with new integrals: {len(rows)}",
        f"new integrals total: {total}",
    ]
    for row in rows:
        lines.append(f"sector {row['sector']}: {row['count']} new integrals")
    lines.extend([
        f"audit JSON: {out_json}",
        f"audit TXT: {out_txt}",
    ])
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
