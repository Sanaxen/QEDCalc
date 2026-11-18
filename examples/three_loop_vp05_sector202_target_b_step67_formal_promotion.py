"""Backup-first formal Step67 promotion, requiring full exact saved evidence.

Default --check-only has no writes. --promote exclusively backs up formal66
and atomically installs byte-identical audited Step67 scratch. Never claims
whole Target B proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from examples.three_loop_vp05_sector202_target_b_step67_exact_audit import (
    context,validate_progress,job_manifest,COEFF,IBP,SCRATCH,
    EXPECTED_STEP67_SHA,EXPECTED_STEP66_SHA,STATUS,sha,
)
from examples.three_loop_vp05_sector202_target_b_step67_scratch import (
    B_STATE,protected_inputs,validate_scratch,NEXT_LEAD,
)
from examples.three_loop_vp05_sector202_target_b_step66_read_only_audit import inspect as inspect66

BACKUP=B_STATE.with_name("vp05_sector202_B_exact_target_state_step66_before_step67_promotion.json")
TEMP=B_STATE.with_name(B_STATE.name+".tmp")
TAG="VP05_B_STEP67_FORMAL_PROMOTION "

def validate():
    inspect66()
    c=context()
    evidence={}
    for phase,path in (("coeff",COEFF),("ibp",IBP)):
        state,jobs=validate_progress(phase,c)
        if not jobs or len(state["checked"])!=len(jobs):
            raise RuntimeError("Incomplete Step67 exact "+phase+" certificates")
        evidence[phase+"_keys"]=len(jobs)
        evidence[phase+"_sha256"]=sha(path)
    if evidence["ibp_keys"]!=32:
        raise RuntimeError("Unexpected Step67 original-IBP key count")
    # Validate coefficient SHA provenance inside the phase-2 certificate.
    saved_ibp=json.loads(IBP.read_text(encoding="utf-8-sig"))
    if saved_ibp["config"].get("coefficient_checkpoint_sha256")!=evidence["coeff_sha256"]:
        raise RuntimeError("Step67 IBP checkpoint not bound to exact coefficient audit")
    formal=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    candidate=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    validate_scratch(formal,candidate)
    if (sha(B_STATE)!=EXPECTED_STEP66_SHA or sha(SCRATCH)!=EXPECTED_STEP67_SHA
        or candidate.get("steps")!=67
        or candidate.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF"
        or candidate.get("pivot_path")!=formal["pivot_path"]+[NEXT_LEAD]
        or candidate.get("config")!=formal.get("config")
        or len(candidate.get("remaining",[]))!=74
        or len(candidate.get("source",[]))!=154
        or candidate["metrics"].get("max_expression_chars")!=5726
        or candidate["metrics"].get("lead")!=[166596414013442,139]
        or candidate.get("exact_target_proven") is not False):
        raise RuntimeError("Step67 candidate does not match pinned exact successor")
    protected=protected_inputs()
    evidence_paths=[COEFF,IBP]
    paths=[p.resolve() for p,d in protected]+[SCRATCH.resolve(),BACKUP.resolve(),TEMP.resolve()]
    paths.extend(p.resolve() for p in evidence_paths)
    if len(paths)!=len(set(paths)):
        raise RuntimeError("Step67 promotion path aliases protected source")
    if BACKUP.exists() or TEMP.exists():
        raise FileExistsError("Step66 backup or state staging already exists")
    return {"status":"B_STEP67_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF",
        "old_sha256":EXPECTED_STEP66_SHA,"new_sha256":EXPECTED_STEP67_SHA,
        "coefficient_keys_verified":evidence["coeff_keys"],
        "original_ibp_keys_verified":evidence["ibp_keys"],
        "coefficient_checkpoint_sha256":evidence["coeff_sha256"],
        "original_ibp_checkpoint_sha256":evidence["ibp_sha256"],
        "new_steps":67,"remainder_terms":74,"original_support":154,
        "target_b_proven":False,"formal_state_modified":False}

def promote(check_only=True):
    summary=validate()
    if check_only:return summary
    old=B_STATE.read_bytes()
    if hashlib.sha256(old).hexdigest()!=EXPECTED_STEP66_SHA:
        raise RuntimeError("Formal Step66 changed before backup")
    with BACKUP.open("xb") as stream:
        stream.write(old);stream.flush();os.fsync(stream.fileno())
    if sha(BACKUP)!=EXPECTED_STEP66_SHA:
        raise RuntimeError("Step66 backup verification failed before promotion")
    raw=SCRATCH.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_STEP67_SHA:
        raise RuntimeError("Step67 candidate modified after preflight")
    with TEMP.open("xb") as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    if sha(TEMP)!=EXPECTED_STEP67_SHA:
        raise RuntimeError("Step67 staging SHA mismatch")
    for path,digest in protected_inputs():
        if sha(path)!=digest:
            raise RuntimeError("Protected file changed during staging")
    if (sha(COEFF)!=summary["coefficient_checkpoint_sha256"]
        or sha(IBP)!=summary["original_ibp_checkpoint_sha256"]
        or sha(SCRATCH)!=EXPECTED_STEP67_SHA
        or sha(BACKUP)!=EXPECTED_STEP66_SHA):
        raise RuntimeError("Step67 evidence changed during staging")
    os.replace(TEMP,B_STATE)
    if sha(B_STATE)!=EXPECTED_STEP67_SHA or sha(BACKUP)!=EXPECTED_STEP66_SHA:
        raise RuntimeError("Step67 promotion or Step66 backup hash mismatch")
    return {**summary,"status":"B_STEP67_FORMAL_PREFIX_PROMOTED_WITH_BACKUP_NOT_TARGET_PROOF",
            "backup_sha256":sha(BACKUP),"formal_state_modified":True}

def main():
    p=argparse.ArgumentParser()
    mode=p.add_mutually_exclusive_group()
    mode.add_argument("--check-only",action="store_true")
    mode.add_argument("--promote",action="store_true")
    args=p.parse_args()
    print(TAG+json.dumps(promote(check_only=not args.promote)),flush=True)

if __name__=="__main__":
    main()
