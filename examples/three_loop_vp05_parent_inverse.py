"""Inverse IBP seed search for the unresolved parent frontier.

Original seed candidates are derived by inverting the actual kernel shifts.
Rank newly generated rows by whether they constrain the current residual
space after eliminating existing pivots; do not merely count occurrences.
Finite-field diagnostic, not a generic rational proof.
"""
import argparse
import collections
import functools
import os
import time
from examples import three_loop_vp05_parent_frontier as h

p=h.p;f=h.f;a=h.a;q=h.q;old=h.old;sp=h.sp;gap=h.gap;n=h.n;v=h.v
ROOT=n.BASE/"output"/"vp05_parent_inverse09"
SOURCE=h.ROOT/"summary.json"
SHA="9c9d851695b1f8520a40f230a8aab020eea54b145b2786f7832b76c8f12ff5f7"
MAX_ROUNDS=6
MAX_RESIDUALS=24
MAX_PROBES=192
BATCH=24

def residuals(checks,candidates):
    count=collections.Counter()
    for check in checks:
        for result in check["targets"]:
            for ex,c in result["remainder"]:
                k=tuple(ex)
                if c and k not in candidates:count[k]+=1
    return count

def exclusion(k,seen,sec,seed):
    mask=gap.sector(k)
    if mask&sec!=mask:return "outside_parent"
    if mask in f.SECTORS or any(mask!=s and mask&s==mask for s in f.SECTORS):return "analytic_or_zero"
    if not q.scope(k,*h.limits(seed)):return "outside_seed_envelope"
    if k in seen:return "already_seeded"
    return "unseeded_in_scope"

def inverse_seeds(target,kernel):
    # IBP shifts: 0, +e_h, +e_h-e_k. Invert each nonzero kernel term.
    # a_h=0 cannot contribute. Cancellation checked by exact row regeneration.
    out=collections.defaultdict(set)
    for ij,entries in sorted(kernel.items()):
        if ij[0]==ij[1]:out[target].add(ij)
        for i,(c0,cs) in enumerate(entries):
            if c0:
                x=list(target);x[i]-=1
                if x[i]:out[tuple(x)].add(ij)
            for j,c in enumerate(cs):
                if c:
                    x=list(target);x[i]-=1;x[j]+=1
                    if x[i]:out[tuple(x)].add(ij)
    return out

def normal(row,engine):
    # Reduce arbitrary row against existing pivots, leaving free columns
    # including protected candidate columns. Does not mutate pivot state.
    cur=dict(row);free={}
    while cur:
        engine.guard(cur)
        k=max(cur,key=lambda x:(x not in engine.candidates,f.e.b.c.key(x)))
        if k in engine.piv:engine.subtract(cur,engine.piv[k],cur[k])
        else:free[k]=cur.pop(k)
    return free

def build_probes(count,seen,sec,seed,kernel,deadline):
    proposals=collections.defaultdict(dict)
    for target in sorted(count,key=lambda k:(-count[k],h.order(k)))[:MAX_RESIDUALS]:
        for ex,derivs in inverse_seeds(target,kernel).items():
            if ex in seen or exclusion(ex,set(),sec,seed)!="unseeded_in_scope":continue
            for ij in sorted(derivs):
                if time.monotonic()>=deadline:raise TimeoutError("Inverse search budget")
                key=(ex,ij)
                proposals[key][target]=count[target]
    # Cheap structural pre-ranking before exact symbolic row generation.
    return sorted(proposals,key=lambda k:(-sum(proposals[k].values()),h.order(k[0]),k[1]))[:MAX_PROBES]

def choose(count,seen,sec,seed,kernel,engines,reduce,deadline):
    probes=build_probes(count,seen,sec,seed,kernel,deadline)
    ranked=[];verified=0;independent=0
    for ex,ij in probes:
        if time.monotonic()>=deadline:raise TimeoutError("Probe budget")
        raw=q.exact_row(ex,kernel[ij],*ij)
        if not set(raw)&set(count):continue
        verified+=1
        sub,_,_=p.substitute(raw,reduce)
        reduced=[normal(p.field_row(sub,pt),eng) for pt,eng in zip(old.POINTS,engines)]
        hits=[set(r)&set(count) for r in reduced]
        if not all(hits):continue
        independent+=1
        # Prefer relations involving existing residual terms, with fewer
        # new noncandidate columns and a pivot that is itself a residual.
        leads=[max((k for k in r if k not in eng.candidates),key=f.e.b.c.key,default=None)
               for r,eng in zip(reduced,engines)]
        score=(sum(k in count for k in leads),
               sum(sum(count[k] for k in hit) for hit in hits),
               -sum(len(set(r)-set(count)-eng.candidates) for r,eng in zip(reduced,engines)))
        ranked.append((score,ex,ij))
    ranked.sort(key=lambda x:(tuple(-y for y in x[0]),h.order(x[1]),x[2]))
    selected=[];keys=set()
    for score,ex,ij in ranked:
        if ex in keys:continue
        selected.append((ex,ij,score));keys.add(ex)
        if len(selected)>=BATCH:break
    return selected,{"probes":len(probes),"verified_occurrence":verified,"residual_relations_both":independent,"selected_seeds":len(selected)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12)
    args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (h.ROOT,p.ROOT,a.ROOT,f.ROOT,f.a.ROOT,f.e.ROOT,q.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={SOURCE:SHA,p.AUDIT:p.AUDIT_SHA,a.PILOT:a.SHA,f.EVIDENCE:f.EVIDENCE_SHA}
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Evidence SHA")
        previous=gap.read(SOURCE);pilot=gap.read(a.PILOT)
        if previous["status"]!="VP05_PARENT_FRONTIER_NOT_CLOSURE" or len(previous["jobs"])!=4:raise RuntimeError("Frontier scope")
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
        # Audit final residuals for all four previous jobs; do not infer
        # their classification from the aggregate log.
        audits=[]
        for job in previous["jobs"]:
            seed,sec=job["seed"],job["sector"];seen=set()
            for rnd in job["rounds"]:
                src=h.ROOT/f"{seed}_sec{sec}_round{rnd['round']}.json"
                pins[src]=rnd["sha256"]
                if n.sha(src)!=pins[src]:raise RuntimeError("Round SHA")
                saved=gap.read(src);seen.update(tuple(k) for k in saved["schedule"])
            count=residuals(saved["checks"],candidates)
            classes=collections.Counter(exclusion(k,seen,sec,seed) for k in count)
            masks=collections.Counter(gap.sector(k) for k in count)
            record={"seed":seed,"sector":sec,"unique_residuals":len(count),"classes":dict(sorted(classes.items())),
                    "masks":dict(sorted(masks.items())),"residuals":[[list(k),c] for k,c in sorted(count.items())]}
            audits.append(record);v.log("VP05_INVERSE_RESIDUAL_AUDIT",**{k:v for k,v in record.items() if k!="residuals"})
        # Smallest prior job first, not all four large expansions.
        job=next(j for j in previous["jobs"] if j["sector"]==204)
        seed,sec=job["seed"],job["sector"];seen=set()
        targets=[tuple(k) for k in job["diagnostic_targets"]]
        engines=[p.Echelon(pt[0],candidates,deadline) for pt in old.POINTS]
        for rnd in job["rounds"]:
            src=h.ROOT/f"{seed}_sec{sec}_round{rnd['round']}.json"
            saved=gap.read(src)
            seen.update(tuple(k) for k in saved["schedule"])
            for rec in saved["rows"]:
                ex=tuple(rec["seed"]);ij=tuple(rec["derivative"])
                raw=q.exact_row(ex,kernel[ij],*ij)
                sub,used,blocked=p.substitute(raw,reduce)
                if p.encode(raw)!=rec["raw"] or p.encode(sub)!=rec["substituted"] or p.encode(used)!=rec["analytic_coefficients"] or [list(k) for k in sorted(blocked)]!=rec["blocked"]:raise RuntimeError("Original/substitution replay")
                for eng,pt in zip(engines,old.POINTS):eng.insert(p.field_row(sub,pt))
            checks=h.pair_results(engines,targets)
            if any(x["targets"]!=y["targets"] for x,y in zip(checks,saved["checks"])):raise RuntimeError("Prior target replay")
        summaries=[]
        for rid in range(MAX_ROUNDS):
            count=residuals(checks,candidates)
            if not count:break
            selection,stats=choose(count,seen,sec,seed,kernel,engines,reduce,deadline)
            v.log("VP05_INVERSE_SELECTION",round=rid,residuals=len(count),**stats)
            if not selection:break
            records=[]
            for ex,ij,score in selection:
                if time.monotonic()>=deadline:raise TimeoutError("Round budget")
                seen.add(ex)
                for deriv,entries in sorted(kernel.items()):
                    raw=q.exact_row(ex,entries,*deriv);sub,used,blocked=p.substitute(raw,reduce)
                    for eng,pt in zip(engines,old.POINTS):eng.insert(p.field_row(sub,pt))
                    records.append({"seed":list(ex),"derivative":list(deriv),"raw":p.encode(raw),"substituted":p.encode(sub),
                                    "analytic_coefficients":p.encode(used),"blocked":[list(k) for k in sorted(blocked)]})
            checks=h.pair_results(engines,targets)
            both=sum(x["candidate_only"] and y["candidate_only"] for x,y in zip(checks[0]["targets"],checks[1]["targets"]))
            after=residuals(checks,candidates)
            # Operation counts include deterministic probing; no timing in immutable records.
            result={"round":rid,"seeds":len(seen),"added_rows":len(records),"residuals_before":len(count),"residuals_after":len(after),
                    "both_points_candidate_only":both,**stats}
            payload={"source_sha256":SHA,"sector":sec,"seed":seed,"stats":result,
                     "selected":[[list(ex),list(ij),list(score)] for ex,ij,score in selection],
                     "rows":records,"checks":checks,"full_closure_proven":False}
            dest=ROOT/f"sec{sec}_round{rid}.json"
            if dest.exists():
                if gap.read(dest)!=payload:raise RuntimeError("Round replay mismatch")
            else:old.atomic(dest,payload)
            summaries.append({**result,"sha256":n.sha(dest)})
            v.log("VP05_INVERSE_ROUND",**result)
            if both==len(targets):break
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_PARENT_INVERSE_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},
                 "residual_audits":audits,"sector":sec,"targets":[list(k) for k in targets],"rounds":summaries,
                 "final_checks":checks,"full_closure_proven":False,"generic_rational_target_proof":False}
        dest=ROOT/"summary.json"
        if dest.exists():
            if gap.read(dest)!=payload:raise RuntimeError("Summary mismatch")
        else:old.atomic(dest,payload)
        v.log("VP05_PARENT_INVERSE_NOT_CLOSURE",sector=sec,rounds=len(summaries),targets=len(targets),
              candidate_only_both=sum(x["candidate_only"] and y["candidate_only"] for x,y in zip(checks[0]["targets"],checks[1]["targets"])),
              residuals=len(residuals(checks,candidates)),sha256=n.sha(dest),elapsed_s=time.monotonic()-start,
              inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
