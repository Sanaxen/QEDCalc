"""Resumable, per-integral-key exact replay of assembled Step64 against ORIGINAL IBP rows.

Verifies R_before - R_after + sum((source_before-source_after)*original_IBP)==0
in exact SymPy rational functions, separately for every integral key. A key
is accepted only after symbolic cancel returns identically zero; no modular
or numeric substitution qualifies. This writes an independent replay
checkpoint, not the formal B state or protected inputs.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
import sympy as sp

from examples.three_loop_vp05_sector202_target_b_step64_exact_assembly import (
    REPORT, OUT, AUDIT, STATE, EXPECTED_STEP63_SHA, EXPECTED_CANDIDATE_SHA,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, SOURCE, CHECKPOINT, CERT, sha,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_step51_scratch import atomic_save

REPLAY = BASE / "vp05_sector202_B_step64_original_ibp_exact_replay_checkpoint.json"


def load():
    if sha(STATE)!=EXPECTED_STEP63_SHA or sha(OUT)!=EXPECTED_CANDIDATE_SHA:
        raise RuntimeError("Protected formal state/candidate changed")
    audit=json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    assembled_sha=sha(REPORT)
    assembled=json.loads(REPORT.read_text(encoding="utf-8-sig"))
    if (assembled.get("status")!="B_STEP64_ASSEMBLED_FROM_259_EXACT_RECHECKS_PENDING_ORIGINAL_IBP"
        or assembled.get("candidate_sha256")!=EXPECTED_CANDIDATE_SHA
        or assembled.get("state_step63_sha256")!=EXPECTED_STEP63_SHA
        or assembled.get("independent_audit_sha256")!=sha(AUDIT)
        or assembled.get("independent_exact_coefficient_checks")!=259
        or assembled.get("source_checkpoint_sha256")!=sha(CHECKPOINT)
        or assembled.get("original_source_sha256")!=sha(SOURCE)
        or assembled.get("certificate_sha256")!=sha(CERT)
        or assembled.get("original_ibp_exact_replay_verified") is not False
        or assembled.get("target_proven") is not False
        or assembled.get("formal_state_modified") is not False
        or assembled.get("remainder_terms")!=86
        or assembled.get("original_support")!=172
        or assembled.get("max_expression_chars",7501)>7500):
        raise RuntimeError("Step64 assembly is incomplete/incompatible")
    before=json.loads(STATE.read_text(encoding="utf-8-sig"))
    old_rem={tuple(k):v for k,v in before["remaining"]}
    new_rem={tuple(k):v for k,v in assembled["remaining"]}
    old_src={int(k):v for k,v in before["source"]}
    new_src={int(k):v for k,v in assembled["source"]}
    if len(old_rem)!=87 or len(new_rem)!=86 or len(old_src)!=168 or len(new_src)!=172:
        raise RuntimeError("Unexpected original/candidate sizes")
    with gzip.open(SOURCE,"rt",encoding="utf-8") as stream:
        original=json.load(stream)
    rows={int(row["global_zero_based"]):row for row in original["rows"]}
    if len(rows)!=len(original["rows"]):
        raise RuntimeError("Duplicate original IBP row IDs")
    changed_ids={rid for rid in set(old_src)|set(new_src)
                 if old_src.get(rid,"0")!=new_src.get(rid,"0")}
    if not changed_ids or any(rid not in rows for rid in changed_ids):
        raise RuntimeError("No changed original source rows or missing row IDs")
    keys=set(old_rem)|set(new_rem)
    by_key={}
    for rid in sorted(changed_ids):
        for term in rows[rid]["terms"]:
            key=tuple(term["key"])
            keys.add(key)
            by_key.setdefault(key,[]).append((rid,term["coefficient"]))
    jobs=sorted(keys)
    if not jobs:
        raise RuntimeError("No replay jobs")
    return before,assembled,assembled_sha,old_rem,new_rem,old_src,new_src,jobs,by_key


def worker(index):
    before,assembled,assembled_sha,old_rem,new_rem,old_src,new_src,jobs,by_key=load()
    if not 0<=index<len(jobs):
        raise ValueError("Bad replay key index")
    k=jobs[index]
    z,d=sp.symbols("z d")
    # Same sign convention as the previously passed Step60 exact-original-IBP
    # audit: (R_before-R_after)+(S_before-S_after)*original_IBP.
    terms=[expr(old_rem.get(k,"0"),z,d), -expr(new_rem.get(k,"0"),z,d)]
    for rid,coefficient in by_key.get(k,[]):
        change=sp.cancel(expr(old_src.get(rid,"0"),z,d)
                         -expr(new_src.get(rid,"0"),z,d))
        if change:
            terms.append(change*expr(coefficient,z,d))
    total=sp.cancel(sp.Add(*terms))
    if total!=0:
        raise AssertionError("Exact original IBP replay residual nonzero at key "+str(k))
    if sha(STATE)!=EXPECTED_STEP63_SHA or sha(OUT)!=EXPECTED_CANDIDATE_SHA or sha(REPORT)!=assembled_sha:
        raise RuntimeError("Input changed during exact replay")
    print("VP05_B_STEP64_ORIGINAL_IBP_REPLAY "+json.dumps({
        "event":"EXACT_ORIGINAL_IBP_KEY_PASS","index":index,"key":list(k),
        "assembled_sha256":assembled_sha,
    }),flush=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worker-index",type=int,default=None,help=argparse.SUPPRESS)
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--timeout-seconds",type=int,default=1200)
    ap.add_argument("--max-new",type=int,default=500)
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--normalized",action="store_true",
                    help="Use exact unscaled source-pivot identity plus 259 independently exact-checked coefficients")
    args=ap.parse_args()
    if args.worker_index is not None:
        worker(args.worker_index)
        return
    if not 0<args.hours<=12 or not 30<=args.timeout_seconds<=3600 or not 1<=args.max_new<=2000:
        ap.error("Safety bound violated: hours<=12, timeout 30..3600, max-new 1..2000")
    before,assembled,assembled_sha,old_rem,new_rem,old_src,new_src,jobs,by_key=load()
    binding={
        "version":1,"candidate_sha256":EXPECTED_CANDIDATE_SHA,
        "state_step63_sha256":EXPECTED_STEP63_SHA,
        "assembled_sha256":assembled_sha,
        "independent_audit_sha256":sha(AUDIT),
        "original_source_sha256":sha(SOURCE),
        "source_checkpoint_sha256":sha(CHECKPOINT),
        "certificate_sha256":sha(CERT),
        "jobs_count":len(jobs),
        "job_keys_sha256":hashlib.sha256(
            json.dumps([list(k) for k in jobs],separators=(",",":")).encode()
        ).hexdigest()
    }
    protected=[STATE,OUT,REPORT,AUDIT,SOURCE,CHECKPOINT,CERT]
    if REPLAY.resolve() in {p.resolve() for p in protected}:
        raise RuntimeError("Replay checkpoint aliases protected input")
    if REPLAY.exists()!=args.resume:
        raise RuntimeError("Replay checkpoint exists: use --resume; otherwise omit it")
    if args.resume:
        progress=json.loads(REPLAY.read_text(encoding="utf-8-sig"))
        if (progress.get("config")!=binding
            or progress.get("status")!="B_STEP64_ORIGINAL_IBP_PREFIX_NOT_PROOF"
            or progress.get("target_b_proven") is not False
            or progress.get("formal_state_modified") is not False):
            raise RuntimeError("Existing replay prefix not bound to same immutable inputs")
        done=progress.get("checked",[])
        if not isinstance(done,list) or len(done)>len(jobs) or any(
            row.get("index")!=i or row.get("key")!=list(jobs[i])
            for i,row in enumerate(done)):
            raise RuntimeError("Replay checkpoint has invalid prefix")
    else:
        progress={"version":1,"status":"B_STEP64_ORIGINAL_IBP_PREFIX_NOT_PROOF",
                  "config":binding,"checked":[],
                  "original_ibp_exact_replay_verified":False,
                  "formal_state_modified":False,"target_b_proven":False}
        atomic_save(REPLAY,progress,False)
    print("VP05_B_STEP64_ORIGINAL_IBP_REPLAY "+json.dumps({
        "event":"START","total_keys":len(jobs),"already_verified":len(progress["checked"]),
        "candidate_sha256":EXPECTED_CANDIDATE_SHA,"assembled_sha256":assembled_sha
    }),flush=True)
    start=time.monotonic()
    count=0
    while len(progress["checked"])<len(jobs) and count<args.max_new:
        if time.monotonic()-start+args.timeout_seconds+30>args.hours*3600:
            break
        i=len(progress["checked"])
        try:
            cmd=([sys.executable,"-m",
                  "examples.three_loop_vp05_sector202_target_b_step64_normalized_replay",
                  "--index",str(i)] if args.normalized else
                 [sys.executable,"-m",
                  "examples.three_loop_vp05_sector202_target_b_step64_original_ibp_replay",
                  "--worker-index",str(i)])
            run=subprocess.run(cmd,text=True,capture_output=True,
                               timeout=args.timeout_seconds,check=False)
        except subprocess.TimeoutExpired:
            print("VP05_B_STEP64_ORIGINAL_IBP_REPLAY "+json.dumps({
                "event":"WORKER_TIMEOUT_NOT_PROOF","index":i}),flush=True)
            break
        if run.returncode:
            print("VP05_B_STEP64_ORIGINAL_IBP_REPLAY "+json.dumps({
                "event":"WORKER_ERROR_NOT_PROOF","index":i,
                "stderr_tail":run.stderr[-1800:]}),flush=True)
            break
        marker="VP05_B_STEP64_ORIGINAL_IBP_REPLAY "
        if marker not in run.stdout:
            raise RuntimeError("Worker did not return replay result")
        result=json.loads(run.stdout.split(marker,1)[1])
        if (result.get("event")!="EXACT_ORIGINAL_IBP_KEY_PASS"
            or result.get("index")!=i or result.get("key")!=list(jobs[i])
            or result.get("assembled_sha256")!=assembled_sha):
            raise RuntimeError("Replay worker returned inconsistent certificate")
        progress["checked"].append({"index":i,"key":list(jobs[i]),
            "method":result.get("method","direct_original_ibp_exact")})
        atomic_save(REPLAY,progress,True)
        count+=1
        print("VP05_B_STEP64_ORIGINAL_IBP_REPLAY "+json.dumps({
            "event":"EXACT_IBP_KEY_SAVED","checked":len(progress["checked"]),
            "total_keys":len(jobs),"elapsed_seconds":round(time.monotonic()-start,2)
        }),flush=True)
    if sha(STATE)!=EXPECTED_STEP63_SHA or sha(OUT)!=EXPECTED_CANDIDATE_SHA or sha(REPORT)!=assembled_sha:
        raise RuntimeError("Protected checkpoint/candidate/assembly changed")
    complete=len(progress["checked"])==len(jobs)
    print("VP05_B_STEP64_ORIGINAL_IBP_REPLAY "+json.dumps({
        "status":"B_STEP64_ALL_ORIGINAL_IBP_KEYS_EXACT_PASS_NOT_TARGET_PROOF"
        if complete else "B_STEP64_ORIGINAL_IBP_PREFIX_NOT_PROOF",
        "verified_keys":len(progress["checked"]),"total_keys":len(jobs),
        "candidate_sha256":EXPECTED_CANDIDATE_SHA,
        "assembled_sha256":assembled_sha,
        "original_ibp_exact_replay_verified":complete,
        "method":"normalized_exact_pivot" if args.normalized else "direct_exact",
        "formal_state_modified":False,"target_b_proven":False
    }),flush=True)


if __name__=="__main__":
    main()
