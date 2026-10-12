"""Targeted VP05-style candidate probe on a fixed-sector numerator simplex.

This diagnostic keeps the target's positive propagator powers fixed and varies
only negative powers on indices outside the target sector.  It reaches the new
s=6 boundary directly without the much larger bounded seed domain that also
varies positive powers/dots.

A positive target pivot is useful evidence.  Failure to find a pivot is still
inconclusive because d>0 / positive-power variations are intentionally omitted.
"""
from __future__ import annotations

import argparse
import itertools
import json

import sympy as sp

from qedcalc.operations.ibp import (
    IntegralIndex,
    compile_ibp_templates,
    connected_rows_for_targets,
    generate_ibp_system,
    project_rows_to_rank_floor,
    prune_zero_sectors,
    rows_at_or_above_rank,
    specialize_ibp_system_mod_prime,
    target_pivot_search_mod_prime,
)
from three_loop.native_ibp_family import build_native_ibp_family
from examples.three_loop_master_basis_candidate_closure import (
    AUDIT_DIR,
    _parse_seed,
    _resolve,
)
from examples.three_loop_master_basis_candidate_sector_closure import _sector


def _idx(text: str) -> IntegralIndex:
    body = text.split("[", 1)[1].rsplit("]", 1)[0]
    return IntegralIndex(tuple(int(x) for x in body.split(",")))


def _weak_compositions(total: int, slots: int):
    if slots == 1:
        yield (total,)
        return
    for cuts in itertools.combinations(range(total + slots - 1), slots - 1):
        points = (-1, *cuts, total + slots - 1)
        yield tuple(points[i + 1] - points[i] - 1 for i in range(slots))


def _numerator_simplex(target: IntegralIndex, max_s: int) -> tuple[IntegralIndex, ...]:
    base = list(target.powers)
    zero_positions = [i for i, a in enumerate(base) if a == 0]
    if not zero_positions:
        raise ValueError("target has no zero-power positions for numerator insertion")

    seeds: list[IntegralIndex] = []
    for s in range(max_s + 1):
        for comp in _weak_compositions(s, len(zero_positions)):
            powers = list(base)
            for pos, amount in zip(zero_positions, comp):
                powers[pos] = -int(amount)
            seeds.append(IntegralIndex(tuple(powers)))
    return tuple(seeds)


def _probe_points():
    D, m2, z = sp.symbols("D m2 z")
    return (
        ({D: sp.Rational(37, 10), m2: 1, z: sp.Rational(2, 7)}, 2147483647),
        ({D: sp.Rational(41, 11), m2: 1, z: sp.Rational(3, 8)}, 2147483629),
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--baseline-seed", type=_parse_seed)
    p.add_argument("--sector", required=True, type=int)
    p.add_argument("--max-s", required=True, type=int)
    args = p.parse_args()

    (
        spec,
        baseline,
        union_audit_path,
        envelope,
        source_targets,
        _,
        candidate_file,
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
            f"sector {args.sector} must contain exactly one refined candidate; found {len(targets)}"
        )

    target_text = targets[0]
    target = _idx(target_text)
    protected = {_idx(x) for x in candidate if x != target_text}
    seeds = _numerator_simplex(target, args.max_s)
    zero_positions = [i for i, a in enumerate(target.powers) if a == 0]

    shell_counts = {}
    for seed in seeds:
        s = sum(max(-a, 0) for a in seed.powers)
        shell_counts[s] = shell_counts.get(s, 0) + 1

    print(f"[sector-numerator] family={spec.family_id}", flush=True)
    print(f"[sector-numerator] target={target_text}", flush=True)
    print(f"[sector-numerator] fixed sector={args.sector}", flush=True)
    print(f"[sector-numerator] numerator slots={len(zero_positions)} positions={zero_positions}", flush=True)
    print(f"[sector-numerator] max_s={args.max_s} seed_count={len(seeds)} shells={shell_counts}", flush=True)

    family = build_native_ibp_family(spec.family_id)
    print("[sector-numerator] compile templates...", flush=True)
    templates = compile_ibp_templates(family)
    print(f"[sector-numerator] templates={len(templates)}", flush=True)
    print("[sector-numerator] generate equations...", flush=True)
    equations = generate_ibp_system(family, seeds, templates=templates)
    equations = prune_zero_sectors(family, equations)
    all_integrals = {i for eq in equations for i in eq.terms}
    print(
        f"[sector-numerator] equations={len(equations)} integrals={len(all_integrals)}",
        flush=True,
    )

    probe_rows = []
    for n, (point, prime) in enumerate(_probe_points(), start=1):
        print(f"[sector-numerator] probe {n}: specialize F_{prime}...", flush=True)
        rows = specialize_ibp_system_mod_prime(equations, point, prime)
        connected = connected_rows_for_targets(rows, (target,))
        ranked = rows_at_or_above_rank(connected, target)
        projected = project_rows_to_rank_floor(
            ranked,
            target,
            protected=protected,
        )
        before_cols = len({idx for row in ranked for idx in row})
        after_cols = len({idx for row in projected for idx in row})
        before_nnz = sum(len(row) for row in ranked)
        after_nnz = sum(len(row) for row in projected)
        print(
            f"[sector-numerator] probe {n}: connected={len(connected)} "
            f"ranked={len(ranked)} columns={after_cols}/{before_cols} "
            f"nnz={after_nnz}/{before_nnz}",
            flush=True,
        )
        solved, pivots, processed = target_pivot_search_mod_prime(
            projected,
            prime,
            target,
            protected=protected,
            progress_every=500,
            progress_callback=lambda done, total, npiv, pn=n: print(
                f"[sector-numerator] probe {pn}: rows={done}/{total} pivots={npiv}",
                flush=True,
            ),
        )
        print(
            f"[sector-numerator] probe {n}: target_solved={solved} "
            f"processed_rows={processed} pivots={len(pivots)}",
            flush=True,
        )
        probe_rows.append({
            "probe": n,
            "prime": prime,
            "connected_equations": len(connected),
            "rank_floor_equations": len(ranked),
            "projected_columns": after_cols,
            "columns_before_projection": before_cols,
            "projected_nnz": after_nnz,
            "nnz_before_projection": before_nnz,
            "processed_rows": processed,
            "pivot_count": len(pivots),
            "target_solved": bool(solved),
        })

    if all(r["target_solved"] for r in probe_rows):
        status = "target-pivot-found-needs-rhs-check"
    elif any(r["target_solved"] for r in probe_rows):
        status = "target-pivot-inconsistent-across-probes"
    else:
        status = "target-pivot-not-found-in-fixed-sector-numerator-simplex"

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    stem = (
        f"three_loop_{spec.family_id.lower()}_sector_numerator_probe_"
        f"{baseline.tag}_sec{args.sector}_s{args.max_s}"
    )
    out_json = AUDIT_DIR / f"{stem}.json"
    out_txt = AUDIT_DIR / f"{stem}.txt"

    payload = {
        "schema_version": 1,
        "stage": "master_basis_candidate_fixed_sector_numerator_probe",
        "family": spec.family_id,
        "baseline_seed": baseline.tag,
        "candidate_envelope": envelope.tag,
        "sector": args.sector,
        "max_s": args.max_s,
        "target": target_text,
        "zero_positions": zero_positions,
        "seed_count": len(seeds),
        "seed_shell_counts": shell_counts,
        "equation_count": len(equations),
        "integral_count": len(all_integrals),
        "protected_candidate_count": len(protected),
        "probe_rows": probe_rows,
        "status": status,
        "audit_pass": False,
        "interpretation": (
            "This probe reaches the s boundary while fixing the target's positive powers. "
            "A consistent target pivot is useful reducibility evidence but still needs RHS "
            "reduction. A negative result is inconclusive because d>0 and other positive-power "
            "variations are omitted."
        ),
        "candidate_master_file": str(candidate_file),
        "union_reduction_audit": str(union_audit_path),
        "source_union_target_file": str(source_targets),
    }
    out_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )

    lines = [
        "QEDCalc fixed-sector numerator-simplex native IBP probe",
        f"family: {spec.family_id}",
        f"baseline seed: {baseline.tag}",
        f"sector: {args.sector}",
        f"target: {target_text}",
        f"max s: {args.max_s}",
        f"numerator slots: {len(zero_positions)}",
        f"seed count: {len(seeds)}",
        f"seed shells: {shell_counts}",
        f"equations: {len(equations)}",
        f"integrals: {len(all_integrals)}",
    ]
    for row in probe_rows:
        lines.append(
            f"probe {row['probe']}: target_solved={row['target_solved']} "
            f"pivots={row['pivot_count']} processed_rows={row['processed_rows']}"
        )
    lines.extend([
        f"status: {status}",
        "audit pass: False",
        f"audit JSON: {out_json}",
        f"audit TXT: {out_txt}",
    ])
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
