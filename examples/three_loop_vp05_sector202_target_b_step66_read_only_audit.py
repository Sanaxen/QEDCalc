"""Read-only post-promotion audit of exact VP05 Target B Step66.

This does not rerun formal65-only validators (which must fail after promotion).
All provenance artifacts, exact certificates, Target A and earlier backups
remain immutable. No promotion and no whole Target B proof.
"""
from __future__ import annotations
import hashlib
import json
from examples.three_loop_vp05_sector202_target_b_step66_formal_promotion import (
    BACKUP, B_STATE, SAVED_STEP65_SHA, EXPECTED_STEP66_SHA, SCRATCH,
    DIRECT, COEFFICIENT, NORMALIZED, DIRECT_COUNT, TOTAL_KEYS, METHOD,
    PROTECTED, sha,
)
from examples.three_loop_vp05_sector202_target_b_step66_original_ibp_replay import (
    context_config,
)
from examples.three_loop_vp05_sector202_target_b_step66_coefficient_audit import (
    STATUS as COEFF_STATUS,
)
from examples.three_loop_vp05_sector202_target_b_step66_normalized_ibp_replay import (
    STATUS as NORMALIZED_STATUS,
)
from examples.three_loop_vp05_sector202_target_b_step65_read_only_audit import (
    SAVED_STEP65_SHA as EXPECTED_OLD,
)

TAG="VP05_B_STEP66_READ_ONLY_AUDIT "

def inspect():
    expected=[(BACKUP,SAVED_STEP65_SHA),(B_STATE,EXPECTED_STEP66_SHA),
              (SCRATCH,EXPECTED_STEP66_SHA)]
    expected.extend((path,digest) for path,digest in PROTECTED if path.resolve()!=B_STATE.resolve())
    paths=[p.resolve() for p,_ in expected]+[
        DIRECT.resolve(),COEFFICIENT.resolve(),NORMALIZED.resolve()]
    # B state, scratch and archived predecessor must be separate physical paths.
    if len(paths)!=len(set(paths)):
        raise RuntimeError("Post-promotion protected path alias")
    if EXPECTED_OLD!=SAVED_STEP65_SHA:
        raise RuntimeError("Expected predecessor hash changed")
    for path,digest in expected:
        if sha(path)!=digest:
            raise RuntimeError("Post-promotion protected SHA mismatch: "+str(path))
    old=json.loads(BACKUP.read_text(encoding="utf-8-sig"))
    now=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    scratch=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    if (now!=scratch or old.get("steps")!=65 or now.get("steps")!=66
        or now.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF"
        or now.get("config")!=old.get("config")
        or now.get("pivot_path")!=old.get("pivot_path",[])+[[166596414013440,139]]
        or len(now.get("remaining",[]))!=75
        or len(now.get("source",[]))!=153
        or len({tuple(k) for k,v in now["remaining"]})!=75
        or len({int(k) for k,v in now["source"]})!=153
        or now.get("exact_target_proven") is not False
        or now.get("original_source_replay_proven") is not False
        or now.get("metrics",{}).get("lead")!=[166596414013441,139]
        or now.get("metrics",{}).get("max_expression_chars")!=5707):
        raise RuntimeError("Saved formal Step66 not matching audited scratch")
    direct_sha=sha(DIRECT)
    coeff_sha=sha(COEFFICIENT)
    direct=json.loads(DIRECT.read_text(encoding="utf-8-sig"))
    coeff=json.loads(COEFFICIENT.read_text(encoding="utf-8-sig"))
    norm=json.loads(NORMALIZED.read_text(encoding="utf-8-sig"))
    checked_direct=direct.get("checked",[])
    checked_coeff=coeff.get("checked",[])
    checked_norm=norm.get("checked",[])
    cfg=norm.get("config",{})
    if (direct.get("status")!="B_STEP66_ORIGINAL_IBP_PREFIX_NOT_PROOF"
        or direct.get("target_b_proven") is not False
        or len(checked_direct)!=DIRECT_COUNT
        or any(not isinstance(r,dict) or r.get("index")!=i
               or r.get("method")!="original_source_delta_exact"
               for i,r in enumerate(checked_direct))
        or coeff.get("status")!=COEFF_STATUS
        or coeff.get("target_b_proven") is not False
        or len(checked_coeff)!=259
        or any(not isinstance(r,dict) or r.get("index")!=i
               or r.get("method")!="exact_step66_local_update"
               for i,r in enumerate(checked_coeff))
        or norm.get("status")!=NORMALIZED_STATUS
        or norm.get("target_b_proven") is not False
        or norm.get("original_ibp_exact_replay_verified") is not False
        or len(checked_norm)!=TOTAL_KEYS-DIRECT_COUNT
        or any(not isinstance(r,dict) or r.get("index")!=DIRECT_COUNT+i
               or r.get("method")!=METHOD
               for i,r in enumerate(checked_norm))
        or cfg.get("formal_step65_sha256")!=SAVED_STEP65_SHA
        or cfg.get("scratch_step66_sha256")!=EXPECTED_STEP66_SHA
        or cfg.get("coefficient_audit_sha256")!=coeff_sha
        or cfg.get("direct_replay_sha256")!=direct_sha
        or cfg.get("direct_verified")!=DIRECT_COUNT
        or cfg.get("normalized_needed")!=TOTAL_KEYS-DIRECT_COUNT):
        raise RuntimeError("Post-promotion exact certificate counts/bindings invalid")
    for path,digest in expected:
        if sha(path)!=digest:
            raise RuntimeError("Protected source changed during audit")
    if sha(DIRECT)!=direct_sha or sha(COEFFICIENT)!=coeff_sha:
        raise RuntimeError("Exact certificate changed during read-only audit")
    return {"status":"B_STEP66_SAVED_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF",
            "steps":66,"remainder_terms":75,"original_support":153,
            "max_expression_chars":5707,"next_lead":[166596414013441,139],
            "formal_state_sha256":sha(B_STATE),"prior_step65_backup_sha256":sha(BACKUP),
            "original_ibp_keys_verified":TOTAL_KEYS,"coefficient_checks":259,
            "target_b_proven":False,"formal_state_modified":False}

if __name__=="__main__":
    print(TAG+json.dumps(inspect()),flush=True)
