"""Isolated, bounded one-step Target B Step72 scratch from saved formal Step71.

Read-only preflight, SHA-bound formal70, exclusive scratch creation. A saved
Step72 scratch is not a proof and must receive independent exact audits.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
from examples.three_loop_vp05_sector202_target_b_step71_read_only_audit import (
    inspect as audit_saved71,
)
from examples.three_loop_vp05_sector202_target_b_step71_formal_promotion import (
    B_STATE, BACKUP, SCRATCH as STEP71_SCRATCH, COEFF, IBP,
    EXPECTED_STEP71_SHA, EXPECTED_STEP70_SHA, sha,
)
from examples.three_loop_vp05_sector202_target_b_step70_formal_promotion import (
    BACKUP as STEP69_BACKUP, SCRATCH as STEP70_SCRATCH,
    COEFF as STEP70_COEFF, IBP as STEP70_IBP, EXPECTED_STEP69_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step69_formal_promotion import (
    BACKUP as STEP68_BACKUP, SCRATCH as STEP69_SCRATCH,
    COEFF as STEP69_COEFF, IBP as STEP69_IBP, EXPECTED_STEP68_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step68_formal_promotion import (
    BACKUP as STEP67_BACKUP, SCRATCH as STEP68_SCRATCH,
    COEFF as STEP68_COEFF, IBP as STEP68_IBP, EXPECTED_STEP67_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step67_formal_promotion import (
    BACKUP as STEP66_BACKUP, SCRATCH as STEP67_SCRATCH,
    COEFF as STEP67_COEFF, IBP as STEP67_IBP, EXPECTED_STEP66_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step66_formal_promotion import (
    BACKUP as STEP65_BACKUP, SAVED_STEP65_SHA,
    SCRATCH as STEP66_SCRATCH, PROTECTED as PRE66_PROTECTED,
    DIRECT as STEP66_DIRECT, COEFFICIENT as STEP66_COEFF,
    NORMALIZED as STEP66_NORMALIZED,
)
from examples.three_loop_vp05_sector202_target_b_multistep_from60 import classify

SCRATCH=B_STATE.with_name("vp05_sector202_B_step72_scratch_state.json")
TEMP=SCRATCH.with_name(SCRATCH.name+".tmp")
PROOF=SCRATCH.with_name(SCRATCH.stem+"_proof.json")
TAG="VP05_B_STEP72_SCRATCH_GUARD "
START_STEP=71
def formal_next_lead(formal):
    """Use the SHA-pinned formal 70 state rather than guessing the pivot."""
    rem=formal.get("remaining",[])
    if not rem:raise RuntimeError("No remaining pivot in formal Step71")
    lead=min(tuple(k) for k,v in rem)
    if tuple(formal.get("metrics",{}).get("lead",[]))!=lead:
        raise RuntimeError("Formal Step71 lead metadata mismatch")
    return list(lead)

PROTECTED_FIXED=[(B_STATE,EXPECTED_STEP71_SHA),(BACKUP,EXPECTED_STEP70_SHA),
    (STEP71_SCRATCH,EXPECTED_STEP71_SHA),
    (STEP70_SCRATCH,EXPECTED_STEP70_SHA),(STEP69_BACKUP,EXPECTED_STEP69_SHA),
    (STEP69_SCRATCH,EXPECTED_STEP69_SHA),(STEP68_BACKUP,EXPECTED_STEP68_SHA),
    (STEP68_SCRATCH,EXPECTED_STEP68_SHA),(STEP67_BACKUP,EXPECTED_STEP67_SHA),
    (STEP67_SCRATCH,EXPECTED_STEP67_SHA),(STEP66_BACKUP,EXPECTED_STEP66_SHA),
    (STEP66_SCRATCH,EXPECTED_STEP66_SHA),(STEP65_BACKUP,SAVED_STEP65_SHA)]
PROTECTED_FIXED.extend((p,d) for p,d in PRE66_PROTECTED
                       if p.resolve()!=B_STATE.resolve())
PROTECTED_CERTS=(STEP66_DIRECT,STEP66_COEFF,STEP66_NORMALIZED,
                 STEP67_COEFF,STEP67_IBP,STEP68_COEFF,STEP68_IBP,
                 STEP69_COEFF,STEP69_IBP,STEP70_COEFF,STEP70_IBP,COEFF,IBP)

def protected_inputs():
    result=PROTECTED_FIXED+[(p,sha(p)) for p in PROTECTED_CERTS]
    paths=[p.resolve() for p,d in result]+[
        SCRATCH.resolve(),TEMP.resolve(),PROOF.resolve()]
    if len(paths)!=len(set(paths)):
        raise RuntimeError("Step72 scratch path aliases protected evidence")
    for p,d in result:
        if sha(p)!=d:raise RuntimeError("Step72 protected input SHA mismatch "+str(p))
    return result

def validate_scratch(formal,scratch):
    if (scratch.get("version")!=formal.get("version")
        or scratch.get("config")!=formal.get("config")
        or scratch.get("status") not in
            ("EXACT_TARGET_PREFIX_NOT_PROOF","EXACT_TARGET_CAP_REACHED_NOT_PROOF")
        or scratch.get("steps") not in (START_STEP,START_STEP+1)
        or scratch.get("pivot_path",[])[:START_STEP]!=formal["pivot_path"]
        or len(scratch.get("pivot_path",[]))!=scratch.get("steps")
        or scratch.get("exact_target_proven") is not False
        or scratch.get("original_source_replay_proven") is not False
        or scratch.get("protected_source_checkpoint_modified") is not False):
        raise RuntimeError("Step72 scratch violates saved formal Step71")
    if scratch["steps"]==START_STEP:
        if (scratch.get("remaining")!=formal.get("remaining")
            or scratch.get("source")!=formal.get("source")
            or scratch.get("pivot_path")!=formal.get("pivot_path")):
            raise RuntimeError("Zero-step scratch changed coefficients")
    elif scratch["pivot_path"][START_STEP]!=formal_next_lead(formal):
        raise RuntimeError("Unexpected Step72 pivot lead")
    rem=scratch.get("remaining",[])
    src=scratch.get("source",[])
    if (len(rem)>256 or len(src)>400
        or len({tuple(k) for k,v in rem})!=len(rem)
        or len({int(k) for k,v in src})!=len(src)
        or any(not isinstance(v,str) or not v or v=="0" or len(v)>7500
               for _,v in rem+src)
        or scratch.get("metrics",{}).get("remainder_terms")!=len(rem)
        or scratch.get("metrics",{}).get("original_support")!=len(src)):
        raise RuntimeError("Step72 scratch cap or metadata violated")
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check-only",action="store_true")
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--hours",type=float,default=12)
    args=ap.parse_args()
    if not 0<args.hours<=12:
        ap.error("Only (0,12] hours permitted")
    audit=audit_saved71()
    if audit.get("status")!="B_STEP71_SAVED_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF":
        raise RuntimeError("Saved Step71 post-promotion audit failed")
    protected=protected_inputs()
    formal=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    if (formal.get("steps")!=START_STEP
        or formal.get("metrics",{}).get("lead")!=formal_next_lead(formal)
        or formal.get("config",{}).get("target")!="B"
        or formal.get("config",{}).get("max_expression_chars")!=7500
        or formal.get("config",{}).get("max_columns")!=256
        or formal.get("config",{}).get("max_support")!=400
        or sha(B_STATE)!=EXPECTED_STEP71_SHA):
        raise RuntimeError("Unexpected formal Step71 baseline")
    if TEMP.exists() or PROOF.exists():
        raise FileExistsError("Existing scratch tmp/proof; inspect before running")
    if SCRATCH.exists()!=args.resume and not args.check_only:
        raise RuntimeError("Scratch exists: use --resume; otherwise omit --resume")
    before=json.loads(SCRATCH.read_text(encoding="utf-8-sig")) if SCRATCH.exists() else formal
    validate_scratch(formal,before)
    if args.resume and before["steps"]!=START_STEP and not args.check_only:
        raise RuntimeError("Step72 already saved; do not run engine again")
    print(TAG+json.dumps({
        "status":"B_STEP72_SCRATCH_PREFLIGHT_PASS_NOT_PROOF",
        "formal_step":71,"formal_sha256":EXPECTED_STEP71_SHA,
        "scratch_steps":before["steps"],"scratch_exists":SCRATCH.exists(),
        "next_lead":formal_next_lead(formal),"formal_state_unchanged":True,
        "target_b_proven":False,
        "scratch_sha256":sha(SCRATCH) if SCRATCH.exists() else None,
        "already_saved":before["steps"]==START_STEP+1}),flush=True)
    if args.check_only:return
    if not args.resume:
        raw=B_STATE.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=EXPECTED_STEP71_SHA:
            raise RuntimeError("Formal Step71 changed before scratch copying")
        with SCRATCH.open("xb") as out:
            out.write(raw);out.flush();os.fsync(out.fileno())
        if sha(SCRATCH)!=EXPECTED_STEP71_SHA:
            raise RuntimeError("Scratch copy hash mismatch")
    cfg=formal["config"]
    cmd=[sys.executable,"-m",
         "examples.three_loop_vp05_sector202_target_exact_checkpoint",
         "--resume","--state",str(SCRATCH),"--target","B",
         "--new-steps","1","--max-columns","256",
         "--max-support","400","--max-expression-chars","7500",
         "--max-steps-total",str(cfg["max_steps_total"])]
    try:
        run=subprocess.run(cmd,timeout=args.hours*3600,check=False)
        rc=run.returncode;timed_out=False
    except subprocess.TimeoutExpired:
        rc=-1;timed_out=True
    for p,d in protected:
        if sha(p)!=d:raise RuntimeError("Protected state modified during Step72")
    after=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    validate_scratch(formal,after)
    status=classify(before,after,1,rc,timed_out,PROOF.exists())
    print(TAG+json.dumps({
        "status":status,"formal_step":START_STEP,
        "scratch_steps_before":before["steps"],
        "scratch_steps_after":after["steps"],
        "new_steps_saved":after["steps"]-before["steps"],
        "remainder_terms":len(after["remaining"]),
        "original_support":len(after["source"]),
        "max_expression_chars":after["metrics"]["max_expression_chars"],
        "scratch_sha256":sha(SCRATCH),"formal_sha256":sha(B_STATE),
        "formal_state_unchanged":True,"timed_out":timed_out,
        "returncode":rc,"exact_target_proven":False,
        "step72_original_ibp_exact_replay_verified":False,
        "target_b_proven":False}),flush=True)
    if rc!=0 and not timed_out:raise SystemExit(rc)

if __name__=="__main__":
    main()
