"""Streaming incremental native-IBP target-pivot search.

Process exact bounded seed shells degree-by-degree and batch-by-batch, carrying
finite-field pivots forward instead of recomputing the full degree-N system.
This is aimed specifically at testing whether an s=0 target loses master status
only when the new s=6 boundary is admitted.

Checkpoint state is written after every batch so long runs are resumable.
"""
from __future__ import annotations

import argparse
import gzip
import json
import pickle
from pathlib import Path

import sympy as sp

from qedcalc.operations.ibp import (
    IntegralIndex,
    bounded_seed_domain,
    compile_ibp_templates,
    generate_ibp_system,
    project_rows_to_rank_floor,
    prune_zero_sectors,
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


def _probe_points():
    D, m2, z = sp.symbols("D m2 z")
    return (
        ({D: sp.Rational(37, 10), m2: 1, z: sp.Rational(2, 7)}, 2147483647),
        ({D: sp.Rational(41, 11), m2: 1, z: sp.Rational(3, 8)}, 2147483629),
    )


def _exact_shell(target: IntegralIndex, degree: int) -> tuple[IntegralIndex, ...]:
    current = set(bounded_seed_domain(target, max_extra_degree=degree))
    if degree == 0:
        previous = set()
    else:
        previous = set(bounded_seed_domain(target, max_extra_degree=degree - 1))
    shell = current - previous
    return tuple(sorted(shell, key=lambda x: x.powers))


def _state_path(family: str, baseline: str, sector: int, max_degree: int) -> Path:
    return AUDIT_DIR / (
        f"three_loop_{family.lower()}_incremental_native_ibp_"
        f"{baseline}_sec{sector}_to_degree{max_degree}.pkl.gz"
    )


def _save_state(path: Path, state: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with gzip.open(tmp, "wb", compresslevel=3) as fh:
        pickle.dump(state, fh, protocol=pickle.HIGHEST_PROTOCOL)
    tmp.replace(path)


def _load_state(path: Path) -> dict | None:
    if not path.exists():
        return None
    with gzip.open(path, "rb") as fh:
        return pickle.load(fh)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family", required=True)
    p.add_argument("--baseline-seed", type=_parse_seed)
    p.add_argument("--sector", required=True, type=int)
    p.add_argument("--max-degree", type=int, default=6)
    p.add_argument("--batch-size", type=int, default=250)
    p.add_argument("--fresh", action="store_true")
    args = p.parse_args()

    (
        spec,
        baseline,
        _,
        envelope,
        _,
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

    target_texts = [x for x in candidate if _sector(x) == args.sector]
    if len(target_texts) != 1:
        raise ValueError(
            f"sector {args.sector} must contain exactly one refined candidate; "
            f"found {len(target_texts)}"
        )
    target_text = target_texts[0]
    target = _idx(target_text)
    protected = {_idx(x) for x in candidate if x != target_text}

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    state_path = _state_path(spec.family_id, baseline.tag, args.sector, args.max_degree)
    if args.fresh and state_path.exists():
        state_path.unlink()

    probes = _probe_points()
    state = _load_state(state_path)
    if state is None:
        state = {
            "schema_version": 1,
            "family": spec.family_id,
            "baseline_seed": baseline.tag,
            "sector": args.sector,
            "target": target_text,
            "max_degree": args.max_degree,
            "batch_size": args.batch_size,
            "next_degree": 0,
            "next_offset": 0,
            "pivots": [{}, {}],
            "probe_target_solved": [False, False],
            "history": [],
        }
    else:
        if (
            state.get("family") != spec.family_id
            or state.get("baseline_seed") != baseline.tag
            or int(state.get("sector")) != args.sector
            or state.get("target") != target_text
            or int(state.get("max_degree")) != args.max_degree
        ):
            raise RuntimeError(f"checkpoint does not match requested run: {state_path}")
        print(
            f"[incremental-ibp] resume degree={state['next_degree']} "
            f"offset={state['next_offset']}",
            flush=True,
        )

    print(f"[incremental-ibp] build family: {spec.family_id}", flush=True)
    family = build_native_ibp_family(spec.family_id)
    print("[incremental-ibp] compile derivative templates...", flush=True)
    templates = compile_ibp_templates(family)
    print(f"[incremental-ibp] templates ready: {len(templates)}", flush=True)

    batch_size = max(1, int(args.batch_size))
    for degree in range(int(state["next_degree"]), args.max_degree + 1):
        shell = _exact_shell(target, degree)
        start = int(state["next_offset"]) if degree == int(state["next_degree"]) else 0
        print(
            f"[incremental-ibp] degree {degree}: exact-shell seeds={len(shell)} "
            f"start={start}",
            flush=True,
        )

        for offset in range(start, len(shell), batch_size):
            batch = shell[offset: offset + batch_size]
            print(
                f"[incremental-ibp] degree {degree}: batch "
                f"{offset}:{offset + len(batch)}/{len(shell)} "
                f"seeds={len(batch)}",
                flush=True,
            )
            equations = generate_ibp_system(family, batch, templates=templates)
            equations = prune_zero_sectors(family, equations)
            symbolic_integrals = len({idx for eq in equations for idx in eq.terms})
            print(
                f"[incremental-ibp] degree {degree}: equations={len(equations)} "
                f"integrals={symbolic_integrals}",
                flush=True,
            )

            batch_record = {
                "degree": degree,
                "offset": offset,
                "seed_count": len(batch),
                "equation_count": len(equations),
                "symbolic_integral_count": symbolic_integrals,
                "probes": [],
            }

            for pno, (point, prime) in enumerate(probes):
                if state["probe_target_solved"][pno]:
                    batch_record["probes"].append({
                        "probe": pno + 1,
                        "prime": prime,
                        "skipped": "target already pivoted",
                    })
                    continue

                rows = specialize_ibp_system_mod_prime(equations, point, prime)
                projected = project_rows_to_rank_floor(
                    rows,
                    target,
                    protected=protected,
                )
                nnz_before = sum(len(r) for r in rows)
                nnz_after = sum(len(r) for r in projected)
                print(
                    f"[incremental-ibp] degree {degree} probe {pno+1}: "
                    f"rows={len(projected)}/{len(rows)} "
                    f"nnz={nnz_after}/{nnz_before} "
                    f"pivots_in={len(state['pivots'][pno])}",
                    flush=True,
                )

                solved, pivots, processed = target_pivot_search_mod_prime(
                    projected,
                    prime,
                    target,
                    protected=protected,
                    initial_pivots=state["pivots"][pno],
                    progress_every=500,
                    progress_callback=lambda done, total, npiv, d=degree, pn=pno+1: print(
                        f"[incremental-ibp] degree {d} probe {pn}: "
                        f"rows={done}/{total} pivots={npiv}",
                        flush=True,
                    ),
                )
                state["pivots"][pno] = pivots
                state["probe_target_solved"][pno] = bool(solved)
                print(
                    f"[incremental-ibp] degree {degree} probe {pno+1}: "
                    f"pivots_out={len(pivots)} target_solved={solved}",
                    flush=True,
                )
                batch_record["probes"].append({
                    "probe": pno + 1,
                    "prime": prime,
                    "row_count": len(rows),
                    "projected_row_count": len(projected),
                    "nnz_before": nnz_before,
                    "nnz_after": nnz_after,
                    "processed_rows": processed,
                    "pivot_count": len(pivots),
                    "target_solved": bool(solved),
                })

            state["history"].append(batch_record)
            state["next_degree"] = degree
            state["next_offset"] = offset + len(batch)
            if state["next_offset"] >= len(shell):
                state["next_degree"] = degree + 1
                state["next_offset"] = 0
            _save_state(state_path, state)

            if all(state["probe_target_solved"]):
                break

        if all(state["probe_target_solved"]):
            break

    status = (
        "target-pivot-found-both-probes"
        if all(state["probe_target_solved"])
        else "target-pivot-not-found-through-max-degree"
    )
    summary = {
        "schema_version": 1,
        "stage": "incremental_native_ibp_target_pivot",
        "family": spec.family_id,
        "baseline_seed": baseline.tag,
        "candidate_envelope": envelope.tag,
        "sector": args.sector,
        "target": target_text,
        "protected_candidate_count": len(protected),
        "candidate_master_file": str(candidate_file),
        "max_degree": args.max_degree,
        "batch_size": batch_size,
        "probe_target_solved": state["probe_target_solved"],
        "pivot_counts": [len(p) for p in state["pivots"]],
        "status": status,
        "checkpoint": str(state_path),
        "history": state["history"],
    }
    out_json = state_path.with_suffix("").with_suffix(".json")
    out_txt = state_path.with_suffix("").with_suffix(".txt")
    out_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )
    lines = [
        "QEDCalc incremental native IBP target-pivot audit",
        f"family: {spec.family_id}",
        f"baseline seed: {baseline.tag}",
        f"sector: {args.sector}",
        f"target: {target_text}",
        f"max degree: {args.max_degree}",
        f"batch size: {batch_size}",
        f"probe target solved: {state['probe_target_solved']}",
        f"pivot counts: {[len(p) for p in state['pivots']]}",
        f"status: {status}",
        f"checkpoint: {state_path}",
        f"audit JSON: {out_json}",
        f"audit TXT: {out_txt}",
    ]
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
