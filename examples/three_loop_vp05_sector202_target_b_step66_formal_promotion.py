"""SHA-guarded, backup-first formal VP05 Target B Step66 promotion.

Requires 113 direct + 217 normalized exact original-IBP certificates and
259 independent exact local coefficient certificates. Preflight is read-only.
The formal Step65 bytes are exclusively backed up before atomic promotion of
the exact, already SHA-pinned Step66 scratch bytes. Never claims Target B proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from examples.three_loop_vp05_sector202_target_b_step66_normalized_ibp_replay import (
    load, OUT as NORMALIZED, STATUS as NORMALIZED_STATUS, METHOD,
    DIRECT_COUNT, TOTAL_KEYS, COEFFICIENT, DIRECT, PROTECTED, SCRATCH,
    B_STATE, SAVED_STEP65_SHA, EXPECTED_STEP66_SHA, CHECKPOINT, SOURCE,
    CERT, sha,
)
from examples.three_loop_vp05_sector202_target_b_step66_coefficient_audit import (
    STATUS as COEFFICIENT_STATUS,
)
from examples.three_loop_vp05_sector202_target_b_step66_original_ibp_replay import (
    context_config,
)
from examples.three_loop_vp05_sector202_target_b_scratch_from65 import (
    validate_scratch,
)
from examples.three_loop_vp05_sector202_target_b_step65_read_only_audit import (
    inspect as inspect_formal65,
)

BACKUP=B_STATE.with_name("vp05_sector202_B_exact_target_state_step65_before_step66_promotion.json")
TEMP=B_STATE.with_name(B_STATE.name+".tmp")
TAG="VP05_B_STEP66_FORMAL_PROMOTION "

def validate():
    # Check the previous formal state before accessing any mutable evidence.
    inspect_formal65()
    jobs,prow,key_terms,coeff_sha,direct_sha=load()
    if len(jobs)!=TOTAL_KEYS:
        raise RuntimeError("Original IBP key inventory incomplete")
    if not NORMALIZED.exists():
        raise FileNotFoundError("Missing normalized 217-key checkpoint")
    evidence_sha=sha(NORMALIZED)
    evidence=json.loads(NORMALIZED.read_text(encoding="utf-8-sig"))
    cfg=evidence.get("config",{})
    checked=evidence.get("checked",[])
    job_sha=hashlib.sha256(json.dumps(
        [list(k) for k in jobs],separators=(",",":")
    ).encode()).hexdigest()
    if (evidence.get("version")!=1
        or evidence.get("status")!=NORMALIZED_STATUS
        or evidence.get("formal_state_modified") is not False
        or evidence.get("target_b_proven") is not False
        or evidence.get("original_ibp_exact_replay_verified") is not False
        or cfg.get("version")!=1
        or cfg.get("formal_step65_sha256")!=SAVED_STEP65_SHA
        or cfg.get("scratch_step66_sha256")!=EXPECTED_STEP66_SHA
        or cfg.get("original_source_sha256")!=sha(SOURCE)
        or cfg.get("source_checkpoint_sha256")!=sha(CHECKPOINT)
        or cfg.get("certificate_sha256")!=sha(CERT)
        or cfg.get("coefficient_audit_sha256")!=coeff_sha
        or cfg.get("direct_replay_sha256")!=direct_sha
        or cfg.get("direct_verified")!=DIRECT_COUNT
        or cfg.get("normalized_needed")!=TOTAL_KEYS-DIRECT_COUNT
        or cfg.get("jobs_sha256")!=job_sha
        or not isinstance(checked,list) or len(checked)!=TOTAL_KEYS-DIRECT_COUNT
        or any(not isinstance(r,dict) or r.get("index")!=DIRECT_COUNT+i
               or r.get("key")!=list(jobs[DIRECT_COUNT+i])
               or r.get("method")!=METHOD for i,r in enumerate(checked))):
        raise RuntimeError("217 normalized exact certificates incomplete or invalid")
    # load() separately verifies all 113 ordered direct and all 259 ordered
    # independently exact coefficient checks, with immutable SHA provenance.
    old=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    new=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    validate_scratch(old,new)
    rem=new["remaining"];src=new["source"]
    if (new.get("steps")!=66 or new.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF"
        or len(new.get("pivot_path",[]))!=66
        or new["pivot_path"][65]!=[166596414013440,139]
        or len(rem)!=75 or len(src)!=153
        or len({tuple(k) for k,v in rem})!=75
        or len({int(k) for k,v in src})!=153
        or rem!=sorted(rem,key=lambda e:tuple(e[0]))
        or src!=sorted(src,key=lambda e:int(e[0]))
        or any(not isinstance(v,str) or not v or v=="0" or len(v)>7500
               for _,v in rem+src)
        or max(len(v) for _,v in rem+src)!=5707
        or new.get("exact_target_proven") is not False
        or new.get("original_source_replay_proven") is not False
        or new.get("protected_source_checkpoint_modified") is not False
        or new["metrics"].get("lead")!=[166596414013441,139]
        or new["metrics"].get("remainder_terms")!=75
        or new["metrics"].get("original_support")!=153
        or new["metrics"].get("max_expression_chars")!=5707):
        raise RuntimeError("Step66 scratch state is not an exact safe formal successor")
    paths=[p for p,_ in PROTECTED]+[SCRATCH,COEFFICIENT,DIRECT,NORMALIZED,BACKUP,TEMP]
    if len(paths)!=len(set(p.resolve() for p in paths)):
        raise RuntimeError("Promotion or evidence path aliases protected input")
    if BACKUP.exists() or TEMP.exists():
        raise FileExistsError("Existing Step65 backup or staging file; inspect, never overwrite")
    return {"old_sha256":SAVED_STEP65_SHA,"new_sha256":EXPECTED_STEP66_SHA,
            "direct_keys":DIRECT_COUNT,"normalized_keys":TOTAL_KEYS-DIRECT_COUNT,
            "original_ibp_keys":TOTAL_KEYS,"coefficient_checks":259,
            "normalized_checkpoint_sha256":evidence_sha,
            "coefficient_checkpoint_sha256":coeff_sha,
            "direct_checkpoint_sha256":direct_sha,
            "new_steps":66,"remainder_terms":75,"original_support":153,
            "target_b_proven":False}

def promote(check_only=True):
    summary=validate()
    if check_only:
        return {"status":"B_STEP66_FORMAL_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF",**summary,
                "formal_state_modified":False}
    old=B_STATE.read_bytes()
    if hashlib.sha256(old).hexdigest()!=SAVED_STEP65_SHA:
        raise RuntimeError("Formal Step65 changed immediately before backup")
    with BACKUP.open("xb") as stream:
        stream.write(old);stream.flush();os.fsync(stream.fileno())
    if sha(BACKUP)!=SAVED_STEP65_SHA:
        raise RuntimeError("Backup SHA mismatch: formal state not modified")
    # Preserve the exact scratch bytes (already hashed and metadata verified).
    new=SCRATCH.read_bytes()
    if hashlib.sha256(new).hexdigest()!=EXPECTED_STEP66_SHA:
        raise RuntimeError("Scratch changed before staging")
    with TEMP.open("xb") as stream:
        stream.write(new);stream.flush();os.fsync(stream.fileno())
    if sha(TEMP)!=EXPECTED_STEP66_SHA:
        raise RuntimeError("Staged state SHA mismatch")
    immutable=[*PROTECTED,(SCRATCH,EXPECTED_STEP66_SHA),
               (COEFFICIENT,summary["coefficient_checkpoint_sha256"]),
               (DIRECT,summary["direct_checkpoint_sha256"]),
               (NORMALIZED,summary["normalized_checkpoint_sha256"])]
    for path,digest in immutable:
        if sha(path)!=digest:
            raise RuntimeError("Protected file changed before promotion")
    os.replace(TEMP,B_STATE)
    if sha(B_STATE)!=EXPECTED_STEP66_SHA or sha(BACKUP)!=SAVED_STEP65_SHA:
        raise RuntimeError("Promotion output or old formal backup SHA mismatch")
    for path,digest in immutable[1:]:
        if sha(path)!=digest:
            raise RuntimeError("Protected evidence changed during promotion")
    return {"status":"B_STEP66_FORMAL_PREFIX_PROMOTED_WITH_BACKUP_NOT_TARGET_PROOF",
            **summary,"backup_sha256":sha(BACKUP),"formal_state_modified":True}

def main():
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group()
    mode.add_argument("--check-only",action="store_true",help="Read-only preflight (default)")
    mode.add_argument("--promote",action="store_true",help="Explicit backup-first promotion")
    args=ap.parse_args()
    print(TAG+json.dumps(promote(check_only=not args.promote)),flush=True)

if __name__=="__main__":
    main()
