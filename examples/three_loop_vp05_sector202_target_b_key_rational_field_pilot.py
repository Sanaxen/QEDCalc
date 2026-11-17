"""Read-only isolated exact QQ(z,d) rational-field pilot for heavy Step66 key113.

Alternative to sp.cancel(huge_Add). All equality checks use exact polynomial
rational functions over QQ; no floating point or modular sampling. This is
a diagnostic pilot, NOT a persisted IBP certificate or formal promotion.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from sympy.polys.fields import field
from sympy.polys.domains import QQ
import sympy as sp
from examples.three_loop_vp05_sector202_target_b_step66_normalized_ibp_replay import (
    load, DIRECT_COUNT, EXPECTED_STEP66_SHA, SAVED_STEP65_SHA,
    B_STATE, SCRATCH, COEFFICIENT, DIRECT, PROTECTED, sha,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr

TAG="VP05_B_STEP66_RATIONAL_FIELD_PILOT "

def exact_field_check(pivot_raw, parts, progress=None):
    """Exact QQ[z,d] fraction-field equality, preserving separate summands."""
    k,z,d=field("z,d",QQ)
    def convert(raw):
        return k.from_expr(expr(raw,sp.Symbol("z"),sp.Symbol("d")))
    total=k.zero
    for index,(weight,coeff) in enumerate(parts):
        total+=convert(weight)*convert(coeff)
        if progress is not None and (index+1)%10==0:
            progress(index+1,len(parts))
    difference=convert(pivot_raw)-total
    if difference!=k.zero:
        raise AssertionError("Original-IBP pivot does not equal source trace (exact QQ rational field)")
    return True

def inspect(index):
    jobs,prow,key_terms,coeff_sha,direct_sha=load()
    if not DIRECT_COUNT<=index<len(jobs):
        raise ValueError("Index outside normalized suffix")
    key=jobs[index]
    parts=key_terms.get(key,[])
    return {"index":index,"key":list(key),"terms":len(parts),
            "max_term_weight_chars":max((len(w) for w,c in parts),default=0),
            "max_term_coefficient_chars":max((len(c) for w,c in parts),default=0),
            "sum_input_chars":sum(len(w)+len(c) for w,c in parts),
            "pivot_coefficient_chars":len(prow.get(key,"0")),
            "formal_step65_sha256":SAVED_STEP65_SHA,
            "scratch_step66_sha256":EXPECTED_STEP66_SHA}

def worker(index):
    jobs,prow,key_terms,coeff_sha,direct_sha=load()
    if not DIRECT_COUNT<=index<len(jobs):
        raise ValueError("Index outside normalized suffix")
    key=jobs[index]
    parts=key_terms.get(key,[])
    print(TAG+json.dumps({"event":"EXACT_FIELD_START",**inspect(index)}),flush=True)
    exact_field_check(prow.get(key,"0"),parts,
        progress=lambda done,total:print(TAG+json.dumps({
            "event":"EXACT_FIELD_PROGRESS","index":index,
            "terms_done":done,"total_terms":total}),flush=True))
    if (sha(B_STATE)!=SAVED_STEP65_SHA or sha(SCRATCH)!=EXPECTED_STEP66_SHA
        or sha(COEFFICIENT)!=coeff_sha or sha(DIRECT)!=direct_sha):
        raise RuntimeError("Protected input changed")
    for p,digest in PROTECTED:
        if sha(p)!=digest:
            raise RuntimeError("Protected hash changed")
    print(TAG+json.dumps({"status":"B_STEP66_KEY_EXACT_FIELD_PASS_NOT_TARGET_PROOF",
       "index":index,"key":list(key),"method":"exact_QQ_z_d_fraction_field",
       "formal_state_modified":False,"certificate_checkpoint_modified":False,
       "target_b_proven":False}),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--index",type=int,default=113)
    ap.add_argument("--inspect",action="store_true")
    ap.add_argument("--worker",action="store_true",help=argparse.SUPPRESS)
    ap.add_argument("--timeout-seconds",type=int,default=3600)
    args=ap.parse_args()
    if not DIRECT_COUNT<=args.index<330:
        ap.error("Only normalized suffix keys are allowed")
    if args.inspect:
        print(TAG+json.dumps({"status":"B_STEP66_KEY_FIELD_INSPECTION_ONLY",
             **inspect(args.index)}),flush=True)
        return
    if args.worker:
        worker(args.index);return
    if not 30<=args.timeout_seconds<=3600:
        ap.error("Worker bound 30..3600 seconds")
    started=time.monotonic()
    cmd=[sys.executable,"-m",
         "examples.three_loop_vp05_sector202_target_b_key_rational_field_pilot",
         "--worker","--index",str(args.index)]
    try:
        r=subprocess.run(cmd,timeout=args.timeout_seconds,check=False)
    except subprocess.TimeoutExpired:
        print(TAG+json.dumps({"status":"B_STEP66_KEY_EXACT_FIELD_TIMEOUT_NOT_PROOF",
             "index":args.index,"seconds":args.timeout_seconds}),flush=True)
        return
    if r.returncode:
        raise SystemExit(r.returncode)
    print(TAG+json.dumps({"event":"PILOT_EXIT","index":args.index,
        "elapsed_seconds":round(time.monotonic()-started,2),
        "formal_state_modified":False}),flush=True)

if __name__=="__main__":
    main()
