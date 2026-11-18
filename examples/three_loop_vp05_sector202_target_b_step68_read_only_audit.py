"""Read-only post-promotion check of saved formal Step68 and original evidence.

Avoids prepromotion validators that require formal67. No writes and no whole
Target B proof claim. The exact certificates are checked against SHA-pinned
provenance, ordered job manifests and the 232/298 verified inventories.
"""
from __future__ import annotations
import hashlib
import json
from examples.three_loop_vp05_sector202_target_b_step68_formal_promotion import (
    B_STATE,BACKUP,SCRATCH,COEFF,IBP,
    EXPECTED_STEP67_SHA,EXPECTED_STEP68_SHA,NEXT_LEAD,sha,
)
from examples.three_loop_vp05_sector202_target_b_step67_formal_promotion import (
    BACKUP as STEP66_BACKUP, EXPECTED_STEP66_SHA,
    SCRATCH as STEP67_SCRATCH,
    COEFF as STEP67_COEFF,IBP as STEP67_IBP,
)
from examples.three_loop_vp05_sector202_target_b_step66_formal_promotion import (
    BACKUP as STEP65_BACKUP,SAVED_STEP65_SHA,
    SCRATCH as STEP66_SCRATCH,
    DIRECT as STEP66_DIRECT,COEFFICIENT as STEP66_COEFF,
    NORMALIZED as STEP66_NORMALIZED,PROTECTED as PRE66_PROTECTED,
)
from examples.three_loop_vp05_sector202_target_b_step68_exact_audit import STATUS
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    CHECKPOINT,SOURCE,CERT,
)
TAG="VP05_B_STEP68_READ_ONLY_AUDIT "

def manifest(phase,path):
    data=json.loads(path.read_text(encoding="utf-8-sig"))
    cfg=data.get("config",{})
    records=data.get("checked",[])
    if (data.get("version")!=1 or data.get("status")!=STATUS
        or data.get("target_b_proven") is not False
        or data.get("formal_state_modified") is not False
        or not isinstance(records,list) or not records
        or cfg.get("version")!=1 or cfg.get("phase")!=phase
        or cfg.get("formal_step67_sha256")!=EXPECTED_STEP67_SHA
        or cfg.get("scratch_step68_sha256")!=EXPECTED_STEP68_SHA
        or cfg.get("source_checkpoint_sha256")!=sha(CHECKPOINT)
        or cfg.get("source_sha256")!=sha(SOURCE)
        or cfg.get("certificate_sha256")!=sha(CERT)
        or cfg.get("job_count")!=len(records)):
        raise RuntimeError("Step68 exact certificate manifest incomplete")
    entries=[]
    for i,row in enumerate(records):
        if (not isinstance(row,dict) or row.get("index")!=i
            or row.get("method")!="exact_QQ_z_d_"+phase):
            raise RuntimeError("Unbound Step68 certificate record")
        if phase=="coeff":
            kind,key=row.get("kind"),row.get("key")
            if (kind=="remainder" and
                    (not isinstance(key,list) or len(key)!=2 or
                     any(type(v) is not int for v in key))):
                raise RuntimeError("Bad remainder coefficient key")
            if kind=="source" and type(key) is not int:
                raise RuntimeError("Bad source coefficient key")
            if kind not in ("remainder","source"):
                raise RuntimeError("Bad coefficient kind")
            entries.append([kind,key])
        else:
            key=row.get("key")
            if (not isinstance(key,list) or len(key)!=2 or
                any(type(v) is not int for v in key)):
                raise RuntimeError("Bad original IBP key")
            entries.append(key)
    digest=hashlib.sha256(json.dumps(entries,separators=(",",":")).encode()).hexdigest()
    if cfg.get("job_sha256")!=digest or len({json.dumps(k) for k in entries})!=len(entries):
        raise RuntimeError("Step68 ordered certificate inventory mismatch")
    return cfg,len(records)

def inspect():
    expected=[
        (B_STATE,EXPECTED_STEP68_SHA),(SCRATCH,EXPECTED_STEP68_SHA),
        (BACKUP,EXPECTED_STEP67_SHA),
        (STEP67_SCRATCH,EXPECTED_STEP67_SHA),
        (STEP66_BACKUP,EXPECTED_STEP66_SHA),
        (STEP66_SCRATCH,EXPECTED_STEP66_SHA),
        (STEP65_BACKUP,SAVED_STEP65_SHA),
    ]
    expected.extend((p,h) for p,h in PRE66_PROTECTED
                    if p.resolve()!=B_STATE.resolve())
    evidence=(COEFF,IBP,STEP67_COEFF,STEP67_IBP,
              STEP66_DIRECT,STEP66_COEFF,STEP66_NORMALIZED)
    paths=[p.resolve() for p,h in expected]+[p.resolve() for p in evidence]
    if len(paths)!=len(set(paths)):
        raise RuntimeError("Step68 post-audit protected paths overlap")
    for p,h in expected:
        if sha(p)!=h:
            raise RuntimeError("Step68 historical protected source SHA mismatch: "+str(p))
    old=json.loads(BACKUP.read_text(encoding="utf-8-sig"))
    now=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    scratch=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    if (now!=scratch or old.get("steps")!=67 or now.get("steps")!=68
        or now.get("config")!=old.get("config")
        or now.get("pivot_path")!=old.get("pivot_path",[])+[NEXT_LEAD]
        or now.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF"
        or len(now.get("remaining",[]))!=59
        or len(now.get("source",[]))!=144
        or len({tuple(k) for k,v in now["remaining"]})!=59
        or len({int(k) for k,v in now["source"]})!=144
        or now.get("exact_target_proven") is not False
        or now.get("original_source_replay_proven") is not False
        or now.get("protected_source_checkpoint_modified") is not False
        or now.get("metrics",{}).get("remainder_terms")!=59
        or now.get("metrics",{}).get("original_support")!=144
        or now.get("metrics",{}).get("max_expression_chars")!=3174
        or now.get("metrics",{}).get("lead")!=[166596414013443,139]):
        raise RuntimeError("Saved formal Step68 inconsistent with exact successor")
    c_cfg,c_count=manifest("coeff",COEFF)
    i_cfg,i_count=manifest("ibp",IBP)
    if (c_count!=232 or i_count!=298
        or i_cfg.get("coefficient_checkpoint_sha256")!=sha(COEFF)):
        raise RuntimeError("Step68 232/298 exact certificate bridge invalid")
    evidence_hashes=[(p,sha(p)) for p in evidence]
    for p,h in expected+evidence_hashes:
        if sha(p)!=h:
            raise RuntimeError("Protected evidence changed during Step68 audit")
    return {"status":"B_STEP68_SAVED_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF",
            "steps":68,"remainder_terms":59,"original_support":144,
            "max_expression_chars":3174,"next_lead":[166596414013443,139],
            "state_sha256":sha(B_STATE),
            "step67_backup_sha256":sha(BACKUP),
            "coefficient_keys_verified":c_count,
            "original_ibp_keys_verified":i_count,
            "formal_state_modified":False,"target_b_proven":False}

if __name__=="__main__":
    print(TAG+json.dumps(inspect()),flush=True)
