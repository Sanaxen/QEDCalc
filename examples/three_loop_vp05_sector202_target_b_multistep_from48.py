"""Bounded multi-step exact Target B continuation from verified sector202 Step48.

The existing engine atomically saves EACH completed elimination. This outer
runner pins the exact state SHA and input artifact hashes before invoking up
to 16 consecutive steps (default 16). No proof is claimed from intermediate
states; a separate exact original-IBP proof artifact is mandatory.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from examples.three_loop_vp05_sector202_target_b_start import B_STATE as STATE, A_STATE, A_PROOF, A_STATE_SHA, A_PROOF_SHA
from examples.three_loop_vp05_sector202_target_exact_reduction import CHECKPOINT, SOURCE, CERT, sha

START_SHA = "0146b3c9be7dc6cdd59998956fb3897860619745fbdc445f677a058bd958e372"
START_STEP = 48
START_REMAINING = 57
START_SUPPORT = 99
START_LEAD = [166595341058050, 139]
START_MAX_CHARS = 2496


def validate_start(path=STATE, checkpoint=CHECKPOINT, source=SOURCE, certificate=CERT):
    if sha(path) != START_SHA:
        raise RuntimeError("Expected exact saved Step48 SHA256; no multi-step computation started")
    state = json.loads(path.read_text(encoding="utf-8-sig"))
    cfg = state.get("config", {})
    if (state.get("steps") != START_STEP
        or state.get("status") != "EXACT_TARGET_PREFIX_NOT_PROOF"
        or state.get("exact_target_proven") is not False
        or cfg.get("target") != "B"
        or len(state.get("remaining", [])) != START_REMAINING
        or len(state.get("source", [])) != START_SUPPORT
        or len(state.get("pivot_path", [])) != START_STEP
        or state.get("metrics", {}).get("lead") != START_LEAD
        or max((len(v) for _,v in state["remaining"] + state["source"]),default=0) != START_MAX_CHARS
        or cfg.get("max_expression_chars") != 7500
        or cfg.get("max_columns") != 256
        or cfg.get("max_support") != 400
        or cfg.get("source_checkpoint_sha256") != sha(checkpoint)
        or cfg.get("source_sha256") != sha(source)
        or cfg.get("certificate_sha256") != sha(certificate)):
        raise RuntimeError("Step48 checkpoint metadata or immutable source inputs mismatch")
    if sha(A_STATE) != A_STATE_SHA or sha(A_PROOF) != A_PROOF_SHA:
        raise RuntimeError("Target A state/proof changed; refusing B continuation")
    return state


def classify(before, after, requested_steps, returncode, timed_out, proof_exists=False):
    first = before["steps"]
    last = after.get("steps")
    if not isinstance(last,int) or not first <= last <= first+requested_steps:
        raise RuntimeError("Unexpected exact step count mutation")
    if len(after.get("pivot_path", [])) != last:
        raise RuntimeError("Checkpoint pivot_path length mismatch")
    if after.get("config") != before.get("config"):
        raise RuntimeError("Checkpoint configuration unexpectedly changed")
    if after.get("exact_target_proven") is not False:
        raise RuntimeError("Unexpected checkpoint proof flag")
    if last == first:
        if after != before and not (
            {k:v for k,v in after.items() if k!="status"} ==
            {k:v for k,v in before.items() if k!="status"}
            and after.get("status") == "EXACT_TARGET_CAP_REACHED_NOT_PROOF"
        ):
            raise RuntimeError("Unexpected mutation without saved progress")
        return "MULTISTEP_NO_NEW_STEP_SAVED_NOT_PROOF"
    if after.get("status") not in ("EXACT_TARGET_PREFIX_NOT_PROOF",
                                   "EXACT_TARGET_CAP_REACHED_NOT_PROOF"):
        raise RuntimeError("Unexpected saved checkpoint status")
    if proof_exists:
        if returncode != 0 or timed_out:
            raise RuntimeError("Proof artifact present but process exited abnormally")
        return "MULTISTEP_PROOF_FILE_REQUIRES_INSPECTION"
    if timed_out:
        return "MULTISTEP_PARTIAL_STEPS_SAVED_TIME_CEILING_NOT_PROOF"
    if returncode != 0:
        return "MULTISTEP_PARTIAL_STEPS_SAVED_ERROR_NOT_PROOF"
    if after["status"] == "EXACT_TARGET_CAP_REACHED_NOT_PROOF":
        return "MULTISTEP_PARTIAL_STEPS_SAVED_CAP_STOP_NOT_PROOF"
    return "MULTISTEP_STEPS_SAVED_NOT_TARGET_PROOF"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state",type=Path,default=STATE)
    ap.add_argument("--steps",type=int,default=16)
    ap.add_argument("--hours",type=float,default=12.0)
    ap.add_argument("--check-only",action="store_true")
    args = ap.parse_args()
    if not 1 <= args.steps <= 16 or not 0 < args.hours <= 12:
        ap.error("--steps must be 1..16; --hours must be within (0,12]")
    before = validate_start(args.state)
    cfg = before["config"]
    if before["steps"]+args.steps > cfg["max_steps_total"]:
        ap.error("Requested steps exceed existing checkpoint max_steps_total")
    print("VP05_SECTOR202_MULTISTEP_GUARD "+json.dumps({
        "status":"MULTISTEP_PREFLIGHT_PASS_NOT_PROOF",
        "steps_before":START_STEP,
        "requested_new_steps":args.steps,
        "max_steps_total":cfg["max_steps_total"],
        "remaining_terms":START_REMAINING,
        "maximum_expression_chars":START_MAX_CHARS,
        "formal_expression_cap":cfg["max_expression_chars"],
        "hours_ceiling":args.hours,
        "state_sha256":sha(args.state)
    }),flush=True)
    if args.check_only:
        return
    proof_path=args.state.with_name(args.state.stem+"_proof.json")
    if proof_path.exists():
        raise FileExistsError("B proof file already exists; inspect it before running")
    cmd = [sys.executable,"-m",
           "examples.three_loop_vp05_sector202_target_exact_checkpoint",
           "--resume","--state",str(args.state),"--target","B",
           "--new-steps",str(args.steps),
           "--max-columns",str(cfg["max_columns"]),
           "--max-support",str(cfg["max_support"]),
           "--max-expression-chars",str(cfg["max_expression_chars"]),
           "--max-steps-total",str(cfg["max_steps_total"])]
    timed_out=False
    try:
        completed=subprocess.run(cmd,timeout=args.hours*3600,check=False)
        rc=completed.returncode
    except subprocess.TimeoutExpired:
        timed_out=True
        rc=-1
    if sha(A_STATE) != A_STATE_SHA or sha(A_PROOF) != A_PROOF_SHA:
        raise RuntimeError("ALERT: protected Target A state/proof changed during B continuation")
    after=json.loads(args.state.read_text(encoding="utf-8-sig"))
    status=classify(before,after,args.steps,rc,timed_out,proof_path.exists())
    print("VP05_SECTOR202_MULTISTEP_GUARD "+json.dumps({
        "status":status,"timed_out":timed_out,"returncode":rc,
        "steps_before":START_STEP,"steps_after":after["steps"],
        "new_steps_saved":after["steps"]-START_STEP,
        "remaining_terms":len(after["remaining"]),
        "original_support":len(after["source"]),
        "maximum_expression_chars":max((len(v) for _,v in after["remaining"]+after["source"]),default=0),
        "state_sha256":sha(args.state),"exact_target_proven":False,
        "proof_file_exists":proof_path.exists(), "a_protected_unchanged":True
    }),flush=True)
    if rc and not timed_out:
        raise SystemExit(rc)


if __name__ == "__main__":
    main()
