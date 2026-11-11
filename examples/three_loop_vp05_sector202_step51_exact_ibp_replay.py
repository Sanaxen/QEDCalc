"""Strict, resumable, read-only original-IBP replay for compact Step51 A.

One exact rational-function equality per integral key. Completion verifies
initial_A == residual_51 + sum(source_51 * original_IBP_rows), but a nonzero
residual means Target A is NOT proven reduced. Never edits the formal state.
"""
from __future__ import annotations
import argparse
import gzip
import json
import subprocess
import sys
import time
from pathlib import Path
import sympy as sp

from examples.three_loop_vp05_sector202_step51_compaction import (
    OUT as COMPACTION, CAP, validate as validate_compaction, entries,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT, FORMULAS, target_row, sha,
)
from examples.three_loop_vp05_sector202_step51_scratch import (
    STATE, SCRATCH, SEAL, atomic_save,
)
from examples.three_loop_vp05_sector202_step51_exact_coefficient_audit import (
    PROGRESS as EXACT_PROGRESS, audit_config,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_sector203_weight_audit import ROOT, load_codec
from examples.three_loop_vp05_sector202_quotient_sensitivity import P, TARGETS

REPORT = BASE / "vp05_sector202_A_step51_exact_original_ibp_replay.json"


def load_candidate(args):
    cfg, originals, oversized = validate_compaction(args)
    compact = json.loads(args.compaction.read_text(encoding="utf-8-sig"))
    if (compact.get("version") != 1
        or compact.get("status") != "STEP51_COMPACTION_CANDIDATE_NOT_PROOF"
        or compact.get("config") != cfg
        or compact.get("processed") != len(oversized)
        or len(compact.get("results", [])) != len(oversized)
        or compact.get("exact_target_proven") is not False):
        raise RuntimeError("Missing/incomplete or mismatched compaction")
    all_values = {(kind, tuple(key) if kind == "remainder" else int(key)): raw
                  for kind, key, raw in originals}
    for index, ((kind, key, original), result) in enumerate(zip(oversized, compact["results"])):
        expected_key = list(key) if kind == "remainder" else key
        candidate = result.get("compacted")
        if (result.get("index") != index or result.get("kind") != kind
            or result.get("key") != expected_key
            or result.get("original_chars") != len(original)
            or not isinstance(candidate, str)
            or result.get("compacted_chars") != len(candidate)
            or len(candidate) > CAP):
            raise RuntimeError("Invalid or unresolved compaction result")
        all_values[(kind, tuple(key) if kind == "remainder" else int(key))] = candidate
    if any(len(v) > CAP for v in all_values.values()):
        raise RuntimeError("Candidate still exceeds formal expression cap")
    rem = {key: val for (kind, key), val in all_values.items() if kind == "remainder"}
    trace = {key: val for (kind, key), val in all_values.items() if kind == "source_trace"}
    return rem, trace


def initial_a():
    z, d = sp.symbols("z d")
    mod = load_codec((ROOT / "output/tools/pyred_weight.py").resolve())
    bits, ordering = mod.from_kiradb(str(P / "results/kira.db"))
    if ordering != 5:
        raise RuntimeError("Unexpected Kira ordering")
    codec = mod.WeightCodec(np=12, bits=bits, iord=ordering, topsectors=[203])
    keys = [(codec.encode(v), 139) for v in TARGETS]
    if any(tuple(codec.decode(k[0])) != v for k, v in zip(keys, TARGETS)):
        raise RuntimeError("Kira weight codec mismatch")
    values = [expr(raw, z, d) for raw in FORMULAS]
    return {k: str(v) for k, v in target_row("A", keys, values).items()}


def original_terms(path, source_ids):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        data = json.load(handle)
    if (data.get("status") != "ORIGINAL_EXACT_SOURCE_ROWS_EXPORTED"
        or len(data.get("rows", [])) != 2241):
        raise RuntimeError("Unexpected original source export")
    by_id = {r["global_zero_based"]: r["terms"] for r in data["rows"]}
    if not set(source_ids).issubset(by_id):
        raise RuntimeError("Source trace has unknown original IBP row")
    return {rid: by_id[rid] for rid in source_ids}


def key_index(initial, rem, rows):
    keys = set(initial) | set(rem)
    for terms in rows.values():
        keys.update(tuple(term["key"]) for term in terms)
    return sorted(keys)


def verify_column(key, initial, rem, trace, rows):
    """Exactly check remainder + source*IBP - initial == 0 for one key."""
    z, d = sp.symbols("z d")
    value = expr(rem.get(key, "0"), z, d)
    if key in initial:
        value -= expr(initial[key], z, d)
    # First accumulate rational terms, then rationally simplify once.
    for rid, terms in rows.items():
        for term in terms:
            if tuple(term["key"]) == key:
                value += expr(trace[rid], z, d) * expr(term["coefficient"], z, d)
    return sp.cancel(value) == 0


def identity_config(args, initial, rem, trace, keys):
    import hashlib
    import json
    key_digest = hashlib.sha256(json.dumps([list(k) for k in keys]).encode()).hexdigest()
    init_digest = hashlib.sha256(json.dumps(
        [[list(k), str(v)] for k, v in sorted(initial.items())],
        separators=(",", ":")).encode()).hexdigest()
    return {"state_sha256": sha(args.state),
            "source_checkpoint_sha256": sha(args.source_checkpoint),
            "source_sha256": sha(args.input),
            "certificate_sha256": sha(args.certificate),
            "scratch_sha256": sha(args.scratch),
            "seal_sha256": sha(args.verified_seal),
            "exact_progress_sha256": sha(args.exact_progress),
            "compaction_sha256": sha(args.compaction),
            "initial_digest": init_digest, "key_digest": key_digest,
            "columns": len(keys), "formal_cap": CAP}


def context(args):
    rem, trace = load_candidate(args)
    initial = initial_a()
    target = json.loads(args.state.read_text(encoding="utf-8-sig"))
    if target["config"].get("initial_sha256") is None:
        raise RuntimeError("Missing initial hash in formal state")
    # Exact source-to-target representation is independently reconstructed.
    import hashlib
    from examples.three_loop_vp05_sector202_target_exact_checkpoint import encoded
    z, d = sp.symbols("z d")
    normalized = {k: expr(v, z, d) for k, v in initial.items()}
    digest = hashlib.sha256(json.dumps(encoded(normalized)).encode()).hexdigest()
    if digest != target["config"]["initial_sha256"]:
        raise RuntimeError("Initial A formula does not match step50 checkpoint")
    rows = original_terms(args.input, trace)
    keys = key_index(initial, rem, rows)
    return initial, rem, trace, rows, keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=STATE)
    ap.add_argument("--source-checkpoint", type=Path, default=CHECKPOINT)
    ap.add_argument("--input", type=Path, default=SOURCE)
    ap.add_argument("--certificate", type=Path, default=CERT)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--verified-seal", type=Path, default=SEAL)
    ap.add_argument("--exact-progress", type=Path, default=EXACT_PROGRESS)
    ap.add_argument("--compaction", type=Path, default=COMPACTION)
    ap.add_argument("--report", type=Path, default=REPORT)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--hours", type=float, default=12)
    ap.add_argument("--timeout-seconds", type=int, default=600)
    ap.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--worker-index", type=int, default=-1, help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.worker:
        initial, rem, trace, rows, keys = context(args)
        if not 0 <= args.worker_index < len(keys):
            raise RuntimeError("Invalid exact replay column index")
        key = keys[args.worker_index]
        if not verify_column(key, initial, rem, trace, rows):
            raise AssertionError("Exact original-IBP replay fails at column: %s" % (key,))
        print(json.dumps({"index": args.worker_index, "key": key,
                          "exact_zero": True}), flush=True)
        return
    if not 0 < args.hours <= 12 or not 30 <= args.timeout_seconds <= 1800:
        ap.error("Invalid bounded execution limits")
    protected = (args.state, args.source_checkpoint, args.input,
                 args.certificate, args.scratch, args.verified_seal,
                 args.exact_progress, args.compaction)
    if args.report.resolve() in {p.resolve() for p in protected}:
        ap.error("Replay report cannot overwrite any input")
    if args.resume != args.report.exists():
        raise RuntimeError("Use --resume for existing replay report")
    initial, rem, trace, rows, keys = context(args)
    cfg = identity_config(args, initial, rem, trace, keys)
    if args.resume:
        progress = json.loads(args.report.read_text(encoding="utf-8-sig"))
        if (progress.get("version") != 1 or progress.get("config") != cfg
            or progress.get("status") != "EXACT_IBP_REPLAY_PREFIX_NOT_TARGET_PROOF"
            or type(progress.get("checked")) is not int
            or not 0 <= progress["checked"] <= len(keys)
            or progress.get("exact_target_proven") is not False):
            raise RuntimeError("Existing replay progress/status/hash mismatch")
    else:
        progress = {"version": 1, "config": cfg,
                    "status": "EXACT_IBP_REPLAY_PREFIX_NOT_TARGET_PROOF",
                    "checked": 0, "exact_target_proven": False,
                    "original_ibp_replay_verified": False,
                    "formal_target_state_modified": False,
                    "protected_source_checkpoint_modified": False}
        atomic_save(args.report, progress, False)
    start = time.monotonic()
    print("VP05_STEP51_EXACT_REPLAY " + json.dumps({
        "event": "START", "columns": len(keys), "already_checked": progress["checked"],
        "remainder_terms": len(rem), "source_support": len(trace),
        "formal_expression_cap": CAP}), flush=True)
    while progress["checked"] < len(keys):
        if args.hours * 3600 - (time.monotonic() - start) < args.timeout_seconds + 30:
            break
        i = progress["checked"]
        cmd = [sys.executable, "-m",
               "examples.three_loop_vp05_sector202_step51_exact_ibp_replay",
               "--worker", "--worker-index", str(i),
               "--state", str(args.state), "--source-checkpoint", str(args.source_checkpoint),
               "--input", str(args.input), "--certificate", str(args.certificate),
               "--scratch", str(args.scratch), "--verified-seal", str(args.verified_seal),
               "--exact-progress", str(args.exact_progress), "--compaction", str(args.compaction)]
        try:
            proc = subprocess.run(cmd, text=True, capture_output=True,
                                  timeout=args.timeout_seconds, check=False)
        except subprocess.TimeoutExpired:
            print("VP05_STEP51_EXACT_REPLAY " + json.dumps({
                "event": "COLUMN_TIMEOUT_NOT_PROOF", "column_index": i}), flush=True)
            break
        if proc.returncode:
            print("VP05_STEP51_EXACT_REPLAY " + json.dumps({
                "event": "COLUMN_ERROR_NOT_PROOF", "column_index": i,
                "returncode": proc.returncode,
                "stderr_tail": proc.stderr[-1400:]}), flush=True)
            break
        result = json.loads(proc.stdout)
        if (result.get("index") != i or result.get("key") != list(keys[i])
            or result.get("exact_zero") is not True):
            raise RuntimeError("Worker output mismatch")
        progress["checked"] = i + 1
        atomic_save(args.report, progress, True)
        print("VP05_STEP51_EXACT_REPLAY " + json.dumps({
            "event": "COLUMN_EXACT_PASS", "checked": i + 1,
            "columns": len(keys), "elapsed_seconds": round(time.monotonic()-start, 2)}),
            flush=True)
    complete = progress["checked"] == len(keys)
    # Completed replay proves the full identity, NOT that Target A vanishes.
    if complete:
        progress["original_ibp_replay_verified"] = True
        atomic_save(args.report, progress, True)
    print("VP05_STEP51_EXACT_REPLAY " + json.dumps({
        "event": ("EXACT_ORIGINAL_IBP_REPLAY_PASS_WITH_NONZERO_REMAINDER_NOT_TARGET_PROOF"
                  if complete and rem else
                  "EXACT_ORIGINAL_IBP_REPLAY_PASS_ZERO_REMAINDER_REVIEW_REQUIRED"
                  if complete else "BOUNDED_STOP_RESUMABLE_NOT_TARGET_PROOF"),
        "checked": progress["checked"], "columns": len(keys),
        "remaining_terms": len(rem),
        "original_ibp_replay_verified": complete,
        "exact_target_proven": False, "formal_target_state_modified": False}),
        flush=True)


if __name__ == "__main__":
    main()
