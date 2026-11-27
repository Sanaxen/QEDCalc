"""Bounded cumulative parent frontier experiment; diagnostic targets, not closure.

Use exact original rows, analytic substitution and two modular echelon bases.
Each round adds rows at unresolved remainder seeds, never discards unknowns.
Checkpoints store ordered seed schedules and results; replay from original
rows on resume. No claim of completeness of seed selection.
"""
import argparse
import collections
import functools
import os
import time
from examples import three_loop_vp05_parent_substitution as p

a=p.a;f=p.f;old=p.old;sp=p.sp;gap=p.gap;n=p.n;v=p.v;q=p.q
ROOT=n.BASE/"output"/"vp05_parent_frontier08"
SOURCE=p.ROOT/"summary.json"
SHA="140c4b3a1df5b6fdf37c9f1adbff275b175b9e75b1d3b5106019ed8c2a659d20"
JOBS=(("r8s6d2",204),("r8s6d2",228),("r8s5d3",71),("r8s5d3",77))
MAX_ROUNDS=6
BATCH=24
TARGET_CAP=16

def limits(seed):
    return (8,6,2) if seed=="r8s6d2" else (8,5,3)

def order(ex):
    return (sum(x>0 for x in ex),sum(max(x,0) for x in ex),sum(-x for x in ex if x<0),ex)

def select_targets(rows,sec,candidates,seed):
    # Prefer actual same-sector, noncandidate low-complexity integrals.
    keys={k for row in rows for k in row if gap.sector(k)==sec and k not in candidates and q.scope(k,*limits(seed))}
    return sorted(keys,key=order)[:TARGET_CAP]

def frontier(checks,seen,sec,seed,candidates):
    counts=collections.Counter()
    for check in checks:
        for result in check["targets"]:
            for ex,c in result["remainder"]:
                k=tuple(ex)
                if c and k not in seen and k not in candidates and gap.sector(k)&sec==gap.sector(k) and q.scope(k,*limits(seed)):
                    # Analytic sectors should not generate new IBP seed work.
                    mask=gap.sector(k)
                    if mask in f.SECTORS or any(mask!=s and mask&s==mask for s in f.SECTORS):continue
                    counts[k]+=1
    return sorted(counts,key=lambda k:(-counts[k],order(k)))[:BATCH]

def pair_results(engines,targets):
    result=[]
    for engine,point in zip(engines,old.POINTS):
        rows=[engine.target(ex) for ex in targets]
        result.append({"point":list(point),"targets":rows,"candidate_only_targets":sum(r["candidate_only"] for r in rows),
                       "pivot_rank":len(engine.piv),"pivot_terms":engine.terms,"operations":engine.ops,
                       "candidate_only_relations":engine.candidate_relations})
    return result

def run_job(seed,sec,initial,targets,kernel,candidates,reduce,deadline,pins):
    if not targets:raise RuntimeError("Vacuous diagnostic target set")
    engines=[p.Echelon(pt[0],candidates,deadline) for pt in old.POINTS]
    seen=set();schedule=list(initial);summaries=[]
    raw_cols=set();after_cols=set();raw_terms=after_terms=0;blocked=set();used=set()
    metadata={"version":1,"source_sha256":SHA,"manifest_sha256":pins["manifest"],"kernel_sha256":f.e.b.c.PIN,
              "seed":seed,"sector":sec,"targets":[list(x) for x in targets],"batch":BATCH}
    for round_id in range(MAX_ROUNDS):
        if not schedule:break
        dest=ROOT/f"{seed}_sec{sec}_round{round_id}.json"
        # Rebuild cumulative pivots deterministically from original rows.
        # Completed round files are immutable; recompute and compare on resume.
        records=[]
        for ex in schedule:
            if ex in seen:raise RuntimeError("Duplicate seed")
            if time.monotonic()>=deadline:raise TimeoutError("Frontier time budget")
            f.e.b.a.memory();seen.add(ex)
            for ij,entries in sorted(kernel.items()):
                raw=q.exact_row(ex,entries,*ij)
                sub,u,b=p.substitute(raw,reduce)
                raw_cols.update(raw);after_cols.update(sub);raw_terms+=len(raw);after_terms+=len(sub)
                blocked.update(b);used.update(u)
                for engine,point in zip(engines,old.POINTS):engine.insert(p.field_row(sub,point))
                records.append({"seed":list(ex),"derivative":list(ij),"raw":p.encode(raw),"substituted":p.encode(sub),
                                "analytic_coefficients":p.encode(u),"blocked":[list(k) for k in sorted(b)]})
        checks=pair_results(engines,targets)
        both=sum(x["candidate_only"] and y["candidate_only"] for x,y in zip(checks[0]["targets"],checks[1]["targets"]))
        support_matches=sum([k for k,c in x["remainder"]]==[k for k,c in y["remainder"]] for x,y in zip(checks[0]["targets"],checks[1]["targets"]))
        next_seeds=[] if both==len(targets) else frontier(checks,seen,sec,seed,candidates)
        stats={"round":round_id,"seeds":len(seen),"rows":15*len(seen),"targets":len(targets),
               "columns_before":len(raw_cols),"columns_after":len(after_cols),"terms_before":raw_terms,"terms_after":after_terms,
               "analytic_targets":len(used),"blocked_targets":len(blocked),"both_points_candidate_only":both,
               "support_matches":support_matches,"next_seeds":len(next_seeds)}
        payload={"meta":metadata,"stats":stats,"schedule":[list(k) for k in schedule],"rows":records,
                 "checks":checks,"next_schedule":[list(k) for k in next_seeds],"full_closure_proven":False}
        if dest.exists():
            if gap.read(dest)!=payload:raise RuntimeError("Round replay mismatch")
        else:old.atomic(dest,payload)
        if gap.read(dest)!=payload:raise RuntimeError("Round save mismatch")
        summaries.append({**stats,"sha256":n.sha(dest)})
        v.log("VP05_PARENT_FRONTIER_ROUND",seed=seed,sector=sec,**stats)
        schedule=next_seeds
    return {"seed":seed,"sector":sec,"diagnostic_targets":[list(k) for k in targets],"rounds":summaries,
            "remaining_schedule":[list(k) for k in schedule],"full_closure_proven":False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (p.ROOT,a.ROOT,f.ROOT,f.a.ROOT,f.e.ROOT,q.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={SOURCE:SHA,p.AUDIT:p.AUDIT_SHA,a.PILOT:a.SHA,f.EVIDENCE:f.EVIDENCE_SHA,f.e.m.SOURCE:f.e.m.SHA}
        if any(n.sha(k)!=h for k,h in pins.items()):raise RuntimeError("Evidence SHA")
        summary=gap.read(SOURCE);pilot=gap.read(a.PILOT)
        if summary["status"]!="VP05_PARENT_SUBSTITUTION_NOT_CLOSURE" or len(summary["jobs"])!=21:raise RuntimeError("Parent pilot scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        path=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[path]=n.sha(path);manifest=gap.read(path)
        candidates=set(gap.indices(x) for x in manifest["candidate_masters"])
        if len(candidates)!=63 or f.a.CAND not in candidates:raise RuntimeError("Candidate scope")
        spec=old.build_family_spec("VP05_full");kernel=old.build_kernel(spec.propagators)
        if old.digest(kernel)!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        reducers={sec:f.Reducer(spec.propagators,sec,deadline) for sec in f.SECTORS}
        if any(r.map not in pilot["maps"] for r in reducers.values()):raise RuntimeError("Affine map")
        @functools.lru_cache(maxsize=4096)
        def reduce(ex):
            r=reducers[gap.sector(ex)];a.begin_seed(r);return r.reduce(ex)
        potential=gap.read(f.e.m.SOURCE)["potential"]
        results=[]
        for seed,sec in JOBS:
            initial=set();raw=[]
            if sec in (204,228):
                item=next(x for x in summary["jobs"] if x["seed"]==seed and x["sector"]==sec)
                src=p.ROOT/f"{seed}_sec{sec}.json";pins[src]=item["sha256"]
                if n.sha(src)!=pins[src]:raise RuntimeError("Parent job SHA")
                job=gap.read(src)
                for record in job["rows"]:
                    ex=tuple(record["seed"]);ij=tuple(record["derivative"])
                    original=q.exact_row(ex,kernel[ij],*ij)
                    if p.encode(original)!=record["raw"]:raise RuntimeError("Original row mismatch")
                    initial.add(ex);raw.append(original)
            else:
                # Actual first-source seeds from earlier partial envelope.
                # Stratify by (numerator degree, dots), low complexity first.
                reps={}
                for ex,info in potential:
                    src=info["first_source"]
                    if src.get("seed")!=seed or src.get("intermediate")!=sec:continue
                    k=tuple(src["ex"]);ij=tuple(src["derivative"])
                    if not q.scope(k,*limits(seed)):continue
                    bucket=a.degrees(k)
                    if bucket not in reps:reps[bucket]=(k,ij,tuple(ex))
                for k,ij,ex in sorted(reps.values(),key=lambda item:order(item[0]))[:BATCH]:
                    original=q.exact_row(k,kernel[ij],*ij)
                    if ex not in original:raise RuntimeError("Potential provenance mismatch")
                    initial.add(k)
                    for deriv,entries in kernel.items():raw.append(q.exact_row(k,entries,*deriv))
            targets=select_targets(raw,sec,candidates,seed)
            v.log("VP05_PARENT_FRONTIER_SCOPE",seed=seed,sector=sec,initial_seeds=len(initial),diagnostic_targets=len(targets))
            results.append(run_job(seed,sec,sorted(initial,key=order),targets,kernel,candidates,reduce,deadline,{"manifest":pins[path]}))
        if any(n.sha(k)!=h for k,h in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_PARENT_FRONTIER_NOT_CLOSURE","inputs":{str(k):h for k,h in pins.items()},"jobs":results,
                 "diagnostic_only":True,"generic_rational_target_proof":False,"full_closure_proven":False}
        dest=ROOT/"summary.json"
        if dest.exists():
            if gap.read(dest)!=payload:raise RuntimeError("Summary mismatch")
        else:old.atomic(dest,payload)
        v.log("VP05_PARENT_FRONTIER_NOT_CLOSURE",jobs=len(results),targets=sum(len(r["diagnostic_targets"]) for r in results),
              candidate_only_both=sum(r["rounds"][-1]["both_points_candidate_only"] for r in results),
              sha256=n.sha(dest),elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
