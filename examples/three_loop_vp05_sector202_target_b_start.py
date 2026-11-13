"""Start exact Sector202 Target B without modifying proven Target A.

Pins Target A's independently audited proof/state SHA256, validates the
protected sources, and starts a DISTINCT Target B checkpoint for up to 16
steps. The engine atomically saves each exact elimination; this wrapper
does not infer proof until a separate B proof artifact is inspected.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

from examples.three_loop_vp05_sector202_target_exact_reduction import BASE, CHECKPOINT, SOURCE, CERT, sha

A_STATE = BASE / "vp05_sector202_A_exact_target_state.json"
A_PROOF = BASE / "vp05_sector202_A_exact_target_state_proof.json"
B_STATE = BASE / "vp05_sector202_B_exact_target_state.json"
A_STATE_SHA = "c685cd2627ad4d6f9bea6c7afc0b5e0f6611184b2382b303616283068a54c13c"
A_PROOF_SHA = "dd4758f2c38648aef87e6c04c76af23c52e524492cb7b1aa8616e0fca31933e5"


def preflight(a_state=A_STATE,a_proof=A_PROOF,b_state=B_STATE,
              checkpoint=CHECKPOINT,source=SOURCE,certificate=CERT):
    if b_state.exists() or b_state.with_name(b_state.name+".tmp").exists():
        raise FileExistsError("B checkpoint already exists; do not restart or overwrite it")
    if b_state.with_name(b_state.stem+"_proof.json").exists():
        raise FileExistsError("B proof already exists; do not rerun")
    if b_state.resolve() in {p.resolve() for p in (
            a_state,a_proof,checkpoint,source,certificate)}:
        raise RuntimeError("B state may not alias protected files")
    if sha(a_state)!=A_STATE_SHA or sha(a_proof)!=A_PROOF_SHA:
        raise RuntimeError("Verified Target A state or proof hash mismatch")
    a=json.loads(a_state.read_text(encoding="utf-8-sig"))
    p=json.loads(a_proof.read_text(encoding="utf-8-sig"))
    cfg=a.get("config",{})
    if (a.get("steps")!=93 or a.get("remaining")!=[]
        or len(a.get("pivot_path",[]))!=93
        or cfg.get("target")!="A"
        or p.get("status")!="EXACT_SINGLE_TARGET_PROVEN"
        or p.get("target")!="A" or p.get("steps")!=93
        or p.get("original_source_replay_verified") is not True
        or p.get("source_multipliers")!=a.get("source")
        or cfg.get("source_checkpoint_sha256")!=sha(checkpoint)
        or cfg.get("source_sha256")!=sha(source)
        or cfg.get("certificate_sha256")!=sha(certificate)
        or p.get("source_checkpoint_sha256")!=sha(checkpoint)
        or p.get("source_sha256")!=sha(source)
        or p.get("certificate_sha256")!=sha(certificate)):
        raise RuntimeError("Target A proof / protected source verification failed")
    return cfg


def classify_b(before_exists, after, requested_steps, rc, timed_out, proof_exists):
    if before_exists:
        raise RuntimeError("B must be a new state, never resumed by this startup guard")
    if after is None:
        return "B_NOT_STARTED_NOT_PROOF"
    n=after.get("steps")
    if (not isinstance(n,int) or not 0<=n<=requested_steps
        or len(after.get("pivot_path",[]))!=n
        or after.get("config",{}).get("target")!="B"
        or after.get("exact_target_proven") is not False):
        raise RuntimeError("Unexpected Target B state")
    if proof_exists:
        if rc!=0 or timed_out:
            raise RuntimeError("B proof artifact written on unsuccessful execution")
        return "B_PROOF_FILE_REQUIRES_INDEPENDENT_AUDIT"
    if after.get("status")=="EXACT_TARGET_CAP_REACHED_NOT_PROOF":
        return "B_PARTIAL_SAVED_CAP_STOP_NOT_PROOF"
    if after.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF":
        raise RuntimeError("Unexpected B state status")
    if timed_out:
        return "B_PARTIAL_SAVED_TIME_CEILING_NOT_PROOF"
    if rc:
        return "B_PARTIAL_SAVED_ERROR_NOT_PROOF"
    if n==0:
        return "B_NO_STEPS_SAVED_NOT_PROOF"
    return "B_STEPS_SAVED_NOT_PROOF"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--steps",type=int,default=16)
    ap.add_argument("--hours",type=float,default=12.0)
    ap.add_argument("--check-only",action="store_true")
    args=ap.parse_args()
    if not 1<=args.steps<=16 or not 0<args.hours<=12:
        ap.error("--steps must be 1..16; --hours must be within (0,12]")
    a_cfg=preflight()
    limits={k:a_cfg[k] for k in ("max_columns","max_support",
                                    "max_expression_chars","max_steps_total")}
    print("VP05_SECTOR202_TARGET_B_START_GUARD "+json.dumps({
        "status":"B_START_PREFLIGHT_PASS_NOT_PROOF",
        "a_step":93,"a_remainder":0,
        "a_proof_sha256":A_PROOF_SHA,
        "b_state":str(B_STATE),
        "requested_new_steps":args.steps,
        "hours_ceiling":args.hours,
        "limits":limits}),flush=True)
    if args.check_only:
        return
    cmd=[sys.executable,"-m",
         "examples.three_loop_vp05_sector202_target_exact_checkpoint",
         "--target","B","--state",str(B_STATE),
         "--new-steps",str(args.steps),
         "--max-columns",str(limits["max_columns"]),
         "--max-support",str(limits["max_support"]),
         "--max-expression-chars",str(limits["max_expression_chars"]),
         "--max-steps-total",str(limits["max_steps_total"])]
    timed_out=False
    try:
        run=subprocess.run(cmd,timeout=args.hours*3600,check=False)
        rc=run.returncode
    except subprocess.TimeoutExpired:
        timed_out=True
        rc=-1
    # Verify A remains exactly unchanged even after a partial B run.
    if sha(A_STATE)!=A_STATE_SHA or sha(A_PROOF)!=A_PROOF_SHA:
        raise RuntimeError("ALERT: Target A saved artifacts changed during B run")
    after=json.loads(B_STATE.read_text(encoding="utf-8-sig")) if B_STATE.exists() else None
    proof=B_STATE.with_name(B_STATE.stem+"_proof.json").exists()
    status=classify_b(False,after,args.steps,rc,timed_out,proof)
    print("VP05_SECTOR202_TARGET_B_START_GUARD "+json.dumps({
        "status":status,"timed_out":timed_out,"returncode":rc,
        "steps":after["steps"] if after else None,
        "remainder_terms":len(after["remaining"]) if after else None,
        "original_support":len(after["source"]) if after else None,
        "state_sha256":sha(B_STATE) if after else None,
        "proof_file_exists":proof,"a_protected_unchanged":True}),flush=True)
    if rc!=0 and not timed_out:
        raise SystemExit(rc)


if __name__=="__main__":
    main()
