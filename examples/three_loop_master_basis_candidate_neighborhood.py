"""Candidate-centered incremental-shell neighborhood audit.

This diagnostic narrows a huge stronger-seed shell to integrals close in index
space to one refined candidate.  It does NOT claim an IBP proof by itself.

Distance is the L1 norm of the 12 propagator-index difference vectors.  Radius 1
captures single-index shifts; radius 2 also captures the common +e_i-e_j style
moves appearing after rewriting IBP numerators into propagators.

The output is intended to size the next exact IBP relation generator.
"""
from __future__ import annotations

import argparse
import json

from three_loop.master_basis_api import parse_integral
from examples.three_loop_master_basis_candidate_closure import (
    AUDIT_DIR,
    _parse_seed,
    _resolve,
)
from examples.three_loop_master_basis_candidate_sector_closure import _sector
from examples.three_loop_master_basis_incremental_shell import (
    _new_shell,
    _subsectors,
)


def _l1(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    return sum(abs(x - y) for x, y in zip(a, b))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--baseline-seed", type=_parse_seed)
    p.add_argument("--from-seed", required=True, type=_parse_seed)
    p.add_argument("--to-seed", required=True, type=_parse_seed)
    p.add_argument("--sector", required=True, type=int)
    p.add_argument("--radius", type=int, default=2)
    args = p.parse_args()

    (
        spec,
        baseline,
        _,
        _,
        _,
        _,
        _,
        candidate,
        _,
        closure_mode,
    ) = _resolve(
        argparse.Namespace(
            family=args.family,
            baseline_seed=args.baseline_seed,
            solver="masters",
        )
    )
    if closure_mode != "refined-candidate-only":
        raise RuntimeError(f"expected refined-candidate-only, got {closure_mode}")

    targets = [x for x in candidate if _sector(x) == args.sector]
    if len(targets) != 1:
        raise ValueError(
            f"sector {args.sector} must contain exactly one refined candidate; "
            f"found {len(targets)}"
        )
    target = targets[0]
    _, target_idx = parse_integral(target)

    rows = []
    total_shell = 0
    total_near = 0
    for sector in _subsectors(args.sector):
        shell = _new_shell(spec.family_id, sector, args.from_seed, args.to_seed)
        if not shell:
            continue
        total_shell += len(shell)
        near = []
        for item in shell:
            _, idx = parse_integral(item)
            d = _l1(target_idx, idx)
            if d <= args.radius:
                near.append((d, item))
        if near:
            near.sort(key=lambda x: (x[0], x[1]))
            rows.append({
                "sector": sector,
                "shell_count": len(shell),
                "near_count": len(near),
                "integrals": [{"distance": d, "integral": x} for d, x in near],
            })
            total_near += len(near)

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    stem = (
        f"three_loop_{spec.family_id.lower()}_candidate_neighborhood_"
        f"{args.from_seed.tag}_to_{args.to_seed.tag}_sec{args.sector}_r{args.radius}"
    )
    out_json = AUDIT_DIR / f"{stem}.json"
    out_txt = AUDIT_DIR / f"{stem}.txt"

    payload = {
        "schema_version": 1,
        "stage": "master_basis_candidate_incremental_neighborhood",
        "family": spec.family_id,
        "baseline_seed": baseline.tag,
        "from_seed": args.from_seed.tag,
        "to_seed": args.to_seed.tag,
        "sector": args.sector,
        "radius": args.radius,
        "target": target,
        "subsector_shell_integral_count": total_shell,
        "nearby_incremental_integral_count": total_near,
        "rows": rows,
    }
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")

    lines = [
        "QEDCalc candidate-centered incremental-shell audit",
        f"family: {spec.family_id}",
        f"baseline seed: {baseline.tag}",
        f"from seed: {args.from_seed.tag}",
        f"to seed: {args.to_seed.tag}",
        f"sector: {args.sector}",
        f"radius: {args.radius}",
        f"target: {target}",
        f"subsector shell integrals total: {total_shell}",
        f"nearby incremental integrals: {total_near}",
    ]
    for row in rows:
        lines.append(
            f"sector {row['sector']}: near={row['near_count']} / shell={row['shell_count']}"
        )
    lines.extend([f"audit JSON: {out_json}", f"audit TXT: {out_txt}"])
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
