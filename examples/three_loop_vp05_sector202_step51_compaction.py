"""Bounded read-only Step51 coefficient compaction, with exact equivalence checks.

Requires completed 288/288 exact-identity checkpoint. Writes only an independent
candidate report; it does not promote Step51 or prove original-IBP replay.
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
    atomic_save,
)
from examples.three_loop_vp05_sector202_step51_candidate_audit import materialize
from examples.three_loop_vp05_sector202_step51_exact_coefficient_audit import (
    PROGRESS as EXACT_PROGRESS, check_progress, checkpoint_config, audit_config,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT, sha,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr

OUT = BASE / "vp05_sector202_A_step51_compaction_candidate.json"
CAP = 7500


def compact_exact(raw, cap=CAP):
    """Only return candidates with an independent exact rational identity."""
    z, d = sp.symbols("z d")
    original = expr(raw, z, d)
    forms = []
    for transform in (sp.factor, sp.factor_terms, sp.together):
        try:
            alternative = str(transform(original))
            if len(alternative) <= cap and alternative not in forms:
                forms.append(alternative)
        except (ValueError, TypeError, NotImplementedError, PolynomialError):
            continue
    for candidate in sorted(forms, key=len):
        if sp.cancel(expr(candidate, z, d) - original) == 0:
            return candidate
    return None


# Avoid referring to PolynomialError through a nonexistent sympy top-level attribute.
from sympy.polys.polyerrors import PolynomialError


def entries(target, scratch, jobs):
    rem, trace = materialize(target, scratch, jobs)
    values = [("remainder", list(k), v) for k, v in sorted(rem.items())]
    values += [("source_trace", rid, v) for rid, v in sorted(trace.items())]
    return values


def validate(args):
    target = json.loads(args.state.read_text(encoding="utf-8-sig"))
    scratch = json.loads(args.scratch.read_text(encoding="utf-8-sig"))
    jobs = audit_config(args, target, scratch)
    exact = json.loads(args.exact_progress.read_text(encoding="utf-8-sig"))
    c = checkpoint_config(args)
    check_progress(exact, c)
    if exact["verified_count"] != len(jobs) or len(jobs) != 288:
        raise RuntimeError("Require completed exact 288/288 identity audit")
    all_entries = entries(target, scratch, jobs)
    oversized = [(kind, key, raw) for kind, key, raw in all_entries if len(raw) > CAP]
    cfg = {"state_sha256": sha(args.state),
           "source_checkpoint_sha256": sha(args.source_checkpoint),
           "source_sha256": sha(args.input),
           "certificate_sha256": sha(args.certificate),
           "scratch_sha256": sha(args.scratch),
           "seal_sha256": sha(args.verified_seal),
           "exact_progress_sha256": sha(args.exact_progress),
           "cap": CAP,
           "total_candidate_entries": len(all_entries),
           "oversized_count": len(oversized)}
    return cfg, all_entries, oversized


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=STATE)
    ap.add_argument("--source-checkpoint", type=Path, default=CHECKPOINT)
    ap.add_argument("--input", type=Path, default=SOURCE)
    ap.add_argument("--certificate", type=Path, default=CERT)
    ap.add_argument("--scratch", type=Path, default=SCRATCH)
    ap.add_argument("--verified-seal", type=Path, default=SEAL)
    ap.add_argument("--exact-progress", type=Path, default=EXACT_PROGRESS)
    ap.add_argument("--output", type=Path, default=OUT)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--hours", type=float, default=12)
    ap.add_argument("--timeout-seconds", type=int, default=600)
    ap.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--worker-index", type=int, default=-1, help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.worker:
        _, _, oversized = validate(args)
        if not 0 <= args.worker_index < len(oversized):
            raise RuntimeError("Invalid compaction worker index")
        kind, key, raw = oversized[args.worker_index]
        compact = compact_exact(raw)
        print(json.dumps({"index": args.worker_index,
                          "kind": kind, "key": key, "original_chars": len(raw),
                          "compacted": compact,
                          "compacted_chars": len(compact) if compact is not None else None}),
              flush=True)
        return
    if not 0 < args.hours <= 12 or not 30 <= args.timeout_seconds <= 1800:
        ap.error("Hours must be (0,12]; timeout-seconds must be 30..1800")
    protected = (args.state, args.source_checkpoint, args.input, args.certificate,
                 args.scratch, args.verified_seal, args.exact_progress)
    if args.output.resolve() in {x.resolve() for x in protected}:
        ap.error("Candidate output must not overwrite protected inputs")
    if args.resume != args.output.exists():
        raise RuntimeError("Use --resume only when independent candidate already exists")
    cfg, all_entries, oversized = validate(args)
    if args.resume:
        progress = json.loads(args.output.read_text(encoding="utf-8-sig"))
        if (progress.get("config") != cfg or progress.get("version") != 1
            or progress.get("status") != "STEP51_COMPACTION_CANDIDATE_NOT_PROOF"
            or progress.get("exact_target_proven") is not False
            or type(progress.get("processed")) is not int
            or not 0 <= progress["processed"] <= len(oversized)
            or len(progress.get("results", [])) != progress["processed"]):
            raise RuntimeError("Compaction candidate hash/status/count mismatch")
    else:
        progress = {"version": 1, "status": "STEP51_COMPACTION_CANDIDATE_NOT_PROOF",
                    "config": cfg, "processed": 0, "results": [],
                    "exact_target_proven": False,
                    "formal_target_state_modified": False,
                    "protected_source_checkpoint_modified": False}
        atomic_save(args.output, progress, False)
    start = time.monotonic()
    print("VP05_STEP51_COMPACTION " + json.dumps({
        "event": "START", "total_entries": len(all_entries),
        "oversized": len(oversized), "already_processed": progress["processed"]}), flush=True)
    while progress["processed"] < len(oversized):
        if args.hours * 3600 - (time.monotonic() - start) < args.timeout_seconds + 30:
            break
        index = progress["processed"]
        cmd = [sys.executable, "-m",
               "examples.three_loop_vp05_sector202_step51_compaction",
               "--worker", "--worker-index", str(index),
               "--state", str(args.state),
               "--source-checkpoint", str(args.source_checkpoint),
               "--input", str(args.input), "--certificate", str(args.certificate),
               "--scratch", str(args.scratch), "--verified-seal",
               str(args.verified_seal), "--exact-progress", str(args.exact_progress)]
        try:
            result = subprocess.run(cmd, text=True, capture_output=True,
                                    check=False, timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            print("VP05_STEP51_COMPACTION " + json.dumps({
                "event": "WORKER_TIMEOUT_NOT_PROOF", "index": index}), flush=True)
            break
        if result.returncode:
            print("VP05_STEP51_COMPACTION " + json.dumps({
                "event": "WORKER_ERROR_NOT_PROOF", "index": index,
                "stderr_tail": result.stderr[-1200:]}), flush=True)
            break
        answer = json.loads(result.stdout)
        kind, key, raw = oversized[index]
        if (answer.get("index") != index or answer.get("kind") != kind
            or answer.get("key") != key or answer.get("original_chars") != len(raw)
            or (answer.get("compacted") is not None
                and (not isinstance(answer["compacted"], str)
                     or answer.get("compacted_chars") != len(answer["compacted"])
                     or len(answer["compacted"]) > CAP))):
            raise RuntimeError("Compaction worker output mismatch")
        progress["results"].append(answer)
        progress["processed"] += 1
        atomic_save(args.output, progress, True)
        print("VP05_STEP51_COMPACTION " + json.dumps({
            "event": "EXACT_COMPACTION_PASS" if answer["compacted"] is not None
                     else "NO_SHORTER_FORM_FOUND",
            "processed": progress["processed"], "total": len(oversized),
            "old_chars": len(raw), "new_chars": answer["compacted_chars"]}),
            flush=True)
    complete = progress["processed"] == len(oversized)
    unresolved = sum(1 for r in progress["results"] if r["compacted"] is None)
    print("VP05_STEP51_COMPACTION " + json.dumps({
        "event": ("ALL_OVERSIZED_EXPRESSIONS_COMPACTED_EXACTLY_NOT_TARGET_PROOF"
                  if complete and unresolved == 0 else
                  "COMPACTION_INCOMPLETE_OR_UNRESOLVED_NOT_TARGET_PROOF"),
        "processed": progress["processed"], "oversized": len(oversized),
        "unresolved": unresolved, "exact_target_proven": False,
        "formal_target_state_modified": False}), flush=True)


if __name__ == "__main__":
    main()
