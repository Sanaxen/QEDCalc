"""Common remaining-parent workflow, with audited factorized extension.

Keep old evidence immutable. Verify the new three-line bases and original
IBP identities before enabling them. Rebuild the remaining parent frontiers
with five analytic sectors and use bounded inverse IBP search. This is a
two-point diagnostic, not a boundary closure or rational certificate.
"""
import argparse
import collections
import functools
import os
import time
from examples import three_loop_vp05_parent_exact_audit as audit
from examples import three_loop_vp05_parent_inverse as inv

h=inv.h;p=inv.p;f=inv.f;a=inv.a;old=inv.old;sp=inv.sp;gap=inv.gap;n=inv.n;v=inv.v;q=inv.q
ROOT=n.BASE/"output"/"vp05_parent_common13"
AUDIT=audit.ROOT/"audit.json"
SHA="400d51ec311240d9c458f08922c988f5db790f544eca48ac5af9f55b233f054e"
SECTORS=(69,76,140,196,200)
NEW=(76,140)
JOBS=(228,71,77)
MAX_ROUNDS=6

def kind(ex):
    sec=gap.sector(ex)
    if sec in SECTORS:
        s,d=a.degrees(ex)
        return "factorized" if s<=f.MAX_DEGREE and d<=f.MAX_DOTS else "blocked"
    if any(sec!=s and sec&s==sec for s in SECTORS):return "zero"
    return "other"

def substitute(row,reduce):
    out={};used={};blocked={}
    for ex,c in sorted(row.items()):
        tag=kind(ex);key=ex
        if tag=="factorized":
            value=reduce(ex);used[ex]=value;key=f.a.CAND;c*=value
        elif tag=="zero":
            used[ex]=sp.S.Zero;continue
        elif tag=="blocked":blocked[ex]=a.degrees(ex)
        out[key]=out.get(key,0)+c
    out={k:sp.cancel(c) for k,c in out.items()}
    return {k:c for k,c in out.items() if c!=0},used,blocked

def extension_seeds(sec):
    base=f.scalar(sec);out={base}
    for i,x in enumerate(base):
        ex=list(base);ex[i]+=1 if x else -1;out.add(tuple(ex))
    return sorted(out)

def validate_extension(reducers,props,kernel,reduce,deadline):
    results=[]
    for sec in NEW:
        base=f.scalar(sec)
        proof=f.a.affine(props,base,f.a.CAND)
        if proof!=reducers[sec].map or reduce(base)!=1:raise RuntimeError("New scalar identity")
        rows=[];seeds=extension_seeds(sec)
        for ex in seeds:
            if time.monotonic()>=deadline:raise TimeoutError("Extension budget")
            f.e.b.a.memory()
            for ij,entries in sorted(kernel.items()):
                raw=q.exact_row(ex,entries,*ij)
                result=a.audit_row(raw,sec,reduce)
                if result["status"]!="PASS":raise RuntimeError("New sector IBP identity failed")
                rows.append({"seed":list(ex),"derivative":list(ij),**result})
        results.append({"sector":sec,"map":proof,"seeds":len(seeds),"rows":rows})
        v.log("VP05_COMMON_EXTENSION",sector=sec,seeds=len(seeds),passed=len(rows),map=proof)
    return results

def choose(count,seen,sec,seed,kernel,engines,reduce,deadline):
    proposals=inv.build_probes(count,seen,sec,seed,kernel,deadline)
    ranked=[];verified=0;hits_both=0
    for ex,ij in proposals:
        if kind(ex)!="other":continue
        if time.monotonic()>=deadline:raise TimeoutError("Probe budget")
        raw=q.exact_row(ex,kernel[ij],*ij)
        if not set(raw)&set(count):continue
        verified+=1
        sub,_,_=substitute(raw,reduce)
        normalized=[inv.normal(p.field_row(sub,pt),eng) for pt,eng in zip(old.POINTS,engines)]
        hits=[set(x)&set(count) for x in normalized]
        if not all(hits):continue
        hits_both+=1
        leads=[max((k for k in row if k not in eng.candidates),key=f.e.b.c.key,default=None)
               for row,eng in zip(normalized,engines)]
        score=(sum(k in count for k in leads),sum(sum(count[k] for k in hit) for hit in hits),
               -sum(len(set(row)-set(count)-eng.candidates) for row,eng in zip(normalized,engines)))
        ranked.append((score,ex,ij))
    ranked.sort(key=lambda x:(tuple(-y for y in x[0]),h.order(x[1]),x[2]))
    selection=[];keys=set()
    for score,ex,ij in ranked:
        if ex in keys:continue
        selection.append((ex,ij,score));keys.add(ex)
        if len(selection)>=inv.BATCH:break
    return selection,{"probes":len(proposals),"verified_occurrence":verified,"residual_relations_both":hits_both}

def save(path,payload):
    if path.exists():
        if gap.read(path)!=payload:raise RuntimeError("Immutable output differs: "+str(path))
    else:old.atomic(path,payload)
    if gap.read(path)!=payload:raise RuntimeError("Output reread mismatch")
    return n.sha(path)

def job_run(job,kernel,candidates,reduce,deadline,pins,extension_sha):
    sec=job["sector"];seed=job["seed"];targets=[tuple(k) for k in job["diagnostic_targets"]]
    if len(targets)!=16 or len(set(targets))!=16 or any(k in candidates for k in targets):raise RuntimeError("Target scope")
    engines=[p.Echelon(pt[0],candidates,deadline) for pt in old.POINTS]
    seen=set();rawcols=set();subcols=set();used_all=set();blocked_all=set()
    terms=[0,0];row_count=0
    def insert(ex,ij,raw):
        nonlocal row_count
        sub,used,blocked=substitute(raw,reduce)
        rawcols.update(raw);subcols.update(sub);used_all.update(used);blocked_all.update(blocked)
        terms[0]+=len(raw);terms[1]+=len(sub);row_count+=1
        for eng,pt in zip(engines,old.POINTS):eng.insert(p.field_row(sub,pt))
        return {"seed":list(ex),"derivative":list(ij),"raw":p.encode(raw),"substituted":p.encode(sub),
                "analytic_coefficients":p.encode(used),"blocked":[list(k) for k in sorted(blocked)]}
    def stats(checks):
        both=sum(x["candidate_only"] and y["candidate_only"] for x,y in zip(checks[0]["targets"],checks[1]["targets"]))
        return {"seeds":len(seen),"rows":row_count,"targets":len(targets),"candidate_only_both":both,
                "residuals":len(inv.residuals(checks,candidates)),"columns_before":len(rawcols),"columns_after":len(subcols),
                "terms_before":terms[0],"terms_after":terms[1],"analytic_targets":len(used_all),"blocked_targets":len(blocked_all)}
    records=[]
    for rnd in job["rounds"]:
        src=h.ROOT/f"{seed}_sec{sec}_round{rnd['round']}.json"
        pins[src]=rnd["sha256"]
        if n.sha(src)!=pins[src]:raise RuntimeError("Frontier round SHA")
        saved=gap.read(src)
        for ex in saved["schedule"]:
            ex=tuple(ex)
            if ex in seen:raise RuntimeError("Duplicate source seed")
            seen.add(ex)
        for rec in saved["rows"]:
            if time.monotonic()>=deadline:raise TimeoutError("Original replay budget")
            ex=tuple(rec["seed"]);ij=tuple(rec["derivative"])
            raw=q.exact_row(ex,kernel[ij],*ij)
            if p.encode(raw)!=rec["raw"]:raise RuntimeError("Original row mismatch")
            records.append(insert(ex,ij,raw))
    if row_count!=15*len(seen):raise RuntimeError("Original source row count")
    checks=h.pair_results(engines,targets)
    metadata={"version":1,"seed":seed,"sector":sec,"source_sha256":inv.SHA,"extension_sha256":extension_sha,
              "targets":[list(x) for x in targets],"kernel_sha256":f.e.b.c.PIN}
    initial=stats(checks)
    dest=ROOT/f"sec{sec}_initial.json"
    initial_sha=save(dest,{"meta":metadata,"stats":initial,"rows":records,"checks":checks,"full_closure_proven":False})
    v.log("VP05_COMMON_INITIAL",sector=sec,**initial)
    rounds=[]
    for rid in range(MAX_ROUNDS):
        count=inv.residuals(checks,candidates)
        if not count:break
        selection,selection_stats=choose(count,seen,sec,seed,kernel,engines,reduce,deadline)
        v.log("VP05_COMMON_SELECTION",sector=sec,round=rid,residuals=len(count),selected_seeds=len(selection),**selection_stats)
        if not selection:break
        records=[]
        for ex,_,_ in selection:
            if time.monotonic()>=deadline:raise TimeoutError("Round budget")
            f.e.b.a.memory();seen.add(ex)
            for ij,entries in sorted(kernel.items()):records.append(insert(ex,ij,q.exact_row(ex,entries,*ij)))
        checks=h.pair_results(engines,targets);result=stats(checks)
        dest=ROOT/f"sec{sec}_round{rid}.json"
        digest=save(dest,{"meta":metadata,"stats":result,"selection":[[list(ex),list(ij),list(score)] for ex,ij,score in selection],
                          "rows":records,"checks":checks,"full_closure_proven":False})
        rounds.append({"round":rid,"sha256":digest,**result});v.log("VP05_COMMON_ROUND",sector=sec,round=rid,**result)
    return {"sector":sec,"seed":seed,"initial_sha256":initial_sha,"initial":initial,"rounds":rounds,
            "final":stats(checks),"final_checks":checks,"diagnostic_targets":[list(k) for k in targets],"full_closure_proven":False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (audit.ROOT,audit.PROOFS,a.ROOT,f.ROOT,h.ROOT,p.ROOT,inv.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={AUDIT:SHA,audit.SOURCE:audit.SHA,inv.SOURCE:inv.SHA,a.PILOT:a.SHA,p.AUDIT:p.AUDIT_SHA,f.EVIDENCE:f.EVIDENCE_SHA,
              audit.r.ROOT/"audit.json":audit.IDENTITY_SHA}
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Evidence SHA")
        prior=gap.read(AUDIT)
        if prior["status"]!="VP05_PARENT_EXACT_AUDIT_NOT_CLOSURE" or prior["unique_verified_pivots"]!=268 or len(prior["results"])!=16:raise RuntimeError("Sec204 audit scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        path=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[path]=n.sha(path);candidates=set(gap.indices(x) for x in gap.read(path)["candidate_masters"])
        if len(candidates)!=63 or None in candidates or f.a.CAND not in candidates:raise RuntimeError("Candidate scope")
        spec=old.build_family_spec("VP05_full");kernel=old.build_kernel(spec.propagators)
        if old.digest(kernel)!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        pilot=gap.read(a.PILOT);reducers={sec:f.Reducer(spec.propagators,sec,deadline) for sec in SECTORS}
        if any(reducers[sec].map not in pilot["maps"] for sec in f.SECTORS):raise RuntimeError("Prior affine map")
        identity=gap.read(audit.r.ROOT/"audit.json")
        for rec in identity["records"]:
            proof=audit.r.affine_match(tuple(rec["integral"]),f.a.CAND,spec.propagators,deadline)
            if not proof or proof not in rec["affine_matches"]:raise RuntimeError("Residual identity replay")
        @functools.lru_cache(maxsize=4096)
        def reduce(ex):
            reducer=reducers[gap.sector(ex)];a.begin_seed(reducer);return reducer.reduce(ex)
        extension=validate_extension(reducers,spec.propagators,kernel,reduce,deadline)
        extension_sha=save(ROOT/"extension.json",{"status":"VP05_COMMON_EXTENSION_NOT_CLOSURE","sectors":list(SECTORS),
                            "kernel_sha256":f.e.b.c.PIN,"identity_sha256":audit.IDENTITY_SHA,"results":extension,"full_closure_proven":False})
        frontier=gap.read(inv.SOURCE)
        results=[]
        for sec in JOBS:
            job=next(x for x in frontier["jobs"] if x["sector"]==sec)
            results.append(job_run(job,kernel,candidates,reduce,deadline,pins,extension_sha))
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_PARENT_COMMON_NOT_CLOSURE","inputs":{str(k):d for k,d in pins.items()},
                 "extension_sha256":extension_sha,"jobs":results,"full_closure_proven":False,"generic_rational_target_proof":False}
        digest=save(ROOT/"summary.json",payload)
        v.log("VP05_PARENT_COMMON_NOT_CLOSURE",jobs=len(results),targets=sum(x["final"]["targets"] for x in results),
              candidate_only_both=sum(x["final"]["candidate_only_both"] for x in results),
              residuals_job_sum=sum(x["final"]["residuals"] for x in results),extension_rows=sum(len(x["rows"]) for x in extension),
              sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
