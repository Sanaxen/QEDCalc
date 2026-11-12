"""Resumable exact original-IBP column replay for completed Step53 candidate.

Checks ALL integral columns of initial_A == R53 + sum(trace53 * original_IBP).
This proves a representation identity only; 101 nonzero residual terms remain.
Never modifies formal Target A step52 or any protected input.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import sympy as sp

from examples.three_loop_vp05_sector202_step51_scratch import STATE, atomic_save, key_id
from examples.three_loop_vp05_sector202_step53_exact_candidate import (
    OUT as CANDIDATE, load_context,
)
from examples.three_loop_vp05_sector202_step51_exact_ibp_replay import (
    initial_a, original_terms, key_index, verify_column,
)
from examples.three_loop_vp05_sector202_target_exact_checkpoint import encoded
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT, sha,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr

REPORT = BASE / "vp05_sector202_A_step53_exact_original_ibp_replay.json"
CAP = 7500


def materialize(state, jobs, candidate):
    done = candidate["done"]
    if len(done) != len(jobs) or len(jobs) != 292:
        raise RuntimeError("Require 292/292 completed local exact coefficients")
    rem = {tuple(k): v for k, v in state["remaining"]}
    trace = {int(k): v for k, v in state["source"]}
    for i, ((kind, key, _), record) in enumerate(zip(jobs, done)):
        actual_key = list(key) if kind == "remainder" else key
        val = record.get("value")
        if (record.get("index") != i or record.get("id") != key_id(kind, key)
            or record.get("kind") != kind or record.get("key") != actual_key
            or record.get("exact_local_identity") is not True
            or record.get("within_formal_cap") is not True
            or not isinstance(val, str) or record.get("chars") != len(val)
            or len(val) > CAP):
            raise RuntimeError("Invalid saved local coefficient at index %s" % i)
        mapping = rem if kind == "remainder" else trace
        if val == "0":
            mapping.pop(key, None)
        else:
            mapping[key] = val
    if (len(rem) != 101 or len(trace) != 188
        or max(map(len, list(rem.values())+list(trace.values())), default=0) > CAP):
        raise RuntimeError("Expected Step53 remainder101 and source188 under formal cap")
    oldlead = min(tuple(k) for k, _ in state["remaining"])
    if oldlead in rem or min(rem) <= oldlead:
        raise RuntimeError("Step53 leading pivot not eliminated")
    return rem, trace


def context(args):
    state, pivot, jobs, binding = load_context(args)
    candidate = json.loads(args.candidate.read_text(encoding="utf-8-sig"))
    if (candidate.get("version") != 1
        or candidate.get("status") != "STEP53_EXACT_COEFFICIENT_PREFIX_NOT_PROOF"
        or candidate.get("config") != binding
        or candidate.get("exact_target_proven") is not False):
        raise RuntimeError("Candidate config/hashes/status mismatch")
    rem, trace = materialize(state, jobs, candidate)
    initial = initial_a()
    z, d = sp.symbols("z d")
    digest = hashlib.sha256(
        json.dumps(encoded({k: expr(v, z, d) for k, v in initial.items()})).encode()
    ).hexdigest()
    if digest != state["config"]["initial_sha256"]:
        raise RuntimeError("Initial Target A hash mismatch")
    rows = original_terms(args.input, trace)
    keys = key_index(initial, rem, rows)
    return rem, trace, initial, rows, keys


def config(args, initial, keys):
    return {
        "state_sha256": sha(args.state),
        "checkpoint_sha256": sha(args.source_checkpoint),
        "source_sha256": sha(args.input),
        "certificate_sha256": sha(args.certificate),
        "candidate_sha256": sha(args.candidate),
        "initial_sha256": hashlib.sha256(json.dumps(
            [[list(k), v] for k, v in sorted(initial.items())],
            separators=(",", ":")).encode()).hexdigest(),
        "keys_sha256": hashlib.sha256(json.dumps(
            [list(k) for k in keys], separators=(",", ":")).encode()).hexdigest(),
        "column_count": len(keys), "cap": CAP,
    }


def check_progress(progress, expected):
    if (progress.get("version") != 1
        or progress.get("config") != expected
        or progress.get("status") != "STEP53_EXACT_IBP_REPLAY_PREFIX_NOT_TARGET_PROOF"
        or type(progress.get("checked")) is not int
        or not 0 <= progress["checked"] <= expected["column_count"]
        or progress.get("exact_target_proven") is not False
        or progress.get("formal_target_state_modified") is not False):
        raise RuntimeError("Replay progress hash/status/count mismatch")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=STATE)
    ap.add_argument("--source-checkpoint", type=Path, default=CHECKPOINT)
    ap.add_argument("--input", type=Path, default=SOURCE)
    ap.add_argument("--certificate", type=Path, default=CERT)
    ap.add_argument("--candidate", type=Path, default=CANDIDATE)
    ap.add_argument("--report", type=Path, default=REPORT)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--hours", type=float, default=12)
    ap.add_argument("--timeout-seconds", type=int, default=1800)
    ap.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--worker-index", type=int, default=-1, help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.worker:
        rem, trace, initial, rows, keys = context(args)
        i = args.worker_index
        if not 0 <= i < len(keys):
            raise RuntimeError("Invalid worker column index")
        if not verify_column(keys[i], initial, rem, trace, rows):
            raise AssertionError("Exact original-IBP identity failed at " + str(keys[i]))
        print(json.dumps({"index": i, "key": list(keys[i]), "exact_zero": True}), flush=True)
        return
    if not 0 < args.hours <= 12 or not 30 <= args.timeout_seconds <= 1800:
        ap.error("hours (0,12], timeout-seconds 30..1800")
    protected = (args.state, args.source_checkpoint, args.input,
                 args.certificate, args.candidate)
    if args.report.resolve() in {p.resolve() for p in protected}:
        ap.error("Replay report must be separate from protected inputs")
    if args.resume != args.report.exists():
        raise RuntimeError("Use --resume only for existing independent replay report")
    rem, trace, initial, rows, keys = context(args)
    cfg = config(args, initial, keys)
    if args.resume:
        progress = json.loads(args.report.read_text(encoding="utf-8-sig"))
        check_progress(progress, cfg)
    else:
        progress = {
            "version": 1,
            "status": "STEP53_EXACT_IBP_REPLAY_PREFIX_NOT_TARGET_PROOF",
            "config": cfg, "checked": 0,
            "original_ibp_replay_verified": False,
            "exact_target_proven": False,
            "formal_target_state_modified": False,
            "protected_source_checkpoint_modified": False,
        }
        atomic_save(args.report, progress, False)
    begin = time.monotonic()
    print("VP05_STEP53_EXACT_REPLAY " + json.dumps({
        "event": "START", "columns": len(keys),
        "already_checked": progress["checked"],
        "remainder_terms": len(rem), "source_support": len(trace)}), flush=True)
    while progress["checked"] < len(keys):
        remaining = args.hours*3600-(time.monotonic()-begin)
        if remaining < args.timeout_seconds+30:
            break
        i = progress["checked"]
        command = [sys.executable, "-m",
                   "examples.three_loop_vp05_sector202_step53_exact_ibp_replay",
                   "--worker", "--worker-index", str(i),
                   "--state", str(args.state),
                   "--source-checkpoint", str(args.source_checkpoint),
                   "--input", str(args.input),
                   "--certificate", str(args.certificate),
                   "--candidate", str(args.candidate)]
        try:
            p = subprocess.run(command, capture_output=True, text=True,
                               timeout=args.timeout_seconds, check=False)
        except subprocess.TimeoutExpired:
            print("VP05_STEP53_EXACT_REPLAY " + json.dumps({
                "event": "COLUMN_TIMEOUT_NOT_PROOF", "column_index": i}), flush=True)
            break
        if p.returncode:
            print("VP05_STEP53_EXACT_REPLAY " + json.dumps({
                "event": "COLUMN_ERROR_NOT_PROOF", "column_index": i,
                "returncode": p.returncode, "stderr_tail": p.stderr[-1500:]}), flush=True)
            break
        result = json.loads(p.stdout)
        if result != {"index": i, "key": list(keys[i]), "exact_zero": True}:
            raise RuntimeError("Replay worker output mismatch")
        progress["checked"] = i+1
        atomic_save(args.report, progress, True)
        print("VP05_STEP53_EXACT_REPLAY " + json.dumps({
            "event": "COLUMN_EXACT_PASS", "checked": progress["checked"],
            "columns": len(keys),
            "elapsed_seconds": round(time.monotonic()-begin, 2)}), flush=True)
    done = progress["checked"] == len(keys)
    if done:
        progress["original_ibp_replay_verified"] = True
        atomic_save(args.report, progress, True)
    print("VP05_STEP53_EXACT_REPLAY " + json.dumps({
        "event": ("EXACT_ORIGINAL_IBP_REPLAY_PASS_WITH_NONZERO_REMAINDER_NOT_TARGET_PROOF"
                  if done else "BOUNDED_STOP_RESUMABLE_NOT_TARGET_PROOF"),
        "checked": progress["checked"], "columns": len(keys),
        "remaining_terms": len(rem),
        "original_ibp_replay_verified": done,
        "exact_target_proven": False,
        "formal_target_state_modified": False}), flush=True)


if __name__ == "__main__":
    main()
