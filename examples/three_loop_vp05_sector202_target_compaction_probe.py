"""Bounded, read-only compaction probe of ONE exact sector202 target coefficient.

Each candidate rewrite runs in a fresh timed subprocess. Never modifies either
the 389-pivot source checkpoint or the target checkpoint. Exact equality is
mandatory before counting a candidate as a useful compaction.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_target_expression_inventory import (
    DEFAULT_STATE, DEFAULT_SOURCE_CHECKPOINT, DEFAULT_SOURCE, DEFAULT_CERT,
    inspect,
)

def chosen_entry(state, kind, key):
    entries=state["remaining"] if kind=="remainder" else state["source"]
    matches=[v for k,v in entries if str(k)==str(key)]
    if len(matches)!=1:
        raise ValueError("Selected coefficient absent or ambiguous")
    return matches[0]

def compact_candidate(value,method):
    if method=="factor_terms":
        return sp.factor_terms(value)
    if method=="factor":
        return sp.factor(value)
    if method=="factor_numden":
        numerator,denominator=sp.fraction(sp.together(value))
        return sp.factor(numerator)/sp.factor(denominator)
    raise ValueError("Unsupported method")

def worker(state_path,kind,key,method):
    state=json.loads(state_path.read_text(encoding="utf-8-sig"))
    raw=chosen_entry(state,kind,key)
    z,d=sp.symbols("z d")
    value=sp.sympify(raw,locals={"z":z,"d":d},evaluate=True)
    candidate=compact_candidate(value,method)
    exact_equal=(sp.cancel(sp.together(candidate-value))==0)
    original_chars=len(str(value))
    candidate_chars=len(str(candidate))
    result={"method":method,"exact_equal":bool(exact_equal),
            "original_chars":original_chars,
            "candidate_chars":candidate_chars,
            "saved_chars":original_chars-candidate_chars if exact_equal else None,
            "improved":bool(exact_equal and candidate_chars<original_chars)}
    print(json.dumps(result,ensure_ascii=True),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--state",type=Path,default=DEFAULT_STATE)
    ap.add_argument("--source-checkpoint",type=Path,default=DEFAULT_SOURCE_CHECKPOINT)
    ap.add_argument("--input",type=Path,default=DEFAULT_SOURCE)
    ap.add_argument("--certificate",type=Path,default=DEFAULT_CERT)
    ap.add_argument("--kind",choices=("remainder","source_trace"),default="remainder")
    ap.add_argument("--key",default="[166596413095937, 139]")
    ap.add_argument("--methods",default="factor_terms,factor_numden,factor")
    ap.add_argument("--timeout-seconds",type=int,default=45)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_sector202_A_exact_step50_compaction_probe.json"))
    ap.add_argument("--worker",action="store_true",help=argparse.SUPPRESS)
    ap.add_argument("--method",choices=("factor_terms","factor_numden","factor"),help=argparse.SUPPRESS)
    args=ap.parse_args()
    if args.worker:
        if not args.method:ap.error("Worker requires method")
        worker(args.state,args.kind,args.key,args.method)
        return
    if not 1<=args.timeout_seconds<=120:
        ap.error("Timeout must be between 1 and 120 seconds")
    methods=args.methods.split(",")
    if (not methods or len(methods)>3 or len(set(methods))!=len(methods)
            or any(x not in ("factor_terms","factor_numden","factor") for x in methods)):
        ap.error("Expected up to three distinct supported methods")
    protected={p.resolve() for p in (args.state,args.source_checkpoint,args.input,args.certificate)}
    if args.output.resolve() in protected:ap.error("Output cannot replace an input")
    if args.output.exists():raise FileExistsError("Output already exists")
    state=json.loads(args.state.read_text(encoding="utf-8-sig"))
    overview=inspect(state,args.source_checkpoint,args.input,args.certificate,1,0)
    if state["steps"]!=50:
        raise RuntimeError("Only the verified step50 state is accepted for this first probe")
    original=chosen_entry(state,args.kind,args.key)
    if len(original)>10000:
        raise RuntimeError("Selected string exceeds safety length")
    records=[]
    for method in methods:
        cmd=[sys.executable,"-m","examples.three_loop_vp05_sector202_target_compaction_probe",
             "--worker","--state",str(args.state),"--kind",args.kind,
             "--key",args.key,"--method",method]
        started=time.monotonic()
        try:
            proc=subprocess.run(cmd,text=True,capture_output=True,
                                timeout=args.timeout_seconds,check=False)
            elapsed=round(time.monotonic()-started,2)
            if proc.returncode:
                outcome={"method":method,"status":"WORKER_ERROR",
                         "returncode":proc.returncode,"stderr_tail":proc.stderr[-400:]}
            else:
                payload=json.loads(proc.stdout)
                outcome={"status":"EXACT_EQUIVALENCE_PASS" if payload["exact_equal"] else "EXACT_EQUIVALENCE_FAIL",
                         **payload}
            outcome["elapsed_seconds"]=elapsed
        except subprocess.TimeoutExpired:
            outcome={"method":method,"status":"TIMEOUT",
                     "elapsed_seconds":round(time.monotonic()-started,2)}
        records.append(outcome)
        print("VP05_SECTOR202_COMPACTION_METHOD "+json.dumps(outcome),flush=True)
    report={"status":"READ_ONLY_BOUNDED_COMPACTION_DIAGNOSTIC_NOT_PROOF",
            "target":overview["target"],"step":state["steps"],
            "kind":args.kind,"key":args.key,"original_chars":len(original),
            "methods":records,"checkpoint_modified":False,
            "next_step_executed":False,"exact_target_proven":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as out:
        json.dump(report,out,indent=2,ensure_ascii=True)
        out.write("\n")
    print("VP05_SECTOR202_COMPACTION_REPORT "+json.dumps(
        {"output":str(args.output),"status":report["status"],
         "checkpoint_modified":False}),flush=True)

if __name__=="__main__":main()
