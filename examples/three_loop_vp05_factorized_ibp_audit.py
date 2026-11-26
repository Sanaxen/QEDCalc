"""Audit factorized reducer against original symbolic IBP identities.

Only proper subsets of a verified independent three-line basis may be
classified as scaleless: in centered coordinates at least one loop has
no denominator and only polynomial numerator dependence. Other sectors
or out-of-envelope terms remain explicitly unresolved.
"""
import argparse
import collections
import functools
import hashlib
import json
import os
import time
from examples import three_loop_vp05_factorized as f

old=f.old
sp=f.sp
gap=f.gap
n=f.n
v=f.v
ROOT=n.BASE/"output"/"vp05_factorized_ibp06"
PILOT=f.ROOT/"pilot.json"
SHA="1802d41f5102473e20bec8c1863a590a664d961dde7db88fcd50f8372c09c6ac"
VERSION=1

def checksum(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def degrees(ex):
    return sum(-x for x in ex if x<0),sum(max(x-1,0) for x in ex)

def classify(ex,sec):
    target=gap.sector(ex)
    if target!=sec:
        return "scaleless_subset" if target&sec==target else "unsupported_sector"
    s,d=degrees(ex)
    return "factorized" if s<=f.MAX_DEGREE and d<=f.MAX_DOTS else "unsupported_envelope"

def audit_row(row,sec,reduce):
    # Exact symbolic coefficients only; no finite-field zero decisions.
    terms=[];unsupported=[];total=sp.S.Zero
    for ex,c in sorted(row.items()):
        kind=classify(ex,sec)
        if kind=="factorized":
            value=reduce(ex);total+=c*value
        elif kind=="scaleless_subset":
            value=sp.S.Zero
        else:
            unsupported.append(list(ex));value=None
        terms.append({"ex":list(ex),"ibp_coefficient":str(c),"classification":kind,
                      "reduction_coefficient":None if value is None else str(value)})
    residual=sp.cancel(total)
    status="UNSUPPORTED" if unsupported else "PASS" if residual==0 else "FAIL"
    return {"status":status,"terms":terms,"unsupported":unsupported,"known_residual":str(residual)}

def seeds(pilot,sec):
    # Reuse all actual pilot targets, then vary dot position and numerator
    # placement deterministically. No full shell enumeration.
    targets={tuple(r["target"]) for r in pilot["results"] if r["sector"]==sec}
    base=f.scalar(sec)
    pos=[i for i,a in enumerate(base) if a];neg=[i for i,a in enumerate(base) if not a]
    for i in pos:
        for j in neg:
            for s in (0,1,2,4):
                ex=list(base);ex[i]+=1;ex[j]-=s
                targets.add(tuple(ex))
    return sorted(targets)

def begin_seed(reducer):
    """Reset only the work counter, not the cached exact results or guards."""
    reducer.count=0
    reducer.guard()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hours",type=float,default=12)
    args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    deadline=time.monotonic()+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    started=time.monotonic()
    try:
        if (f.ROOT/"running.lock").exists():raise RuntimeError("Factorized pilot running")
        if n.sha(PILOT)!=SHA:raise RuntimeError("Pilot SHA")
        pilot=gap.read(PILOT)
        if pilot["status"]!="VP05_FACTORIZED_PILOT_NOT_CLOSURE" or len(pilot["results"])!=141 or len(pilot["maps"])!=3 or pilot["unsupported"]:raise RuntimeError("Pilot scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        path=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins={PILOT:SHA,path:n.sha(path),f.EVIDENCE:f.EVIDENCE_SHA}
        if f.a.CAND not in [gap.indices(x) for x in gap.read(path)["candidate_masters"]]:raise RuntimeError("Candidate missing")
        if any(n.sha(p)!=h for p,h in pins.items()):raise RuntimeError("Input SHA")
        spec=old.build_family_spec("VP05_full");kernel=old.build_kernel(spec.propagators)
        if old.digest(kernel)!=f.e.b.c.PIN:raise RuntimeError("Kernel mismatch")
        summaries=[]
        for sec in f.SECTORS:
            reducer=f.Reducer(spec.propagators,sec,deadline)
            if reducer.map not in pilot["maps"]:raise RuntimeError("Affine map mismatch")
            reduce=functools.lru_cache(maxsize=2048)(reducer.reduce)
            targets=seeds(pilot,sec);counts=collections.Counter();classes=collections.Counter()
            base_meta={"version":VERSION,"pilot_sha256":SHA,"kernel_sha256":f.e.b.c.PIN,"sector":sec}
            coverage=collections.Counter()
            run_contractions=0
            for i,ex in enumerate(targets):
                if time.monotonic()>=deadline:raise TimeoutError("Audit time budget; rerun resumes completed seed files")
                f.e.b.a.memory()
                dest=ROOT/f"sec{sec}_seed{i:04d}.json"
                meta={**base_meta,"seed":list(ex)}
                reused=dest.exists()
                if reused:
                    envelope=gap.read(dest);payload=envelope["payload"]
                    if checksum(payload)!=envelope["sha256"]:raise RuntimeError("Saved seed checksum")
                    if payload["meta"]!=meta or len(payload["rows"])!=15:raise RuntimeError("Saved seed scope")
                    # Replay saved coefficients and regenerated original rows,
                    # without expensive repeated tensor calculation.
                    saved=payload["rows"]
                    for (ij,entries),record in zip(sorted(kernel.items()),saved):
                        raw=f.e.m.q.exact_row(ex,entries,*ij)
                        coeffs={tuple(t["ex"]):sp.sympify(t["reduction_coefficient"],locals={"d":f.D,"z":f.Z}) for t in record["terms"] if t["classification"]=="factorized"}
                        replay=audit_row(raw,sec,lambda k:coeffs[k])
                        if record!={"derivative":list(ij),**replay}:raise RuntimeError("Saved row replay mismatch")
                else:
                    begin_seed(reducer)
                    rows=[]
                    for ij,entries in sorted(kernel.items()):
                        if time.monotonic()>=deadline:raise TimeoutError("Audit time budget")
                        raw=f.e.m.q.exact_row(ex,entries,*ij)
                        result=audit_row(raw,sec,reduce)
                        record={"derivative":list(ij),**result};rows.append(record)
                        if result["status"]=="FAIL":
                            v.log("VP05_FACTORIZED_IBP_FAIL",sector=sec,seed=list(ex),**record)
                            raise RuntimeError("Nonzero exact IBP residual")
                    run_contractions+=reducer.count
                    payload={"meta":meta,"rows":rows}
                    envelope={"payload":payload,"sha256":checksum(payload)}
                    old.atomic(dest,envelope)
                    if gap.read(dest)!=envelope:raise RuntimeError("Saved seed mismatch")
                for r in payload["rows"]:
                    if r["status"] not in ("PASS","UNSUPPORTED"):raise RuntimeError("Saved nonzero or unknown residual")
                    counts[r["status"]]+=1
                    classes.update(t["classification"] for t in r["terms"])
                    if r["status"]=="PASS":coverage[degrees(ex)]+=1
                v.log("VP05_FACTORIZED_IBP_SEED",sector=sec,index=i+1,expected=len(targets),seed=list(ex),counts=dict(counts),reused=reused,seed_contractions=0 if reused else reducer.count,run_contractions=run_contractions)
            summary={"sector":sec,"seeds":len(targets),"rows":sum(counts.values()),"counts":dict(counts),
                     "term_classes":dict(classes),"pass_degree_coverage":[[list(k),c] for k,c in sorted(coverage.items())]}
            summaries.append(summary);v.log("VP05_FACTORIZED_IBP_SECTOR",**summary,run_contractions=run_contractions)
            reduce.cache_clear();reducer.close()
        if any(n.sha(p)!=h for p,h in pins.items()):raise RuntimeError("Protected input changed")
        # Pin all per-seed evidence, reject extra seed files.
        files=sorted(ROOT.glob("sec*_seed*.json"))
        if len(files)!=sum(r["seeds"] for r in summaries):raise RuntimeError("Evidence file count")
        payload={"status":"VP05_FACTORIZED_IBP_AUDIT_NOT_CLOSURE","inputs":{str(p):h for p,h in pins.items()},"summaries":summaries,
                 "seed_sha256":{p.name:n.sha(p) for p in files},"full_closure_proven":False,"recursive_parent_reduction_proven":False}
        dest=ROOT/"audit.json"
        if dest.exists():
            if gap.read(dest)!=payload:raise RuntimeError("Existing audit differs")
        else:old.atomic(dest,payload)
        v.log("VP05_FACTORIZED_IBP_AUDIT_NOT_CLOSURE",rows=sum(r["rows"] for r in summaries),
              passed=sum(r["counts"].get("PASS",0) for r in summaries),
              unsupported=sum(r["counts"].get("UNSUPPORTED",0) for r in summaries),
              failed=0,sha256=n.sha(dest),elapsed_s=time.monotonic()-started,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
