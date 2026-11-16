"""Assemble independently rechecked Step65 coefficients without changing formal state.

This is a strict, read-only-with-respect-to-inputs assembly and NOT an
original-IBP replay or Target B proof. Creates one separate candidate
snapshot only after all 40 exact independent local checks passed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from examples.three_loop_vp05_sector202_target_b_step65_independent_audit import (
    context, AUDIT, EXPECTED_STEP64_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step65_exact_candidate import (
    OUT, STATE,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT, sha,
)
from examples.three_loop_vp05_sector202_target_b_start import (
    A_STATE, A_PROOF, A_STATE_SHA, A_PROOF_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step59_formal_promotion import (
    BACKUP as STEP58_BACKUP, B_STEP58_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step60_formal_promotion import (
    BACKUP as STEP59_BACKUP, B_STEP59_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step64_formal_promotion import (
    BACKUP as STEP63_BACKUP, EXPECTED_STEP63_SHA,
)
from examples.three_loop_vp05_sector202_step51_scratch import atomic_save

REPORT = BASE / "vp05_sector202_B_step65_assembled_candidate_pending_original_ibp.json"
EXPECTED_CANDIDATE_SHA = "9d4a2a24f0d6f15c54fd6cc72b0a542bcfc6fe6756bcd5965594fc73d4608d12"


def assemble(report_path=REPORT):
    state, pivot, jobs, done, candidate_sha = context()
    if candidate_sha != EXPECTED_CANDIDATE_SHA or sha(STATE) != EXPECTED_STEP64_SHA:
        raise RuntimeError("Step65 candidate or previous saved state SHA mismatch")
    if sha(A_STATE)!=A_STATE_SHA or sha(A_PROOF)!=A_PROOF_SHA or sha(STEP58_BACKUP)!=B_STEP58_SHA or sha(STEP59_BACKUP)!=B_STEP59_SHA or sha(STEP63_BACKUP)!=EXPECTED_STEP63_SHA:
        raise RuntimeError("Protected input hashes changed")
    audit_sha=sha(AUDIT)
    audit=json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    prefix=audit.get("checked")
    if (audit.get("version")!=1 or audit.get("status")!="INDEPENDENT_LOCAL_PREFIX_NOT_PROOF"
        or audit.get("target_b_proven") is not False
        or audit.get("original_ibp_exact_replay_verified") is not False
        or audit.get("formal_state_modified") is not False
        or audit.get("config",{}).get("candidate_sha256")!=EXPECTED_CANDIDATE_SHA
        or audit.get("config",{}).get("state_step64_sha256")!=EXPECTED_STEP64_SHA
        or not isinstance(prefix,list) or len(prefix)!=40
        or any(row.get("index")!=i or row.get("id")!=done[i]["id"]
               or row.get("coefficient_sha256")!=hashlib.sha256(done[i]["value"].encode()).hexdigest()
               for i,row in enumerate(prefix))):
        raise RuntimeError("40 independent exact checks are incomplete or mismatched")
    lead=min(tuple(k) for k,v in state["remaining"])
    if lead!=(166596413882371,139):
        raise RuntimeError("Unexpected Step65 pivot lead")
    rem={tuple(k):v for k,v in state["remaining"]}
    src={int(k):v for k,v in state["source"]}
    if len(rem)!=86 or len(src)!=172:
        raise RuntimeError("Step64 input dimensions mismatch")
    for (kind,key,_),item in zip(jobs,done):
        if item.get("within_formal_cap") is not True or item.get("exact_local_identity") is not True:
            raise RuntimeError("Coefficient lacks local exact certificate")
        target=rem if kind=="remainder" else src
        val=item["value"]
        if not isinstance(val,str) or len(val)>7500:
            raise RuntimeError("Oversize or malformed candidate coefficient")
        if val=="0":
            target.pop(key,None)
        else:
            target[key]=val
    if lead in rem or len(rem)!=85 or len(src)!=173:
        raise RuntimeError("Step65 assembled terms/support differ from saved cap-stop forecast")
    if any(not v or v=="0" or len(v)>7500 for v in list(rem.values())+list(src.values())):
        raise RuntimeError("Invalid assembled coefficient")
    sizes=[len(v) for v in list(rem.values())+list(src.values())]
    max_chars=max(sizes,default=0)
    payload={
        "status":"B_STEP65_ASSEMBLED_FROM_40_EXACT_RECHECKS_PENDING_ORIGINAL_IBP",
        "target":"B","steps_before":63,"candidate_step":64,
        "state_step64_sha256":EXPECTED_STEP64_SHA,
        "candidate_sha256":candidate_sha,
        "independent_audit_sha256":audit_sha,
        "independent_exact_coefficient_checks":40,
        "source_checkpoint_sha256":sha(CHECKPOINT),
        "original_source_sha256":sha(SOURCE),
        "certificate_sha256":sha(CERT),
        "a_state_sha256":A_STATE_SHA,"a_proof_sha256":A_PROOF_SHA,
        "step58_backup_sha256":B_STEP58_SHA,
        "step59_backup_sha256":B_STEP59_SHA,
        "step63_backup_sha256":EXPECTED_STEP63_SHA,
        "pivot_lead":list(lead),
        "remainder_terms":len(rem),"original_support":len(src),
        "max_expression_chars":max_chars,
        "remaining":[[list(k),v] for k,v in sorted(rem.items())],
        "source":[[k,v] for k,v in sorted(src.items())],
        "original_ibp_exact_replay_verified":False,
        "formal_state_modified":False,
        "target_proven":False,
    }
    protected=[STATE,OUT,AUDIT,CHECKPOINT,SOURCE,CERT,A_STATE,A_PROOF,STEP58_BACKUP,STEP59_BACKUP,STEP63_BACKUP]
    if report_path.resolve() in {p.resolve() for p in protected}:
        raise RuntimeError("Assembled report aliases protected input")
    if report_path.exists():
        raise FileExistsError("Report exists; refusing overwrite")
    for p,h in [(STATE,EXPECTED_STEP64_SHA),(OUT,EXPECTED_CANDIDATE_SHA),
                (AUDIT,audit_sha),(A_STATE,A_STATE_SHA),(A_PROOF,A_PROOF_SHA),
                (STEP58_BACKUP,B_STEP58_SHA),(STEP59_BACKUP,B_STEP59_SHA),(STEP63_BACKUP,EXPECTED_STEP63_SHA)]:
        if sha(p)!=h:raise RuntimeError("Input mutated during assembly: "+str(p))
    atomic_save(report_path,payload,False)
    return {k:v for k,v in payload.items() if k not in ("remaining","source")}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,default=REPORT)
    args=ap.parse_args()
    print("VP05_B_STEP65_ASSEMBLY "+json.dumps(assemble(args.output)),flush=True)


if __name__=="__main__":
    main()
