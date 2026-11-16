"""Independent, bounded and resumable local exact audit of Step65's 40 coefficients.

Audits the saved *candidate* in separate processes; writes only its own
checkpoint. Does not change B state, candidate, protected input or proof.
Full original-IBP replay is a separate subsequent requirement.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import sympy as sp
from examples.three_loop_vp05_sector202_target_b_step65_exact_candidate import (
    STATE, OUT, load_context,
)
from examples.three_loop_vp05_sector202_step51_scratch import atomic_save, key_id
from examples.three_loop_vp05_sector202_target_exact_reduction import BASE, CHECKPOINT, SOURCE, CERT, sha
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_target_b_start import A_STATE, A_PROOF, A_STATE_SHA, A_PROOF_SHA
from examples.three_loop_vp05_sector202_target_b_step59_formal_promotion import BACKUP as STEP58_BACKUP, B_STEP58_SHA
from examples.three_loop_vp05_sector202_target_b_step60_formal_promotion import BACKUP as STEP59_BACKUP, B_STEP59_SHA
from examples.three_loop_vp05_sector202_target_b_step65_scratch_guard import verify_scratch
from examples.three_loop_vp05_sector202_target_b_step64_formal_promotion import BACKUP as STEP63_BACKUP, EXPECTED_STEP63_SHA

AUDIT = BASE / "vp05_sector202_B_step65_independent_local_exact_audit_checkpoint.json"
EXPECTED_STEP64_SHA = "9e5ba49502e24f9367e15b42221086c470dd9670519798e8ab555e147a33992a"


def context():
    verify_scratch()
    if sha(STATE) != EXPECTED_STEP64_SHA:
        raise RuntimeError("Saved Step64 changed; audit refused")
    args=argparse.Namespace(state=STATE,source_checkpoint=CHECKPOINT,input=SOURCE,certificate=CERT)
    state,pivot,jobs,binding=load_context(args)
    candidate_sha=sha(OUT)
    candidate=json.loads(OUT.read_text(encoding="utf-8-sig"))
    done=candidate.get("done",[])
    if (candidate.get("status")!="B_STEP65_EXACT_COEFFICIENT_PREFIX_NOT_PROOF"
        or candidate.get("config")!=binding
        or candidate.get("exact_target_proven") is not False
        or len(done)!=40 or len(jobs)!=40
        or any(r.get("index")!=i or r.get("id")!=key_id(kind,key)
               or r.get("kind")!=kind or
               r.get("key")!=(list(key) if kind=="remainder" else key)
               or r.get("exact_local_identity") is not True
               or r.get("within_formal_cap") is not True
               or not isinstance(r.get("value"),str)
               or r.get("chars")!=len(r["value"]) or len(r["value"])>7500
               for i,(r,(kind,key,_)) in enumerate(zip(done,jobs)))):
        raise RuntimeError("Candidate missing/incomplete/incompatible or oversized")
    return state,pivot,jobs,done,candidate_sha


def worker(index):
    state,pivot,jobs,done,candidate_sha=context()
    if not 0<=index<len(jobs):
        raise ValueError("Bad coefficient index")
    z,d=sp.symbols("z d")
    kind,key,pivot_raw=jobs[index]
    before={tuple(k):v for k,v in state["remaining"]} if kind=="remainder" else {
        int(k):v for k,v in state["source"]}
    rem={tuple(k):v for k,v in state["remaining"]}
    lead=min(rem)
    prior=expr(before.get(key,"0"),z,d)
    factor=expr(rem[lead],z,d)
    pivot_coeff=expr(pivot_raw,z,d)
    value=expr(done[index]["value"],z,d)
    sign=-1 if kind=="remainder" else 1
    if sp.cancel(value-(prior+sign*factor*pivot_coeff))!=0:
        raise AssertionError("Step65 independent exact identity mismatch "+str(index))
    if sha(STATE)!=EXPECTED_STEP64_SHA or sha(OUT)!=candidate_sha:
        raise RuntimeError("Input changed during coefficient audit")
    print("VP05_B_STEP65_INDEPENDENT_AUDIT "+json.dumps({
        "event":"EXACT_LOCAL_RECHECK_PASS","index":index,
        "id":done[index]["id"],"candidate_sha256":candidate_sha,
        "coefficient_sha256":hashlib.sha256(done[index]["value"].encode()).hexdigest(),
    }),flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worker-index",type=int,default=None,help=argparse.SUPPRESS)
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--timeout-seconds",type=int,default=600)
    ap.add_argument("--max-new",type=int,default=40)
    args=ap.parse_args()
    if args.worker_index is not None:
        worker(args.worker_index)
        return
    if not 0<args.hours<=12 or not 30<=args.timeout_seconds<=1800 or not 1<=args.max_new<=40:
        ap.error("Safety limits: hours (0,12], timeout 30..1800, max-new 1..40")
    state,pivot,jobs,done,candidate_sha=context()
    binding={"candidate_sha256":candidate_sha,"state_step64_sha256":EXPECTED_STEP64_SHA,
             "candidate_total":len(done),"a_state_sha256":A_STATE_SHA,
             "a_proof_sha256":A_PROOF_SHA,"step58_backup_sha256":B_STEP58_SHA,
             "step59_backup_sha256":B_STEP59_SHA,
             "step63_backup_sha256":EXPECTED_STEP63_SHA}
    protected={p.resolve() for p in (STATE,OUT,CHECKPOINT,SOURCE,CERT,A_STATE,A_PROOF,STEP58_BACKUP,STEP59_BACKUP,STEP63_BACKUP)}
    if AUDIT.resolve() in protected:
        raise RuntimeError("Audit checkpoint overlaps protected input")
    if AUDIT.exists()!=args.resume:
        raise RuntimeError("Audit checkpoint exists: use --resume; otherwise omit it")
    if args.resume:
        progress=json.loads(AUDIT.read_text(encoding="utf-8-sig"))
        if progress.get("config")!=binding or progress.get("status")!="INDEPENDENT_LOCAL_PREFIX_NOT_PROOF":
            raise RuntimeError("Prior audit checkpoint not bound to these exact inputs")
        checked=progress.get("checked",[])
        if not isinstance(checked,list) or len(checked)>40 or any(
            r.get("index")!=i or r.get("id")!=done[i]["id"]
            or r.get("coefficient_sha256")!=hashlib.sha256(done[i]["value"].encode()).hexdigest()
            for i,r in enumerate(checked)):
            raise RuntimeError("Audit prefix invalid")
    else:
        progress={"version":1,"status":"INDEPENDENT_LOCAL_PREFIX_NOT_PROOF",
                  "config":binding,"checked":[],"target_b_proven":False,
                  "original_ibp_exact_replay_verified":False,
                  "formal_state_modified":False}
        atomic_save(AUDIT,progress,False)
    started=time.monotonic()
    print("VP05_B_STEP65_INDEPENDENT_AUDIT "+json.dumps({
        "event":"START","checked":len(progress["checked"]),"total":40,
        "candidate_sha256":candidate_sha}),flush=True)
    count=0
    while len(progress["checked"])<40 and count<args.max_new:
        if time.monotonic()-started+args.timeout_seconds+30>args.hours*3600:
            break
        i=len(progress["checked"])
        cmd=[sys.executable,"-m","examples.three_loop_vp05_sector202_target_b_step65_independent_audit",
             "--worker-index",str(i)]
        try:
            run=subprocess.run(cmd,capture_output=True,text=True,timeout=args.timeout_seconds,check=False)
        except subprocess.TimeoutExpired:
            print("VP05_B_STEP65_INDEPENDENT_AUDIT "+json.dumps({
                "event":"WORKER_TIMEOUT_NOT_PROOF","index":i}),flush=True)
            break
        if run.returncode:
            print("VP05_B_STEP65_INDEPENDENT_AUDIT "+json.dumps({
                "event":"WORKER_ERROR_NOT_PROOF","index":i,"stderr_tail":run.stderr[-1500:]}),flush=True)
            break
        marker="VP05_B_STEP65_INDEPENDENT_AUDIT "
        if marker not in run.stdout:
            raise RuntimeError("Worker result missing")
        result=json.loads(run.stdout.split(marker,1)[1])
        if result.get("event")!="EXACT_LOCAL_RECHECK_PASS" or result.get("index")!=i or (
            result.get("candidate_sha256")!=candidate_sha or result.get("id")!=done[i]["id"]
            or result.get("coefficient_sha256")!=hashlib.sha256(done[i]["value"].encode()).hexdigest()
        ):
            raise RuntimeError("Worker identity mismatch")
        progress["checked"].append({"index":i,"id":result["id"],
                                    "coefficient_sha256":result["coefficient_sha256"]})
        atomic_save(AUDIT,progress,True)
        count+=1
        print("VP05_B_STEP65_INDEPENDENT_AUDIT "+json.dumps({
            "event":"EXACT_LOCAL_RECHECK_SAVED","checked":len(progress["checked"]),
            "total":40,"elapsed_seconds":round(time.monotonic()-started,2)}),flush=True)
    if sha(STATE)!=EXPECTED_STEP64_SHA or sha(OUT)!=candidate_sha or sha(A_STATE)!=A_STATE_SHA or sha(A_PROOF)!=A_PROOF_SHA or sha(STEP58_BACKUP)!=B_STEP58_SHA or sha(STEP59_BACKUP)!=B_STEP59_SHA or sha(STEP63_BACKUP)!=EXPECTED_STEP63_SHA:
        raise RuntimeError("Protected inputs changed during audit")
    complete=len(progress["checked"])==40
    print("VP05_B_STEP65_INDEPENDENT_AUDIT "+json.dumps({
        "event":"ALL_40_LOCAL_RECHECKS_PASS_PENDING_ORIGINAL_IBP_REPLAY" if complete
        else "INDEPENDENT_LOCAL_PREFIX_NOT_PROOF",
        "checked":len(progress["checked"]),"total":40,
        "candidate_sha256":candidate_sha,"formal_state_modified":False,
        "original_ibp_exact_replay_verified":False,"target_b_proven":False}),flush=True)


if __name__=="__main__":
    main()
