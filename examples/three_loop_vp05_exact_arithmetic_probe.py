"""Isolated, read-only QQ(z,d) fraction-field subtraction benchmark.

Does not change any production engine, checkpoint, original IBP source or proof.
Conversion to/from FracElement is part of the measured candidate time.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp
from sympy.polys.fields import field

FIELD, _, _ = field("z,d", sp.QQ)
Z, D = sp.symbols("z d")


def sympy_sparse_subtract(dest, source, multiplier):
    result = dict(dest)
    for key, value in source.items():
        updated = sp.cancel(result.get(key, sp.S.Zero) - multiplier * value)
        if updated == 0:
            result.pop(key, None)
        else:
            result[key] = updated
    return result


def fraction_field_sparse_subtract(dest, source, multiplier):
    """Exact candidate; this is not wired into the production source engine."""
    result = {key: FIELD.from_expr(value) for key, value in dest.items()}
    m = FIELD.from_expr(multiplier)
    for key, value in source.items():
        updated = result.get(key, FIELD.zero) - m * FIELD.from_expr(value)
        if updated == FIELD.zero:
            result.pop(key, None)
        else:
            result[key] = updated
    return {key: value.as_expr() for key, value in result.items()}


def exact_same(a, b):
    return set(a) == set(b) and all(
        sp.cancel(a[key] - b[key]) == 0 for key in a)


def bench_case(case):
    name, dest, source, multiplier = case
    started = time.monotonic()
    baseline = sympy_sparse_subtract(dest, source, multiplier)
    baseline_s = time.monotonic() - started
    started = time.monotonic()
    candidate = fraction_field_sparse_subtract(dest, source, multiplier)
    candidate_s = time.monotonic() - started
    passed = exact_same(baseline, candidate)
    return {
        "name": name, "baseline_s": round(baseline_s, 6),
        "candidate_s": round(candidate_s, 6),
        "speed_ratio": round(baseline_s / candidate_s, 4) if candidate_s else None,
        "exact_pass": passed, "dest_terms": len(dest),
        "source_terms": len(source), "output_terms": len(candidate),
    }


def sampled_cases_from_checkpoint(path, *, max_terms=6, max_chars=160,
                                  cases=2, expected_sha256=None):
    """Sample a bounded number of genuine saved provenance coefficients."""
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if expected_sha256 and sha != expected_sha256:
        raise ValueError("Checkpoint SHA256 mismatch: refusing unpinned input")
    state = json.loads(raw)
    if (state.get("version") != 1 or
        state.get("status") != "EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF" or
        state.get("config", {}).get("target") != "A" or
        state.get("exact_target_reduction_proven") is not False or
        state.get("source_pivots_exact_replay_verified") is not True or
        state.get("processed", 0) < 200 or
        len(state.get("pivots", [])) !=
            state.get("processed") - state.get("dependent", -1)):
        raise ValueError("Not a valid fully-accounted saved A exact source checkpoint")
    pivots = []
    for entry in reversed(state["pivots"]):
        filtered = [(int(original_id), sp.sympify(value, locals={"z": Z, "d": D}))
                    for original_id, value in entry["trace"]
                    if len(value) <= max_chars]
        if len(filtered) >= max_terms:
            pivots.append((tuple(entry["lead"]), dict(filtered[:max_terms])))
        if len(pivots) >= max(6, cases * 3):
            break
    if len(pivots) < 2:
        raise ValueError("Insufficient compact provenance entries within sample bounds")
    selected = []
    for index in range(min(cases, len(pivots) - 1)):
        lead, source = pivots[index]
        _, dest = pivots[index + 1]
        selected.append((
            "saved_provenance_%s_%02d" % ("_".join(map(str, lead)), index),
            dest, source, (Z + D + 1) / (Z - D + 2)))
    return selected, sha, state["processed"]


def basic_cases():
    return [
        ("zero_cancel", {1: Z + D}, {1: Z + D}, sp.S.One),
        ("rational_overlap",
         {1: (Z + D)/(Z - D), 2: (Z**2 + 1)/(D + 2)},
         {1: (D + 1)/(Z - D), 3: Z/(D + 2)},
         (Z**2 - D)/(D + 1)),
        ("rational_nontrivial",
         {1: (Z + 1)**2/(D - 1)},
         {1: (Z**2 - 1)/(D**2 - 1), 2: (D - Z)/(D + Z + 1)},
         (D + 2)/(Z + 2)),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--max-terms", type=int, default=6)
    parser.add_argument("--max-chars", type=int, default=160)
    parser.add_argument("--cases", type=int, default=2)
    args = parser.parse_args()
    if not (1 <= args.cases <= 5 and 1 <= args.max_terms <= 12
            and 16 <= args.max_chars <= 240):
        parser.error("Bounded sample parameters required")
    if args.expected_sha256 and not args.checkpoint:
        parser.error("--expected-sha256 requires --checkpoint")
    selected = basic_cases()
    sha = None
    processed = None
    if args.checkpoint:
        real, sha, processed = sampled_cases_from_checkpoint(
            args.checkpoint, max_terms=args.max_terms,
            max_chars=args.max_chars, cases=args.cases,
            expected_sha256=args.expected_sha256)
        selected.extend(real)
    results = [bench_case(case) for case in selected]
    passed = all(item["exact_pass"] for item in results)
    print("VP05_EXACT_ARITHMETIC_PROBE " + json.dumps({
        "status": ("EXACT_EQUIVALENCE_PASS_PROBE_ONLY" if passed else
                   "EXACT_EQUIVALENCE_FAIL"),
        "results": results,
        "checkpoint_sha256": sha, "checkpoint_processed": processed,
        "checkpoint_modified": False, "production_engine_modified": False,
        "target_A_proven": False, "kira_executed": False,
    }), flush=True)
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
