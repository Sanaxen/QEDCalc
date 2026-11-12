"""Guarded formal promotion of EXACTLY audited VP05 Target A Step53.

Requires 292 exact local updates and 369/369 strict original-IBP columns.
Preserves byte-identical Step52 backup, atomically updates only Target A.
The nonzero 101-term residual means Target A is NOT fully proved.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path

from examples.three_loop_vp05_sector202_step51_scratch import STATE, atomic_save
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    CHECKPOINT, SOURCE, CERT, sha,
)
from examples.three_loop_vp05_sector202_step53_exact_candidate import OUT as CANDIDATE, load_context
from examples.three_loop_vp05_sector202_step53_exact_ibp_replay import (
    REPORT, CAP, context, config as replay_config, check_progress,
)

EXPECTED_STEP52_SHA = "743ecc699f5da7f511ac886bce41cdf6cdaf7e999db72f77ecfb8537c61d3715"
BACKUP = STATE.with_name("vp05_sector202_A_exact_target_state_step52_backup.json")


def validate_complete_replay(report, cfg, nkeys):
    check_progress(report, cfg)
    if (nkeys != 369 or report["checked"] != nkeys
        or report.get("original_ibp_replay_verified") is not True
        or report.get("protected_source_checkpoint_modified") is not False):
        raise RuntimeError("369/369 strict original IBP replay is required")


def build_promoted(old, rem, trace, pivot_lead):
    if (old.get("steps") != 52 or old.get("config", {}).get("target") != "A"
        or old.get("status") not in (
            "EXACT_TARGET_CAP_REACHED_NOT_PROOF", "EXACT_TARGET_PREFIX_NOT_PROOF")
        or old.get("exact_target_proven") is not False
        or len(old.get("pivot_path", [])) != 52):
        raise RuntimeError("Require canonical Target A exact Step52")
    if (not old.get("remaining") or
        min(tuple(k) for k, _ in old["remaining"]) != tuple(pivot_lead)
        or not rem or min(rem) <= tuple(pivot_lead)
        or tuple(pivot_lead) in rem):
        raise RuntimeError("Step53 pivot elimination invariant failed")
    if len(rem) != 101 or len(trace) != 188:
        raise RuntimeError("Unexpected Step53 candidate support")
    longest = max((len(v) for v in list(rem.values()) + list(trace.values())), default=0)
    if longest > CAP:
        raise RuntimeError("Formal expression cap exceeded")
    cfg = old["config"]
    if (cfg.get("max_expression_chars") != CAP or
        len(rem) > cfg["max_columns"] or len(trace) > cfg["max_support"] or
        53 > cfg["max_steps_total"]):
        raise RuntimeError("Formal safety caps violated")
    promoted = dict(old)
    promoted["status"] = "EXACT_TARGET_PREFIX_NOT_PROOF"
    promoted["steps"] = 53
    promoted["remaining"] = [[list(k), v] for k, v in sorted(rem.items())]
    promoted["source"] = [[k, v] for k, v in sorted(trace.items())]
    promoted["pivot_path"] = old["pivot_path"] + [list(pivot_lead)]
    row_max = max((len(v) for v in rem.values()), default=0)
    trace_max = max((len(v) for v in trace.values()), default=0)
    promoted["metrics"] = {
        "remainder_terms": len(rem), "original_support": len(trace),
        "row_expression_chars": row_max, "source_expression_chars": trace_max,
        "max_expression_chars": max(row_max, trace_max),
        "lead": list(min(rem)),
    }
    promoted["exact_target_proven"] = False
    promoted["original_source_replay_proven"] = False
    promoted["protected_source_checkpoint_modified"] = False
    promoted["step53_original_ibp_replay_verified"] = True
    promoted["step53_exact_coefficient_count"] = 292
    return promoted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=STATE)
    ap.add_argument("--source-checkpoint", type=Path, default=CHECKPOINT)
    ap.add_argument("--input", type=Path, default=SOURCE)
    ap.add_argument("--certificate", type=Path, default=CERT)
    ap.add_argument("--candidate", type=Path, default=CANDIDATE)
    ap.add_argument("--report", type=Path, default=REPORT)
    ap.add_argument("--backup", type=Path, default=BACKUP)
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    inputs = (args.state, args.source_checkpoint, args.input,
              args.certificate, args.candidate, args.report)
    if args.backup.resolve() in {p.resolve() for p in inputs}:
        ap.error("Backup must be separate from every protected input")
    if sha(args.state) != EXPECTED_STEP52_SHA:
        raise RuntimeError("Formal Step52 does not match saved cap-stop SHA")
    before = args.state.read_bytes()
    old = json.loads(before.decode("utf-8-sig"))
    state, pivot, jobs, binding = load_context(args)
    rem, trace, initial, rows, keys = context(args)
    candidate = json.loads(args.candidate.read_text(encoding="utf-8-sig"))
    if (candidate.get("config") != binding
        or len(candidate.get("done", [])) != 292):
        raise RuntimeError("Missing 292 local strict coefficient identities")
    progress = json.loads(args.report.read_text(encoding="utf-8-sig"))
    validate_complete_replay(progress, replay_config(args, initial, keys), len(keys))
    lead = min(tuple(k) for k, _ in state["remaining"])
    if tuple(pivot["lead"]) != lead:
        raise RuntimeError("Step53 pivot not the first remaining integral")
    promoted = build_promoted(old, rem, trace, lead)
    result = {
        "status": "STEP53_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF",
        "steps_before": 52, "steps_after": 53,
        "remainder_terms": len(rem), "original_support": len(trace),
        "max_expression_chars": promoted["metrics"]["max_expression_chars"],
        "replay_columns": len(keys), "source_sha256": sha(args.state),
        "replay_sha256": sha(args.report), "exact_target_proven": False,
    }
    if args.check_only:
        print("VP05_STEP53_FORMAL_PROMOTION " + json.dumps(result), flush=True)
        return
    if args.backup.exists() or args.state.with_name(args.state.name+".tmp").exists():
        raise FileExistsError("Step52 backup or promotion temp already exists")
    args.backup.parent.mkdir(parents=True, exist_ok=True)
    with args.backup.open("xb") as handle:
        handle.write(before)
        handle.flush()
        os.fsync(handle.fileno())
    if args.backup.read_bytes() != before or args.state.read_bytes() != before:
        raise RuntimeError("Step52 backup mismatch or concurrent update")
    atomic_save(args.state, promoted, True)
    if json.loads(args.state.read_text(encoding="utf-8-sig")) != promoted:
        raise RuntimeError("Post-promotion verification failed")
    result["status"] = "STEP53_FORMAL_PREFIX_PROMOTED_WITH_BACKUP_NOT_TARGET_PROOF"
    result["backup_sha256"] = sha(args.backup)
    result["new_state_sha256"] = sha(args.state)
    print("VP05_STEP53_FORMAL_PROMOTION " + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
