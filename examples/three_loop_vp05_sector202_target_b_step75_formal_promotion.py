"""Guarded backup-first promotion of audited VP05 Target B Step75.

Default is read-only preflight. --promote must be explicit and can succeed
only once. Does not imply Target B full proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from examples.three_loop_vp05_sector202_target_b_step75_exact_audit import (
    context,validate_progress,COEFF,IBP,SCRATCH,
    EXPECTED_STEP75_SHA,STATUS,sha,
)
from examples.three_loop_vp05_sector202_target_b_step75_scratch import (
    B_STATE,EXPECTED_STEP74_SHA,protected_inputs,validate_scratch,formal_next_lead,
)
from examples.three_loop_vp05_sector202_target_b_step74_read_only_audit import inspect as inspect74

BACKUP=B_STATE.with_name("vp05_sector202_B_exact_target_state_step74_before_step75_promotion.json")
TEMP=B_STATE.with_name(B_STATE.name+".tmp")
TAG="VP05_B_STEP75_FORMAL_PROMOTION "

def valid_nonmonotone_successor(formal,candidate):
    """Fill-in may increase support; require actual pivot elimination and order."""
    old_lead=tuple(formal_next_lead(formal))
    old_keys={tuple(k) for k,v in formal.get("remaining",[])}
    new_keys={tuple(k) for k,v in candidate.get("remaining",[])}
    return (bool(new_keys)
            and old_lead in old_keys
            and old_lead not in new_keys
            and min(new_keys)>old_lead)

def validate():
    if inspect74().get("status")!="B_STEP74_SAVED_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF":
        raise RuntimeError("Formal Step74 saved-state audit failed")
    c=context()
    evidence={}
    for phase,path in (("coeff",COEFF),("ibp",IBP)):
        state,jobs=validate_progress(phase,c)
        if not jobs or len(state["checked"])!=len(jobs):
            raise RuntimeError("Step75 exact "+phase+" audit incomplete")
        evidence[phase+"_keys"]=len(jobs)
        evidence[phase+"_sha256"]=sha(path)
    if evidence["coeff_keys"]<=0 or evidence["ibp_keys"]!=362:
        raise RuntimeError("Wrong Step75 coefficient/original-IBP key inventory")
    cfg=json.loads(IBP.read_text(encoding="utf-8-sig"))["config"]
    if cfg.get("coefficient_checkpoint_sha256")!=evidence["coeff_sha256"]:
        raise RuntimeError("Step75 original-IBP certificate not tied to exact coefficients")
    formal=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    candidate=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    validate_scratch(formal,candidate)
    rem=candidate.get("remaining",[])
    source=candidate.get("source",[])
    metrics=candidate.get("metrics",{})
    if (sha(B_STATE)!=EXPECTED_STEP74_SHA or sha(SCRATCH)!=EXPECTED_STEP75_SHA
        or formal.get("steps")!=74 or candidate.get("steps")!=75
        or candidate.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF"
        or candidate.get("config")!=formal.get("config")
        or candidate.get("pivot_path")!=formal["pivot_path"]+[formal_next_lead(formal)]
        or not rem or not valid_nonmonotone_successor(formal,candidate)
        or len(rem)!=43 or len(source)!=231
        or len(source)>400 or len(rem)>256
        or metrics.get("max_expression_chars")!=3685
        or metrics.get("lead")!=[166596414799874,139]
        or metrics.get("remainder_terms")!=len(rem)
        or metrics.get("original_support")!=len(source)
        or tuple(metrics.get("lead",[]))!=min(tuple(k) for k,v in rem)
        or candidate.get("exact_target_proven") is not False
        or candidate.get("original_source_replay_proven") is not False
        or candidate.get("protected_source_checkpoint_modified") is not False):
        raise RuntimeError("Step75 candidate mismatches pinned formal successor")
    protected=protected_inputs()
    paths=[p.resolve() for p,d in protected]+[
        SCRATCH.resolve(),COEFF.resolve(),IBP.resolve(),
        BACKUP.resolve(),TEMP.resolve()]
    if len(paths)!=len(set(paths)):
        raise RuntimeError("Protected paths overlap")
    if BACKUP.exists() or TEMP.exists():
        raise FileExistsError("Step74 backup or promotion staging already exists; never overwrite")
    return {"status":"B_STEP75_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF",
        "old_sha256":EXPECTED_STEP74_SHA,"new_sha256":EXPECTED_STEP75_SHA,
        "coefficient_keys_verified":evidence["coeff_keys"],
        "original_ibp_keys_verified":evidence["ibp_keys"],
        "coefficient_checkpoint_sha256":evidence["coeff_sha256"],
        "original_ibp_checkpoint_sha256":evidence["ibp_sha256"],
        "new_steps":75,"remainder_terms":len(rem),
        "original_support":len(source),
        "max_expression_chars":metrics.get("max_expression_chars"),
        "next_lead":metrics.get("lead"),
        "target_b_proven":False,"formal_state_modified":False}

def promote(check_only=True):
    summary=validate()
    if check_only:return summary
    old=B_STATE.read_bytes()
    if hashlib.sha256(old).hexdigest()!=EXPECTED_STEP74_SHA:
        raise RuntimeError("Formal Step74 modified before backup")
    with BACKUP.open("xb") as stream:
        stream.write(old);stream.flush();os.fsync(stream.fileno())
    if sha(BACKUP)!=EXPECTED_STEP74_SHA:
        raise RuntimeError("Step74 backup verification failed")
    raw=SCRATCH.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_STEP75_SHA:
        raise RuntimeError("Step75 scratch changed after preflight")
    with TEMP.open("xb") as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    if sha(TEMP)!=EXPECTED_STEP75_SHA:
        raise RuntimeError("Step75 staging hash mismatch")
    for p,d in protected_inputs():
        if sha(p)!=d:raise RuntimeError("Protected input changed during staging")
    if (sha(COEFF)!=summary["coefficient_checkpoint_sha256"]
        or sha(IBP)!=summary["original_ibp_checkpoint_sha256"]
        or sha(SCRATCH)!=EXPECTED_STEP75_SHA
        or sha(BACKUP)!=EXPECTED_STEP74_SHA):
        raise RuntimeError("Step75 evidence changed during staging")
    os.replace(TEMP,B_STATE)
    if sha(B_STATE)!=EXPECTED_STEP75_SHA or sha(BACKUP)!=EXPECTED_STEP74_SHA:
        raise RuntimeError("Step75 promotion or backup digest mismatch")
    return {**summary,
        "status":"B_STEP75_FORMAL_PREFIX_PROMOTED_WITH_BACKUP_NOT_TARGET_PROOF",
        "backup_sha256":sha(BACKUP),"formal_state_modified":True}

def main():
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group()
    mode.add_argument("--check-only",action="store_true")
    mode.add_argument("--promote",action="store_true")
    args=ap.parse_args()
    print(TAG+json.dumps(promote(check_only=not args.promote)),flush=True)

if __name__=="__main__":
    main()
