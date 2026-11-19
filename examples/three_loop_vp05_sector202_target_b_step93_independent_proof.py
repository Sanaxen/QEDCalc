"""Independent, read-only Step93 Target B proof verifier.

Two exact QQ(z,d) phases:
  pivot: independently replay Step92->93 against the original checkpoint pivot;
  source: independently sum the ORIGINAL unscaled IBP rows into Target B.
No changes to formal B, Step93 proof, source checkpoint or original source.
Per-key certificates are new and resumable. A full result is the proof of
this sector202 Target B identity, not of all VP05 or three-loop QED.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import sympy as sp
from sympy.polys.fields import field
from sympy.polys.domains import QQ
from examples.three_loop_vp05_sector202_target_exact_reduction import BASE,CHECKPOINT,SOURCE,CERT,FORMULAS,sha
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
from examples.three_loop_vp05_sector202_quotient_sensitivity import P,TARGETS
from examples.three_loop_vp05_sector202_target_b_step77_formal_promotion import B_STATE,EXPECTED_STEP77_SHA

DIRECTORY=BASE/"vp05_sector202_B_continuous_batch_from77"
WORK=DIRECTORY/"working_state.json"
PROOF=DIRECTORY/"working_state_proof.json"
BEFORE=DIRECTORY/"before_step93.json"
JOURNAL=DIRECTORY/"batch_journal.json"
OUTPUT=DIRECTORY/"independent_step93_verification"
TAG="VP05_B_STEP93_INDEPENDENT "
STATUS="INDEPENDENT_STEP93_EXACT_PREFIX_NOT_TARGET_PROOF"
PHASES=("pivot","source")

def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,obj,exclusive=False):
    p.parent.mkdir(parents=True,exist_ok=True)
    if exclusive and p.exists():raise FileExistsError(str(p))
    tmp=p.with_name(p.name+"."+str(os.getpid())+".tmp")
    with tmp.open("x",encoding="utf-8") as f:
        json.dump(obj,f,separators=(",",":"))
        f.flush();os.fsync(f.fileno())
    try:
        if exclusive and p.exists():raise FileExistsError(str(p))
        os.replace(tmp,p)
    finally:
        if tmp.exists():tmp.unlink()

def rows(raw,integral):
    r={}
    for key,value in raw:
        k=tuple(key) if integral else int(key)
        if k in r or not isinstance(value,str) or not value:raise RuntimeError("Invalid duplicated coefficient")
        r[k]=value
    return r

def equal(lhs,weighted):
    ring,z,d=field("z,d",QQ)
    zs,ds=sp.symbols("z d")
    def cv(raw):return ring.from_expr(expr(raw,zs,ds))
    value=ring.zero
    for a,b in weighted:value+=cv(a)*cv(b)
    return cv(lhs)==value

def expected_target():
    mod=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
    bits,order=mod.from_kiradb(str(P/"results/kira.db"))
    if order!=5:raise RuntimeError("Unexpected Kira codec ordering")
    codec=mod.WeightCodec(np=12,bits=bits,iord=order,topsectors=[203])
    keys=[(codec.encode(x),139) for x in TARGETS]
    if any(tuple(codec.decode(k[0]))!=v for k,v in zip(keys,TARGETS)):
        raise RuntimeError("Target codec is not reversible")
    return {(keys[1]):"1",(keys[3]):"-("+FORMULAS[2]+")",(4,73):"-("+FORMULAS[3]+")"}

def context():
    paths=[WORK,PROOF,BEFORE,JOURNAL,CHECKPOINT,SOURCE,CERT,B_STATE]
    if any(not p.exists() for p in paths):raise FileNotFoundError("Missing proof or original IBP source")
    old,new,proof,j=map(load,(BEFORE,WORK,PROOF,JOURNAL))
    if sha(B_STATE)!=EXPECTED_STEP77_SHA:
        raise RuntimeError("Protected formal Step77 changed")
    if j.get("audited_step")!=92 or j.get("audited_sha256")!=sha(BEFORE):
        raise RuntimeError("Step92 audit-chain mismatch")
    if (j.get("target_b_proven") is not False or j.get("formal_unchanged") is not True
        or old.get("steps")!=92 or new.get("steps")!=93
        or new.get("remaining")!=[] or new.get("metrics",{}).get("remainder_terms")!=0
        or len(new.get("source",[]))!=389
        or new.get("pivot_path")!=old.get("pivot_path",[])+[old["metrics"]["lead"]]
        or proof.get("status")!="EXACT_SINGLE_TARGET_PROVEN"
        or proof.get("target")!="B" or proof.get("steps")!=93
        or proof.get("original_source_replay_verified") is not True
        or proof.get("source_multipliers")!=new.get("source")
        or new.get("exact_target_proven") is not False
        or new.get("original_source_replay_proven") is not False):
        raise RuntimeError("Proof/Step93/Step92 metadata mismatch")
    names=("source_checkpoint_sha256","source_sha256","certificate_sha256")
    artifacts=(CHECKPOINT,SOURCE,CERT)
    for name,path in zip(names,artifacts):
        if new["config"].get(name)!=sha(path) or proof.get(name)!=sha(path):
            raise RuntimeError("Original IBP source/checkpoint SHA mismatch: "+name)
    if (j.get("source_hashes")!={"checkpoint":sha(CHECKPOINT),"source":sha(SOURCE),
        "certificate":sha(CERT)}):raise RuntimeError("Batch source SHA mismatch")
    target=rows(proof["target_terms"],True)
    expected=expected_target()
    if set(target)!=set(expected) or any(not equal(target[k],[("1",expected[k])]) for k in target):
        raise RuntimeError("Proof target does not match independently reconstructed Target B")
    checkpoint=load(CHECKPOINT)
    selected=[p for p in checkpoint["pivots"] if p["lead"]==old["metrics"]["lead"]]
    if len(selected)!=1:raise RuntimeError("Step93 exact checkpoint pivot not unique")
    pv=selected[0]
    prow,ptrace=rows(pv["row"],True),rows(pv["trace"],False)
    before_rem,after_rem=rows(old["remaining"],True),rows(new["remaining"],True)
    before_source,after_source=rows(old["source"],False),rows(new["source"],False)
    lead=tuple(old["metrics"]["lead"])
    if lead not in before_rem or lead not in prow or not equal(prow[lead],[("1","1")]):
        raise RuntimeError("Step93 selected pivot invalid")
    with gzip.open(SOURCE,"rt",encoding="utf-8") as f: original=json.load(f)
    originals={int(x["global_zero_based"]):x for x in original["rows"]}
    if len(originals)!=len(original["rows"]) or not set(after_source).issubset(originals):
        raise RuntimeError("Original IBP row reference invalid")
    target_terms={}
    for rid,weight in after_source.items():
        for term in originals[rid]["terms"]:
            key=tuple(term["key"])
            target_terms.setdefault(key,[]).append((weight,term["coefficient"]))
    pivot_jobs=[("rem",k) for k in sorted(set(before_rem)|set(after_rem)|set(prow))]
    pivot_jobs += [("src",k) for k in sorted(set(before_source)|set(after_source)|set(ptrace))]
    source_jobs=sorted(set(target)|set(target_terms))
    sources={str(p):sha(p) for p in paths}
    return (old,new,proof,before_rem,after_rem,before_source,after_source,
            prow,ptrace,target,target_terms,pivot_jobs,source_jobs,sources)

def jobs_for(phase,c):
    return c[11] if phase=="pivot" else c[12]

def manifest(phase,c):
    jobs=jobs_for(phase,c)
    encoded=[[kind,list(k) if kind=="rem" else k] for kind,k in jobs] if phase=="pivot" else [list(k) for k in jobs]
    return {"phase":phase,"job_count":len(jobs),
        "job_sha256":hashlib.sha256(json.dumps(encoded,separators=(",",":")).encode()).hexdigest(),
        "source_hashes":c[13]}

def checkpoint_path(phase):return OUTPUT/(phase+"_verified.json")

def verify_progress(phase,c):
    path=checkpoint_path(phase);m=manifest(phase,c)
    if path.exists():
        saved=load(path)
        if (saved.get("status")!=STATUS or saved.get("manifest")!=m
            or type(saved.get("verified")) is not int or
            not 0<=saved["verified"]<=m["job_count"]):
            raise RuntimeError("Incompatible existing independent verification checkpoint")
    else:saved={"status":STATUS,"manifest":m,"verified":0}
    return saved,path

def check_worker(phase,index):
    c=context();jobs=jobs_for(phase,c)
    if not 0<=index<len(jobs):raise RuntimeError("Invalid source audit index")
    if phase=="pivot":
        kind,key=jobs[index];a=c[3] if kind=="rem" else c[5]
        b=c[4] if kind=="rem" else c[6]
        pivot=c[7] if kind=="rem" else c[8]
        fac=c[3][tuple(c[0]["metrics"]["lead"])]
        # rem: old = new + fac*pivot; provenance: new = old + fac*trace
        ok=(equal(a.get(key,"0"),[("1",b.get(key,"0")),(fac,pivot.get(key,"0"))])
             if kind=="rem" else
             equal(b.get(key,"0"),[("1",a.get(key,"0")),(fac,pivot.get(key,"0"))]))
    else:
        key=jobs[index]
        ok=equal(c[9].get(key,"0"),c[10].get(key,[]))
    if not ok:raise AssertionError("Independent exact QQ(z,d) mismatch: "+str((phase,index)))
    print(TAG+json.dumps({"event":"WORKER_EXACT_PASS","phase":phase,
        "index":index,"work_sha256":sha(WORK)}),flush=True)

def worker_proc(phase,index,expected_sha,timeout):
    run=subprocess.run([sys.executable,"-m",
        "examples.three_loop_vp05_sector202_target_b_step93_independent_proof",
        "--worker-phase",phase,"--worker-index",str(index)],
        capture_output=True,text=True,timeout=timeout)
    if run.returncode:raise RuntimeError("Worker failed "+str((phase,index))+": "+run.stderr[-1800:])
    lines=[x[len(TAG):] for x in run.stdout.splitlines() if x.startswith(TAG)]
    if len(lines)!=1 or json.loads(lines[0])!={"event":"WORKER_EXACT_PASS",
        "phase":phase,"index":index,"work_sha256":expected_sha}:
        raise RuntimeError("Unbound source exact worker report")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check-only",action="store_true")
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--workers",type=int,default=4)
    ap.add_argument("--worker-timeout",type=int,default=1200)
    ap.add_argument("--worker-phase",choices=PHASES)
    ap.add_argument("--worker-index",type=int)
    args=ap.parse_args()
    if args.worker_phase is not None:
        if args.worker_index is None:ap.error("Worker index required")
        check_worker(args.worker_phase,args.worker_index);return
    if not 0<args.hours<=12 or not 1<=args.workers<=8 or not 30<=args.worker_timeout<=3600:
        ap.error("Invalid resource limits")
    c=context()
    record={}
    for phase in PHASES:
        checkpoint,path=verify_progress(phase,c)
        record[phase]={"verified":checkpoint["verified"],"total":manifest(phase,c)["job_count"],
                       "checkpoint_exists":path.exists()}
    print(TAG+json.dumps({"status":"STEP93_INDEPENDENT_PREFLIGHT_PASS_NOT_FULL_PROOF",
        "phase_progress":record,"step93_sha256":sha(WORK),
        "proof_sha256":sha(PROOF),"formal_unchanged":True}),flush=True)
    if args.check_only:return
    if any(x["checkpoint_exists"] for x in record.values()) and not args.resume:
        raise RuntimeError("Independent audit checkpoint exists; use --resume")
    deadline=time.monotonic()+args.hours*3600
    for phase in PHASES:
        state,path=verify_progress(phase,c)
        if not path.exists():atomic(path,state,exclusive=True)
        total=manifest(phase,c)["job_count"]
        while state["verified"]<total:
            if deadline-time.monotonic()<10:
                print(TAG+json.dumps({"status":"STEP93_INDEPENDENT_PARTIAL_RESUMABLE_NOT_PROOF",
                    "phase":phase,"verified":state["verified"],"total":total}),flush=True)
                return
            indices=range(state["verified"],min(state["verified"]+args.workers,total))
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futures={i:pool.submit(worker_proc,phase,i,sha(WORK),
                   min(args.worker_timeout,max(1,deadline-time.monotonic()))) for i in indices}
                for i in indices:
                    futures[i].result()
                    if any(sha(Path(p))!=h for p,h in c[13].items()):
                        raise RuntimeError("Protected original or proof file changed")
                    state["verified"]+=1
                    atomic(path,state)
            if state["verified"]%25<args.workers or state["verified"]==total:
                print(TAG+json.dumps({"event":"AUDIT_PROGRESS","phase":phase,
                    "verified":state["verified"],"total":total}),flush=True)
    if any(verify_progress(phase,c)[0]["verified"]!=manifest(phase,c)["job_count"] for phase in PHASES):
        raise RuntimeError("Independent audit incomplete")
    print(TAG+json.dumps({"status":"STEP93_TARGET_B_INDEPENDENT_EXACT_REPLAY_PASS",
        "step":93,"pivot_coefficient_keys":len(c[11]),
        "original_source_keys":len(c[12]),
        "original_ibp_multipliers":len(c[6]),
        "step93_sha256":sha(WORK),"proof_sha256":sha(PROOF),
        "formal_state_modified":False}),flush=True)

if __name__=="__main__":main()
