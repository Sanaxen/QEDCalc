"""Resumable INTRA-STEP scratch for VP05 sector202 Target A step51.

NOT a target proof and NOT the 389-pivot checkpoint. Processes one or two
individual exact coefficients per run in independent time-capped subprocesses.
No partial row can ever be promoted by this command to the formal target state.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import sympy as sp
from examples.three_loop_vp05_sector202_target_exact_checkpoint import (
    decoded, trace_decoded, metrics,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, CHECKPOINT, SOURCE, CERT, POINTS, modular, sha,
)
from examples.three_loop_vp05_sector202_target_expression_inventory import inspect
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr

STATE = BASE / "vp05_sector202_A_exact_target_state.json"
SCRATCH = BASE / "vp05_sector202_A_step51_scratch.json"

def key_id(kind, key):
    return "%s:%s" % (kind, ",".join(map(str,key)) if kind=="remainder" else str(key))

def source_context(target, protected):
    if target.get("steps")!=50 or target.get("config",{}).get("target")!="A":
        raise RuntimeError("Target A exact saved step50 required")
    remaining_entries=target["remaining"]
    if not remaining_entries:raise RuntimeError("Empty residual, step51 not applicable")
    lead=min(tuple(k) for k,_ in remaining_entries)
    saved=json.loads(protected.read_text(encoding="utf-8-sig"))
    matches=[row for row in saved["pivots"] if tuple(row["lead"])==lead]
    if len(matches)!=1:raise RuntimeError("Saved pivot for next lead missing or duplicated")
    pivot=matches[0]
    # Always use the exact checkpoint ordering, fixed across resumed batches.
    jobs=[("remainder",k,v) for k,v in pivot["row"]]
    jobs.extend(("source_trace",k,v) for k,v in pivot["trace"])
    if len({key_id(kind,k) for kind,k,_ in jobs})!=len(jobs):
        raise RuntimeError("Duplicate coefficient operation in selected pivot")
    return lead,pivot,jobs

def compute_one(target, protected, kind, key):
    z,d=sp.symbols("z d")
    remaining=decoded(target["remaining"],z,d)
    source=trace_decoded(target["source"],z,d)
    lead,pivot,_=source_context(target,protected)
    factor=remaining[lead]
    if kind=="remainder":
        pivot_row=decoded(pivot["row"],z,d)
        old=remaining.get(tuple(key),sp.S.Zero)
        value=pivot_row[tuple(key)]
        result=sp.cancel(old-factor*value)
    else:
        pivot_trace=trace_decoded(pivot["trace"],z,d)
        rid=int(key)
        old=source.get(rid,sp.S.Zero)
        result=sp.cancel(old+factor*pivot_trace[rid])
    return str(result)

def modular_check(target, pivot, kind, key, result_string):
    z,d=sp.symbols("z d")
    remaining=decoded(target["remaining"],z,d)
    factor=remaining[min(remaining)]
    result=expr(result_string,z,d)
    if kind=="remainder":
        prior=decoded(target["remaining"],z,d).get(tuple(key),sp.S.Zero)
        pval=decoded(pivot["row"],z,d)[tuple(key)]
        sign=-1
    else:
        prior=trace_decoded(target["source"],z,d).get(int(key),sp.S.Zero)
        pval=trace_decoded(pivot["trace"],z,d)[int(key)]
        sign=1
    for point in POINTS:
        p=point[0]
        expected=(modular(prior,z,d,point)+sign*modular(factor,z,d,point)*
                  modular(pval,z,d,point))%p
        if modular(result,z,d,point)!=expected:
            raise AssertionError("Saved coefficient fails modular equation at "+str(point))

def atomic_save(path,payload,replace):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+".tmp")
    if tmp.exists():raise FileExistsError("Unresolved scratch temp exists: "+str(tmp))
    if replace and not path.exists():raise RuntimeError("Scratch checkpoint vanished")
    if not replace and path.exists():raise FileExistsError("Scratch already exists")
    try:
        with tmp.open("x",encoding="utf-8") as handle:
            json.dump(payload,handle,ensure_ascii=True,separators=(",",":"))
            handle.flush()
            os.fsync(handle.fileno())
        if not replace and path.exists():raise FileExistsError("Scratch appeared unexpectedly")
        os.replace(tmp,path)
    finally:
        if tmp.exists():tmp.unlink()

def scratch_config(target_path,protected_path,source,certificate,target,lead,
                   jobs,scratch_limit):
    return {"target_state_sha256":sha(target_path),
            "source_checkpoint_sha256":sha(protected_path),
            "source_sha256":sha(source),"certificate_sha256":sha(certificate),
            "target_step":50,"next_lead":list(lead),
            "operation_ids":[key_id(kind,key) for kind,key,_ in jobs],
            "target_max_expression_chars":target["config"]["max_expression_chars"],
            "scratch_max_expression_chars":scratch_limit}

def verify_scratch(scratch, config, target, pivot, jobs):
    if (scratch.get("version")!=1 or scratch.get("config")!=config or
        scratch.get("status")!="INTRA_STEP51_SCRATCH_NOT_PROOF" or
        scratch.get("exact_target_proven") is not False):
        raise RuntimeError("Scratch metadata, hashes or status mismatch")
    done=scratch.get("done")
    if not isinstance(done,list) or len(done)>len(jobs):
        raise RuntimeError("Invalid scratch completed count")
    if [record.get("id") for record in done] != config["operation_ids"][:len(done)]:
        raise RuntimeError("Scratch coefficient order inconsistent with pivot")
    for record, (kind,key,_) in zip(done,jobs):
        value=record.get("value")
        if not isinstance(value,str) or len(value)>config["scratch_max_expression_chars"]:
            raise RuntimeError("Saved scratch expression violates hard cap")
        if record.get("chars")!=len(value):
            raise RuntimeError("Scratch coefficient length mismatch")
        modular_check(target,pivot,kind,key,value)

def summarize(scratch,target,pivot,jobs):
    z,d=sp.symbols("z d")
    rem=decoded(target["remaining"],z,d)
    trace=trace_decoded(target["source"],z,d)
    for record,(kind,key,_) in zip(scratch["done"],jobs):
        v=expr(record["value"],z,d)
        if kind=="remainder":
            k=tuple(key)
            if v==0:rem.pop(k,None)
            else:rem[k]=v
        else:
            k=int(key)
            if v==0:trace.pop(k,None)
            else:trace[k]=v
    stats=metrics(rem,trace)
    stats["complete"]=len(scratch["done"])==len(jobs)
    stats["exceeds_formal_expression_cap"]=(
        stats["max_expression_chars"]>scratch["config"]["target_max_expression_chars"])
    return stats

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--state",type=Path,default=STATE)
    ap.add_argument("--source-checkpoint",type=Path,default=CHECKPOINT)
    ap.add_argument("--input",type=Path,default=SOURCE)
    ap.add_argument("--certificate",type=Path,default=CERT)
    ap.add_argument("--scratch",type=Path,default=SCRATCH)
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--coefficients",type=int,default=1)
    ap.add_argument("--timeout-seconds",type=int,default=60)
    ap.add_argument("--scratch-max-expression-chars",type=int,default=9000)
    ap.add_argument("--worker",action="store_true",help=argparse.SUPPRESS)
    ap.add_argument("--worker-kind",choices=("remainder","source_trace"),help=argparse.SUPPRESS)
    ap.add_argument("--worker-key",help=argparse.SUPPRESS)
    args=ap.parse_args()
    if args.worker:
        target=json.loads(args.state.read_text(encoding="utf-8-sig"))
        if args.worker_kind=="remainder":
            key=tuple(int(x) for x in args.worker_key.split(","))
        else:key=int(args.worker_key)
        print(json.dumps({"value":compute_one(target,args.source_checkpoint,
                                              args.worker_kind,key)}),flush=True)
        return
    if not 1<=args.coefficients<=2 or not 1<=args.timeout_seconds<=120:
        ap.error("Limits: --coefficients 1..2 and --timeout-seconds 1..120")
    if not 7500<=args.scratch_max_expression_chars<=10000:
        ap.error("Scratch-only hard cap must be 7500..10000")
    inputs=(args.state,args.source_checkpoint,args.input,args.certificate)
    if args.scratch.resolve() in {x.resolve() for x in inputs}:
        ap.error("Scratch path may not be a protected input")
    if args.resume != args.scratch.exists():
        raise RuntimeError("Use --resume for an existing scratch; otherwise choose a new scratch path")
    target=json.loads(args.state.read_text(encoding="utf-8-sig"))
    inspect(target,args.source_checkpoint,args.input,args.certificate,1,0)
    lead,pivot,jobs=source_context(target,args.source_checkpoint)
    config=scratch_config(args.state,args.source_checkpoint,args.input,args.certificate,
                          target,lead,jobs,args.scratch_max_expression_chars)
    if args.resume:
        scratch=json.loads(args.scratch.read_text(encoding="utf-8-sig"))
        verify_scratch(scratch,config,target,pivot,jobs)
    else:
        scratch={"version":1,"status":"INTRA_STEP51_SCRATCH_NOT_PROOF",
                 "config":config,"done":[],"exact_target_proven":False,
                 "formal_target_state_modified":False,
                 "protected_source_checkpoint_modified":False}
        atomic_save(args.scratch,scratch,False)
    finished=0
    status="INTRA_STEP51_SCRATCH_NOT_PROOF"
    while finished<args.coefficients and len(scratch["done"])<len(jobs):
        kind,key,_=jobs[len(scratch["done"])]
        cmd=[sys.executable,"-m",
             "examples.three_loop_vp05_sector202_step51_scratch",
             "--worker","--state",str(args.state),
             "--source-checkpoint",str(args.source_checkpoint),
             "--worker-kind",kind,"--worker-key",
             ",".join(map(str,key)) if kind=="remainder" else str(key)]
        started=time.monotonic()
        try:
            result=subprocess.run(cmd,text=True,capture_output=True,
                                  timeout=args.timeout_seconds,check=False)
            if result.returncode:
                status="WORKER_ERROR_NOT_PROOF"
                print("VP05_SECTOR202_STEP51_WORKER_ERROR "+
                      json.dumps({"index":len(scratch["done"])+1,
                                  "stderr_tail":result.stderr[-400:]}),flush=True)
                break
            value=json.loads(result.stdout)["value"]
            if len(value)>config["scratch_max_expression_chars"]:
                status="SCRATCH_HARD_CAP_NOT_PROOF"
                print("VP05_SECTOR202_STEP51_SCRATCH_CAP "+
                      json.dumps({"index":len(scratch["done"])+1,
                                  "chars":len(value),"scratch_hard_cap":config["scratch_max_expression_chars"]}),flush=True)
                break
            modular_check(target,pivot,kind,key,value)
        except subprocess.TimeoutExpired:
            status="COEFFICIENT_TIMEOUT_NOT_PROOF"
            break
        # Each completed coefficient is saved atomically; no formal step promotion.
        record={"id":key_id(kind,key),"value":value,"chars":len(value)}
        scratch["done"].append(record)
        atomic_save(args.scratch,scratch,True)
        finished+=1
        print("VP05_SECTOR202_STEP51_SCRATCH_PROGRESS "+
              json.dumps({"index":len(scratch["done"]),"total":len(jobs),
                          "kind":kind,"key":key,"chars":len(value),
                          "elapsed_seconds":round(time.monotonic()-started,2),
                          "formal_target_state_modified":False}),flush=True)
    final=summarize(scratch,target,pivot,jobs)
    report={"status":status,"saved_coefficient_count":len(scratch["done"]),
            "total_coefficients":len(jobs),"coefficients_this_run":finished,
            "next_operation_id":(config["operation_ids"][len(scratch["done"])]
                 if len(scratch["done"])<len(jobs) else None),
            "candidate_metrics":final,"formal_target_state_modified":False,
            "protected_source_checkpoint_modified":False,
            "exact_target_proven":False}
    print("VP05_SECTOR202_STEP51_SCRATCH_RESULT "+
          json.dumps(report,ensure_ascii=True),flush=True)

if __name__=="__main__":
    main()
