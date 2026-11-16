"""Guarded B Step65–80 scratch continuation from audited formal Step64.

Never runs the exact engine against the formal B state. Creates a byte-identical
exclusive scratch copy, then uses the existing resumable engine there. On a
cap stop, even a no-step coefficient reserialization affects only scratch.
Any successful scratch eliminations must be independently replayed and
backup-first promoted before changing the formal B state.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from examples.three_loop_vp05_sector202_target_b_start import (
    B_STATE, A_STATE, A_PROOF, A_STATE_SHA, A_PROOF_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step64_read_only_audit import SAVED_STEP64_SHA
from examples.three_loop_vp05_sector202_target_b_step64_formal_promotion import (
    BACKUP as STEP63_BACKUP, EXPECTED_STEP63_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step51_formal_promotion import (
    BACKUP as STEP50_BACKUP, B_STEP50_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step52_formal_promotion import (
    BACKUP as STEP51_BACKUP, B_STEP51_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step53_formal_promotion import (
    BACKUP as STEP52_BACKUP, B_STEP52_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step59_formal_promotion import (
    BACKUP as STEP58_BACKUP, B_STEP58_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step60_formal_promotion import (
    BACKUP as STEP59_BACKUP, B_STEP59_SHA,
    SOURCE_CHECKPOINT_SHA, ORIGINAL_SOURCE_SHA, CERTIFICATE_SHA,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    CHECKPOINT, SOURCE, CERT, sha,
)
from examples.three_loop_vp05_sector202_target_b_multistep_from60 import classify

SCRATCH = B_STATE.with_name("vp05_sector202_B_step64_to80_scratch_state.json")
START_STEP = 64
START_REMAINING = 86
START_SUPPORT = 172
START_MAX_CHARS = 7310
PROTECTED = [
    (B_STATE,SAVED_STEP64_SHA),(A_STATE,A_STATE_SHA),(A_PROOF,A_PROOF_SHA),
    (STEP50_BACKUP,B_STEP50_SHA),(STEP51_BACKUP,B_STEP51_SHA),
    (STEP52_BACKUP,B_STEP52_SHA),(STEP58_BACKUP,B_STEP58_SHA),
    (STEP59_BACKUP,B_STEP59_SHA),(STEP63_BACKUP,EXPECTED_STEP63_SHA),
    (CHECKPOINT,SOURCE_CHECKPOINT_SHA),(SOURCE,ORIGINAL_SOURCE_SHA),
    (CERT,CERTIFICATE_SHA),
]


def validate():
    paths=[p.resolve() for p,_ in PROTECTED]+[SCRATCH.resolve()]
    if len(set(paths))!=len(paths):
        raise RuntimeError("Scratch aliases immutable formal or source file")
    for p,digest in PROTECTED:
        if sha(p)!=digest:
            raise RuntimeError("Protected source or target modified: "+str(p))
    state=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    cfg=state.get("config",{})
    if (state.get("steps")!=64 or state.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF"
        or state.get("exact_target_proven") is not False
        or state.get("original_source_replay_proven") is not False
        or len(state.get("remaining",[]))!=START_REMAINING
        or len(state.get("source",[]))!=START_SUPPORT
        or len(state.get("pivot_path",[]))!=64
        or cfg.get("target")!="B"
        or cfg.get("max_expression_chars")!=7500
        or cfg.get("max_columns")!=256 or cfg.get("max_support")!=400
        or cfg.get("source_checkpoint_sha256")!=SOURCE_CHECKPOINT_SHA
        or cfg.get("source_sha256")!=ORIGINAL_SOURCE_SHA
        or cfg.get("certificate_sha256")!=CERTIFICATE_SHA
        or state.get("metrics",{}).get("max_expression_chars")!=START_MAX_CHARS
        or max((len(v) for _,v in state["remaining"]+state["source"]),default=0)!=START_MAX_CHARS
        or state.get("metrics",{}).get("lead")!=[166596413882371,139]):
        raise RuntimeError("Audited Step64 formal metadata mismatch")
    return state


def validate_scratch(formal, scratch):
    if (scratch.get("config")!=formal["config"] or scratch.get("steps",0)<64
        or scratch.get("steps",0)>80
        or scratch.get("exact_target_proven") is not False
        or scratch.get("pivot_path",[])[:64]!=formal["pivot_path"]
        or len(scratch.get("pivot_path",[]))!=scratch.get("steps")
        or scratch.get("status") not in
           ("EXACT_TARGET_PREFIX_NOT_PROOF","EXACT_TARGET_CAP_REACHED_NOT_PROOF")):
        raise RuntimeError("Scratch checkpoint is not a continuation of pinned Step64")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--steps",type=int,default=16)
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--check-only",action="store_true")
    args=ap.parse_args()
    if not 1<=args.steps<=16 or not 0<args.hours<=12:
        ap.error("Safety bounds: steps 1..16, hours (0,12]")
    before=validate()
    if 64+args.steps>before["config"]["max_steps_total"]:
        raise RuntimeError("Requested steps exceed saved total cap")
    if SCRATCH.exists() and not args.resume:
        raise FileExistsError("Scratch already exists; use --resume or inspect existing result")
    if args.resume and not SCRATCH.exists():
        raise FileNotFoundError("No prior scratch to resume")
    if SCRATCH.exists():
        scratch=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
        validate_scratch(before,scratch)
        if scratch["steps"]+args.steps>80:
            raise RuntimeError("Cannot continue beyond this scratch's audited Step80 range")
    else:
        scratch=before
    print("VP05_B_STEP64_SCRATCH_GUARD "+json.dumps({
        "status":"B_STEP65_SCRATCH_PREFLIGHT_PASS_NOT_PROOF",
        "formal_step":64,"formal_state_sha256":SAVED_STEP64_SHA,
        "scratch_steps":scratch["steps"],"steps_requested":args.steps,
        "scratch_exists":SCRATCH.exists(),"expression_cap":7500,
        "next_lead":scratch["metrics"]["lead"],
    }),flush=True)
    if args.check_only:return
    if not SCRATCH.exists():
        raw=B_STATE.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=SAVED_STEP64_SHA:
            raise RuntimeError("Formal checkpoint changed while preparing scratch")
        with SCRATCH.open("xb") as out:
            out.write(raw);out.flush();os.fsync(out.fileno())
        if sha(SCRATCH)!=SAVED_STEP64_SHA:
            raise RuntimeError("Scratch is not a byte-identical Step64 snapshot")
    proof=SCRATCH.with_name(SCRATCH.stem+"_proof.json")
    if proof.exists():
        raise FileExistsError("Scratch proof artifact exists; inspect before restart")
    cfg=before["config"]
    cmd=[sys.executable,"-m",
         "examples.three_loop_vp05_sector202_target_exact_checkpoint",
         "--resume","--state",str(SCRATCH),"--target","B",
         "--new-steps",str(args.steps),"--max-columns","256",
         "--max-support","400","--max-expression-chars","7500",
         "--max-steps-total",str(cfg["max_steps_total"])]
    try:
        run=subprocess.run(cmd,timeout=args.hours*3600,check=False)
        rc=run.returncode
        timed_out=False
    except subprocess.TimeoutExpired:
        timed_out=True
        rc=-1
    for p,digest in PROTECTED:
        if sha(p)!=digest:
            raise RuntimeError("Protected file changed during scratch continuation: "+str(p))
    after=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    validate_scratch(before,after)
    category=classify(scratch,after,args.steps,rc,timed_out,proof.exists())
    print("VP05_B_STEP64_SCRATCH_GUARD "+json.dumps({
        "status":category,"scratch_steps_before":scratch["steps"],
        "scratch_steps_after":after["steps"],
        "new_steps_saved":after["steps"]-scratch["steps"],
        "remainder_terms":len(after.get("remaining",[])),
        "original_support":len(after.get("source",[])),
        "maximum_expression_chars":max((len(v) for _,v in after.get("remaining",[])+after.get("source",[])),default=0),
        "scratch_sha256":sha(SCRATCH),"formal_state_sha256":sha(B_STATE),
        "formal_state_unchanged":True,"a_protected_unchanged":True,
        "timed_out":timed_out,"returncode":rc,
        "exact_target_proven":False,"proof_file_exists":proof.exists()
    }),flush=True)
    if rc!=0 and not timed_out:raise SystemExit(rc)


if __name__=="__main__":
    main()
