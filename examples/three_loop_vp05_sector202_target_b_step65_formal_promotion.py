"""Backup-first promotion of independently exact-replayed B Step65 candidate.

No whole-target proof is claimed. The full 102-key original-IBP exact replay
checkpoint and all 40 independent coefficient certificates are required.
The old Step64 checkpoint is backed up exclusively before atomic replacement.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os

from examples.three_loop_vp05_sector202_target_b_step65_exact_assembly import (
    REPORT, OUT, AUDIT, STATE, EXPECTED_STEP64_SHA, EXPECTED_CANDIDATE_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step65_original_ibp_replay import (
    REPLAY, load as load_replay,
)
from examples.three_loop_vp05_sector202_target_b_step65_independent_audit import (
    context as coefficient_context,
)
from examples.three_loop_vp05_sector202_target_b_start import (
    A_STATE, A_PROOF, A_STATE_SHA, A_PROOF_SHA,
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
from examples.three_loop_vp05_sector202_target_b_step64_formal_promotion import (BACKUP as STEP63_BACKUP, EXPECTED_STEP63_SHA)
from examples.three_loop_vp05_sector202_target_b_step60_formal_promotion import (
    BACKUP as STEP59_BACKUP, B_STEP59_SHA, SOURCE_CHECKPOINT_SHA,
    ORIGINAL_SOURCE_SHA, CERTIFICATE_SHA,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    CHECKPOINT, SOURCE, CERT, sha,
)

BACKUP = STATE.with_name("vp05_sector202_B_exact_target_state_step64_before_step65_promotion.json")
ASSEMBLED_SHA = "ea51e8c0661fdd68c676d4daf1be03c0bace659156f10ee58b021587a0597861"



def valid_replay_method(row):
    return isinstance(row,dict) and row.get("method")=="unscaled_source_pivot_exact_with_40_certificates"


def protected_hashes():
    return [
        (A_STATE,A_STATE_SHA),(A_PROOF,A_PROOF_SHA),
        (CHECKPOINT,SOURCE_CHECKPOINT_SHA),(SOURCE,ORIGINAL_SOURCE_SHA),
        (CERT,CERTIFICATE_SHA),
        (STEP50_BACKUP,B_STEP50_SHA),(STEP51_BACKUP,B_STEP51_SHA),
        (STEP52_BACKUP,B_STEP52_SHA),(STEP58_BACKUP,B_STEP58_SHA),
        (STEP59_BACKUP,B_STEP59_SHA),
        (STEP63_BACKUP,EXPECTED_STEP63_SHA),
    ]


def validate():
    inputs=[STATE,OUT,AUDIT,REPORT,REPLAY,BACKUP]+[p for p,_ in protected_hashes()]
    if len({p.resolve() for p in inputs})!=len(inputs):
        raise RuntimeError("Protected files alias")
    if sha(STATE)!=EXPECTED_STEP64_SHA or sha(OUT)!=EXPECTED_CANDIDATE_SHA or sha(REPORT)!=ASSEMBLED_SHA:
        raise RuntimeError("Saved Step64 or audited Step65 inputs changed")
    for p,h in protected_hashes():
        if sha(p)!=h:
            raise RuntimeError("Protected input hash mismatch: "+str(p))
    if BACKUP.exists() or STATE.with_name(STATE.name+".tmp").exists():
        raise FileExistsError("Backup or temporary state already exists")
    assembled_sha,lead,pivot_trace,original_rows,pivot_row,jobs=load_replay()
    before=json.loads(STATE.read_text(encoding="utf-8-sig"))
    assembled=json.loads(REPORT.read_text(encoding="utf-8-sig"))
    old_rem={tuple(k):v for k,v in before["remaining"]}
    new_rem={tuple(k):v for k,v in assembled["remaining"]}
    old_src={int(k):v for k,v in before["source"]}
    new_src={int(k):v for k,v in assembled["source"]}
    candidate_state, pivot, coeff_jobs, done, candidate_sha=coefficient_context()
    if candidate_sha!=EXPECTED_CANDIDATE_SHA or len(done)!=40 or len(coeff_jobs)!=40:
        raise RuntimeError("40 independently audited exact coefficient operations are incomplete")
    audit=json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    audited=audit.get("checked",[])
    if (len(audited)!=40 or audit.get("config",{}).get("candidate_sha256")!=EXPECTED_CANDIDATE_SHA
        or audit.get("config",{}).get("state_step64_sha256")!=EXPECTED_STEP64_SHA
        or any(row.get("index")!=i or row.get("id")!=done[i]["id"]
            or row.get("coefficient_sha256")!=hashlib.sha256(done[i]["value"].encode()).hexdigest()
            for i,row in enumerate(audited))):
        raise RuntimeError("Exact coefficient certificates mismatch")
    replay=json.loads(REPLAY.read_text(encoding="utf-8-sig"))
    checked=replay.get("checked",[])
    cfg=replay.get("config",{})
    if (replay.get("version")!=1
        or replay.get("status")!="B_STEP65_ORIGINAL_IBP_PREFIX_NOT_PROOF"
        or replay.get("target_b_proven") is not False
        or replay.get("formal_state_modified") is not False
        or cfg.get("candidate_sha256")!=EXPECTED_CANDIDATE_SHA
        or cfg.get("state_step64_sha256")!=EXPECTED_STEP64_SHA
        or cfg.get("assembled_sha256")!=ASSEMBLED_SHA
        or cfg.get("independent_audit_sha256")!=sha(AUDIT)
        or cfg.get("original_source_sha256")!=ORIGINAL_SOURCE_SHA
        or cfg.get("source_checkpoint_sha256")!=SOURCE_CHECKPOINT_SHA
        or cfg.get("certificate_sha256")!=CERTIFICATE_SHA
        or cfg.get("jobs_count")!=102
        or cfg.get("job_keys_sha256")!=hashlib.sha256(json.dumps([list(k) for k in jobs],separators=(",",":")).encode()).hexdigest()
        or len(jobs)!=102 or not isinstance(checked,list) or len(checked)!=102
        or any(row.get("index")!=i or row.get("key")!=list(jobs[i])
               or not valid_replay_method(row)
               for i,row in enumerate(checked))):
        raise RuntimeError("102/102 exact original-IBP key certificates incomplete or incompatible")
    if (before.get("steps")!=64 or before.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF"
        or before.get("exact_target_proven") is not False
        or len(before.get("pivot_path",[]))!=64 or len(old_rem)!=86 or len(old_src)!=172):
        raise RuntimeError("Formal predecessor Step64 is incompatible")
    lead=min(old_rem)
    if lead!=(166596413882371,139) or len(new_rem)!=85 or len(new_src)!=173 or lead in new_rem:
        raise RuntimeError("Step65 dimensions or pivot cancellation incorrect")
    rem=assembled["remaining"]
    src=assembled["source"]
    if (assembled.get("pivot_lead")!=list(lead) or len(rem)!=85 or len(src)!=173
        or len({tuple(k) for k,v in rem})!=85 or len({int(k) for k,v in src})!=173
        or rem!=[[list(k),v] for k,v in sorted(new_rem.items())]
        or src!=[[k,v] for k,v in sorted(new_src.items())]
        or any(not isinstance(v,str) or not v or v=="0" or len(v)>7500
               for _,v in rem+src)):
        raise RuntimeError("Assembled formal coefficients invalid")
    max_len=max(len(v) for _,v in rem+src)
    if max_len!=assembled.get("max_expression_chars"):
        raise RuntimeError("Saved expression length metadata mismatch")
    config=before.get("config",{})
    if (config.get("target")!="B" or config.get("max_expression_chars")!=7500
        or config.get("max_columns")!=256 or config.get("max_support")!=400
        or config.get("source_checkpoint_sha256")!=SOURCE_CHECKPOINT_SHA
        or config.get("source_sha256")!=ORIGINAL_SOURCE_SHA
        or config.get("certificate_sha256")!=CERTIFICATE_SHA):
        raise RuntimeError("Formal reduction safety config mismatch")
    if (assembled.get("steps_before")!=64 or assembled.get("candidate_step")!=65
        or assembled.get("status")!="B_STEP65_ASSEMBLED_FROM_40_EXACT_RECHECKS_PENDING_ORIGINAL_IBP"
        or assembled.get("independent_exact_coefficient_checks")!=40):
        raise RuntimeError("Step65 assembly metadata mismatch")
    new=dict(before)
    new.update({
        "status":"EXACT_TARGET_PREFIX_NOT_PROOF","steps":65,
        "remaining":rem,"source":src,
        "pivot_path":before["pivot_path"]+[list(lead)],
        "metrics":{
            "remainder_terms":len(rem),"original_support":len(src),
            "row_expression_chars":max((len(v) for _,v in rem),default=0),
            "source_expression_chars":max((len(v) for _,v in src),default=0),
            "max_expression_chars":max_len,
            "lead":list(min(new_rem)) if new_rem else None,
        },
        "exact_target_proven":False,
        "original_source_replay_proven":False,
        "protected_source_checkpoint_modified":False,
    })
    return new


def promote(check_only=False):
    new=validate()
    if check_only:
        return {"status":"B_STEP65_PROMOTION_PREFLIGHT_PASS_NOT_TARGET_PROOF",
                "old_sha256":EXPECTED_STEP64_SHA,"new_steps":65,
                "remainder_terms":85,"original_support":173,
                "max_expression_chars":new["metrics"]["max_expression_chars"],
                "original_ibp_keys_verified":102}
    old=STATE.read_bytes()
    if hashlib.sha256(old).hexdigest()!=EXPECTED_STEP64_SHA:
        raise RuntimeError("Step64 changed before backup")
    with BACKUP.open("xb") as fh:
        fh.write(old);fh.flush();os.fsync(fh.fileno())
    if sha(BACKUP)!=EXPECTED_STEP64_SHA:
        raise RuntimeError("Backup verification failed; formal state remains unchanged")
    for p,h in protected_hashes():
        if sha(p)!=h:raise RuntimeError("Protected input changed after backup")
    temp=STATE.with_name(STATE.name+".tmp")
    with temp.open("x",encoding="utf-8") as fh:
        json.dump(new,fh,ensure_ascii=True,separators=(",",":"))
        fh.flush();os.fsync(fh.fileno())
    if sha(STATE)!=EXPECTED_STEP64_SHA or sha(BACKUP)!=EXPECTED_STEP64_SHA:
        raise RuntimeError("State changed during staging; retaining temporary file")
    os.replace(temp,STATE)
    if json.loads(STATE.read_text(encoding="utf-8-sig"))!=new:
        raise RuntimeError("Saved formal state content mismatch")
    for p,h in protected_hashes():
        if sha(p)!=h:raise RuntimeError("Protected input modified by promotion")
    return {
        "status":"B_STEP65_FORMAL_PREFIX_PROMOTED_WITH_BACKUP_NOT_TARGET_PROOF",
        "old_sha256":EXPECTED_STEP64_SHA,"new_sha256":sha(STATE),
        "backup_sha256":sha(BACKUP),"new_steps":65,
        "remainder_terms":85,"original_support":173,
        "max_expression_chars":new["metrics"]["max_expression_chars"],
        "original_ibp_keys_verified":102,
        "a_protected_unchanged":True,"exact_target_proven":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check-only",action="store_true")
    args=ap.parse_args()
    print("VP05_B_STEP65_PROMOTION "+json.dumps(promote(args.check_only)),flush=True)


if __name__=="__main__":
    main()
