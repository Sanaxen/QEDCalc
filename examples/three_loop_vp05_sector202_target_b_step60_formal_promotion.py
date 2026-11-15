"""SHA-pinned, backup-first formal promotion of audited VP05 sector202 B Step60.

This promotes the previously independently replayed exact Step60 candidate,
NOT a whole Target B proof. All protected original input and A proof hashes
are checked; the old formal B Step59 state is backed up byte-for-byte before
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
from examples.three_loop_vp05_sector202_target_b_step60_exact_candidate import OUT
from examples.three_loop_vp05_sector202_target_b_step51_formal_promotion import BACKUP as STEP50_BACKUP, B_STEP50_SHA
from examples.three_loop_vp05_sector202_target_b_step52_formal_promotion import BACKUP as STEP51_BACKUP, B_STEP51_SHA
from examples.three_loop_vp05_sector202_target_b_step53_formal_promotion import BACKUP as STEP52_BACKUP, B_STEP52_SHA
from examples.three_loop_vp05_sector202_target_b_step60_exact_audit import REPORT
from examples.three_loop_vp05_sector202_target_b_step59_formal_promotion import BACKUP as STEP58_BACKUP, B_STEP58_SHA
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    CHECKPOINT, SOURCE, CERT, sha,
)

B_STEP59_SHA = "a5a341737487cc4a1f2e20323b1adc927ead02e043af44db4442857a7cfdc38a"
B_CANDIDATE_SHA = "3c75321db601464d35163838f712b675955ca5db9fec7290e116851ac8d4fd09"
SOURCE_CHECKPOINT_SHA = "df4bb33ceec4e9bdc60b88090eb358f7a5c5cffbb24ae345c92ffdec821f7107"
ORIGINAL_SOURCE_SHA = "f0dd7f338ead97e455306bc49c4ce475fe8a8bee3e5a866f6fa17de1e9ad0163"
CERTIFICATE_SHA = "512114a669d3fb8761d89bfe11a51cc8ec146d46739a36b61e869edcddb583eb"
BACKUP = B_STATE.with_name("vp05_sector202_B_exact_target_state_step59_before_step60_promotion.json")


def validate(state_path=B_STATE,candidate_path=OUT,report_path=REPORT,backup_path=BACKUP):
    protected = [A_STATE, A_PROOF, CHECKPOINT, SOURCE, CERT]
    if len({p.resolve() for p in [state_path,candidate_path,report_path,backup_path,STEP50_BACKUP,STEP51_BACKUP,STEP52_BACKUP,STEP58_BACKUP]+protected})!=13:
        raise RuntimeError("State, audit, candidate, backup, or protected files alias")
    if (sha(STEP50_BACKUP)!=B_STEP50_SHA or sha(STEP51_BACKUP)!=B_STEP51_SHA
            or sha(STEP52_BACKUP)!=B_STEP52_SHA
            or sha(STEP58_BACKUP)!=B_STEP58_SHA):
        raise RuntimeError("Protected Prior B backup hash mismatch")
    if sha(state_path)!=B_STEP59_SHA or sha(candidate_path)!=B_CANDIDATE_SHA:
        raise RuntimeError("Verified Step59 or exact candidate hash mismatch")
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
    if (state.get("steps")!=59
        or state.get("status")!="EXACT_TARGET_CAP_REACHED_NOT_PROOF"
        or state.get("exact_target_proven") is not False
        or cfg.get("target")!="B"
        or len(state.get("remaining",[]))!=86
        or len(state.get("source",[]))!=163
        or len(state.get("pivot_path",[]))!=59
        or cfg.get("max_expression_chars")!=7500
        or cfg.get("max_columns")!=256
        or cfg.get("max_support")!=400
        or cfg.get("source_checkpoint_sha256")!=SOURCE_CHECKPOINT_SHA
        or cfg.get("source_sha256")!=ORIGINAL_SOURCE_SHA
        or cfg.get("certificate_sha256")!=CERTIFICATE_SHA):
        raise RuntimeError("Unexpected formal Step59 metadata")
    lead=min(tuple(k) for k,_ in state["remaining"])
    if lead!=(166596413227009,139):
        raise RuntimeError("Unexpected next pivot lead")
    if (report.get("status")!="B_STEP60_EXACT_ORIGINAL_IBP_REPLAY_PASS_NOT_TARGET_PROOF"
        or report.get("target")!="B"
        or report.get("steps_before")!=59
        or report.get("candidate_step")!=60
        or report.get("candidate_sha256")!=B_CANDIDATE_SHA
        or report.get("state_step59_sha256")!=B_STEP59_SHA
        or report.get("a_state_sha256")!=A_STATE_SHA
        or report.get("a_proof_sha256")!=A_PROOF_SHA
        or report.get("source_checkpoint_sha256")!=SOURCE_CHECKPOINT_SHA
        or report.get("original_source_sha256")!=ORIGINAL_SOURCE_SHA
        or report.get("certificate_sha256")!=CERTIFICATE_SHA
        or report.get("step50_backup_sha256")!=B_STEP50_SHA
        or report.get("step51_backup_sha256")!=B_STEP51_SHA
        or report.get("step52_backup_sha256")!=B_STEP52_SHA
        or report.get("step58_backup_sha256")!=B_STEP58_SHA
        or report.get("remainder_terms")!=85
        or report.get("source_support")!=164
        or report.get("original_ibp_exact_replay_verified") is not True
        or report.get("local_exact_identities_verified")!=24
        or report.get("target_proven") is not False
        or report.get("formal_state_modified") is not False
        or len(report.get("remaining",[]))!=85
        or len(report.get("source",[]))!=164
        or report.get("max_expression_chars")!=7356):
        raise RuntimeError("Audited Step60 proof payload mismatch")
    rem=report["remaining"]
    src=report["source"]
    if len({tuple(k) for k,v in rem})!=85 or len({int(k) for k,v in src})!=164:
        raise RuntimeError("Duplicate post-step keys")
    if (any(not isinstance(v,str) or v=="0" for k,v in rem+src)
        or any(len(v)>7500 for k,v in rem+src)):
        raise RuntimeError("Invalid or oversized formal coefficient")
    sizes=[len(v) for _,v in rem+src]
    if max(sizes,default=0)!=7356:
        raise RuntimeError("Audited max expression length mismatch")
    if any(tuple(k)==lead for k,_ in rem):
        raise RuntimeError("Eliminated pivot lead still present")
    # Reject stale audit/changed candidate before constructing the formal state.
    if sha(candidate_path)!=B_CANDIDATE_SHA:
        raise RuntimeError("Step60 candidate changed after independent exact replay")
    new=state.copy()
    new.update({"status":"EXACT_TARGET_PREFIX_NOT_PROOF",
                "steps":60,
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
        return {"status":"B_STEP60_PROMOTION_PREFLIGHT_PASS_NOT_PROOF",
                "old_sha256":B_STEP59_SHA,"new_steps":60,
                "remainder_terms":85,"original_support":164,
                "max_expression_chars":7356}
    old=state_path.read_bytes()
    if hashlib.sha256(old).hexdigest()!=B_STEP59_SHA:
        raise RuntimeError("Step59 changed during preflight")
    # Persistent, exclusive, fsync'd backup before formal replacement.
    with backup_path.open("xb") as stream:
        stream.write(old);stream.flush();os.fsync(stream.fileno())
    if (sha(backup_path)!=B_STEP59_SHA or sha(STEP50_BACKUP)!=B_STEP50_SHA
            or sha(STEP51_BACKUP)!=B_STEP51_SHA or sha(STEP52_BACKUP)!=B_STEP52_SHA
            or sha(STEP58_BACKUP)!=B_STEP58_SHA):
        raise RuntimeError("Backup integrity failure; formal state not changed")
    tmp=state_path.with_name(state_path.name+".tmp")
    with tmp.open("x",encoding="utf-8") as stream:
        json.dump(new,stream,ensure_ascii=True,separators=(",",":"))
        stream.flush();os.fsync(stream.fileno())
    if sha(state_path)!=B_STEP59_SHA:
        raise RuntimeError("Step59 changed while preparing new state; .tmp retained")
    os.replace(tmp,state_path)
    actual=json.loads(state_path.read_text(encoding="utf-8-sig"))
    if (actual!=new or sha(backup_path)!=B_STEP59_SHA
            or sha(STEP50_BACKUP)!=B_STEP50_SHA or sha(STEP51_BACKUP)!=B_STEP51_SHA
            or sha(STEP52_BACKUP)!=B_STEP52_SHA
            or sha(STEP58_BACKUP)!=B_STEP58_SHA):
        raise RuntimeError("Post-promotion mismatch")
    for path,expected in [(A_STATE,A_STATE_SHA),(A_PROOF,A_PROOF_SHA),
                          (CHECKPOINT,SOURCE_CHECKPOINT_SHA),
                          (SOURCE,ORIGINAL_SOURCE_SHA),(CERT,CERTIFICATE_SHA)]:
        if sha(path)!=expected:
            raise RuntimeError("Post-promotion protected input mismatch")
    return {"status":"B_STEP60_FORMAL_PREFIX_PROMOTED_WITH_BACKUP_NOT_TARGET_PROOF",
            "old_sha256":B_STEP59_SHA,"new_sha256":sha(state_path),
            "backup_sha256":sha(backup_path),"step50_backup_sha256":sha(STEP50_BACKUP),"step51_backup_sha256":sha(STEP51_BACKUP),"step52_backup_sha256":sha(STEP52_BACKUP),"step58_backup_sha256":sha(STEP58_BACKUP),
            "new_steps":actual["steps"],
            "remainder_terms":len(actual["remaining"]),
            "original_support":len(actual["source"]),
            "max_expression_chars":max((len(v) for _,v in actual["remaining"]+actual["source"]),default=0),
            "exact_target_proven":False,"a_protected_unchanged":True}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check-only",action="store_true")
    args=ap.parse_args()
    print("VP05_B_STEP60_PROMOTION "+json.dumps(promote(check_only=args.check_only)),flush=True)


if __name__=="__main__":
    main()
