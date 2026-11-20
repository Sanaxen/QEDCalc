"""Read-only multi-step exact provenance arithmetic pilot.

Compares the production-like SymPy cancel path against a persistent QQ(z,d)
fraction-field representation across a bounded sequence. This never edits
the saved source checkpoint, original IBP equations, Kira jobs or engine.
Cases are formed from genuine saved pivot traces, not a recorded IBP pivot path.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from examples import three_loop_vp05_exact_arithmetic_probe as probe


def trace_sequence(path: Path, *, expected_sha256: str, terms: int,
                   max_chars: int, rounds: int):
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != expected_sha256:
        raise ValueError("Checkpoint SHA256 mismatch: refusing unpinned input")
    state = json.loads(raw)
    if (state.get("version") != 1 or
        state.get("status") != "EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF" or
        state.get("config", {}).get("target") != "A" or
        state.get("exact_target_reduction_proven") is not False or
        state.get("source_pivots_exact_replay_verified") is not True or
        state.get("processed", 0) < 200 or
        len(state.get("pivots", [])) !=
            state["processed"] - state.get("dependent", -1)):
        raise ValueError("Invalid isolated exact A checkpoint scope or metadata")
    selected = []
    for entry in reversed(state["pivots"]):
        eligible = [(int(key), value) for key, value in entry["trace"]
                    if len(value) <= max_chars]
        if len(eligible) >= terms:
            # Convert only the chosen bounded entries, never all saved coefficients.
            converted = {
                key: sp.sympify(value, locals={"z": probe.Z, "d": probe.D})
                for key, value in eligible[:terms]
            }
            selected.append(converted)
            if len(selected) >= rounds + 1:
                break
    if len(selected) < rounds + 1:
        raise ValueError("Insufficient distinct qualifying saved pivot traces")
    return selected, sha, state["processed"]


def compare_sequence(traces, *, multipliers=None):
    if len(traces) < 2:
        raise ValueError("Need initial trace and one update trace")
    if multipliers is None:
        multipliers = [
            (probe.Z + probe.D + k + 1) / (probe.Z - probe.D + k + 2)
            for k in range(len(traces) - 1)
        ]
    if len(multipliers) != len(traces) - 1:
        raise ValueError("Multiplier count mismatch")
    sym_state = dict(traces[0])
    field_state = {key: probe.FIELD.from_expr(value)
                   for key, value in traces[0].items()}
    field_sources = [
        {key: probe.FIELD.from_expr(value) for key, value in trace.items()}
        for trace in traces[1:]
    ]
    field_multipliers = [probe.FIELD.from_expr(value) for value in multipliers]
    results = []
    for number, (source, m, field_source, field_m) in enumerate(
            zip(traces[1:], multipliers, field_sources, field_multipliers), 1):
        clock = time.monotonic()
        sym_state = probe.sympy_sparse_subtract(sym_state, source, m)
        sym_time = time.monotonic() - clock
        clock = time.monotonic()
        for key, value in field_source.items():
            result = field_state.get(key, probe.FIELD.zero) - field_m * value
            if result == probe.FIELD.zero:
                field_state.pop(key, None)
            else:
                field_state[key] = result
        field_time = time.monotonic() - clock
        clock = time.monotonic()
        # Strict independent full symbolic equality after each update.
        candidate = {key: value.as_expr() for key, value in field_state.items()}
        passed = probe.exact_same(sym_state, candidate)
        verification_time = time.monotonic() - clock
        results.append({
            "round": number, "source_terms": len(source),
            "output_terms": len(candidate),
            "baseline_s": round(sym_time, 6),
            "field_update_s": round(field_time, 6),
            "verification_s": round(verification_time, 6),
            "exact_pass": passed,
        })
        if not passed:
            break
    # One-time conversion overhead is included below in end-to-end timing
    # separately by callers; timing records distinguish updates and verification.
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--terms", type=int, default=50)
    parser.add_argument("--max-chars", type=int, default=600)
    parser.add_argument("--rounds", type=int, default=2)
    args = parser.parse_args()
    if not (1 <= args.rounds <= 3 and 1 <= args.terms <= 128
            and 16 <= args.max_chars <= 600):
        parser.error("Only bounded 1..3 rounds, <=128 terms and <=600 chars permitted")
    traces, sha, processed = trace_sequence(
        args.checkpoint, expected_sha256=args.expected_sha256,
        terms=args.terms, max_chars=args.max_chars, rounds=args.rounds)
    t = time.monotonic()
    outcome = compare_sequence(traces)
    total_s = round(time.monotonic()-t, 6)
    passed = len(outcome) == args.rounds and all(r["exact_pass"] for r in outcome)
    print("VP05_EXACT_SEQUENTIAL_PROBE " + json.dumps({
        "status": "EXACT_SEQUENCE_PASS_PROBE_ONLY" if passed
                  else "EXACT_SEQUENCE_MISMATCH",
        "rounds": outcome, "wall_s": total_s,
        "requested_rounds": args.rounds, "terms": args.terms,
        "checkpoint_sha256": sha, "checkpoint_processed": processed,
        "checkpoint_modified": False, "production_engine_modified": False,
        "target_A_proven": False, "kira_executed": False,
        "real_original_ibp_path_replayed": False,
    }), flush=True)
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
