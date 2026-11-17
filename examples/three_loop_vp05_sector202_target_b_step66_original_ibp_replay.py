"""Exact, isolated Step65->66 original-IBP delta replay. Never promotes B.

For every integral key, verify symbolically:
    old_remaining - new_remaining == sum((new_source-old_source)*original_IBP).
This checks the complete step transition against ORIGINAL rows rather than a
checkpoint pivot alone. Each key runs in its own bounded worker process.
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

from examples.three_loop_vp05_sector202_target_b_scratch_from65 import (
    validate, validate_scratch, SCRATCH, B_STATE, PROTECTED, SAVED_STEP65_SHA,
)
from examples.three_loop_vp05_sector202_target_exact_reduction import (
    BASE, SOURCE, CHECKPOINT, CERT, sha,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_step51_scratch import atomic_save

EXPECTED_STEP66_SHA = "9b30bed319c5e23cc84016acdb1605fe8082bedb09c84a4f8f4d8f676de82d7d"
AUDIT = BASE / "vp05_sector202_B_step66_original_ibp_exact_replay_checkpoint.json"
TAG = "VP05_B_STEP66_ORIGINAL_IBP_REPLAY "
STATUS = "B_STEP66_ORIGINAL_IBP_PREFIX_NOT_PROOF"

def rows_dict(items, integral):
    out = {}
    for k,v in items:
        key = tuple(k) if integral else int(k)
        if key in out or not isinstance(v,str) or not v:
            raise RuntimeError("Duplicate or invalid saved coefficient")
        out[key]=v
    return out

def prepare():
    old=validate()
    if sha(B_STATE)!=SAVED_STEP65_SHA or sha(SCRATCH)!=EXPECTED_STEP66_SHA:
        raise RuntimeError("Formal Step65 or Step66 scratch SHA mismatch")
    new=json.loads(SCRATCH.read_text(encoding="utf-8-sig"))
    validate_scratch(old,new)
    if (new.get("steps")!=66 or len(new["pivot_path"])!=66
        or new["pivot_path"][:65]!=old["pivot_path"]
        or new["pivot_path"][65]!=old["metrics"]["lead"]
        or len(new["remaining"])!=75 or len(new["source"])!=153
        or new["metrics"].get("max_expression_chars")!=5707
        or new["metrics"].get("lead")!=[166596414013441,139]
        or new.get("exact_target_proven") is not False
        or new.get("original_source_replay_proven") is not False):
        raise RuntimeError("Step66 scratch transition metadata mismatch")
    orem=rows_dict(old["remaining"],True)
    nrem=rows_dict(new["remaining"],True)
    osrc=rows_dict(old["source"],False)
    nsrc=rows_dict(new["source"],False)
    if len(orem)!=85 or len(osrc)!=173:
        raise RuntimeError("Step65 dimensions mismatch")
    changed=sorted(set(osrc)|set(nsrc))
    with gzip.open(SOURCE,"rt",encoding="utf-8") as f:
        original=json.load(f)
    originals={int(r["global_zero_based"]):r for r in original["rows"]}
    if len(originals)!=len(original["rows"]) or not set(changed).issubset(originals):
        raise RuntimeError("Missing original IBP source row")
    keys=set(orem)|set(nrem)
    for rid in changed:
        keys.update(tuple(t["key"]) for t in originals[rid]["terms"])
    return orem,nrem,osrc,nsrc,originals,sorted(keys)

def verify_key(key,oldrem,newrem,oldsrc,newsrc,originals):
    z,d=sp.symbols("z d")
    terms=[expr(oldrem.get(key,"0"),z,d),-expr(newrem.get(key,"0"),z,d)]
    for rid in sorted(set(oldsrc)|set(newsrc)):
        original_coeff=[term["coefficient"] for term in originals[rid]["terms"]
                        if tuple(term["key"])==key]
        if original_coeff:
            delta=sp.cancel(expr(newsrc.get(rid,"0"),z,d)-
                            expr(oldsrc.get(rid,"0"),z,d))
            if delta!=0:
                for val in original_coeff:
                    terms.append(-delta*expr(val,z,d))
    result=sp.cancel(sp.Add(*terms))
    if result!=0:
        raise AssertionError("Exact original-IBP Step66 delta mismatch: "+str(key))
    return True

def context_config(jobs):
    return {"version":1,"formal_step65_sha256":SAVED_STEP65_SHA,
            "scratch_step66_sha256":EXPECTED_STEP66_SHA,
            "original_source_sha256":sha(SOURCE),
            "source_checkpoint_sha256":sha(CHECKPOINT),
            "certificate_sha256":sha(CERT),
            "job_count":len(jobs),
            "job_keys_sha256":hashlib.sha256(
                json.dumps([list(k) for k in jobs],separators=(",",":")).encode()
            ).hexdigest()}

def worker(index):
    oldrem,newrem,oldsrc,newsrc,originals,jobs=prepare()
    if not 0<=index<len(jobs):
        raise RuntimeError("Invalid worker index")
    key=jobs[index]
    verify_key(key,oldrem,newrem,oldsrc,newsrc,originals)
    if sha(B_STATE)!=SAVED_STEP65_SHA or sha(SCRATCH)!=EXPECTED_STEP66_SHA:
        raise RuntimeError("Protected B state changed during worker")
    print(TAG+json.dumps({"event":"EXACT_ORIGINAL_IBP_KEY_PASS",
                          "index":index,"key":list(key),
                          "scratch_sha256":EXPECTED_STEP66_SHA}),flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--worker-index",type=int,default=None,help=argparse.SUPPRESS)
    p.add_argument("--hours",type=float,default=12)
    p.add_argument("--timeout-seconds",type=int,default=1200)
    p.add_argument("--max-new",type=int,default=500)
    p.add_argument("--resume",action="store_true")
    p.add_argument("--check-only",action="store_true")
    args=p.parse_args()
    if args.worker_index is not None:
        worker(args.worker_index)
        return
    if not 0<args.hours<=12 or not 30<=args.timeout_seconds<=3600 or not 1<=args.max_new<=2000:
        p.error("Safety limits exceeded")
    _,_,_,_,_,jobs=prepare()
    config=context_config(jobs)
    paths=[p.resolve() for p,_ in PROTECTED]+[SCRATCH.resolve(),AUDIT.resolve()]
    if len(paths)!=len(set(paths)):
        raise RuntimeError("Audit path overlaps protected file")
    if AUDIT.exists()!=args.resume:
        raise RuntimeError("Audit exists: use --resume; otherwise omit --resume")
    if args.resume:
        checkpoint=json.loads(AUDIT.read_text(encoding="utf-8-sig"))
        verified=checkpoint.get("checked",[])
        if (checkpoint.get("config")!=config or checkpoint.get("status")!=STATUS
            or checkpoint.get("formal_state_modified") is not False
            or checkpoint.get("target_b_proven") is not False
            or not isinstance(verified,list) or len(verified)>len(jobs)
            or any(x.get("index")!=i or x.get("key")!=list(jobs[i])
                   for i,x in enumerate(verified))):
            raise RuntimeError("Invalid saved replay prefix")
    else:
        checkpoint={"version":1,"status":STATUS,"config":config,"checked":[],
                    "original_ibp_exact_replay_verified":False,
                    "formal_state_modified":False,"target_b_proven":False}
    print(TAG+json.dumps({"status":"B_STEP66_ORIGINAL_IBP_PREFLIGHT_PASS_NOT_PROOF",
                          "total_keys":len(jobs),
                          "verified_keys":len(checkpoint["checked"]),
                          "formal_state_unchanged":True}),flush=True)
    if args.check_only:
        return
    if not args.resume:
        atomic_save(AUDIT,checkpoint,False)
    t0=time.monotonic()
    newly=0
    while len(checkpoint["checked"])<len(jobs) and newly<args.max_new:
        if time.monotonic()-t0+args.timeout_seconds+30>args.hours*3600:
            break
        i=len(checkpoint["checked"])
        try:
            run=subprocess.run([sys.executable,"-m",
                "examples.three_loop_vp05_sector202_target_b_step66_original_ibp_replay",
                "--worker-index",str(i)],text=True,capture_output=True,
                timeout=args.timeout_seconds,check=False)
        except subprocess.TimeoutExpired:
            print(TAG+json.dumps({"event":"WORKER_TIMEOUT_NOT_PROOF","index":i}),flush=True)
            break
        if run.returncode:
            print(TAG+json.dumps({"event":"WORKER_ERROR_NOT_PROOF","index":i,
                                  "stderr_tail":run.stderr[-2500:]}),flush=True)
            break
        marker=TAG
        if marker not in run.stdout:
            raise RuntimeError("Worker did not emit exact PASS")
        result=json.loads(run.stdout.split(marker,1)[1].strip())
        if (result.get("event")!="EXACT_ORIGINAL_IBP_KEY_PASS"
            or result.get("index")!=i or result.get("key")!=list(jobs[i])
            or result.get("scratch_sha256")!=EXPECTED_STEP66_SHA):
            raise RuntimeError("Unbound Step66 original-IBP certificate")
        checkpoint["checked"].append({"index":i,"key":list(jobs[i]),
                                      "method":"original_source_delta_exact"})
        atomic_save(AUDIT,checkpoint,True)
        newly+=1
        print(TAG+json.dumps({"event":"EXACT_IBP_KEY_SAVED",
                              "checked":len(checkpoint["checked"]),
                              "total_keys":len(jobs),
                              "elapsed_seconds":round(time.monotonic()-t0,2)}),flush=True)
    for source,digest in PROTECTED:
        if sha(source)!=digest:
            raise RuntimeError("Protected artifact changed")
    if sha(SCRATCH)!=EXPECTED_STEP66_SHA:
        raise RuntimeError("Step66 scratch changed")
    complete=len(checkpoint["checked"])==len(jobs)
    print(TAG+json.dumps({"status":"B_STEP66_ALL_ORIGINAL_IBP_KEYS_EXACT_PASS_NOT_TARGET_PROOF"
                          if complete else STATUS,
                          "verified_keys":len(checkpoint["checked"]),
                          "total_keys":len(jobs),
                          "formal_state_modified":False,
                          "original_ibp_exact_replay_verified":complete,
                          "target_b_proven":False}),flush=True)

if __name__=="__main__":
    main()
