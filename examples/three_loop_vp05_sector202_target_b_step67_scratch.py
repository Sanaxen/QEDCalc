"""Guarded isolated Target B Step67 one-step scratch from saved formal Step66.

Never runs the exact checkpoint engine against formal B. Never promotes.
Preflight requires the saved Step66 read-only audit, then exclusively copies
the SHA-pinned formal66 bytes to an entirely separate Step67 scratch path.
All source, A, historical backups and Step66 evidence hashes are rechecked
after computation. A completed step remains unproved pending an independent
Step66->67 coefficient and original-IBP exact replay.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
from examples.three_loop_vp05_sector202_target_b_step66_read_only_audit import (
    inspect as audit_saved66,
)
from examples.three_loop_vp05_sector202_target_b_step66_formal_promotion import (
    B_STATE, BACKUP, SCRATCH as OLD_SCRATCH, DIRECT, COEFFICIENT,
    NORMALIZED, PROTECTED, EXPECTED_STEP66_SHA, SAVED_STEP65_SHA,
    CHECKPOINT, SOURCE, CERT, sha,
)
from examples.three_loop_vp05_sector202_target_b_multistep_from60 import classify

SCRATCH=B_STATE.with_name("vp05_sector202_B_step67_scratch_state.json")
TAG="VP05_B_STEP67_SCRATCH_GUARD "
PROOF=SCRATCH.with_name(SCRATCH.stem+"_proof.json")
TEMP=SCRATCH.with_name(SCRATCH.name+".tmp")
START_STEP=66
NEXT_LEAD=[166596414013441,139]

def protected_inputs():
    # Old formal65 is now a backup, not the formal state.
    result=[(B_STATE,EXPECTED_STEP66_SHA),(BACKUP,SAVED_STEP65_SHA),
            (OLD_SCRATCH,EXPECTED_STEP66_SHA)]
    result.extend((p,digest) for p,digest in PROTECTED
                  if p.resolve()!=B_STATE.resolve())
    result.extend((p,sha(p)) for p in (DIRECT,COEFFICIENT,NORMALIZED))
    paths=[p.resolve() for p,digest in result]+[
        SCRATCH.resolve(),TEMP.resolve(),PROOF.resolve()]
    if len(paths)!=len(set(paths)):
        raise RuntimeError("Step67 scratch path overlaps protected evidence")
    for path,digest in result:
        if sha(path)!=digest:
            raise RuntimeError("Step67 input SHA guard failed: "+str(path))
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
        raise RuntimeError("Step67 scratch violates saved Step66 transition")
    if scratch["steps"]==START_STEP:
        if (scratch.get("remaining")!=formal.get("remaining")
            or scratch.get("source")!=formal.get("source")
            or scratch.get("pivot_path")!=formal.get("pivot_path")):
            raise RuntimeError("Zero-step scratch changed integral coefficients")
    else:
        if scratch["pivot_path"][START_STEP]!=NEXT_LEAD:
            raise RuntimeError("Unexpected Step67 pivot lead")
    rem=scratch.get("remaining",[])
    src=scratch.get("source",[])
    if (len(rem)>256 or len(src)>400
        or len({tuple(k) for k,v in rem})!=len(rem)
        or len({int(k) for k,v in src})!=len(src)
        or any(not isinstance(v,str) or not v or v=="0" or len(v)>7500
               for _,v in rem+src)
        or scratch.get("metrics",{}).get("remainder_terms")!=len(rem)
        or scratch.get("metrics",{}).get("original_support")!=len(src)):
        raise RuntimeError("Step67 scratch bounds or metadata failed")
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check-only",action="store_true")
    p.add_argument("--resume",action="store_true")
    p.add_argument("--hours",type=float,default=12)
    args=p.parse_args()
    if not 0<args.hours<=12:
        p.error("Only (0,12] hour bounded runs permitted")
    formal_audit=audit_saved66()
    if formal_audit.get("status")!="B_STEP66_SAVED_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF":
        raise RuntimeError("Saved formal66 audit not PASS")
    protected=protected_inputs()
    formal=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    if (formal.get("steps")!=START_STEP
        or formal.get("metrics",{}).get("lead")!=NEXT_LEAD
        or formal.get("config",{}).get("target")!="B"
        or formal.get("config",{}).get("max_expression_chars")!=7500
        or formal.get("config",{}).get("max_columns")!=256
        or formal.get("config",{}).get("max_support")!=400):
        raise RuntimeError("Unexpected formal66 starting configuration")
    if TEMP.exists() or PROOF.exists():
        raise FileExistsError("Preexisting scratch tmp or proof; inspect before continuation")
    if SCRATCH.exists()!=args.resume:
        raise RuntimeError("Step67 scratch exists: use --resume; or omit --resume if absent")
    if args.resume:
        before=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
        validate_scratch(formal,before)
        if before["steps"]!=START_STEP:
            raise RuntimeError("Step67 already saved; do not run engine again")
    else:
        before=formal
    print(TAG+json.dumps({
        "status":"B_STEP67_SCRATCH_PREFLIGHT_PASS_NOT_PROOF",
        "formal_step":START_STEP,"next_lead":NEXT_LEAD,
        "formal_sha256":EXPECTED_STEP66_SHA,"scratch_exists":SCRATCH.exists(),
        "scratch_steps":before["steps"],"formal_state_unchanged":True,
        "target_b_proven":False}),flush=True)
    if args.check_only:return
    if not args.resume:
        raw=B_STATE.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=EXPECTED_STEP66_SHA:
            raise RuntimeError("Formal66 changed during exclusive scratch creation")
        with SCRATCH.open("xb") as out:
            out.write(raw);out.flush();os.fsync(out.fileno())
        if sha(SCRATCH)!=EXPECTED_STEP66_SHA:
            raise RuntimeError("Scratch copy failed SHA verification")
    cfg=formal["config"]
    cmd=[sys.executable,"-m",
         "examples.three_loop_vp05_sector202_target_exact_checkpoint",
         "--resume","--state",str(SCRATCH),"--target","B",
         "--new-steps","1","--max-columns","256",
         "--max-support","400","--max-expression-chars","7500",
         "--max-steps-total",str(cfg["max_steps_total"])]
    try:
        r=subprocess.run(cmd,timeout=args.hours*3600,check=False)
        rc=r.returncode;timed_out=False
    except subprocess.TimeoutExpired:
        rc=-1;timed_out=True
    for path,digest in protected:
        if sha(path)!=digest:
            raise RuntimeError("Protected state or certificate modified")
    after=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    validate_scratch(formal,after)
    category=classify(before,after,1,rc,timed_out,PROOF.exists())
    print(TAG+json.dumps({
        "status":category,"formal_step":START_STEP,
        "scratch_steps_before":before["steps"],
        "scratch_steps_after":after["steps"],
        "new_steps_saved":after["steps"]-before["steps"],
        "remainder_terms":len(after["remaining"]),
        "original_support":len(after["source"]),
        "scratch_sha256":sha(SCRATCH),
        "formal_sha256":sha(B_STATE),
        "formal_state_unchanged":True,
        "timed_out":timed_out,"returncode":rc,
        "exact_target_proven":False,
        "step67_original_ibp_exact_replay_verified":False,
        "target_b_proven":False}),flush=True)
    if rc!=0 and not timed_out:
        raise SystemExit(rc)

if __name__=="__main__":
    main()
