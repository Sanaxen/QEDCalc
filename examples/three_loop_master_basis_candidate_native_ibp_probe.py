"""Finite candidate-centered native-IBP reducibility probe.

This uses QEDCalc's own IBP generator and sparse generic-point Laporta path,
not Kira.  The refined target is unprotected; the other refined candidates are
protected.  A result is considered a positive reducibility witness only when
recursive reduction of the target terminates entirely on protected candidate
masters (or zero), consistently at all generic probe points.

An unsolved target is inconclusive: the finite bounded neighborhood may simply
be too small.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

from qedcalc.operations.ibp import (
    IntegralIndex,
    bounded_seed_domain,
    compile_ibp_templates,
    connected_rows_for_targets,
    generate_ibp_system,
    laporta_forward_eliminate_mod_prime,
    prune_zero_sectors,
    reduce_integral_mod_prime,
    specialize_ibp_system_mod_prime,
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


def _probe_points():
    D, m2, z = sp.symbols("D m2 z")
    return (
        {D: sp.Rational(37, 10), m2: 1, z: sp.Rational(2, 7)},
        {D: sp.Rational(41, 11), m2: 1, z: sp.Rational(3, 8)},
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--baseline-seed", type=_parse_seed)
    p.add_argument("--sector", required=True, type=int)
    p.add_argument("--degree", required=True, type=int)
    args = p.parse_args()

    (
        spec,
        baseline,
        union_audit_path,
        envelope,
        source_targets,
        union_targets,
        candidate_file,
        candidate,
        closure,
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
    seeds = bounded_seed_domain(target, max_extra_degree=args.degree)

    print(f"[native-ibp] build family: {spec.family_id}", flush=True)
    family = build_native_ibp_family(spec.family_id)
    print(f"[native-ibp] compile templates: loops={len(family.loop_momenta)} vectors={len(family.loop_momenta) + len(family.external_momenta)}", flush=True)
    templates = compile_ibp_templates(family)
    print(f"[native-ibp] templates ready: {len(templates)}", flush=True)
    print(f"[native-ibp] seed count: {len(seeds)}", flush=True)
    print("[native-ibp] generate equations...", flush=True)
    equations = generate_ibp_system(family, seeds, templates=templates)
    print(f"[native-ibp] raw equations: {len(equations)}", flush=True)
    equations = prune_zero_sectors(family, equations)
    all_integrals = {i for eq in equations for i in eq.terms}
    print(f"[native-ibp] after zero-sector prune: equations={len(equations)} integrals={len(all_integrals)}", flush=True)

    rows = []
    all_reducible_to_protected = True
    primes = (2147483647, 2147483629)
    for n, (point, prime) in enumerate(zip(_probe_points(), primes), start=1):
        print(f"[native-ibp] probe {n}: specialize to F_{prime}...", flush=True)
        prows = specialize_ibp_system_mod_prime(equations, point, prime)
        print(f"[native-ibp] probe {n}: target-connected prune from {len(prows)} equations...", flush=True)
        crows = connected_rows_for_targets(prows, (target,))
        print(f"[native-ibp] probe {n}: connected equations={len(crows)}", flush=True)
        print(f"[native-ibp] probe {n}: eliminate {len(crows)} equations over F_{prime}...", flush=True)
        rule_map = laporta_forward_eliminate_mod_prime(
            crows,
            prime,
            protected=protected,
        )
        print(f"[native-ibp] probe {n}: rules={len(rule_map)}", flush=True)
        target_solved = target in rule_map
        reduced = reduce_integral_mod_prime(target, rule_map, prime)
        residual = sorted(
            (idx, coeff) for idx, coeff in reduced.items() if coeff % prime
        )
        residual_unprotected = [
            (idx, coeff) for idx, coeff in residual if idx not in protected
        ]
        reducible_to_protected = target_solved and not residual_unprotected
        all_reducible_to_protected &= reducible_to_protected
        rows.append({
            "probe": n,
            "point": {str(k): str(v) for k, v in point.items()},
            "prime": prime,
            "equation_count": len(prows),
            "connected_equation_count": len(crows),
            "rule_count": len(rule_map),
            "target_solved": target_solved,
            "residual_count": len(residual),
            "residual_protected_count": len(residual) - len(residual_unprotected),
            "residual_unprotected_count": len(residual_unprotected),
            "residual_unprotected": [
                {
                    "integral": list(idx.powers),
                    "coefficient_mod_prime": int(coeff),
                }
                for idx, coeff in residual_unprotected[:50]
            ],
            "reducible_to_protected_basis": reducible_to_protected,
        })

    if all_reducible_to_protected:
        status = "reducible-to-refined-basis"
    elif any(row["target_solved"] for row in rows):
        status = "partially-solved-inconclusive"
    else:
        status = "unsolved-in-finite-neighborhood"

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    stem = (
        f"three_loop_{spec.family_id.lower()}_native_ibp_candidate_probe_"
        f"{baseline.tag}_sec{args.sector}_degree{args.degree}"
    )
    out_json = AUDIT_DIR / f"{stem}.json"
    out_txt = AUDIT_DIR / f"{stem}.txt"

    payload = {
        "schema_version": 1,
        "stage": "master_basis_candidate_native_ibp_probe",
        "family": spec.family_id,
        "baseline_seed": baseline.tag,
        "candidate_envelope": envelope.tag,
        "sector": args.sector,
        "degree": args.degree,
        "target": target_text,
        "candidate_master_file": str(candidate_file),
        "protected_candidate_count": len(protected),
        "seed_count": len(seeds),
        "equation_count_symbolic": len(equations),
        "integral_count_symbolic": len(all_integrals),
        "probe_rows": rows,
        "status": status,
        "audit_pass": all_reducible_to_protected,
        "interpretation": (
            "audit_pass=True is a finite-field generic-rank reducibility witness at two "
            "independent rational probe points/primes. It is not yet a symbolic coefficient proof. "
            "audit_pass=False is not evidence that the target is a master; it means the "
            "bounded native-IBP neighborhood was insufficient."
        ),
        "union_reduction_audit": str(union_audit_path),
        "source_union_target_file": str(source_targets),
    }
    out_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )

    lines = [
        "QEDCalc native IBP candidate probe",
        f"family: {spec.family_id}",
        f"baseline seed: {baseline.tag}",
        f"candidate envelope: {envelope.tag}",
        f"sector: {args.sector}",
        f"degree: {args.degree}",
        f"target: {target_text}",
        f"protected refined candidates: {len(protected)}",
        f"seed count: {len(seeds)}",
        f"symbolic equations: {len(equations)}",
        f"symbolic integrals: {len(all_integrals)}",
    ]
    for row in rows:
        lines.extend([
            f"probe {row['probe']}: rules={row['rule_count']} target_solved={row['target_solved']}",
            f"  residual={row['residual_count']} protected={row['residual_protected_count']} "
            f"unprotected={row['residual_unprotected_count']}",
            f"  reducible_to_protected_basis={row['reducible_to_protected_basis']}",
        ])
    lines.extend([
        f"status: {status}",
        f"audit pass: {all_reducible_to_protected}",
        f"audit JSON: {out_json}",
        f"audit TXT: {out_txt}",
    ])
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
