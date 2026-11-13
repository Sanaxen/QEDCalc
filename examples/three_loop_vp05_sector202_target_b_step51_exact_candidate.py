"""Read-only, resumable exact coefficient pilot for VP05 Target B Step51.

Start from the saved canonical Step50 cap-stop state. Each child process
computes one rational coefficient, optionally shortens its representation,
and independently verifies the algebraic update before recording it.
Neither formal target state nor protected source checkpoint is written.
This pilot does NOT prove the full original-IBP replay or Target B.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import sympy as sp
from sympy.polys.polyerrors import PolynomialError
from examples.three_loop_vp05_sector202_target_b_start import B_STATE as STATE, A_STATE, A_PROOF, A_STATE_SHA, A_PROOF_SHA
from examples.three_loop_vp05_sector202_step51_scratch import atomic_save, key_id
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT, sha,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr

OUT = BASE / "vp05_sector202_A_target_b_step51_exact_coefficients_candidate.json"
KNOWN_B_STEP50_SHA = "f4c480ee9cd555549f690817c7f6cc4c8d80fcec329fa795e53ef5165955ba47"


def get_jobs(state, source):
    if (state.get("steps") != 50 or state.get("status") not in
            ("EXACT_TARGET_CAP_REACHED_NOT_PROOF", "EXACT_TARGET_PREFIX_NOT_PROOF")
            or state.get("exact_target_proven") is not False
            or state.get("config", {}).get("target") != "B"
            or len(state.get("remaining", [])) != 102
            or len(state.get("source", [])) != 185
            or state.get("config", {}).get("max_expression_chars") != 7500):
        raise RuntimeError("Expected preserved Step52 Target B after cap stop")
    lead = min(tuple(k) for k, _ in state["remaining"])
    matches = [p for p in source["pivots"] if tuple(p["lead"]) == lead]
    if len(matches) != 1:
        raise RuntimeError("Missing or duplicate Step51 pivot")
    pivot = matches[0]
    jobs = [("remainder", tuple(k), v) for k, v in pivot["row"]]
    jobs += [("source_trace", int(k), v) for k, v in pivot["trace"]]
    if len({key_id(kind, key) for kind, key, _ in jobs}) != len(jobs):
        raise RuntimeError("Duplicate Step51 coefficient operation")
    return lead, pivot, jobs


def exact_coefficient(previous, factor, pivot_coefficient, sign, cap=7500):
    """Compute the exact rational coefficient and check the local equality."""
    z, d = sp.symbols("z d")
    prev = expr(previous, z, d)
    fac = expr(factor, z, d)
    piv = expr(pivot_coefficient, z, d)
    raw = sp.cancel(prev + sign * fac * piv)
    if raw == 0:
        return "0", 0, False
    candidates = [str(raw)]
    if len(candidates[0]) > cap:
        for transform in (sp.factor_terms, sp.factor, sp.together):
            try:
                v = str(transform(raw))
                if len(v) < len(candidates[0]):
                    candidates.append(v)
            except (ValueError, TypeError, NotImplementedError, PolynomialError):
                pass
    best = min(candidates, key=len)
    if sp.cancel(expr(best, z, d) - (prev + sign * fac * piv)) != 0:
        raise AssertionError("Exact coefficient identity mismatch")
    return best, len(candidates[0]), len(best) < len(candidates[0])


def worker(index, state, pivot, jobs):
    if not 0 <= index < len(jobs):
        raise RuntimeError("Invalid worker index")
    kind, key, pivot_value = jobs[index]
    prior = (
        {tuple(k): v for k, v in state["remaining"]}
        if kind == "remainder" else
        {int(k): v for k, v in state["source"]}
    )
    lead = min(tuple(k) for k, _ in state["remaining"])
    factor = {tuple(k): v for k, v in state["remaining"]}[lead]
    old = prior.get(key, "0")
    val, raw_chars, shortened = exact_coefficient(
        old, factor, pivot_value, -1 if kind == "remainder" else 1)
    result = {"index": index, "id": key_id(kind, key), "kind": kind,
              "key": list(key) if kind == "remainder" else key,
              "value": val, "chars": len(val), "raw_chars": raw_chars,
              "shortened": shortened, "exact_local_identity": True,
              "within_formal_cap": len(val) <= 7500}
    print(json.dumps(result), flush=True)


def load_context(args):
    h = sha(args.state)
    if h != KNOWN_B_STEP50_SHA:
        raise RuntimeError("Step52 state SHA does not match audited log")
    state = json.loads(args.state.read_text(encoding="utf-8-sig"))
    if sha(A_STATE) != A_STATE_SHA or sha(A_PROOF) != A_PROOF_SHA:
        raise RuntimeError("Protected Target A state/proof hash mismatch")
    checkpoint = json.loads(args.source_checkpoint.read_text(encoding="utf-8-sig"))
    config = state["config"]
    if (config.get("source_checkpoint_sha256") != sha(args.source_checkpoint)
            or config.get("source_sha256") != sha(args.input)
            or config.get("certificate_sha256") != sha(args.certificate)):
        raise RuntimeError("Protected original inputs changed")
    lead, pivot, jobs = get_jobs(state, checkpoint)
    binding = {
        "target_sha256": h,
        "source_checkpoint_sha256": sha(args.source_checkpoint),
        "source_sha256": sha(args.input),
        "certificate_sha256": sha(args.certificate),
        "lead": list(lead), "jobs": [key_id(k, i) for k, i, _ in jobs],
        "formal_cap": 7500, "a_state_sha256": A_STATE_SHA,
        "a_proof_sha256": A_PROOF_SHA,
    }
    return state, pivot, jobs, binding


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=STATE)
    ap.add_argument("--source-checkpoint", type=Path, default=CHECKPOINT)
    ap.add_argument("--input", type=Path, default=SOURCE)
    ap.add_argument("--certificate", type=Path, default=CERT)
    ap.add_argument("--output", type=Path, default=OUT)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--hours", type=float, default=12)
    ap.add_argument("--timeout-seconds", type=int, default=600)
    ap.add_argument("--max-new-coefficients", type=int, default=300)
    ap.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--worker-index", type=int, default=-1, help=argparse.SUPPRESS)
    args = ap.parse_args()
    state, pivot, jobs, binding = load_context(args)
    if args.worker:
        worker(args.worker_index, state, pivot, jobs)
        return
    if not 0 < args.hours <= 12 or not 30 <= args.timeout_seconds <= 1800:
        ap.error("hours (0,12], timeout-seconds 30..1800")
    if not 1 <= args.max_new_coefficients <= 1000:
        ap.error("max-new-coefficients 1..1000")
    protected = (args.state, args.source_checkpoint, args.input, args.certificate)
    if args.output.resolve() in {p.resolve() for p in protected}:
        ap.error("Output must be independent of all protected inputs")
    if args.output.exists() != args.resume:
        raise RuntimeError("Use --resume when candidate exists; otherwise start fresh")
    if args.resume:
        progress = json.loads(args.output.read_text(encoding="utf-8-sig"))
        if (progress.get("version") != 1 or progress.get("config") != binding
                or progress.get("status") != "B_STEP51_EXACT_COEFFICIENT_PREFIX_NOT_PROOF"
                or progress.get("exact_target_proven") is not False
                or not isinstance(progress.get("done"), list)
                or len(progress["done"]) > len(jobs)
                or [r.get("id") for r in progress["done"]] !=
                    binding["jobs"][:len(progress["done"])]):
            raise RuntimeError("Candidate progress not compatible with source")
    else:
        progress = {
            "version": 1, "status": "B_STEP51_EXACT_COEFFICIENT_PREFIX_NOT_PROOF",
            "config": binding, "done": [], "exact_target_proven": False,
            "formal_target_state_modified": False,
            "protected_source_checkpoint_modified": False,
        }
        atomic_save(args.output, progress, False)
    start = time.monotonic()
    new = 0
    print("VP05_B_STEP51_EXACT_CANDIDATE " + json.dumps({
        "event": "START", "total": len(jobs),
        "already_verified": len(progress["done"]),
        "cap": 7500, "hours": args.hours}), flush=True)
    while len(progress["done"]) < len(jobs) and new < args.max_new_coefficients:
        if args.hours * 3600 - (time.monotonic() - start) < args.timeout_seconds + 30:
            break
        index = len(progress["done"])
        cmd = [sys.executable, "-m",
               "examples.three_loop_vp05_sector202_target_b_step51_exact_candidate",
               "--worker", "--worker-index", str(index),
               "--state", str(args.state), "--source-checkpoint",
               str(args.source_checkpoint), "--input", str(args.input),
               "--certificate", str(args.certificate)]
        try:
            run = subprocess.run(cmd, text=True, capture_output=True,
                                 check=False, timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            print("VP05_B_STEP51_EXACT_CANDIDATE " + json.dumps({
                "event": "WORKER_TIMEOUT_NOT_PROOF", "index": index}), flush=True)
            break
        if run.returncode:
            print("VP05_B_STEP51_EXACT_CANDIDATE " + json.dumps({
                "event": "WORKER_ERROR_NOT_PROOF", "index": index,
                "stderr_tail": run.stderr[-1500:]}), flush=True)
            break
        item = json.loads(run.stdout)
        kind, key, _ = jobs[index]
        if (item.get("index") != index or item.get("id") != key_id(kind, key)
                or item.get("exact_local_identity") is not True
                or item.get("chars") != len(item.get("value", ""))):
            raise RuntimeError("Inconsistent worker result")
        progress["done"].append(item)
        atomic_save(args.output, progress, True)
        new += 1
        print("VP05_B_STEP51_EXACT_CANDIDATE " + json.dumps({
            "event": "EXACT_COEFFICIENT_PASS", "checked": len(progress["done"]),
            "total": len(jobs), "chars": item["chars"],
            "within_formal_cap": item["within_formal_cap"],
            "elapsed_seconds": round(time.monotonic() - start, 2)}), flush=True)
    if sha(A_STATE) != A_STATE_SHA or sha(A_PROOF) != A_PROOF_SHA:
        raise RuntimeError("Protected Target A changed during pilot")
    complete = len(progress["done"]) == len(jobs)
    above = [r for r in progress["done"] if not r["within_formal_cap"]]
    print("VP05_B_STEP51_EXACT_CANDIDATE " + json.dumps({
        "event": ("ALL_LOCAL_IDENTITIES_PASS_PENDING_FULL_IBP_REPLAY"
                  if complete else "BOUNDED_PREFIX_NOT_PROOF"),
        "checked": len(progress["done"]), "total": len(jobs),
        "still_oversized": len(above),
        "max_saved_chars": max((r["chars"] for r in progress["done"]), default=0),
        "exact_target_proven": False, "formal_target_state_modified": False}),
        flush=True)


if __name__ == "__main__":
    main()
