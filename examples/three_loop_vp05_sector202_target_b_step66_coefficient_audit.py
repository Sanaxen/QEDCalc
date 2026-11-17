"""Independent exact coefficient certificates for saved Step65->66 elimination.

Read-only to formal Step65, scratch Step66, earlier replay and source files.
This is a prerequisite to using normalized source-pivot replay for keys
that time out under direct original-IBP delta replay.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
import time
import sympy as sp

from examples.three_loop_vp05_sector202_target_b_step66_original_ibp_replay import (
    prepare, B_STATE, SCRATCH, PROTECTED, EXPECTED_STEP66_SHA, SAVED_STEP65_SHA,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT, sha,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_step51_scratch import atomic_save

OUT=BASE/"vp05_sector202_B_step66_independent_coefficient_audit.json"
TAG="VP05_B_STEP66_COEFFICIENT_AUDIT "
STATUS="B_STEP66_COEFFICIENT_PREFIX_NOT_PROOF"

def context():
    oldrem,newrem,oldsrc,newsrc,_,_=prepare()
    lead=min(oldrem)
    if lead!=(166596414013440,139):
        raise RuntimeError("Unexpected Step66 pivot lead")
    source=json.loads(CHECKPOINT.read_text(encoding="utf-8-sig"))
    matches=[row for row in source["pivots"] if tuple(row["lead"])==lead]
    if len(matches)!=1:
        raise RuntimeError("Missing or duplicate original source pivot")
    pivot=matches[0]
    prow={tuple(k):v for k,v in pivot["row"]}
    psrc={int(k):v for k,v in pivot["trace"]}
    if len(prow)!=len(pivot["row"]) or len(psrc)!=len(pivot["trace"]):
        raise RuntimeError("Duplicate pivot row or trace key")
    # Verify EVERY coefficient in the union, even keys that were not changed.
    # This makes zero-outside-pivot and support-cancellation cases explicit.
    jobs=[("remainder",k) for k in sorted(set(oldrem)|set(newrem)|set(prow))]
    jobs += [("source",rid) for rid in sorted(set(oldsrc)|set(newsrc)|set(psrc))]
    return oldrem,newrem,oldsrc,newsrc,prow,psrc,jobs

def verify_coefficient(kind,key,old,new,pivot,factor):
    z,d=sp.symbols("z d")
    sign=-1 if kind=="remainder" else 1
    diff=sp.cancel(expr(new,z,d)-expr(old,z,d)-
                   sign*expr(factor,z,d)*expr(pivot,z,d))
    if diff!=0:
        raise AssertionError("Step66 independent coefficient mismatch "+str((kind,key)))
    return True

def worker(index):
    oldrem,newrem,oldsrc,newsrc,prow,psrc,jobs=context()
    if not 0<=index<len(jobs):
        raise RuntimeError("Coefficient index out of range")
    kind,key=jobs[index]
    old,new,pivot=(oldrem,newrem,prow) if kind=="remainder" else (oldsrc,newsrc,psrc)
    verify_coefficient(kind,key,old.get(key,"0"),new.get(key,"0"),
                       pivot.get(key,"0"),oldrem[min(oldrem)])
    if sha(B_STATE)!=SAVED_STEP65_SHA or sha(SCRATCH)!=EXPECTED_STEP66_SHA:
        raise RuntimeError("Protected state changed during coefficient audit")
    print(TAG+json.dumps({"event":"EXACT_COEFFICIENT_PASS","index":index,
        "kind":kind,"key":list(key) if kind=="remainder" else key,
        "scratch_sha256":EXPECTED_STEP66_SHA}),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worker-index",type=int,default=None,help=argparse.SUPPRESS)
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--check-only",action="store_true")
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--timeout-seconds",type=int,default=1200)
    ap.add_argument("--max-new",type=int,default=500)
    args=ap.parse_args()
    if args.worker_index is not None:
        worker(args.worker_index);return
    if not 0<args.hours<=12 or not 30<=args.timeout_seconds<=3600 or not 1<=args.max_new<=2000:
        ap.error("Guard exceeded")
    _,_,_,_,_,_,jobs=context()
    cfg={"version":1,"step65_sha256":SAVED_STEP65_SHA,
         "scratch_step66_sha256":EXPECTED_STEP66_SHA,
         "source_checkpoint_sha256":sha(CHECKPOINT),
         "original_source_sha256":sha(SOURCE),"certificate_sha256":sha(CERT),
         "jobs_count":len(jobs),
         "jobs_sha256":hashlib.sha256(json.dumps(
             [[kind,list(k) if kind=="remainder" else k] for kind,k in jobs],
             separators=(",",":")).encode()).hexdigest()}
    protected=[p for p,_ in PROTECTED]+[SCRATCH,CHECKPOINT,SOURCE,CERT]
    if len(set(p.resolve() for p in protected+[OUT]))!=len(protected)+1:
        raise RuntimeError("Coefficient checkpoint aliases protected input")
    if OUT.exists()!=args.resume:
        raise RuntimeError("Coefficient checkpoint exists: use --resume")
    if args.resume:
        progress=json.loads(OUT.read_text(encoding="utf-8-sig"))
        checked=progress.get("checked",[])
        if (progress.get("config")!=cfg or progress.get("status")!=STATUS
            or progress.get("target_b_proven") is not False
            or progress.get("formal_state_modified") is not False
            or not isinstance(checked,list) or len(checked)>len(jobs)
            or any(r.get("index")!=i or r.get("kind")!=jobs[i][0]
                   or r.get("key")!=(list(jobs[i][1]) if jobs[i][0]=="remainder" else jobs[i][1])
                   for i,r in enumerate(checked))):
            raise RuntimeError("Saved exact coefficient prefix invalid")
    else:
        progress={"version":1,"status":STATUS,"config":cfg,"checked":[],
                  "formal_state_modified":False,"target_b_proven":False}
    print(TAG+json.dumps({"status":"B_STEP66_COEFFICIENT_PREFLIGHT_PASS_NOT_PROOF",
          "already_verified":len(progress["checked"]),"total":len(jobs)}),flush=True)
    if args.check_only:return
    if not args.resume:atomic_save(OUT,progress,False)
    start=time.monotonic();new=0
    while len(progress["checked"])<len(jobs) and new<args.max_new:
        if time.monotonic()-start+args.timeout_seconds+30>args.hours*3600:
            break
        i=len(progress["checked"])
        try:
            r=subprocess.run([sys.executable,"-m",
                "examples.three_loop_vp05_sector202_target_b_step66_coefficient_audit",
                "--worker-index",str(i)],capture_output=True,text=True,
                timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            print(TAG+json.dumps({"event":"WORKER_TIMEOUT_NOT_PROOF","index":i}),flush=True)
            break
        if r.returncode:
            print(TAG+json.dumps({"event":"WORKER_ERROR_NOT_PROOF",
                   "index":i,"stderr_tail":r.stderr[-2000:]}),flush=True)
            break
        if TAG not in r.stdout:raise RuntimeError("Missing worker PASS marker")
        result=json.loads(r.stdout.split(TAG,1)[1].strip())
        kind,key=jobs[i]
        if (result.get("event")!="EXACT_COEFFICIENT_PASS"
            or result.get("index")!=i or result.get("kind")!=kind
            or result.get("key")!=(list(key) if kind=="remainder" else key)
            or result.get("scratch_sha256")!=EXPECTED_STEP66_SHA):
            raise RuntimeError("Unbound coefficient result")
        progress["checked"].append({"index":i,"kind":kind,
            "key":list(key) if kind=="remainder" else key,
            "method":"exact_step66_local_update"})
        atomic_save(OUT,progress,True)
        new+=1
        print(TAG+json.dumps({"event":"EXACT_COEFFICIENT_SAVED",
              "checked":len(progress["checked"]),"total":len(jobs),
              "elapsed_seconds":round(time.monotonic()-start,2)}),flush=True)
    for p,digest in PROTECTED:
        if sha(p)!=digest:raise RuntimeError("Protected file changed")
    if sha(SCRATCH)!=EXPECTED_STEP66_SHA:
        raise RuntimeError("Scratch changed")
    complete=len(progress["checked"])==len(jobs)
    print(TAG+json.dumps({"status":"B_STEP66_ALL_LOCAL_COEFFICIENTS_EXACT_PASS_PENDING_NORMALIZED_IBP"
              if complete else STATUS,"checked":len(progress["checked"]),
              "total":len(jobs),"formal_state_modified":False,
              "target_b_proven":False}),flush=True)

if __name__=="__main__":
    main()
