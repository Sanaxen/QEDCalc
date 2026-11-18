"""Read-only post-promotion audit of Target B formal Step67 and saved evidence.

Runs only AFTER successful Step67 --promote. Never writes or claims full
Target B proof. Avoids predecessor validators that require formal Step66.
"""
from __future__ import annotations
import hashlib
import json
from examples.three_loop_vp05_sector202_target_b_step67_formal_promotion import (
    B_STATE,BACKUP,SCRATCH,COEFF,IBP,EXPECTED_STEP66_SHA,
    EXPECTED_STEP67_SHA,NEXT_LEAD,sha,
)
from examples.three_loop_vp05_sector202_target_b_step66_formal_promotion import (
    BACKUP as STEP65_BACKUP, SAVED_STEP65_SHA,
    SCRATCH as OLD_SCRATCH, PROTECTED as BEFORE_66_PROTECTED,
    DIRECT as STEP66_DIRECT, COEFFICIENT as STEP66_COEFF,
    NORMALIZED as STEP66_NORMALIZED,
)
from examples.three_loop_vp05_sector202_target_b_step67_exact_audit import STATUS
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    CHECKPOINT,SOURCE,CERT,
)

TAG="VP05_B_STEP67_READ_ONLY_AUDIT "

def manifest(phase,path):
    data=json.loads(path.read_text(encoding="utf-8-sig"))
    cfg=data.get("config",{})
    checked=data.get("checked",[])
    if (data.get("version")!=1 or data.get("status")!=STATUS
        or data.get("target_b_proven") is not False
        or data.get("formal_state_modified") is not False
        or not isinstance(checked,list) or not checked
        or cfg.get("version")!=1 or cfg.get("phase")!=phase
        or cfg.get("formal_step66_sha256")!=EXPECTED_STEP66_SHA
        or cfg.get("scratch_step67_sha256")!=EXPECTED_STEP67_SHA
        or cfg.get("source_checkpoint_sha256")!=sha(CHECKPOINT)
        or cfg.get("source_sha256")!=sha(SOURCE)
        or cfg.get("certificate_sha256")!=sha(CERT)
        or cfg.get("job_count")!=len(checked)):
        raise RuntimeError("Step67 "+phase+" exact evidence incomplete")
    entries=[]
    for i,row in enumerate(checked):
        if (not isinstance(row,dict) or row.get("index")!=i
            or row.get("method")!="exact_QQ_z_d_"+phase):
            raise RuntimeError("Invalid exact Step67 "+phase+" record")
        if phase=="coeff":
            kind,key=row.get("kind"),row.get("key")
            if kind not in ("remainder","source") or (
                kind=="remainder" and (not isinstance(key,list) or len(key)!=2)
            ) or (kind=="source" and type(key) is not int):
                raise RuntimeError("Invalid coefficient record key")
            entries.append([kind,key])
        else:
            key=row.get("key")
            if not isinstance(key,list) or len(key)!=2:
                raise RuntimeError("Invalid original IBP key")
            entries.append(key)
    digest=hashlib.sha256(json.dumps(entries,separators=(",",":")).encode()).hexdigest()
    if cfg.get("job_sha256")!=digest or len(set(json.dumps(k) for k in entries))!=len(entries):
        raise RuntimeError("Step67 exact evidence manifest/hash mismatch")
    return cfg,len(checked)

def inspect():
    expected=[(B_STATE,EXPECTED_STEP67_SHA),(SCRATCH,EXPECTED_STEP67_SHA),
              (BACKUP,EXPECTED_STEP66_SHA),(STEP65_BACKUP,SAVED_STEP65_SHA),
              (OLD_SCRATCH,EXPECTED_STEP66_SHA)]
    expected.extend((p,h) for p,h in BEFORE_66_PROTECTED if p.resolve()!=B_STATE.resolve())
    protected=[p.resolve() for p,h in expected]+[
        COEFF.resolve(),IBP.resolve(),
        STEP66_DIRECT.resolve(),STEP66_COEFF.resolve(),STEP66_NORMALIZED.resolve()]
    if len(set(protected))!=len(protected):
        raise RuntimeError("Step67 post-audit protected paths overlap")
    for p,h in expected:
        if sha(p)!=h:raise RuntimeError("Step67 historical protected SHA mismatch: "+str(p))
    old=json.loads(BACKUP.read_text(encoding="utf-8-sig"))
    now=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    saved=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    if (now!=saved or old.get("steps")!=66 or now.get("steps")!=67
        or now.get("config")!=old.get("config")
        or now.get("pivot_path")!=old.get("pivot_path",[])+[NEXT_LEAD]
        or now.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF"
        or len(now.get("remaining",[]))!=74 or len(now.get("source",[]))!=154
        or len({tuple(k) for k,v in now["remaining"]})!=74
        or len({int(k) for k,v in now["source"]})!=154
        or now.get("exact_target_proven") is not False
        or now.get("original_source_replay_proven") is not False
        or now.get("protected_source_checkpoint_modified") is not False
        or now.get("metrics",{}).get("remainder_terms")!=74
        or now.get("metrics",{}).get("original_support")!=154
        or now.get("metrics",{}).get("lead")!=[166596414013442,139]
        or now.get("metrics",{}).get("max_expression_chars")!=5726):
        raise RuntimeError("Formal Step67 does not match audited Step66 successor")
    coeff_cfg,coeff_count=manifest("coeff",COEFF)
    ibp_cfg,ibp_count=manifest("ibp",IBP)
    if (ibp_count!=32 or ibp_cfg.get("coefficient_checkpoint_sha256")!=sha(COEFF)):
        raise RuntimeError("Step67 exact coefficient/IBP certificate bridge invalid")
    protected_evidence=[(p,sha(p)) for p in (
        COEFF,IBP,STEP66_DIRECT,STEP66_COEFF,STEP66_NORMALIZED)]
    for p,h in expected+protected_evidence:
        if sha(p)!=h:raise RuntimeError("Source or certificates changed during post-audit")
    return {"status":"B_STEP67_SAVED_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF",
        "steps":67,"remainder_terms":74,"original_support":154,
        "max_expression_chars":5726,"next_lead":[166596414013442,139],
        "state_sha256":sha(B_STATE),"step66_backup_sha256":sha(BACKUP),
        "coefficient_keys_verified":coeff_count,
        "original_ibp_keys_verified":ibp_count,
        "formal_state_modified":False,"target_b_proven":False}

if __name__=="__main__":
    print(TAG+json.dumps(inspect()),flush=True)
