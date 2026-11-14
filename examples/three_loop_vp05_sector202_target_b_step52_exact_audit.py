"""Read-only assembly and exact consistency audit for B Step52 coefficient pilot.

No formal state, candidate file, Target A artifact, or source checkpoint is
modified. Assembles 35 locally checked coefficients, verifies each exact
operation, and independently verifies original-IBP target/residual identity.
A successful report is a prerequisite for a separately guarded promotion.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_target_b_step52_exact_candidate import (
    OUT, STATE, load_context,
)
from examples.three_loop_vp05_sector202_target_b_start import A_STATE,A_PROOF,A_STATE_SHA,A_PROOF_SHA
from examples.three_loop_vp05_sector202_step51_scratch import atomic_save,key_id
from examples.three_loop_vp05_sector202_target_b_step51_formal_promotion import BACKUP, B_STEP50_SHA
from examples.three_loop_vp05_sector202_target_exact_checkpoint import (
    decoded, trace_decoded, encoded, trace_encoded, metrics,
    assert_modular_invariant,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE,CHECKPOINT,SOURCE,CERT,POINTS,sha,add,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr

REPORT = BASE / "vp05_sector202_B_step52_exact_candidate_audit.json"
EXPECTED_B_STEP51_SHA = "382e76dbbfc6f57c0dbf6468b53329d91a869ed9267a98093ac7165d8c6c7aac"


def audit(candidate_path=OUT, state_path=STATE, report_path=REPORT):
    if (sha(state_path)!=EXPECTED_B_STEP51_SHA or sha(A_STATE)!=A_STATE_SHA
            or sha(A_PROOF)!=A_PROOF_SHA or sha(BACKUP)!=B_STEP50_SHA):
        raise RuntimeError("Formal B Step51 or proven A inputs changed")
    candidate=json.loads(candidate_path.read_text(encoding="utf-8-sig"))
    args=argparse.Namespace(state=state_path,source_checkpoint=CHECKPOINT,input=SOURCE,certificate=CERT)
    state,pivot,jobs,binding=load_context(args)
    done=candidate.get("done",[])
    if (candidate.get("status")!="B_STEP52_EXACT_COEFFICIENT_PREFIX_NOT_PROOF"
        or candidate.get("config")!=binding
        or candidate.get("exact_target_proven") is not False
        or len(done)!=35 or len(done)!=len(jobs)
        or [r.get("id") for r in done]!=binding["jobs"]
        or any(r.get("exact_local_identity") is not True or
               r.get("within_formal_cap") is not True or
               r.get("chars")!=len(r.get("value","")) or
               r.get("chars")>7500 for r in done)):
        raise RuntimeError("Pilot is incomplete, oversized, or not bound to Step51 inputs")
    z,d=sp.symbols("z d")
    before_rem=decoded(state["remaining"],z,d)
    before_src=trace_decoded(state["source"],z,d)
    pivot_rem=decoded(pivot["row"],z,d)
    pivot_src=trace_decoded(pivot["trace"],z,d)
    lead=min(before_rem)
    fac=before_rem[lead]
    after_rem=dict(before_rem)
    after_src=dict(before_src)
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
        if val==0:target.pop(key,None)
        else:target[key]=val
        max_chars=max(max_chars,len(raw))
    if lead in after_rem:
        raise AssertionError("Exact elimination did not cancel pivot lead")
    if len(after_rem)!=103 or len(after_src)!=187:
        raise AssertionError("Step52 candidate dimensions differ from cap-stop metrics")
    if max((len(str(v)) for v in list(after_rem.values())+list(after_src.values())),default=0)>7500:
        raise RuntimeError("Candidate canonical expression exceeds formal cap")
    if sha(state_path)!=EXPECTED_B_STEP51_SHA or sha(BACKUP)!=B_STEP50_SHA:
        raise RuntimeError("Protected B Step51 or Step50 backup modified during audit")
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
    payload={
        "status":"B_STEP52_EXACT_ORIGINAL_IBP_REPLAY_PASS_NOT_TARGET_PROOF",
        "target":"B","steps_before":51,"candidate_step":52,
        "candidate_sha256":sha(candidate_path),"state_step51_sha256":sha(state_path),
        "a_state_sha256":A_STATE_SHA,"a_proof_sha256":A_PROOF_SHA,
        "source_checkpoint_sha256":sha(CHECKPOINT),
        "original_source_sha256":sha(SOURCE),
        "certificate_sha256":sha(CERT),
        "original_ibp_exact_replay_verified":True,
        "local_exact_identities_verified":len(done),
        "step50_backup_sha256":B_STEP50_SHA,
        "remainder_terms":len(after_rem),"source_support":len(after_src),
        "max_expression_chars":max_chars,
        "remaining":encoded(after_rem),"source":trace_encoded(after_src),
        "formal_state_modified":False,"target_proven":False
    }
    atomic_save(report_path,payload,False)
    return {k:v for k,v in payload.items() if k not in ("remaining","source")}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",type=Path,default=OUT)
    ap.add_argument("--state",type=Path,default=STATE)
    ap.add_argument("--output",type=Path,default=REPORT)
    args=ap.parse_args()
    result=audit(args.candidate,args.state,args.output)
    print("VP05_B_STEP52_EXACT_AUDIT "+json.dumps(result),flush=True)


if __name__=="__main__":
    main()
