"""Step66 exact normalized original-IBP replay for remaining keys 113..329.

The prior 113 direct exact certificates and 259 independent exact coefficient
certificates establish the complete local Step65->66 update. For each remaining
key prove the UNSCALED source-pivot identity against ORIGINAL gzipped IBP
equations (no sampling or modular substitutions). Preserve both prior
checkpoints; write only a distinct resume-safe normalized audit file.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
import time
import sympy as sp
from sympy.polys.fields import field
from sympy.polys.domains import QQ
from examples.three_loop_vp05_sector202_target_b_step66_original_ibp_replay import (
    prepare, AUDIT as DIRECT, STATUS as DIRECT_STATUS, context_config,
    EXPECTED_STEP66_SHA, SAVED_STEP65_SHA, B_STATE, SCRATCH, PROTECTED,
    SOURCE, CHECKPOINT, CERT, BASE, sha,
)
from examples.three_loop_vp05_sector202_target_b_step66_coefficient_audit import (
    OUT as COEFFICIENT, STATUS as COEFF_STATUS, context as coefficient_context,
)
from examples.three_loop_vp05_sector202_exact_prefix_smoke import expr
from examples.three_loop_vp05_sector202_step51_scratch import atomic_save

TAG="VP05_B_STEP66_NORMALIZED_IBP_REPLAY "
OUT=BASE/"vp05_sector202_B_step66_normalized_original_ibp_replay_checkpoint.json"
STATUS="B_STEP66_NORMALIZED_ORIGINAL_IBP_PREFIX_NOT_PROOF"
DIRECT_COUNT=113
TOTAL_KEYS=330
METHOD="unscaled_QQ_z_d_rational_field_with_259_exact_coefficients"

def check_certificate_prefix(rows,jobs,allowed_method):
    if not isinstance(rows,list) or len(rows)>len(jobs):
        raise RuntimeError("Invalid certificate list length")
    for index,item in enumerate(rows):
        if (not isinstance(item,dict) or item.get("index")!=index
            or item.get("key")!=list(jobs[index])
            or item.get("method")!=allowed_method):
            raise RuntimeError("Unbound exact certificate at "+str(index))
    return True

def load():
    oldrem,newrem,oldsrc,newsrc,originals,jobs=prepare()
    if len(jobs)!=TOTAL_KEYS:
        raise RuntimeError("Unexpected integral key count")
    c_oldrem,c_newrem,c_oldsrc,c_newsrc,pivotrow,pivottrace,cjobs=coefficient_context()
    if (c_oldrem!=oldrem or c_newrem!=newrem
        or c_oldsrc!=oldsrc or c_newsrc!=newsrc
        or len(cjobs)!=259):
        raise RuntimeError("Coefficient context incompatible with Step66 state")
    coeff_sha=sha(COEFFICIENT)
    audit=json.loads(COEFFICIENT.read_text(encoding="utf-8-sig"))
    cfg=audit.get("config",{})
    expected_jobs=[[kind,list(key) if kind=="remainder" else key] for kind,key in cjobs]
    expected_jobs_sha=hashlib.sha256(
        json.dumps(expected_jobs,separators=(",",":")).encode()
    ).hexdigest()
    rows=audit.get("checked",[])
    if (audit.get("version")!=1 or audit.get("status")!=COEFF_STATUS
        or audit.get("target_b_proven") is not False
        or audit.get("formal_state_modified") is not False
        or cfg.get("version")!=1
        or cfg.get("step65_sha256")!=SAVED_STEP65_SHA
        or cfg.get("scratch_step66_sha256")!=EXPECTED_STEP66_SHA
        or cfg.get("source_checkpoint_sha256")!=sha(CHECKPOINT)
        or cfg.get("original_source_sha256")!=sha(SOURCE)
        or cfg.get("certificate_sha256")!=sha(CERT)
        or cfg.get("jobs_count")!=len(cjobs)
        or cfg.get("jobs_sha256")!=expected_jobs_sha
        or not isinstance(rows,list) or len(rows)!=len(cjobs)):
        raise RuntimeError("259 independent exact coefficient certificates incomplete")
    for i,(row,(kind,key)) in enumerate(zip(rows,cjobs)):
        if (row.get("index")!=i or row.get("kind")!=kind
            or row.get("key")!=(list(key) if kind=="remainder" else key)
            or row.get("method")!="exact_step66_local_update"):
            raise RuntimeError("Coefficient certificate mismatch at "+str(i))
    direct_sha=sha(DIRECT)
    direct=json.loads(DIRECT.read_text(encoding="utf-8-sig"))
    if (direct.get("version")!=1 or direct.get("status")!=DIRECT_STATUS
        or direct.get("config")!=context_config(jobs)
        or direct.get("formal_state_modified") is not False
        or direct.get("target_b_proven") is not False
        or direct.get("original_ibp_exact_replay_verified") is not False
        or len(direct.get("checked",[]))!=DIRECT_COUNT):
        raise RuntimeError("Expected 113 saved direct exact keys")
    check_certificate_prefix(direct["checked"],jobs,"original_source_delta_exact")
    checkpoint=json.loads(CHECKPOINT.read_text(encoding="utf-8-sig"))
    lead=min(oldrem)
    matches=[row for row in checkpoint["pivots"] if tuple(row["lead"])==lead]
    if len(matches)!=1 or lead!=(166596414013440,139):
        raise RuntimeError("Expected unique Step66 pivot")
    pivot=matches[0]
    trace={int(k):v for k,v in pivot["trace"]}
    prow={tuple(k):v for k,v in pivot["row"]}
    if (len(trace)!=len(pivot["trace"]) or len(prow)!=len(pivot["row"])
        or trace!={k:v for k,v in pivottrace.items()}
        or prow!={k:v for k,v in pivotrow.items()}
        or not set(trace).issubset(originals)):
        raise RuntimeError("Pivot source trace incompatible with original IBP rows")
    key_terms={}
    for rid,weight in trace.items():
        for t in originals[rid]["terms"]:
            k=tuple(t["key"])
            key_terms.setdefault(k,[]).append((weight,t["coefficient"]))
    if not (set(prow)|set(key_terms)).issubset(set(jobs)):
        raise RuntimeError("Original pivot contains unexpected integral keys")
    return jobs,prow,key_terms,coeff_sha,direct_sha

def verify_unscaled_key(key,prow,key_terms):
    z,d=sp.symbols("z d")
    parts=[expr(weight,z,d)*expr(coefficient,z,d)
           for weight,coefficient in key_terms.get(key,[])]
    value=sp.cancel(expr(prow.get(key,"0"),z,d)-sp.Add(*parts))
    if value!=0:
        raise AssertionError("Step66 unscaled original-IBP pivot mismatch "+str(key))
    return True

def verify_unscaled_key_field(key, prow, key_terms):
    """Exact unsampled fraction-field replay; avoids SymPy.cancel(huge Add).

    Mirrors the independently PASSed key113 rational-field pilot. Do not
    fall back to modular checks on a worker failure.
    """
    ring,z,d=field("z,d",QQ)
    zs,ds=sp.symbols("z d")
    def to_field(raw):
        return ring.from_expr(expr(raw,zs,ds))
    total=ring.zero
    for weight,coefficient in key_terms.get(key,[]):
        total+=to_field(weight)*to_field(coefficient)
    if to_field(prow.get(key,"0"))-total!=ring.zero:
        raise AssertionError("Step66 exact QQ(z,d) original IBP mismatch "+str(key))
    return True

def worker(index):
    jobs,prow,key_terms,coeff_sha,direct_sha=load()
    if not DIRECT_COUNT<=index<len(jobs):
        raise RuntimeError("Index not in normalized suffix")
    key=jobs[index]
    verify_unscaled_key_field(key,prow,key_terms)
    if (sha(B_STATE)!=SAVED_STEP65_SHA or sha(SCRATCH)!=EXPECTED_STEP66_SHA
        or sha(COEFFICIENT)!=coeff_sha or sha(DIRECT)!=direct_sha):
        raise RuntimeError("Protected exact certificates changed during worker")
    print(TAG+json.dumps({"event":"EXACT_UNSCALED_ORIGINAL_IBP_KEY_PASS",
           "index":index,"key":list(key),
           "method":METHOD,"coefficient_audit_sha256":coeff_sha,
           "direct_replay_sha256":direct_sha}),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worker-index",type=int,default=None,help=argparse.SUPPRESS)
    ap.add_argument("--check-only",action="store_true")
    ap.add_argument("--resume",action="store_true")
    ap.add_argument("--hours",type=float,default=12)
    ap.add_argument("--timeout-seconds",type=int,default=1200)
    ap.add_argument("--max-new",type=int,default=217)
    args=ap.parse_args()
    if args.worker_index is not None:
        worker(args.worker_index);return
    if not 0<args.hours<=12 or not 30<=args.timeout_seconds<=3600 or not 1<=args.max_new<=217:
        ap.error("Safety bounds exceeded")
    jobs,prow,key_terms,coeff_sha,direct_sha=load()
    protected=[p for p,_ in PROTECTED]+[SCRATCH,COEFFICIENT,DIRECT]
    if len(set(p.resolve() for p in protected+[OUT]))!=len(protected)+1:
        raise RuntimeError("Normalized audit path aliases protected state")
    config={"version":1,"formal_step65_sha256":SAVED_STEP65_SHA,
        "scratch_step66_sha256":EXPECTED_STEP66_SHA,
        "original_source_sha256":sha(SOURCE),
        "source_checkpoint_sha256":sha(CHECKPOINT),
        "certificate_sha256":sha(CERT),
        "coefficient_audit_sha256":coeff_sha,
        "direct_replay_sha256":direct_sha,
        "direct_verified":DIRECT_COUNT,
        "normalized_needed":len(jobs)-DIRECT_COUNT,
        "jobs_sha256":hashlib.sha256(
            json.dumps([list(k) for k in jobs],separators=(",",":")).encode()
        ).hexdigest()}
    if OUT.exists()!=args.resume:
        raise RuntimeError("Normalized checkpoint exists: use --resume, or omit it for new run")
    if args.resume:
        state=json.loads(OUT.read_text(encoding="utf-8-sig"))
        checked=state.get("checked",[])
        if (state.get("version")!=1 or state.get("status")!=STATUS
            or state.get("config")!=config
            or state.get("formal_state_modified") is not False
            or state.get("target_b_proven") is not False
            or not isinstance(checked,list) or len(checked)>len(jobs)-DIRECT_COUNT
            or any(r.get("index")!=DIRECT_COUNT+i
                   or r.get("key")!=list(jobs[DIRECT_COUNT+i])
                   or r.get("method")!=METHOD for i,r in enumerate(checked))):
            raise RuntimeError("Invalid normalized saved exact certificate prefix")
    else:
        state={"version":1,"status":STATUS,"config":config,"checked":[],
            "formal_state_modified":False,
            "original_ibp_exact_replay_verified":False,
            "target_b_proven":False}
    print(TAG+json.dumps({"status":"B_STEP66_NORMALIZED_PREFLIGHT_PASS_NOT_PROOF",
        "direct_keys_verified":DIRECT_COUNT,"normalized_keys_verified":len(state["checked"]),
        "total_keys":len(jobs),"formal_state_unchanged":True}),flush=True)
    if args.check_only:return
    if not args.resume:atomic_save(OUT,state,False)
    started=time.monotonic();new=0
    while len(state["checked"])<len(jobs)-DIRECT_COUNT and new<args.max_new:
        if time.monotonic()-started+args.timeout_seconds+30>args.hours*3600:
            break
        index=DIRECT_COUNT+len(state["checked"])
        try:
            r=subprocess.run([sys.executable,"-m",
                "examples.three_loop_vp05_sector202_target_b_step66_normalized_ibp_replay",
                "--worker-index",str(index)],capture_output=True,text=True,
                timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            print(TAG+json.dumps({"event":"WORKER_TIMEOUT_NOT_PROOF","index":index}),flush=True)
            break
        if r.returncode:
            print(TAG+json.dumps({"event":"WORKER_ERROR_NOT_PROOF",
                "index":index,"stderr_tail":r.stderr[-2000:]}),flush=True)
            break
        if TAG not in r.stdout:raise RuntimeError("Missing exact normalized PASS")
        result=json.loads(r.stdout.split(TAG,1)[1].strip())
        if (result.get("event")!="EXACT_UNSCALED_ORIGINAL_IBP_KEY_PASS"
            or result.get("index")!=index or result.get("key")!=list(jobs[index])
            or result.get("method")!=METHOD
            or result.get("coefficient_audit_sha256")!=coeff_sha
            or result.get("direct_replay_sha256")!=direct_sha):
            raise RuntimeError("Invalid normalized exact worker certificate")
        state["checked"].append({"index":index,"key":list(jobs[index]),"method":METHOD})
        atomic_save(OUT,state,True)
        new+=1
        print(TAG+json.dumps({"event":"EXACT_NORMALIZED_KEY_SAVED",
            "checked":DIRECT_COUNT+len(state["checked"]),
            "total":len(jobs),"elapsed_seconds":round(time.monotonic()-started,2)}),flush=True)
    for p,digest in PROTECTED:
        if sha(p)!=digest:raise RuntimeError("Protected state changed")
    if (sha(SCRATCH)!=EXPECTED_STEP66_SHA or sha(COEFFICIENT)!=coeff_sha
        or sha(DIRECT)!=direct_sha):
        raise RuntimeError("Protected certificates changed")
    complete=len(state["checked"])==len(jobs)-DIRECT_COUNT
    print(TAG+json.dumps({
        "status":"B_STEP66_ALL_330_COMBINED_ORIGINAL_IBP_KEYS_EXACT_PASS_NOT_TARGET_PROOF"
                 if complete else STATUS,
        "verified_direct":DIRECT_COUNT,"verified_normalized":len(state["checked"]),
        "total_verified":DIRECT_COUNT+len(state["checked"]),"total_keys":len(jobs),
        "original_ibp_exact_replay_verified":complete,
        "formal_state_modified":False,"target_b_proven":False}),flush=True)

if __name__=="__main__":
    main()
