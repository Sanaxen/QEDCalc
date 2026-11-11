"""Resumable EXACT symbolic identity audit of Step51 saved coefficients.

Checks each saved rational function against the actual Step50 elimination
operation, with isolated timeout-bounded workers. Never edits formal target,
original source checkpoint, or the completed scratch/seal. A PASS here proves
only the 288 local algebraic identities, not the full original-IBP target.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_step51_scratch import (
    STATE, SCRATCH, SEAL, source_context, scratch_config, seal_matches,
    key_id, atomic_save,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT, sha,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr

PROGRESS = BASE / "vp05_sector202_A_step51_exact_coefficient_audit_progress.json"


def identity_difference(saved_value, previous, factor, pivot, sign):
    """Return zero iff saved_value == previous + sign*factor*pivot."""
    z, d = sp.symbols("z d")
    saved = expr(saved_value, z, d)
    a = expr(previous, z, d)
    b = expr(factor, z, d)
    c = expr(pivot, z, d)
    return sp.cancel(saved - a - sign * b * c)


def raw_for(target, pivot, kind, key):
    if kind == "remainder":
        before = {tuple(k): v for k, v in target["remaining"]}
        term = {tuple(k): v for k, v in pivot["row"]}
        return before.get(tuple(key), "0"), term[tuple(key)], -1
    before = {int(k): v for k, v in target["source"]}
    term = {int(k): v for k, v in pivot["trace"]}
    return before.get(int(key), "0"), term[int(key)], 1


def run_worker(args):
    target = json.loads(args.state.read_text(encoding="utf-8-sig"))
    _, pivot, jobs = source_context(target, args.source_checkpoint)
    scratch = json.loads(args.scratch.read_text(encoding="utf-8-sig"))
    index = args.worker_index
    if not 0 <= index < len(jobs) or len(scratch["done"]) != len(jobs):
        raise RuntimeError("Worker index or scratch count invalid")
    kind, key, _ = jobs[index]
    record = scratch["done"][index]
    if record["id"] != key_id(kind, key):
        raise RuntimeError("Worker operation ID mismatch")
    factor = {tuple(k):v for k,v in target["remaining"]}[
        min(tuple(k) for k,_ in target["remaining"])]
    previous, pval, sign = raw_for(target, pivot, kind, key)
    diff = identity_difference(record["value"], previous, factor, pval, sign)
    if diff != 0:
        raise AssertionError("Nonzero EXACT rational-function difference: %s" % record["id"])
    print(json.dumps({"index": index + 1, "id": record["id"],
                      "exact_identity": True}), flush=True)


def audit_config(args, target, scratch):
    lead, pivot, jobs = source_context(target, args.source_checkpoint)
    config = scratch_config(args.state, args.source_checkpoint, args.input,
                            args.certificate, target, lead, jobs, 9000)
    if (scratch.get("version") != 1
        or scratch.get("status") != "INTRA_STEP51_SCRATCH_NOT_PROOF"
        or scratch.get("exact_target_proven") is not False
        or scratch.get("config") != config
        or len(scratch.get("done", [])) != len(jobs)
        or [record.get("id") for record in scratch["done"]] != config["operation_ids"]):
        raise RuntimeError("Scratch incomplete or invalid")
    for record in scratch["done"]:
        value = record.get("value")
        if (not isinstance(value, str) or record.get("chars") != len(value)
            or len(value) > config["scratch_max_expression_chars"]):
            raise RuntimeError("Invalid saved coefficient")
    if not seal_matches(args.verified_seal, args.scratch, config, scratch):
        raise RuntimeError("Scratch verified seal mismatch")
    if target.get("config", {}).get("max_expression_chars") != 7500:
        raise RuntimeError("Unexpected formal cap")
    return jobs


def checkpoint_config(args):
    return {
        "target_sha256": sha(args.state),
        "checkpoint_sha256": sha(args.source_checkpoint),
        "source_sha256": sha(args.input),
        "certificate_sha256": sha(args.certificate),
        "scratch_sha256": sha(args.scratch),
        "seal_sha256": sha(args.verified_seal),
        "operation_count": 288,
        "formal_expression_cap": 7500,
    }


def check_progress(progress, config):
    if (progress.get("version") != 1 or progress.get("config") != config
        or progress.get("status") != "EXACT_STEP51_COEFFICIENT_PREFIX_NOT_TARGET_PROOF"
        or progress.get("exact_target_proven") is not False
        or type(progress.get("verified_count")) is not int
        or not 0 <= progress["verified_count"] <= config["operation_count"]):
        raise RuntimeError("Exact audit progress/hashes mismatch")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=STATE)
    ap.add_argument("--source-checkpoint", type=Path, default=CHECKPOINT)
    ap.add_argument("--input", type=Path, default=SOURCE)
    ap.add_argument("--certificate", type=Path, default=CERT)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--verified-seal", type=Path, default=SEAL)
    ap.add_argument("--progress", type=Path, default=PROGRESS)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--hours", type=float, default=12)
    ap.add_argument("--timeout-seconds", type=int, default=600)
    ap.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--worker-index", type=int, default=-1, help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.worker:
        run_worker(args)
        return
    if not 0 < args.hours <= 12 or not 30 <= args.timeout_seconds <= 1800:
        ap.error("Limits: hours (0,12], per coefficient timeout 30..1800")
    protected = (args.state, args.source_checkpoint, args.input,
                 args.certificate, args.scratch, args.verified_seal)
    if args.progress.resolve() in {p.resolve() for p in protected}:
        ap.error("Progress must be separate from protected inputs")
    if args.resume != args.progress.exists():
        raise RuntimeError("Use --resume only for existing progress, or start fresh")
    target = json.loads(args.state.read_text(encoding="utf-8-sig"))
    scratch = json.loads(args.scratch.read_text(encoding="utf-8-sig"))
    jobs = audit_config(args, target, scratch)
    config = checkpoint_config(args)
    if args.resume:
        progress = json.loads(args.progress.read_text(encoding="utf-8-sig"))
        check_progress(progress, config)
    else:
        progress = {
            "version": 1,
            "status": "EXACT_STEP51_COEFFICIENT_PREFIX_NOT_TARGET_PROOF",
            "config": config, "verified_count": 0,
            "exact_target_proven": False,
            "formal_target_state_modified": False,
            "protected_source_checkpoint_modified": False,
        }
        atomic_save(args.progress, progress, False)
    start = time.monotonic()
    total = len(jobs)
    print("VP05_STEP51_EXACT_AUDIT " + json.dumps(
        {"event": "START", "verified_count": progress["verified_count"],
         "total": total, "hours_ceiling": args.hours,
         "timeout_seconds": args.timeout_seconds}), flush=True)
    while progress["verified_count"] < total:
        remaining = args.hours * 3600 - (time.monotonic() - start)
        if remaining < args.timeout_seconds + 30:
            break
        index = progress["verified_count"]
        cmd = [sys.executable, "-m",
               "examples.three_loop_vp05_sector202_step51_exact_coefficient_audit",
               "--worker", "--worker-index", str(index),
               "--state", str(args.state), "--source-checkpoint",
               str(args.source_checkpoint), "--scratch", str(args.scratch)]
        try:
            result = subprocess.run(cmd, text=True, capture_output=True,
                                    timeout=args.timeout_seconds, check=False)
        except subprocess.TimeoutExpired:
            print("VP05_STEP51_EXACT_AUDIT " + json.dumps(
                {"event": "WORKER_TIMEOUT_NOT_PROOF", "index": index + 1,
                 "verified_count": index}), flush=True)
            break
        if result.returncode:
            print("VP05_STEP51_EXACT_AUDIT " + json.dumps(
                {"event": "WORKER_ERROR_NOT_PROOF", "index": index + 1,
                 "returncode": result.returncode,
                 "stderr_tail": result.stderr[-1400:]}), flush=True)
            break
        data = json.loads(result.stdout)
        kind, key, _ = jobs[index]
        if (data.get("index") != index + 1
            or data.get("id") != key_id(kind, key)
            or data.get("exact_identity") is not True):
            raise AssertionError("Worker output inconsistent")
        progress["verified_count"] = index + 1
        atomic_save(args.progress, progress, True)
        print("VP05_STEP51_EXACT_AUDIT " + json.dumps(
            {"event": "EXACT_COEFFICIENT_PASS",
             "verified_count": index + 1, "total": total,
             "elapsed_seconds": round(time.monotonic() - start, 2)}),
             flush=True)
    print("VP05_STEP51_EXACT_AUDIT " + json.dumps({
        "event": ("ALL_288_EXACT_LOCAL_IDENTITIES_PASS_NOT_TARGET_PROOF"
                  if progress["verified_count"] == total
                  else "BOUNDED_STOP_RESUMABLE_NOT_TARGET_PROOF"),
        "verified_count": progress["verified_count"], "total": total,
        "formal_target_state_modified": False,
        "protected_source_checkpoint_modified": False,
        "exact_target_proven": False}), flush=True)


if __name__ == "__main__":
    main()
