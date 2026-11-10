"""Isolate one step51 exact residual coefficient without repeating prior columns.

Read-only. Each rewrite executes in its own time-capped subprocess. No output
from a timed-out worker is treated as an algebraic identity or proof.
"""
from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_target_exact_checkpoint import decoded
from examples.three_loop_vp05_sector202_target_expression_inventory import (
    inspect, DEFAULT_STATE, DEFAULT_SOURCE_CHECKPOINT, DEFAULT_SOURCE, DEFAULT_CERT,
)
BASE=Path(__file__).resolve().parents[1]/"output/three_loop_integral_family_audit"
KEY=(166596412964865,139)

def operands(state, checkpoint, key=KEY):
    z,d=sp.symbols("z d")
    row=decoded(state["remaining"],z,d)
    lead=min(row)
    saved=json.loads(checkpoint.read_text(encoding="utf-8-sig"))
    matching=[v for v in saved["pivots"] if tuple(v["lead"])==lead]
    if len(matching)!=1:
        raise RuntimeError("Expected one matching saved source pivot")
    pivot=decoded(matching[0]["row"],z,d)
    if key not in pivot:
        raise RuntimeError("Requested key is not in next pivot")
    return row.get(key,sp.S.Zero),row[lead],pivot[key],lead

def calculation(original,factor,pivot,method):
    raw=original-factor*pivot
    if method=="cancel":
        return sp.cancel(raw)
    if method=="together_cancel":
        return sp.cancel(sp.together(raw))
    if method=="factor_first":
        return sp.cancel(sp.factor_terms(original)-sp.factor_terms(factor)*sp.factor_terms(pivot))
    raise ValueError("Unknown exact method")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--state",type=Path,default=DEFAULT_STATE)
    ap.add_argument("--source-checkpoint",type=Path,default=DEFAULT_SOURCE_CHECKPOINT)
    ap.add_argument("--input",type=Path,default=DEFAULT_SOURCE)
    ap.add_argument("--certificate",type=Path,default=DEFAULT_CERT)
    ap.add_argument("--key",default="166596412964865,139")
    ap.add_argument("--methods",default="cancel,together_cancel")
    ap.add_argument("--timeout-seconds",type=int,default=45)
    ap.add_argument("--output",type=Path,default=BASE/"vp05_sector202_A_step51_coefficient12_methods.json")
    ap.add_argument("--worker",action="store_true",help=argparse.SUPPRESS)
    ap.add_argument("--method",choices=("cancel","together_cancel","factor_first"),help=argparse.SUPPRESS)
    args=ap.parse_args()
    key=tuple(map(int,args.key.split(",")))
    if len(key)!=2 or not 1<=args.timeout_seconds<=90:ap.error("Invalid key/timeout")
    if args.worker:
        state=json.loads(args.state.read_text(encoding="utf-8-sig"))
        original,factor,pivot,lead=operands(state,args.source_checkpoint,key)
        started=time.monotonic()
        result=calculation(original,factor,pivot,args.method)
        print(json.dumps({"method":args.method,"result_chars":len(str(result)),
                          "zero":bool(result==0),"elapsed_calculation_seconds":round(time.monotonic()-started,2),
                          "result_sha256":__import__("hashlib").sha256(str(result).encode()).hexdigest()}),flush=True)
        return
    if args.output.resolve() in {p.resolve() for p in
                                 (args.state,args.source_checkpoint,args.input,args.certificate)}:
        ap.error("Output path is a protected input")
    if args.output.exists():raise FileExistsError("Output exists")
    state=json.loads(args.state.read_text(encoding="utf-8-sig"))
    inspect(state,args.source_checkpoint,args.input,args.certificate,1,0)
    if state["steps"]!=50 or state["config"]["target"]!="A":
        raise RuntimeError("Target A step50 required")
    methods=args.methods.split(",")
    if not methods or len(set(methods))!=len(methods) or len(methods)>3 or any(
            x not in ("cancel","together_cancel","factor_first") for x in methods):
        ap.error("Invalid method list")
    outcomes=[]
    for method in methods:
        cmd=[sys.executable,"-m","examples.three_loop_vp05_sector202_target_coefficient_probe",
             "--worker","--state",str(args.state),
             "--source-checkpoint",str(args.source_checkpoint),"--key",args.key,
             "--method",method]
        start=time.monotonic()
        try:
            process=subprocess.run(cmd,capture_output=True,text=True,
                                   timeout=args.timeout_seconds,check=False)
            if process.returncode:
                result={"method":method,"status":"WORKER_ERROR","stderr_tail":process.stderr[-300:]}
            else:
                result={"status":"COMPUTED_EXACT_EXPRESSION_NOT_PROOF",**json.loads(process.stdout)}
        except subprocess.TimeoutExpired:
            result={"method":method,"status":"TIMEOUT_NOT_PROOF"}
        result["elapsed_total_seconds"]=round(time.monotonic()-start,2)
        outcomes.append(result)
        print("VP05_SECTOR202_COEFFICIENT_METHOD "+json.dumps(result),flush=True)
    hashes={r["result_sha256"] for r in outcomes if "result_sha256" in r}
    report={"status":"READ_ONLY_SINGLE_COEFFICIENT_DIAGNOSTIC_NOT_PROOF",
            "saved_step":50,"attempted_step":51,"key":list(key),
            "methods":outcomes,"identical_result_strings":len(hashes)==1 if len(hashes)>1 else None,
            "note":"Matching strings are only a consistency check; full symbolic difference or source replay required for proof",
            "checkpoint_modified":False,"exact_target_proven":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as file:
        json.dump(report,file,ensure_ascii=True,indent=2);file.write("\n")
    print("VP05_SECTOR202_COEFFICIENT_REPORT "+json.dumps(
        {"status":report["status"],"output":str(args.output),"checkpoint_modified":False}),flush=True)

if __name__=="__main__":main()
