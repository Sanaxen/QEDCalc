"""Read-only, time-bounded trial compaction of sector202 target A next pivot.

The worker reconstructs exactly ONE candidate elimination from the saved
Target A checkpoint. It never persists that candidate. Each over-cap
coefficient can be factored only up to a bounded count, and exact equivalence
must pass before the candidate's adjusted length is reported.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
import sympy as sp
from examples.three_loop_vp05_sector202_target_exact_reduction import add
from examples.three_loop_vp05_sector202_target_exact_checkpoint import (
    decoded,trace_decoded,metrics,
)
from examples.three_loop_vp05_sector202_target_compaction_probe import compact_candidate
from examples.three_loop_vp05_sector202_target_expression_inventory import (
    inspect,DEFAULT_STATE,DEFAULT_SOURCE_CHECKPOINT,DEFAULT_SOURCE,DEFAULT_CERT,
)

BASE=Path(__file__).resolve().parents[1]/"output/three_loop_integral_family_audit"

def one_step(state,source_checkpoint,max_candidates):
    z,d=sp.symbols("z d")
    residual=decoded(state["remaining"],z,d)
    trace=trace_decoded(state["source"],z,d)
    lead=min(residual)
    saved=json.loads(source_checkpoint.read_text(encoding="utf-8-sig"))
    match=[v for v in saved["pivots"] if tuple(v["lead"])==lead]
    if len(match)!=1:
        raise RuntimeError("No unique next pivot in protected source checkpoint")
    pivot_row=decoded(match[0]["row"],z,d)
    pivot_trace=trace_decoded(match[0]["trace"],z,d)
    factor=residual[lead]
    add(residual,pivot_row,-factor)
    add(trace,pivot_trace,factor)
    before=metrics(residual,trace)
    cap=state["config"]["max_expression_chars"]
    candidates=[(kind,key,value) for kind,values in
                (("remainder",residual),("source_trace",trace))
                for key,value in values.items() if len(str(value))>cap]
    candidates.sort(key=lambda x:len(str(x[2])),reverse=True)
    results=[]
    for kind,key,value in candidates[:max_candidates]:
        proposed=compact_candidate(value,"factor_numden")
        equal=sp.cancel(sp.together(proposed-value))==0
        if not equal:
            raise AssertionError("Compacted candidate is not exactly equal")
        results.append({"kind":kind,"key":list(key) if kind=="remainder" else key,
                        "original_chars":len(str(value)),
                        "compacted_chars":len(str(proposed)),
                        "saved_chars":len(str(value))-len(str(proposed)),
                        "under_cap":len(str(proposed))<=cap,"exact_equal":True})
    return {"status":"READ_ONLY_NEXT_STEP_COMPACTION_DIAGNOSTIC_NOT_PROOF",
            "last_saved_step":state["steps"],
            "attempted_step":state["steps"]+1,
            "next_lead":list(lead),
            "candidate_before":before,"max_expression_chars_limit":cap,
            "oversized_coefficient_count":len(candidates),
            "inspected_count":len(results),
            "remaining_uninspected_count":max(0,len(candidates)-len(results)),
            "results":results,"checkpoint_modified":False,
            "next_step_saved":False,"exact_target_proven":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--state",type=Path,default=DEFAULT_STATE)
    ap.add_argument("--source-checkpoint",type=Path,default=DEFAULT_SOURCE_CHECKPOINT)
    ap.add_argument("--input",type=Path,default=DEFAULT_SOURCE)
    ap.add_argument("--certificate",type=Path,default=DEFAULT_CERT)
    ap.add_argument("--max-coefficients",type=int,default=3)
    ap.add_argument("--timeout-seconds",type=int,default=120)
    ap.add_argument("--output",type=Path,default=BASE/"vp05_sector202_A_step51_compaction_diagnostic.json")
    ap.add_argument("--worker",action="store_true",help=argparse.SUPPRESS)
    args=ap.parse_args()
    if not 1<=args.max_coefficients<=10 or not 1<=args.timeout_seconds<=180:
        ap.error("Invalid limits")
    if args.worker:
        state=json.loads(args.state.read_text(encoding="utf-8-sig"))
        print(json.dumps(one_step(state,args.source_checkpoint,args.max_coefficients),
                         ensure_ascii=True),flush=True)
        return
    protected={p.resolve() for p in
               (args.state,args.source_checkpoint,args.input,args.certificate)}
    if args.output.resolve() in protected:
        ap.error("Output may not overwrite state/source")
    if args.output.exists():
        raise FileExistsError("Report already exists")
    state=json.loads(args.state.read_text(encoding="utf-8-sig"))
    inspect(state,args.source_checkpoint,args.input,args.certificate,count=1,preview=0)
    if state["steps"]!=50 or state["config"]["target"]!="A":
        raise RuntimeError("Expected Target A saved step50")
    cmd=[sys.executable,"-m",
         "examples.three_loop_vp05_sector202_target_next_step_compaction",
         "--worker","--state",str(args.state),
         "--source-checkpoint",str(args.source_checkpoint),
         "--max-coefficients",str(args.max_coefficients)]
    start=time.monotonic()
    try:
        done=subprocess.run(cmd,text=True,capture_output=True,
                            timeout=args.timeout_seconds,check=False)
        elapsed=round(time.monotonic()-start,2)
        if done.returncode:
            report={"status":"NEXT_STEP_COMPACTION_WORKER_ERROR_NOT_PROOF",
                    "returncode":done.returncode,"stderr_tail":done.stderr[-500:]}
        else:
            report=json.loads(done.stdout)
    except subprocess.TimeoutExpired:
        elapsed=round(time.monotonic()-start,2)
        report={"status":"NEXT_STEP_COMPACTION_TIMEOUT_NOT_PROOF"}
    report.update({"elapsed_seconds":elapsed,"checkpoint_modified":False,
                   "next_step_saved":False,"exact_target_proven":False})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x",encoding="utf-8") as handle:
        json.dump(report,handle,indent=2,ensure_ascii=True)
        handle.write("\n")
    print("VP05_SECTOR202_TARGET_NEXT_STEP_COMPACTION "+
          json.dumps(report,ensure_ascii=True),flush=True)

if __name__=="__main__":main()
