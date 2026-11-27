"""Audit residual identities from all three common parent jobs.

Only verified exact rules are applied to saved modular remainders.
Unresolved integrals remain explicit; no claim of parent closure.
"""
import argparse
import os
import time
from examples import three_loop_vp05_parent_common as c
from examples import three_loop_vp05_residual_identity as r

inv=c.inv;p=c.p;f=c.f;a=c.a;old=c.old;sp=c.sp;gap=c.gap;n=c.n;v=c.v
ROOT=n.BASE/"output"/"vp05_parent_common_residual14"
SOURCE=c.ROOT/"summary.json"
SHA="e3c421f8088388720c51c23eeb6eca9723e1acdc5ca7c36fdeaca70be41f7a9e"

def identify(key,candidates,props,kernel,deadline):
    sec=gap.sector(key);rank=r.rank_certificate(key,props)
    out={"integral":list(key),"sector":sec,"degrees":list(a.degrees(key)),
         "rank_certificate":rank,"same_sector_candidates":[list(k) for k in sorted(candidates) if gap.sector(k)==sec],
         "kind":"unresolved","rule":[]}
    if rank["scaleless_free_loop"]:
        out["kind"]="free_loop_zero";return out
    # General analytic factorization requires exactly three independent
    # massive lines, unimodular basis, and a supported numerator/dot degree.
    lines=r.positive(key);s,d=a.degrees(key)
    if len(lines)==3 and all(props[i].mass=="m2" for i in lines) and s<=f.MAX_DEGREE and d<=f.MAX_DOTS:
        mat=sp.Matrix([f.a.momentum(props[i]) for i in lines]).jacobian(old.MOM[:3])
        if abs(mat.det())==1:
            reducer=f.Reducer(props,sec,deadline)
            def reduce(ex):
                a.begin_seed(reducer);return reducer.reduce(ex)
            try:
                if reduce(f.scalar(sec))!=1:raise RuntimeError("Scalar ratio")
                checks=[]
                # Audit actual residual and low-degree basis sample; rows
                # exceeding the supported envelope remain explicitly unsupported.
                for ex in sorted(set(c.extension_seeds(sec))|{key}):
                    for ij,entries in sorted(kernel.items()):
                        if time.monotonic()>=deadline:raise TimeoutError("Identity budget")
                        result=a.audit_row(c.q.exact_row(ex,entries,*ij),sec,reduce)
                        if result["status"]=="FAIL":raise RuntimeError("Factorized IBP residual")
                        checks.append({"seed":list(ex),"derivative":list(ij),**result})
                if sum(x["status"]=="PASS" for x in checks)<195:raise RuntimeError("Low-degree audit incomplete")
                coeff=sp.cancel(reduce(key))
                out.update(kind="factorized",rule=[[list(f.a.CAND),str(coeff)]] if coeff else [],
                           affine_map=reducer.map,ibp_checks=checks)
                return out
            finally:reducer.close()
    matches=[]
    for cand in sorted(candidates):
        if time.monotonic()>=deadline:raise TimeoutError("Identity budget")
        proof=r.affine_match(key,cand,props,deadline)
        if proof:matches.append(proof)
    if matches:
        out.update(kind="affine",affine_matches=matches,rule=[[matches[0]["destination"],"1"]])
    return out

def apply(checks,records,candidates):
    rules={tuple(x["integral"]):p.decode(x["rule"]) for x in records if x["kind"]!="unresolved"}
    final=[]
    for check in checks:
        point=tuple(check["point"]);prime=point[0];results=[]
        for item in check["targets"]:
            row={}
            for ex,value in item["remainder"]:
                k=tuple(ex)
                terms=p.field_row(rules[k],point) if k in rules else {k:1}
                for dest,c0 in terms.items():row[dest]=(row.get(dest,0)+value*c0)%prime
            row={k:c0 for k,c0 in row.items() if c0}
            results.append({"target":item["target"],"remainder":[[list(k),v0] for k,v0 in sorted(row.items())],
                            "candidate_only":all(k in candidates for k in row)})
        final.append({"point":list(point),"targets":results})
    return final

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (c.ROOT,c.audit.ROOT,c.audit.PROOFS,r.ROOT,inv.ROOT,inv.h.ROOT,p.ROOT,a.ROOT,f.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={SOURCE:SHA,c.AUDIT:c.SHA}
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Input SHA")
        source=gap.read(SOURCE)
        if source["status"]!="VP05_PARENT_COMMON_NOT_CLOSURE" or set(x["sector"] for x in source["jobs"])!=set(c.JOBS) or len(source["jobs"])!=3:raise RuntimeError("Common scope")
        extension=c.ROOT/"extension.json";pins[extension]=source["extension_sha256"]
        if n.sha(extension)!=pins[extension]:raise RuntimeError("Extension SHA")
        ext=gap.read(extension)
        if sum(len(x["rows"]) for x in ext["results"])!=390 or any(y["status"]!="PASS" for x in ext["results"] for y in x["rows"]):raise RuntimeError("Extension scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[manifest]=n.sha(manifest)
        if source["inputs"].get(str(manifest))!=pins[manifest]:raise RuntimeError("Manifest differs from common run")
        candidates=set(gap.indices(x) for x in gap.read(manifest)["candidate_masters"])
        if len(candidates)!=63 or None in candidates or f.a.CAND not in candidates:raise RuntimeError("Candidate scope")
        spec=old.build_family_spec("VP05_full");kernel=old.build_kernel(spec.propagators)
        if old.digest(kernel)!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        union=set();counts={}
        for job in source["jobs"]:
            sec=job["sector"];files=[(c.ROOT/f"sec{sec}_initial.json",job["initial_sha256"])]
            files.extend((c.ROOT/f"sec{sec}_round{x['round']}.json",x["sha256"]) for x in job["rounds"])
            rows=0
            for path,digest in files:
                pins[path]=digest
                if n.sha(path)!=digest:raise RuntimeError("Round SHA")
                saved=gap.read(path);rows+=len(saved["rows"])
                if saved["meta"]["sector"]!=sec or saved["meta"]["extension_sha256"]!=pins[extension]:raise RuntimeError("Round scope")
            checks=job["final_checks"]
            if saved["checks"]!=checks or rows!=job["final"]["rows"]:raise RuntimeError("Final scope")
            targets=job["diagnostic_targets"]
            if len(targets)!=16 or len(set(map(tuple,targets)))!=16 or len(checks)!=2:raise RuntimeError("Target scope")
            for pt,check in zip(old.POINTS,checks):
                if list(pt)!=check["point"] or [x["target"] for x in check["targets"]]!=targets:raise RuntimeError("Point/target scope")
            count=inv.residuals(checks,candidates)
            if len(count)!=job["final"]["residuals"]:raise RuntimeError("Residual scope")
            counts[sec]=count;union.update(count)
        if sum(map(len,counts.values()))!=11:raise RuntimeError("Expected eleven job residuals")
        records=[]
        for key in sorted(union):
            f.e.b.a.memory()
            item=identify(key,candidates,spec.propagators,kernel,deadline)
            item["occurrences"]=[{"parent_sector":j["sector"],**x} for j in source["jobs"] for x in r.occurrences(j["final_checks"],key)]
            records.append(item)
            v.log("VP05_COMMON_RESIDUAL_IDENTITY",**{k:val for k,val in item.items() if k not in ("ibp_checks","occurrences")},
                  occurrences=len(item["occurrences"]),ibp_pass=sum(x["status"]=="PASS" for x in item.get("ibp_checks",[])))
        jobs=[]
        for job in source["jobs"]:
            checks=apply(job["final_checks"],records,candidates)
            ready=[x["target"] for x,y in zip(checks[0]["targets"],checks[1]["targets"]) if x["candidate_only"] and y["candidate_only"]]
            remaining=inv.residuals(checks,candidates)
            result={"sector":job["sector"],"candidate_only_before":job["final"]["candidate_only_both"],"candidate_only_after":len(ready),
                    "residuals_before":len(counts[job["sector"]]),"residuals_after":len(remaining),
                    "ready_targets":ready,"unresolved":[[list(k),count] for k,count in sorted(remaining.items())],"post_identity_checks":checks}
            jobs.append(result)
            v.log("VP05_COMMON_RESIDUAL_JOB",**{k:x for k,x in result.items() if k!="post_identity_checks"})
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_COMMON_RESIDUAL_NOT_CLOSURE","inputs":{str(k):d for k,d in pins.items()},"records":records,"jobs":jobs,
                 "generic_rational_target_proof":False,"full_closure_proven":False}
        digest=c.save(ROOT/"audit.json",payload)
        v.log("VP05_COMMON_RESIDUAL_NOT_CLOSURE",unique_residuals=len(union),identities=sum(x["kind"]!="unresolved" for x in records),
              candidate_only_both=sum(x["candidate_only_after"] for x in jobs),residuals_job_sum=sum(x["residuals_after"] for x in jobs),
              sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
