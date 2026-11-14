"""SHA-pinned, backup-first formal promotion of audited VP05 sector202 B Step51.

This promotes the previously independently replayed exact Step51 candidate,
NOT a whole Target B proof. All protected original input and A proof hashes
are checked; the old formal B Step50 state is backed up byte-for-byte before
an atomic replacement. Refuses re-use or unexpected prior mutations.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path

from examples.three_loop_vp05_sector202_target_b_start import (
    A_STATE, A_PROOF, A_STATE_SHA, A_PROOF_SHA, B_STATE,
)
from examples.three_loop_vp05_sector202_target_b_step51_exact_candidate import OUT
from examples.three_loop_vp05_sector202_target_b_step51_exact_audit import REPORT
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    CHECKPOINT, SOURCE, CERT, sha,
)

B_STEP50_SHA = "f4c480ee9cd555549f690817c7f6cc4c8d80fcec329fa795e53ef5165955ba47"
B_CANDIDATE_SHA = "bf83c2cf10534e922f2994fd2af0a94516d9460854c97c202ccd728867a4b489"
SOURCE_CHECKPOINT_SHA = "df4bb33ceec4e9bdc60b88090eb358f7a5c5cffbb24ae345c92ffdec821f7107"
ORIGINAL_SOURCE_SHA = "f0dd7f338ead97e455306bc49c4ce475fe8a8bee3e5a866f6fa17de1e9ad0163"
CERTIFICATE_SHA = "512114a669d3fb8761d89bfe11a51cc8ec146d46739a36b61e869edcddb583eb"
BACKUP = B_STATE.with_name("vp05_sector202_B_exact_target_state_step50_before_step51_promotion.json")


def validate(state_path=B_STATE,candidate_path=OUT,report_path=REPORT,backup_path=BACKUP):
    protected = [A_STATE, A_PROOF, CHECKPOINT, SOURCE, CERT]
    if len({p.resolve() for p in [state_path,candidate_path,report_path,backup_path]+protected})!=9:
        raise RuntimeError("State, audit, candidate, backup, or protected files alias")
    if sha(state_path)!=B_STEP50_SHA or sha(candidate_path)!=B_CANDIDATE_SHA:
        raise RuntimeError("Verified Step50 or exact candidate hash mismatch")
    for path,known in [(A_STATE,A_STATE_SHA),(A_PROOF,A_PROOF_SHA),
                       (CHECKPOINT,SOURCE_CHECKPOINT_SHA),
                       (SOURCE,ORIGINAL_SOURCE_SHA),(CERT,CERTIFICATE_SHA)]:
        if sha(path)!=known:
            raise RuntimeError("Protected input changed: "+str(path))
    if backup_path.exists() or state_path.with_name(state_path.name+".tmp").exists():
        raise FileExistsError("Backup or state .tmp already exists; refusing promotion")
    state=json.loads(state_path.read_text(encoding="utf-8-sig"))
    report=json.loads(report_path.read_text(encoding="utf-8-sig"))
    cfg=state.get("config",{})
    if (state.get("steps")!=50
        or state.get("status")!="EXACT_TARGET_CAP_REACHED_NOT_PROOF"
        or state.get("exact_target_proven") is not False
        or cfg.get("target")!="B"
        or len(state.get("remaining",[]))!=102
        or len(state.get("source",[]))!=185
        or len(state.get("pivot_path",[]))!=50
        or cfg.get("max_expression_chars")!=7500
        or cfg.get("max_columns")!=256
        or cfg.get("max_support")!=400
        or cfg.get("source_checkpoint_sha256")!=SOURCE_CHECKPOINT_SHA
        or cfg.get("source_sha256")!=ORIGINAL_SOURCE_SHA
        or cfg.get("certificate_sha256")!=CERTIFICATE_SHA):
        raise RuntimeError("Unexpected formal Step50 metadata")
    lead=min(tuple(k) for k,_ in state["remaining"])
    if lead!=(166595341189120,139):
        raise RuntimeError("Unexpected next pivot lead")
    if (report.get("status")!="B_STEP51_EXACT_ORIGINAL_IBP_REPLAY_PASS_NOT_TARGET_PROOF"
        or report.get("target")!="B"
        or report.get("steps_before")!=50
        or report.get("candidate_step")!=51
        or report.get("candidate_sha256")!=B_CANDIDATE_SHA
        or report.get("state_step50_sha256")!=B_STEP50_SHA
        or report.get("a_state_sha256")!=A_STATE_SHA
        or report.get("a_proof_sha256")!=A_PROOF_SHA
        or report.get("source_checkpoint_sha256")!=SOURCE_CHECKPOINT_SHA
        or report.get("original_source_sha256")!=ORIGINAL_SOURCE_SHA
        or report.get("certificate_sha256")!=CERTIFICATE_SHA
        or report.get("original_ibp_exact_replay_verified") is not True
        or report.get("local_exact_identities_verified")!=288
        or report.get("target_proven") is not False
        or report.get("formal_state_modified") is not False
        or len(report.get("remaining",[]))!=100
        or len(report.get("source",[]))!=186
        or report.get("max_expression_chars")!=7252):
        raise RuntimeError("Audited Step51 proof payload mismatch")
    rem=report["remaining"]
    src=report["source"]
    if len({tuple(k) for k,v in rem})!=100 or len({int(k) for k,v in src})!=186:
        raise RuntimeError("Duplicate post-step keys")
    if (any(not isinstance(v,str) or v=="0" for k,v in rem+src)
        or any(len(v)>7500 for k,v in rem+src)):
        raise RuntimeError("Invalid or oversized formal coefficient")
    sizes=[len(v) for _,v in rem+src]
    if max(sizes,default=0)!=7252:
        raise RuntimeError("Audited max expression length mismatch")
    if any(tuple(k)==lead for k,_ in rem):
        raise RuntimeError("Eliminated pivot lead still present")
    new=state.copy()
    new.update({"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                "steps":51,
                "remaining":rem,"source":src,
                "pivot_path":state["pivot_path"]+[list(lead)],
                "metrics":{
                    "remainder_terms":len(rem),"original_support":len(src),
                    "row_expression_chars":max((len(v) for _,v in rem),default=0),
                    "source_expression_chars":max((len(v) for _,v in src),default=0),
                    "max_expression_chars":max(sizes,default=0),
                    "lead":list(min(tuple(k) for k,v in rem)) if rem else None},
                "exact_target_proven":False,
                "original_source_replay_proven":False,
                "protected_source_checkpoint_modified":False})
    return new


def promote(state_path=B_STATE,candidate_path=OUT,report_path=REPORT,backup_path=BACKUP,
            check_only=False):
    new=validate(state_path,candidate_path,report_path,backup_path)
    if check_only:
        return {"status":"B_STEP51_PROMOTION_PREFLIGHT_PASS_NOT_PROOF",
                "old_sha256":B_STEP50_SHA,"new_steps":51,
                "remainder_terms":100,"original_support":186,
                "max_expression_chars":7252}
    old=state_path.read_bytes()
    if hashlib.sha256(old).hexdigest()!=B_STEP50_SHA:
        raise RuntimeError("Step50 changed during preflight")
    # Persistent, exclusive, fsync'd backup before formal replacement.
    with backup_path.open("xb") as stream:
        stream.write(old);stream.flush();os.fsync(stream.fileno())
    if sha(backup_path)!=B_STEP50_SHA:
        raise RuntimeError("Backup integrity failure; formal state not changed")
    tmp=state_path.with_name(state_path.name+".tmp")
    with tmp.open("x",encoding="utf-8") as stream:
        json.dump(new,stream,ensure_ascii=True,separators=(",",":"))
        stream.flush();os.fsync(stream.fileno())
    if sha(state_path)!=B_STEP50_SHA:
        raise RuntimeError("Step50 changed while preparing new state; .tmp retained")
    os.replace(tmp,state_path)
    actual=json.loads(state_path.read_text(encoding="utf-8-sig"))
    if actual!=new or sha(backup_path)!=B_STEP50_SHA:
        raise RuntimeError("Post-promotion mismatch")
    for path,expected in [(A_STATE,A_STATE_SHA),(A_PROOF,A_PROOF_SHA),
                          (CHECKPOINT,SOURCE_CHECKPOINT_SHA),
                          (SOURCE,ORIGINAL_SOURCE_SHA),(CERT,CERTIFICATE_SHA)]:
        if sha(path)!=expected:
            raise RuntimeError("Post-promotion protected input mismatch")
    return {"status":"B_STEP51_FORMAL_PREFIX_PROMOTED_WITH_BACKUP_NOT_TARGET_PROOF",
            "old_sha256":B_STEP50_SHA,"new_sha256":sha(state_path),
            "backup_sha256":sha(backup_path),"new_steps":51,
            "remainder_terms":100,"original_support":186,
            "max_expression_chars":7252,
            "exact_target_proven":False,"a_protected_unchanged":True}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check-only",action="store_true")
    args=ap.parse_args()
    print("VP05_B_STEP51_PROMOTION "+json.dumps(promote(check_only=args.check_only)),flush=True)


if __name__=="__main__":
    main()
