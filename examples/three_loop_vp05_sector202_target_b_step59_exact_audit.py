"""Read-only assembly and exact consistency audit for B Step59 coefficient pilot.

No formal state, candidate file, Target A artifact, or source checkpoint is
modified. Assembles 24 locally checked coefficients, verifies each exact
operation, and independently verifies original-IBP target/residual identity.
A successful report is a prerequisite for a separately guarded promotion.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_target_b_step59_exact_candidate import (
    OUT, STATE, load_context,
)
from examples.three_loop_vp05_sector202_target_b_start import A_STATE,A_PROOF,A_STATE_SHA,A_PROOF_SHA
from examples.three_loop_vp05_sector202_step51_scratch import atomic_save,key_id
from examples.three_loop_vp05_sector202_target_b_step52_formal_promotion import BACKUP as STEP51_BACKUP
from examples.three_loop_vp05_sector202_target_b_step53_formal_promotion import BACKUP as STEP52_BACKUP, B_STEP52_SHA
from examples.three_loop_vp05_sector202_target_b_step51_formal_promotion import BACKUP as STEP50_BACKUP, B_STEP50_SHA
from examples.three_loop_vp05_sector202_target_b_step52_formal_promotion import B_STEP51_SHA
from examples.three_loop_vp05_sector202_target_exact_checkpoint import (
    decoded, trace_decoded, encoded, trace_encoded, metrics,
    assert_modular_invariant,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE,CHECKPOINT,SOURCE,CERT,POINTS,sha,add,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr

REPORT = BASE / "vp05_sector202_B_step59_exact_candidate_audit.json"
EXPECTED_B_STEP58_SHA = "565af78b3e8604782f614515fb2b93d8a25efa6022174a2ca4bcc9673fc56d4b"


def audit(candidate_path=OUT, state_path=STATE, report_path=REPORT):
    if (sha(state_path)!=EXPECTED_B_STEP58_SHA or sha(A_STATE)!=A_STATE_SHA
            or sha(A_PROOF)!=A_PROOF_SHA or sha(STEP50_BACKUP)!=B_STEP50_SHA
            or sha(STEP51_BACKUP)!=B_STEP51_SHA
            or sha(STEP52_BACKUP)!=B_STEP52_SHA):
        raise RuntimeError("Formal B Step58 or proven A inputs changed")
    candidate_sha_start=sha(candidate_path)
    candidate=json.loads(candidate_path.read_text(encoding="utf-8-sig"))
    args=argparse.Namespace(state=state_path,source_checkpoint=CHECKPOINT,input=SOURCE,certificate=CERT)
    state,pivot,jobs,binding=load_context(args)
    done=candidate.get("done",[])
    if (candidate.get("status")!="B_STEP59_EXACT_COEFFICIENT_PREFIX_NOT_PROOF"
        or candidate.get("config")!=binding
        or candidate.get("exact_target_proven") is not False
        or len(done)!=24 or len(done)!=len(jobs)
        or [r.get("id") for r in done]!=binding["jobs"]
        or [r.get("index") for r in done]!=list(range(len(jobs)))
        or any(r.get("kind")!=kind or r.get("key")!=(list(key) if kind=="remainder" else key)
               for r,(kind,key,_) in zip(done,jobs))
        or any(r.get("exact_local_identity") is not True or
               r.get("within_formal_cap") is not True or
               r.get("chars")!=len(r.get("value","")) or
               r.get("chars")>7500 for r in done)):
        raise RuntimeError("Pilot is incomplete, oversized, or not bound to Step58 inputs")
    z,d=sp.symbols("z d")
    before_rem=decoded(state["remaining"],z,d)
    before_src=trace_decoded(state["source"],z,d)
    pivot_rem=decoded(pivot["row"],z,d)
    pivot_src=trace_decoded(pivot["trace"],z,d)
    lead=min(before_rem)
    fac=before_rem[lead]
    after_rem=dict(before_rem)
    after_src=dict(before_src)
    # Preserve short, exact expressions as stored by the coefficient pilot.
    # Re-stringifying a SymPy expression may expand it beyond 7500 characters.
    saved_rem={tuple(k):v for k,v in state["remaining"]}
    saved_src={int(k):v for k,v in state["source"]}
    max_chars=0
    for i,(kind,key,pivot_raw) in enumerate(jobs):
        item=done[i]
        raw=item["value"]
        val=expr(raw,z,d)
        sign=-1 if kind=="remainder" else 1
        target=after_rem if kind=="remainder" else after_src
        old=(before_rem if kind=="remainder" else before_src).get(key,sp.S.Zero)
        # All local identities are rechecked independently, not trusted from the pilot flag.
        if sp.cancel(val-(old+sign*fac*expr(pivot_raw,z,d)))!=0:
            raise AssertionError("Exact coefficient update mismatch at "+str(i))
        saved_target=saved_rem if kind=="remainder" else saved_src
        if val==0:
            target.pop(key,None)
            saved_target.pop(key,None)
        else:
            target[key]=val
            saved_target[key]=raw
        max_chars=max(max_chars,len(raw))
    if lead != (166596413095937,139):
        raise AssertionError("Unexpected Step59 lead")
    if any(len(v)>7500 for v in list(saved_rem.values())+list(saved_src.values())):
        raise RuntimeError("Formal saved expression cap violation")
    if lead in after_rem:
        raise AssertionError("Exact elimination did not cancel pivot lead")
    if len(after_rem)!=86 or len(after_src)!=163:
        raise AssertionError("Step59 candidate dimensions differ from cap-stop metrics")
    if max((len(v) for v in list(saved_rem.values())+list(saved_src.values())),default=0)>7500:
        raise RuntimeError("Candidate saved expression exceeds formal cap")
    if (sha(state_path)!=EXPECTED_B_STEP58_SHA or sha(STEP50_BACKUP)!=B_STEP50_SHA
            or sha(STEP51_BACKUP)!=B_STEP51_SHA or sha(STEP52_BACKUP)!=B_STEP52_SHA
            or sha(A_STATE)!=A_STATE_SHA
            or sha(A_PROOF)!=A_PROOF_SHA or sha(CHECKPOINT)!=binding["source_checkpoint_sha256"]
            or sha(SOURCE)!=binding["source_sha256"] or sha(CERT)!=binding["certificate_sha256"]):
        raise RuntimeError("Protected B Step58 or Step50 backup modified during audit")
    with gzip.open(SOURCE,"rt",encoding="utf-8") as stream:
        src=json.load(stream)
    originals={r["global_zero_based"]:r for r in src["rows"]}
    # Verify new symbolic reduction against the previous symbolic checkpoint
    # using a complete exact original-IBP replay of the changed expression:
    # R_before + sum(source_before * IBP) = R_after + sum(source_after * IBP).
    # This is enough when combined with the verified predecessor.
    differences={}
    for k in set(before_rem)|set(after_rem):
        v=sp.cancel(before_rem.get(k,0)-after_rem.get(k,0))
        if v!=0:differences[k]=v
    for rid in set(before_src)|set(after_src):
        factor=sp.cancel(before_src.get(rid,0)-after_src.get(rid,0))
        if factor==0:continue
        if rid not in originals:raise RuntimeError("Unknown original IBP source ID")
        for term in originals[rid]["terms"]:
            k=tuple(term["key"])
            value=expr(term["coefficient"],z,d)
            v=sp.cancel(differences.get(k,0)+factor*value)
            if v==0:differences.pop(k,None)
            else:differences[k]=v
    if differences:
        raise AssertionError("Original IBP exact replay failed; residual keys "+str(list(differences)[:5]))
    if sha(state_path)!=EXPECTED_B_STEP58_SHA or sha(candidate_path)!=candidate_sha_start:
        raise RuntimeError("Candidate or formal state changed during audit")
    payload={
        "status":"B_STEP59_EXACT_ORIGINAL_IBP_REPLAY_PASS_NOT_TARGET_PROOF",
        "target":"B","steps_before":58,"candidate_step":59,
        "candidate_sha256":sha(candidate_path),"state_step58_sha256":sha(state_path),
        "a_state_sha256":A_STATE_SHA,"a_proof_sha256":A_PROOF_SHA,
        "source_checkpoint_sha256":sha(CHECKPOINT),
        "original_source_sha256":sha(SOURCE),
        "certificate_sha256":sha(CERT),
        "original_ibp_exact_replay_verified":True,
        "local_exact_identities_verified":len(done),
        "step50_backup_sha256":B_STEP50_SHA,
        "step51_backup_sha256":B_STEP51_SHA,
        "step52_backup_sha256":B_STEP52_SHA,
        "remainder_terms":len(after_rem),"source_support":len(after_src),
        "max_expression_chars":max(list(map(len,saved_rem.values()))+list(map(len,saved_src.values())),default=0),
        "remaining":[[list(k),v] for k,v in sorted(saved_rem.items())],
        "source":[[k,v] for k,v in sorted(saved_src.items())],
        "formal_state_modified":False,"target_proven":False
    }
    protected_paths = (candidate_path,state_path,CHECKPOINT,SOURCE,CERT,A_STATE,A_PROOF,STEP50_BACKUP,STEP51_BACKUP,STEP52_BACKUP)
    if report_path.resolve() in {p.resolve() for p in protected_paths}:
        raise RuntimeError("Audit output aliases protected input")
    if report_path.exists():
        raise FileExistsError("Audit output exists; refusing overwrite")
    atomic_save(report_path,payload,False)
    return {k:v for k,v in payload.items() if k not in ("remaining","source")}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",type=Path,default=OUT)
    ap.add_argument("--state",type=Path,default=STATE)
    ap.add_argument("--output",type=Path,default=REPORT)
    args=ap.parse_args()
    result=audit(args.candidate,args.state,args.output)
    print("VP05_B_STEP59_EXACT_AUDIT "+json.dumps(result),flush=True)


if __name__=="__main__":
    main()
