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
        # Filter by source character length BEFORE parsing: avoid converting
        # thousands of unused coefficients from the large exact checkpoint.
        entries = [(int(original_id), value)
                   for original_id, value in entry["trace"]
                   if len(value) <= max_chars]
        if len(entries) >= max_terms:
            filtered = [(key, sp.sympify(value, locals={"z": Z, "d": D}))
                        for key, value in entries[:max_terms]]
            pivots.append((tuple(entry["lead"]), dict(filtered)))
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




def sampled_mixed_support_case(path, *, source_terms=100, dest_terms=50,
                               max_chars=240, expected_sha256=None):
    """Read-only, SHA-pinned unequal-support case from two distinct saved pivots.

    Benchmarks source/destination exact arithmetic only; not the original
    elimination path or actual multiplier from a timed source row.
    """
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if expected_sha256 and sha != expected_sha256:
        raise ValueError("Checkpoint SHA256 mismatch: refusing unpinned input")
    state = json.loads(raw)
    if (state.get("version") != 1 or
        state.get("status") != "EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF" or
        state.get("config", {}).get("target") != "A" or
        state.get("source_pivots_exact_replay_verified") is not True or
        state.get("exact_target_reduction_proven") is not False or
        state.get("processed", 0) < 200 or
        len(state.get("pivots", [])) !=
            state.get("processed") - state.get("dependent", -1)):
        raise ValueError("Not a valid fully-accounted saved A exact source checkpoint")
    eligible = []
    for index, entry in enumerate(state["pivots"]):
        values = [(int(k), v) for k, v in entry["trace"]
                  if len(v) <= max_chars]
        eligible.append((index, values, entry["lead"]))
    sources = [(i, values, lead) for i, values, lead in eligible
               if len(values) >= source_terms]
    if not sources:
        raise ValueError("Insufficient source provenance support for mixed sample")
    src_index, src_values, src_lead = sources[-1]
    destinations = [(i, values, lead) for i, values, lead in eligible
                    if i != src_index and len(values) >= dest_terms]
    if not destinations:
        raise ValueError("Insufficient distinct destination provenance support")
    dst_index, dst_values, _ = destinations[-1]
    def parse(entries):
        return {k: sp.sympify(v, locals={"z": Z, "d": D}) for k, v in entries}
    case = (
        "mixed_saved_source_%s_%d_to_%d" %
        ("_".join(map(str, src_lead)), source_terms, dest_terms),
        parse(dst_values[:dest_terms]), parse(src_values[:source_terms]),
        (Z + D + 1) / (Z - D + 2))
    return case, sha, state["processed"]



def checkpoint_support_inventory(path, *, max_chars, expected_sha256=None):
    """Read-only count of candidate source support; never parse coefficients."""
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if expected_sha256 and sha != expected_sha256:
        raise ValueError("Checkpoint SHA256 mismatch: refusing unpinned input")
    state = json.loads(raw)
    if (state.get("version") != 1 or
        state.get("config", {}).get("target") != "A" or
        state.get("status") != "EXACT_SOURCE_CHECKPOINT_NOT_TARGET_PROOF" or
        state.get("exact_target_reduction_proven") is not False or
        state.get("source_pivots_exact_replay_verified") is not True or
        state.get("processed", 0) < 200 or
        len(state.get("pivots", [])) !=
            state.get("processed") - state.get("dependent", -1)):
        raise ValueError("Not a valid fully-accounted saved A exact source checkpoint")
    qualified = [
        sum(len(value) <= max_chars for _, value in entry["trace"])
        for entry in state["pivots"]
    ]
    return {"status": "READ_ONLY_SAVED_PROVENANCE_INVENTORY_NOT_PROOF",
            "checkpoint_sha256": sha, "checkpoint_processed": state["processed"],
            "max_chars": max_chars, "max_support": max(qualified, default=0),
            "pivots_with_50_entries": sum(n >= 50 for n in qualified),
            "pivots_with_100_entries": sum(n >= 100 for n in qualified),
            "pivots_with_128_entries": sum(n >= 128 for n in qualified),
            "checkpoint_modified": False, "production_engine_modified": False,
            "target_A_proven": False}

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
    parser.add_argument("--inventory-only", action="store_true", help="Read-only support count, no symbolic arithmetic")
    parser.add_argument("--mixed-source-terms", type=int, help="Use a distinct saved pivot with at least N source coefficients")
    parser.add_argument("--mixed-dest-terms", type=int, default=50)
    args = parser.parse_args()
    if not (1 <= args.cases <= 5 and 1 <= args.max_terms <= 128
            and 16 <= args.max_chars <= 600):
        parser.error("Bounded sample parameters required")
    if args.expected_sha256 and not args.checkpoint:
        parser.error("--expected-sha256 requires --checkpoint")
    if args.inventory_only:
        if not args.checkpoint or not args.expected_sha256:
            parser.error("--inventory-only requires a checkpoint and expected SHA256")
        print("VP05_EXACT_ARITHMETIC_INVENTORY " + json.dumps(
            checkpoint_support_inventory(args.checkpoint, max_chars=args.max_chars,
                                         expected_sha256=args.expected_sha256)), flush=True)
        return
    if args.mixed_source_terms is not None and (not args.checkpoint or not args.expected_sha256 or
        not 1 <= args.mixed_source_terms <= 128 or not 1 <= args.mixed_dest_terms <= 128):
        parser.error("Mixed support requires SHA-pinned checkpoint and term caps <=128")
    selected = [] if args.mixed_source_terms is not None else basic_cases()
    sha = None
    processed = None
    if args.mixed_source_terms is not None:
        mixed, sha, processed = sampled_mixed_support_case(
            args.checkpoint, source_terms=args.mixed_source_terms,
            dest_terms=args.mixed_dest_terms, max_chars=args.max_chars,
            expected_sha256=args.expected_sha256)
        selected.append(mixed)
    elif args.checkpoint:
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
