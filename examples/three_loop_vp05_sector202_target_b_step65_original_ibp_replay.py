"""Bounded resumable exact original-IBP replay of assembled B Step65.

For each integral key, the original IBP pivot identity is checked exactly in
SymPy. Independently proven 40 coefficient updates give the algebraic equality
of the full Step64-to-Step65 residual/source difference after multiplying
the pivot identity by the nonzero lead coefficient. No numeric shortcuts,
no writes to formal B state, and no Target B proof claim.
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

from examples.three_loop_vp05_sector202_target_b_step65_exact_assembly import (
    REPORT, OUT, AUDIT, STATE, EXPECTED_STEP64_SHA, EXPECTED_CANDIDATE_SHA,
)
from examples.three_loop_vp05_sector202_target_b_step65_independent_audit import context
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, SOURCE, CHECKPOINT, CERT, sha,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_step51_scratch import atomic_save
from examples.three_loop_vp05_sector202_target_b_step64_formal_promotion import (
    BACKUP as STEP63_BACKUP, EXPECTED_STEP63_SHA,
)
from examples.three_loop_vp05_sector202_target_b_start import A_STATE, A_PROOF, A_STATE_SHA, A_PROOF_SHA

REPLAY=BASE/"vp05_sector202_B_step65_original_ibp_exact_replay_checkpoint.json"


def load():
    state,pivot,operations,done,candidate_sha=context()
    if candidate_sha!=EXPECTED_CANDIDATE_SHA or sha(STATE)!=EXPECTED_STEP64_SHA:
        raise RuntimeError("Step65 immutable input mismatch")
    report_sha=sha(REPORT)
    report=json.loads(REPORT.read_text(encoding="utf-8-sig"))
    audit=json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    checked=audit.get("checked",[])
    if (report.get("status")!="B_STEP65_ASSEMBLED_FROM_40_EXACT_RECHECKS_PENDING_ORIGINAL_IBP"
        or report.get("candidate_sha256")!=EXPECTED_CANDIDATE_SHA
        or report.get("state_step64_sha256")!=EXPECTED_STEP64_SHA
        or report.get("independent_audit_sha256")!=sha(AUDIT)
        or report.get("independent_exact_coefficient_checks")!=40
        or report.get("source_checkpoint_sha256")!=sha(CHECKPOINT)
        or report.get("original_source_sha256")!=sha(SOURCE)
        or report.get("certificate_sha256")!=sha(CERT)
        or report.get("remainder_terms")!=85
        or report.get("original_support")!=173
        or report.get("max_expression_chars",7501)>7500
        or report.get("formal_state_modified") is not False
        or report.get("original_ibp_exact_replay_verified") is not False
        or report.get("target_proven") is not False
        or len(operations)!=40 or len(done)!=40 or len(checked)!=40
        or any(r.get("index")!=i or r.get("id")!=done[i]["id"]
               or r.get("coefficient_sha256")!=hashlib.sha256(done[i]["value"].encode()).hexdigest()
               for i,r in enumerate(checked))
        or sha(STEP63_BACKUP)!=EXPECTED_STEP63_SHA
        or sha(A_STATE)!=A_STATE_SHA or sha(A_PROOF)!=A_PROOF_SHA):
        raise RuntimeError("40 exact coefficients or Step65 assembly not fully audited")
    old_rem={tuple(k):v for k,v in state["remaining"]}
    new_rem={tuple(k):v for k,v in report["remaining"]}
    old_src={int(k):v for k,v in state["source"]}
    new_src={int(k):v for k,v in report["source"]}
    lead=min(old_rem)
    if (lead!=(166596413882371,139) or tuple(pivot["lead"])!=lead
        or len(old_rem)!=86 or len(new_rem)!=85 or lead in new_rem
        or len(old_src)!=172 or len(new_src)!=173
        or len(new_rem)!=len(report["remaining"]) or len(new_src)!=len(report["source"])):
        raise RuntimeError("Unexpected assembled source/pivot dimensions")
    # Build all integral keys touched by changed original IBP multipliers.
    changed={rid for rid in old_src.keys()|new_src.keys()
             if old_src.get(rid,"0")!=new_src.get(rid,"0")}
    trace={int(rid):raw for rid,raw in pivot["trace"]}
    if not changed or not changed.issubset(trace):
        raise RuntimeError("Changed original source multipliers not in pivot trace")
    with gzip.open(SOURCE,"rt",encoding="utf-8") as fh:
        original=json.load(fh)
    original_rows={int(r["global_zero_based"]):r for r in original["rows"]}
    if len(original_rows)!=len(original["rows"]) or not set(trace).issubset(original_rows):
        raise RuntimeError("Missing or duplicated original source equation")
    keys=set(old_rem)|set(new_rem)|{tuple(k) for k,_ in pivot["row"]}
    for rid in trace:
        keys.update(tuple(t["key"]) for t in original_rows[rid]["terms"])
    jobs=sorted(keys)
    row={tuple(k):raw for k,raw in pivot["row"]}
    # Source pivot trace is also independently pinned to the saved checkpoint.
    return report_sha,lead,trace,original_rows,row,jobs


def worker(index):
    report_sha,lead,trace,original_rows,row,jobs=load()
    if not 0<=index<len(jobs):raise ValueError("Invalid integral key")
    k=jobs[index]
    z,d=sp.symbols("z d")
    parts=[]
    for rid,weight in trace.items():
        for term in original_rows[rid]["terms"]:
            if tuple(term["key"])==k:
                parts.append(expr(weight,z,d)*expr(term["coefficient"],z,d))
    exact=sp.cancel(expr(row.get(k,"0"),z,d)-sp.Add(*parts))
    if exact!=0:
        raise AssertionError("Step65 original IBP exact source-pivot identity mismatch: "+str(k))
    if sha(STATE)!=EXPECTED_STEP64_SHA or sha(OUT)!=EXPECTED_CANDIDATE_SHA or sha(REPORT)!=report_sha:
        raise RuntimeError("Protected input changed in exact replay worker")
    print("VP05_B_STEP65_ORIGINAL_IBP_REPLAY "+json.dumps({
        "event":"EXACT_ORIGINAL_IBP_KEY_PASS",
        "index":index,"key":list(k),
        "assembled_sha256":report_sha,
        "method":"unscaled_source_pivot_exact_with_40_certificates",
    }),flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worker-index",type=int,default=None,help=argparse.SUPPRESS)
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--timeout-seconds",type=int,default=1200)
    ap.add_argument("--max-new",type=int,default=500)
    args=ap.parse_args()
    if args.worker_index is not None:
        worker(args.worker_index)
        return
    if not 0<args.hours<=12 or not 30<=args.timeout_seconds<=3600 or not 1<=args.max_new<=2000:
        ap.error("Safety bounds exceeded")
    report_sha,lead,trace,original_rows,row,jobs=load()
    config={
        "version":1,"state_step64_sha256":EXPECTED_STEP64_SHA,
        "candidate_sha256":EXPECTED_CANDIDATE_SHA,
        "assembled_sha256":report_sha,
        "independent_audit_sha256":sha(AUDIT),
        "original_source_sha256":sha(SOURCE),
        "source_checkpoint_sha256":sha(CHECKPOINT),
        "certificate_sha256":sha(CERT),
        "jobs_count":len(jobs),
        "job_keys_sha256":hashlib.sha256(
            json.dumps([list(k) for k in jobs],separators=(",",":")).encode()
        ).hexdigest(),
    }
    protected=[STATE,OUT,REPORT,AUDIT,SOURCE,CHECKPOINT,CERT,A_STATE,A_PROOF,STEP63_BACKUP]
    if REPLAY.resolve() in {p.resolve() for p in protected}:
        raise RuntimeError("Replay aliases protected source")
    if REPLAY.exists()!=args.resume:
        raise RuntimeError("Replay exists: use --resume; otherwise omit it")
    if args.resume:
        progress=json.loads(REPLAY.read_text(encoding="utf-8-sig"))
        checked=progress.get("checked",[])
        if (progress.get("config")!=config
            or progress.get("status")!="B_STEP65_ORIGINAL_IBP_PREFIX_NOT_PROOF"
            or progress.get("target_b_proven") is not False
            or progress.get("formal_state_modified") is not False
            or not isinstance(checked,list) or len(checked)>len(jobs)
            or any(r.get("index")!=i or r.get("key")!=list(jobs[i])
                   or r.get("method")!="unscaled_source_pivot_exact_with_40_certificates"
                   for i,r in enumerate(checked))):
            raise RuntimeError("Invalid saved Step65 exact replay checkpoint")
    else:
        progress={"version":1,"status":"B_STEP65_ORIGINAL_IBP_PREFIX_NOT_PROOF",
                  "config":config,"checked":[],
                  "original_ibp_exact_replay_verified":False,
                  "formal_state_modified":False,"target_b_proven":False}
        atomic_save(REPLAY,progress,False)
    print("VP05_B_STEP65_ORIGINAL_IBP_REPLAY "+json.dumps({
        "event":"START","total_keys":len(jobs),
        "already_verified":len(progress["checked"]),
        "candidate_sha256":EXPECTED_CANDIDATE_SHA,
        "assembled_sha256":report_sha,
    }),flush=True)
    started=time.monotonic()
    count=0
    while len(progress["checked"])<len(jobs) and count<args.max_new:
        if time.monotonic()-started+args.timeout_seconds+30>args.hours*3600:
            break
        i=len(progress["checked"])
        try:
            run=subprocess.run([sys.executable,"-m",
                "examples.three_loop_vp05_sector202_target_b_step65_original_ibp_replay",
                "--worker-index",str(i)],text=True,capture_output=True,
                timeout=args.timeout_seconds,check=False)
        except subprocess.TimeoutExpired:
            print("VP05_B_STEP65_ORIGINAL_IBP_REPLAY "+json.dumps({
                "event":"WORKER_TIMEOUT_NOT_PROOF","index":i}),flush=True)
            break
        if run.returncode:
            print("VP05_B_STEP65_ORIGINAL_IBP_REPLAY "+json.dumps({
                "event":"WORKER_ERROR_NOT_PROOF","index":i,
                "stderr_tail":run.stderr[-1800:]}),flush=True)
            break
        marker="VP05_B_STEP65_ORIGINAL_IBP_REPLAY "
        if marker not in run.stdout:raise RuntimeError("Missing exact worker result")
        result=json.loads(run.stdout.split(marker,1)[1])
        if (result.get("event")!="EXACT_ORIGINAL_IBP_KEY_PASS"
            or result.get("index")!=i or result.get("key")!=list(jobs[i])
            or result.get("assembled_sha256")!=report_sha
            or result.get("method")!="unscaled_source_pivot_exact_with_40_certificates"):
            raise RuntimeError("Unbound original-IBP worker certificate")
        progress["checked"].append({"index":i,"key":list(jobs[i]),
            "method":result["method"]})
        atomic_save(REPLAY,progress,True)
        count+=1
        print("VP05_B_STEP65_ORIGINAL_IBP_REPLAY "+json.dumps({
            "event":"EXACT_IBP_KEY_SAVED","checked":len(progress["checked"]),
            "total_keys":len(jobs),
            "elapsed_seconds":round(time.monotonic()-started,2),
        }),flush=True)
    if sha(STATE)!=EXPECTED_STEP64_SHA or sha(OUT)!=EXPECTED_CANDIDATE_SHA or sha(REPORT)!=report_sha:
        raise RuntimeError("Immutable Step64 or Step65 inputs changed")
    complete=len(progress["checked"])==len(jobs)
    print("VP05_B_STEP65_ORIGINAL_IBP_REPLAY "+json.dumps({
        "status":"B_STEP65_ALL_ORIGINAL_IBP_KEYS_EXACT_PASS_NOT_TARGET_PROOF"
        if complete else "B_STEP65_ORIGINAL_IBP_PREFIX_NOT_PROOF",
        "verified_keys":len(progress["checked"]),"total_keys":len(jobs),
        "candidate_sha256":EXPECTED_CANDIDATE_SHA,
        "assembled_sha256":report_sha,
        "original_ibp_exact_replay_verified":complete,
        "formal_state_modified":False,"target_b_proven":False,
    }),flush=True)


if __name__=="__main__":
    main()
