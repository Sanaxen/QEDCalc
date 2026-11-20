"""Read-only, SHA-pinned real VP05 A original-IBP pivot-path field pilot.

Use exactly the next exported source equation after the immutable 296-row
checkpoint, follow the actual min-key stored pivot order, compare baseline
SymPy cancellation to persistent exact QQ(z,d) arithmetic after each update,
and independently replay literal original-source IBP equations. No writes.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import sympy as sp

from examples import three_loop_vp05_exact_arithmetic_probe as ar
from examples import three_loop_vp05_exact_real_first_pivot_probe as first
from examples import three_loop_vp05_sector202_exact_support_checkpoint as engine


def advance_exact_path(saved, rows, ids, *, max_steps=4):
    if not 1 <= max_steps <= 8:
        raise ValueError("Only 1..8 exact original-IBP pivot steps permitted")
    rid = ids[saved["processed"]]
    z, d = ar.Z, ar.D
    initial = {}
    for term in rows[rid]["terms"]:
        k = tuple(term["key"])
        value = sp.cancel(initial.get(k, sp.S.Zero) +
                          engine.expr(term["coefficient"], z, d))
        if value:
            initial[k] = value
        else:
            initial.pop(k, None)
    if not initial:
        raise RuntimeError("Next original IBP equation is initially zero")
    reference_row = dict(initial)
    reference_trace = {rid: sp.S.One}

    conversion_start = time.monotonic()
    field_row = {k: ar.FIELD.from_expr(v) for k, v in initial.items()}
    field_trace = {rid: ar.FIELD.one}
    init_conversion_s = time.monotonic() - conversion_start

    # Decoding is lazy: only actual pivots used on this path are loaded.
    pivot_lookup = {tuple(entry["lead"]): entry for entry in saved["pivots"]}
    used = []
    rounds = []
    for step in range(1, max_steps + 1):
        if not reference_row:
            break
        lead = min(reference_row)
        if lead not in pivot_lookup:
            break
        if lead in used:
            raise AssertionError("Exact pivot repeated without eliminating lead")
        entry = pivot_lookup[lead]
        brow = engine.decode_terms(entry["row"], z, d)
        btrace = {int(k): engine.expr(v, z, d) for k, v in entry["trace"]}
        if not brow or min(brow) != lead or sp.cancel(brow[lead] - 1) != 0:
            raise AssertionError("Stored pivot normalization mismatch")
        if not set(btrace).issubset(set(ids[:saved["processed"]])):
            raise AssertionError("Stored pivot provenance references later source")
        # Independently check each consumed saved pivot against literal IBP.
        engine.verify(brow, btrace, rows, z, d)

        factor = reference_row[lead]
        start = time.monotonic()
        updated_row = ar.sympy_sparse_subtract(reference_row, brow, factor)
        updated_trace = ar.sympy_sparse_subtract(reference_trace, btrace, factor)
        baseline_s = time.monotonic() - start

        start = time.monotonic()
        fbrow = {k: ar.FIELD.from_expr(v) for k, v in brow.items()}
        fbtrace = {k: ar.FIELD.from_expr(v) for k, v in btrace.items()}
        ffactor = field_row[lead]  # retain exact field value from prior update
        pivot_conversion_s = time.monotonic() - start

        start = time.monotonic()
        for dest, src in ((field_row, fbrow), (field_trace, fbtrace)):
            for key, value in src.items():
                out = dest.get(key, ar.FIELD.zero) - ffactor * value
                if out == ar.FIELD.zero:
                    dest.pop(key, None)
                else:
                    dest[key] = out
        field_update_s = time.monotonic() - start

        start = time.monotonic()
        candidate_row = {k: v.as_expr() for k, v in field_row.items()}
        candidate_trace = {k: v.as_expr() for k, v in field_trace.items()}
        back_conversion_s = time.monotonic() - start

        verify_start = time.monotonic()
        equal_row = ar.exact_same(updated_row, candidate_row)
        equal_trace = ar.exact_same(updated_trace, candidate_trace)
        if not equal_row or not equal_trace:
            raise AssertionError("Real original-IBP exact-path arithmetic mismatch")
        engine.verify(candidate_row, candidate_trace, rows, z, d)
        verification_s = time.monotonic() - verify_start

        rounds.append({
            "step": step,
            "pivot": list(lead),
            "pivot_row_columns": len(brow),
            "pivot_provenance_support": len(btrace),
            "output_columns": len(updated_row),
            "output_provenance_support": len(updated_trace),
            "baseline_s": round(baseline_s, 6),
            "field_pivot_conversion_s": round(pivot_conversion_s, 6),
            "field_update_s": round(field_update_s, 6),
            "field_back_conversion_s": round(back_conversion_s, 6),
            "strict_exact_row_equal": equal_row,
            "strict_exact_trace_equal": equal_trace,
            "original_ibp_replay_verified": True,
            "verification_s": round(verification_s, 6),
        })
        reference_row, reference_trace = updated_row, updated_trace
        used.append(lead)
    return {
        "status": "REAL_ORIGINAL_IBP_MULTISTEP_EXACT_PASS_NOT_TARGET_PROOF",
        "original_source_id": rid,
        "requested_max_steps": max_steps,
        "completed_steps": len(rounds),
        "next_lead": list(min(reference_row)) if reference_row else None,
        "stopped_because": (
            "zero_remainder" if not reference_row else
            "no_saved_pivot" if len(rounds) < max_steps else
            "max_steps"
        ),
        "initial_field_conversion_s": round(init_conversion_s, 6),
        "total_baseline_s": round(sum(x["baseline_s"] for x in rounds), 6),
        "total_field_conversion_plus_update_s": round(
            init_conversion_s + sum(x["field_pivot_conversion_s"] +
                                    x["field_update_s"] + x["field_back_conversion_s"]
                                    for x in rounds), 6),
        "steps": rounds,
        "real_original_ibp_path_replayed": bool(rounds),
        "real_original_ibp_path_steps": len(rounds),
        "checkpoint_processed": saved["processed"],
        "checkpoint_modified": False,
        "production_engine_modified": False,
        "target_A_proven": False,
        "kira_executed": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--source", type=Path, default=engine.SOURCE)
    ap.add_argument("--certificate", type=Path, default=engine.CERT)
    ap.add_argument("--max-steps", type=int, default=4)
    args = ap.parse_args()
    if not 1 <= args.max_steps <= 8:
        ap.error("--max-steps must be 1..8")
    saved, rows, ids = first.validated_inputs(
        args.checkpoint, args.source, args.certificate)
    result = advance_exact_path(saved, rows, ids, max_steps=args.max_steps)
    if first.sha(args.checkpoint.read_bytes()) != first.EXPECTED_A_CHECKPOINT_SHA256:
        raise RuntimeError("Immutable checkpoint changed during the pilot")
    result["checkpoint_sha256"] = first.EXPECTED_A_CHECKPOINT_SHA256
    print("VP05_REAL_ORIGINAL_IBP_MULTISTEP_FIELD_PROBE " +
          json.dumps(result), flush=True)
    if result["completed_steps"] == 0:
        raise SystemExit("No saved pivot matched the next original row")


if __name__ == "__main__":
    main()
