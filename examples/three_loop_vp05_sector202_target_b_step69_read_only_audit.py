"""Read-only independently verifies saved formal Step69 after explicit promotion.

The original source, historical states, exact coefficient/IBP checkpoints,
and SHA-pinned Step68 backup remain immutable. No Step69 computation.
"""
from __future__ import annotations
import hashlib
import json
from examples.three_loop_vp05_sector202_target_b_step69_formal_promotion import (
    B_STATE,BACKUP,SCRATCH,COEFF,IBP,
    EXPECTED_STEP68_SHA,EXPECTED_STEP69_SHA,sha,NEXT_LEAD,
)
from examples.three_loop_vp05_sector202_target_b_step68_formal_promotion import (
    BACKUP as STEP67_BACKUP, EXPECTED_STEP67_SHA,
    SCRATCH as STEP68_SCRATCH,
    COEFF as STEP68_COEFF,IBP as STEP68_IBP,
)
from examples.three_loop_vp05_sector202_target_b_step67_formal_promotion import (
    BACKUP as STEP66_BACKUP,EXPECTED_STEP66_SHA,
    SCRATCH as STEP67_SCRATCH,
    COEFF as STEP67_COEFF,IBP as STEP67_IBP,
)
from examples.three_loop_vp05_sector202_target_b_step66_formal_promotion import (
    BACKUP as STEP65_BACKUP,SAVED_STEP65_SHA,
    SCRATCH as STEP66_SCRATCH,PROTECTED as PRE66_PROTECTED,
    DIRECT as STEP66_DIRECT,COEFFICIENT as STEP66_COEFF,
    NORMALIZED as STEP66_NORMALIZED,
)
from examples.three_loop_vp05_sector202_target_b_step69_exact_audit import STATUS
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    CHECKPOINT,SOURCE,CERT,
)
TAG="VP05_B_STEP69_READ_ONLY_AUDIT "

def manifest(phase,path):
    data=json.loads(path.read_text(encoding="utf-8-sig"))
    cfg=data.get("config",{})
    records=data.get("checked",[])
    if (data.get("version")!=1 or data.get("status")!=STATUS
        or data.get("target_b_proven") is not False
        or data.get("formal_state_modified") is not False
        or not isinstance(records,list) or not records
        or cfg.get("version")!=1 or cfg.get("phase")!=phase
        or cfg.get("formal_step68_sha256")!=EXPECTED_STEP68_SHA
        or cfg.get("scratch_step69_sha256")!=EXPECTED_STEP69_SHA
        or cfg.get("source_checkpoint_sha256")!=sha(CHECKPOINT)
        or cfg.get("source_sha256")!=sha(SOURCE)
        or cfg.get("certificate_sha256")!=sha(CERT)
        or cfg.get("job_count")!=len(records)):
        raise RuntimeError("Step69 saved exact checkpoint has invalid provenance")
    entries=[]
    for i,row in enumerate(records):
        if (not isinstance(row,dict) or row.get("index")!=i
            or row.get("method")!="exact_QQ_z_d_"+phase):
            raise RuntimeError("Step69 saved exact certificate record invalid")
        if phase=="coeff":
            kind,key=row.get("kind"),row.get("key")
            if (kind=="remainder" and
                (not isinstance(key,list) or len(key)!=2
                 or any(type(v) is not int for v in key))):
                raise RuntimeError("Invalid remainder key")
            if kind=="source" and type(key) is not int:
                raise RuntimeError("Invalid source key")
            if kind not in ("source","remainder"):
                raise RuntimeError("Invalid coefficient record kind")
            entries.append([kind,key])
        else:
            key=row.get("key")
            if (not isinstance(key,list) or len(key)!=2
                or any(type(v) is not int for v in key)):
                raise RuntimeError("Invalid original IBP key")
            entries.append(key)
    digest=hashlib.sha256(json.dumps(entries,separators=(",",":")).encode()).hexdigest()
    if (cfg.get("job_sha256")!=digest or
        len({json.dumps(x) for x in entries})!=len(entries)):
        raise RuntimeError("Step69 saved exact job manifest mismatch")
    return cfg,len(records)

def validate_certificate_bridge(coeff_cfg,coeff_count,ibp_cfg,ibp_count,coeff_sha):
    """Different phase counts are expected: 43 original-IBP keys need not equal coefficient keys."""
    if (coeff_count<=0 or ibp_count!=43
        or coeff_cfg.get("job_count")!=coeff_count
        or ibp_cfg.get("job_count")!=ibp_count
        or ibp_cfg.get("coefficient_checkpoint_sha256")!=coeff_sha):
        raise RuntimeError("Step69 coefficient->original IBP evidence not linked")

def inspect():
    expected=[
        (B_STATE,EXPECTED_STEP69_SHA),(SCRATCH,EXPECTED_STEP69_SHA),
        (BACKUP,EXPECTED_STEP68_SHA),
        (STEP68_SCRATCH,EXPECTED_STEP68_SHA),
        (STEP67_BACKUP,EXPECTED_STEP67_SHA),
        (STEP67_SCRATCH,EXPECTED_STEP67_SHA),
        (STEP66_BACKUP,EXPECTED_STEP66_SHA),
        (STEP66_SCRATCH,EXPECTED_STEP66_SHA),
        (STEP65_BACKUP,SAVED_STEP65_SHA)]
    expected.extend((p,h) for p,h in PRE66_PROTECTED
                    if p.resolve()!=B_STATE.resolve())
    evidence=(COEFF,IBP,STEP68_COEFF,STEP68_IBP,STEP67_COEFF,STEP67_IBP,
              STEP66_DIRECT,STEP66_COEFF,STEP66_NORMALIZED)
    paths=[p.resolve() for p,h in expected]+[p.resolve() for p in evidence]
    if len(paths)!=len(set(paths)):
        raise RuntimeError("Step69 post-promotion protected paths overlap")
    for p,h in expected:
        if sha(p)!=h:
            raise RuntimeError("Protected historical Step69 source hash mismatch: "+str(p))
    before=json.loads(BACKUP.read_text(encoding="utf-8-sig"))
    after=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    scratch=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    rem=after.get("remaining",[])
    source=after.get("source",[])
    metrics=after.get("metrics",{})
    if (after!=scratch or before.get("steps")!=68 or after.get("steps")!=69
        or after.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF"
        or after.get("config")!=before.get("config")
        or after.get("pivot_path")!=before.get("pivot_path",[])+[NEXT_LEAD]
        or not rem or len(rem)>=len(before["remaining"])
        or len(rem)>256 or len(source)>400
        or len({tuple(k) for k,v in rem})!=len(rem)
        or len({int(k) for k,v in source})!=len(source)
        or metrics.get("remainder_terms")!=len(rem)
        or metrics.get("original_support")!=len(source)
        or tuple(metrics.get("lead",[]))!=min(tuple(k) for k,v in rem)
        or after.get("exact_target_proven") is not False
        or after.get("original_source_replay_proven") is not False
        or after.get("protected_source_checkpoint_modified") is not False):
        raise RuntimeError("Saved formal Step69 not a valid successor")
    cc,nc=manifest("coeff",COEFF)
    ci,ni=manifest("ibp",IBP)
    validate_certificate_bridge(cc,nc,ci,ni,sha(COEFF))
    saved_evidence=[(p,sha(p)) for p in evidence]
    for p,h in expected+saved_evidence:
        if sha(p)!=h:
            raise RuntimeError("Step69 historical source or evidence changed during audit")
    return {"status":"B_STEP69_SAVED_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF",
        "steps":69,"remainder_terms":len(rem),"original_support":len(source),
        "max_expression_chars":metrics.get("max_expression_chars"),
        "next_lead":metrics.get("lead"),
        "state_sha256":sha(B_STATE),"step68_backup_sha256":sha(BACKUP),
        "coefficient_keys_verified":nc,"original_ibp_keys_verified":ni,
        "formal_state_modified":False,"target_b_proven":False}

if __name__=="__main__":
    print(TAG+json.dumps(inspect()),flush=True)
