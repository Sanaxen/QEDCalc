"""Isolated exact Step69->69 coefficient and original-IBP replay, no promotion.

Two ordered, independently resumable phases: coefficient identities and
unscaled original-IBP pivot identity. Each worker uses exact QQ(z,d) rational
functions (no modular/numeric sampling). Pinned formal Step69 and scratch69
remain read-only; two new checkpoint files are never overwritten without
--resume. Phase-2 requires all phase-1 certificates.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import time
import sympy as sp
from sympy.polys.fields import field
from sympy.polys.domains import QQ
from examples.three_loop_vp05_sector202_target_b_step70_scratch import (
    SCRATCH, B_STATE, formal_next_lead, EXPECTED_STEP69_SHA,
    protected_inputs, validate_scratch, sha,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT,
)
from examples.three_loop_vp05_sector202_target_b_step69_read_only_audit import (
    inspect as audit_saved69,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_step51_scratch import atomic_save

EXPECTED_STEP70_SHA="b738b82b038d229850e043f63796fd01db4cb50a404ad3247ef1a5962ee07c04"
COEFF=BASE/"vp05_sector202_B_step70_exact_coefficient_checkpoint.json"
IBP=BASE/"vp05_sector202_B_step70_exact_original_ibp_checkpoint.json"
TAG="VP05_B_STEP70_EXACT_AUDIT "
STATUS="B_STEP70_EXACT_PREFIX_NOT_TARGET_PROOF"

def rows_dict(rows,integral):
    result={}
    for key,val in rows:
        k=tuple(key) if integral else int(key)
        if k in result or not isinstance(val,str) or not val:
            raise RuntimeError("Duplicate/invalid saved coefficient")
        result[k]=val
    return result

def field_equal(lhs,parts):
    """Exact fraction-field identity without monolithic SymPy cancel."""
    ring,z,d=field("z,d",QQ)
    zs,ds=sp.symbols("z d")
    def cv(raw):return ring.from_expr(expr(raw,zs,ds))
    total=ring.zero
    for weight,coeff in parts:
        total+=cv(weight)*cv(coeff)
    return cv(lhs)==total

def coefficient_identity(kind,old,new,pivot,factor):
    # remaining: old-new = factor*pivot ; source: new-old = factor*pivot
    if kind=="remainder":
        return field_equal(old,[("1",new),(factor,pivot)])
    if kind=="source":
        return field_equal(new,[("1",old),(factor,pivot)])
    raise ValueError("Invalid coefficient kind")

def context():
    if audit_saved69().get("status")!="B_STEP69_SAVED_STATE_READ_ONLY_AUDIT_PASS_NOT_TARGET_PROOF":
        raise RuntimeError("Formal Step69 not audited")
    protected=protected_inputs()
    if sha(SCRATCH)!=EXPECTED_STEP70_SHA or sha(B_STATE)!=EXPECTED_STEP69_SHA:
        raise RuntimeError("Step70 scratch or formal Step69 SHA changed")
    old=json.loads(B_STATE.read_text(encoding="utf-8-sig"))
    new=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    validate_scratch(old,new)
    if (new.get("steps")!=70 or len(new.get("remaining",[]))!=57
        or len(new.get("source",[]))!=145
        or new.get("metrics",{}).get("max_expression_chars")!=3392
        or not new.get("remaining") or new.get("status")!="EXACT_TARGET_PREFIX_NOT_PROOF"
        or new["metrics"].get("remainder_terms")!=len(new["remaining"])
        or new["metrics"].get("original_support")!=len(new["source"])
        or new["metrics"].get("lead")!=[166596414144515,139]):
        raise RuntimeError("Expected audited Step70 result dimensions mismatch")
    orem=rows_dict(old["remaining"],True);nrem=rows_dict(new["remaining"],True)
    osrc=rows_dict(old["source"],False);nsrc=rows_dict(new["source"],False)
    lead=tuple(formal_next_lead(old))
    if min(orem)!=lead or lead in nrem:raise RuntimeError("Wrong Step70 eliminated pivot")
    pivots=json.loads(CHECKPOINT.read_text(encoding="utf-8-sig"))["pivots"]
    matches=[row for row in pivots if tuple(row["lead"])==lead]
    if len(matches)!=1:raise RuntimeError("Missing or duplicate original pivot")
    pivot=matches[0]
    prow=rows_dict(pivot["row"],True)
    ptrace=rows_dict(pivot["trace"],False)
    coefficient_jobs=[("remainder",k) for k in sorted(set(orem)|set(nrem)|set(prow))]
    coefficient_jobs += [("source",k) for k in sorted(set(osrc)|set(nsrc)|set(ptrace))]
    with gzip.open(SOURCE,"rt",encoding="utf-8") as stream:
        original=json.load(stream)
    originals={int(row["global_zero_based"]):row for row in original["rows"]}
    if len(originals)!=len(original["rows"]) or not set(ptrace).issubset(originals):
        raise RuntimeError("Missing or duplicate ORIGINAL IBP rows")
    keyed={}
    for rid,weight in ptrace.items():
        for term in originals[rid]["terms"]:
            key=tuple(term["key"])
            keyed.setdefault(key,[]).append((weight,term["coefficient"]))
    ibp_jobs=sorted(set(prow)|set(keyed))
    if not ibp_jobs:raise RuntimeError("Empty original-IBP key inventory")
    return (orem,nrem,osrc,nsrc,prow,ptrace,coefficient_jobs,
            keyed,ibp_jobs,protected)

def job_manifest(phase,c):
    orem,nrem,osrc,nsrc,prow,ptrace,cjobs,keyed,ijobs,protected=c
    jobs=cjobs if phase=="coeff" else ijobs
    serial=[[kind,list(k) if kind=="remainder" else k] for kind,k in jobs] if phase=="coeff" else [list(k) for k in jobs]
    config={"version":1,"phase":phase,"formal_step69_sha256":EXPECTED_STEP69_SHA,
      "scratch_step70_sha256":EXPECTED_STEP70_SHA,
      "source_checkpoint_sha256":sha(CHECKPOINT),"source_sha256":sha(SOURCE),
      "certificate_sha256":sha(CERT),
      "job_count":len(jobs),
      "job_sha256":hashlib.sha256(json.dumps(serial,separators=(",",":")).encode()).hexdigest()}
    if phase=="ibp":config["coefficient_checkpoint_sha256"]=sha(COEFF)
    return jobs,config

def validate_progress(phase,c):
    path=COEFF if phase=="coeff" else IBP
    jobs,cfg=job_manifest(phase,c)
    state=json.loads(path.read_text(encoding="utf-8-sig"))
    checked=state.get("checked",[])
    if (state.get("version")!=1 or state.get("status")!=STATUS
        or state.get("config")!=cfg
        or state.get("target_b_proven") is not False
        or state.get("formal_state_modified") is not False
        or not isinstance(checked,list) or len(checked)>len(jobs)):
        raise RuntimeError("Exact Step70 certificate checkpoint incompatible")
    for i,row in enumerate(checked):
        expected=(list(jobs[i][1]) if jobs[i][0]=="remainder" else jobs[i][1]) if phase=="coeff" else list(jobs[i])
        if (not isinstance(row,dict) or row.get("index")!=i
            or row.get("key")!=expected
            or row.get("method")!="exact_QQ_z_d_"+phase
            or (phase=="coeff" and row.get("kind")!=jobs[i][0])):
            raise RuntimeError("Unbound Step70 exact certificate")
    return state,jobs

def require_coeff_complete(c):
    if not COEFF.exists():raise RuntimeError("Independent coefficient checkpoint missing")
    state,jobs=validate_progress("coeff",c)
    if len(state["checked"])!=len(jobs):
        raise RuntimeError("Independent Step70 coefficients not all PASS")

def worker(phase,index):
    c=context()
    if phase=="ibp":require_coeff_complete(c)
    jobs,cfg=job_manifest(phase,c)
    if not 0<=index<len(jobs):raise RuntimeError("Invalid Step70 job index")
    orem,nrem,osrc,nsrc,prow,ptrace,cjobs,keyed,ijobs,protected=c
    if phase=="coeff":
        kind,key=jobs[index]
        old,new,piv=(orem,nrem,prow) if kind=="remainder" else (osrc,nsrc,ptrace)
        if not coefficient_identity(kind,old.get(key,"0"),new.get(key,"0"),
                                    piv.get(key,"0"),orem[tuple(formal_next_lead(json.loads(B_STATE.read_text(encoding="utf-8-sig"))))]):
            raise AssertionError("Step70 coefficient exact mismatch "+str((kind,key)))
        encoded=list(key) if kind=="remainder" else key
    else:
        key=jobs[index]
        if not field_equal(prow.get(key,"0"),keyed.get(key,[])):
            raise AssertionError("Step70 exact ORIGINAL IBP mismatch "+str(key))
        encoded=list(key)
    if sha(SCRATCH)!=EXPECTED_STEP70_SHA:
        raise RuntimeError("Step70 scratch SHA changed during exact worker")
    for path,digest in protected:
        if sha(path)!=digest:raise RuntimeError("Protected input changed")
    print(TAG+json.dumps({"event":"EXACT_KEY_PASS","phase":phase,
        "index":index,"key":encoded,
        "kind":kind if phase=="coeff" else None,
        "scratch_sha256":EXPECTED_STEP70_SHA}),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--phase",choices=["coeff","ibp"],required=True)
    ap.add_argument("--worker-index",type=int,default=None,help=argparse.SUPPRESS)
    ap.add_argument("--check-only",action="store_true")
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--timeout-seconds",type=int,default=1200)
    ap.add_argument("--max-new",type=int,default=500)
    args=ap.parse_args()
    if args.worker_index is not None:
        worker(args.phase,args.worker_index);return
    if not 0<args.hours<=12 or not 30<=args.timeout_seconds<=3600 or not 1<=args.max_new<=500:
        ap.error("Safety bounds exceeded")
    c=context()
    if args.phase=="ibp":require_coeff_complete(c)
    jobs,cfg=job_manifest(args.phase,c)
    path=COEFF if args.phase=="coeff" else IBP
    if len(set(p.resolve() for p,_ in c[-1]+[(SCRATCH,EXPECTED_STEP70_SHA)])|set((COEFF.resolve(),IBP.resolve())))!=len(c[-1])+3:
        raise RuntimeError("Audit outputs alias protected paths")
    if path.exists()!=args.resume:
        raise RuntimeError("Step70 phase checkpoint exists: use --resume or omit for new")
    if args.resume:
        state,_=validate_progress(args.phase,c)
    else:
        state={"version":1,"status":STATUS,"config":cfg,"checked":[],
               "formal_state_modified":False,"target_b_proven":False}
    print(TAG+json.dumps({"status":"B_STEP70_"+args.phase.upper()+"_PREFLIGHT_PASS_NOT_PROOF",
        "verified":len(state["checked"]),"total":len(jobs),
        "formal_state_unchanged":True}),flush=True)
    if args.check_only:return
    if not args.resume:atomic_save(path,state,False)
    start=time.monotonic();new=0
    while len(state["checked"])<len(jobs) and new<args.max_new:
        if time.monotonic()-start+args.timeout_seconds+30>args.hours*3600:break
        i=len(state["checked"])
        try:
            run=subprocess.run([sys.executable,"-m",
                "examples.three_loop_vp05_sector202_target_b_step70_exact_audit",
                "--phase",args.phase,"--worker-index",str(i)],
                capture_output=True,text=True,timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            print(TAG+json.dumps({"event":"WORKER_TIMEOUT_NOT_PROOF","phase":args.phase,"index":i}),flush=True)
            break
        if run.returncode:
            print(TAG+json.dumps({"event":"WORKER_ERROR_NOT_PROOF","phase":args.phase,
                "index":i,"stderr_tail":run.stderr[-2500:]}),flush=True)
            break
        if TAG not in run.stdout:raise RuntimeError("Worker missing PASS")
        payload=json.loads(run.stdout.split(TAG,1)[1].strip())
        key=(list(jobs[i][1]) if jobs[i][0]=="remainder" else jobs[i][1]) if args.phase=="coeff" else list(jobs[i])
        kind=jobs[i][0] if args.phase=="coeff" else None
        if (payload.get("event")!="EXACT_KEY_PASS" or payload.get("phase")!=args.phase
            or payload.get("index")!=i or payload.get("key")!=key
            or payload.get("kind")!=kind
            or payload.get("scratch_sha256")!=EXPECTED_STEP70_SHA):
            raise RuntimeError("Unbound Step70 exact worker")
        record={"index":i,"key":key,"method":"exact_QQ_z_d_"+args.phase}
        if kind is not None:record["kind"]=kind
        state["checked"].append(record)
        atomic_save(path,state,True)
        new+=1
        print(TAG+json.dumps({"event":"EXACT_KEY_SAVED","phase":args.phase,
            "verified":len(state["checked"]),"total":len(jobs),
            "elapsed_seconds":round(time.monotonic()-start,2)}),flush=True)
    for p,digest in c[-1]:
        if sha(p)!=digest:raise RuntimeError("Protected state changed")
    complete=len(state["checked"])==len(jobs)
    print(TAG+json.dumps({"status":"B_STEP70_"+args.phase.upper()+
          ("_ALL_EXACT_PASS_NOT_TARGET_PROOF" if complete else "_PREFIX_NOT_PROOF"),
        "verified":len(state["checked"]),"total":len(jobs),
        "formal_state_modified":False,"target_b_proven":False}),flush=True)

if __name__=="__main__":
    main()
