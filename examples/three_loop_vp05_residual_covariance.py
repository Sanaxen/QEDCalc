"""Final sector228 numerator reduction using Lorentz covariance.

For a denominator independent of q, replace L.q by (p.q/p^2)*L.p
under the integral, for each loop vector L. Only linear q contractions
are supported here. Rebuild earlier moment and symmetry rules before use.
"""
import argparse
import os
import time
from examples import three_loop_vp05_residual_moments as m

s=m.s;c=m.c;r=m.r;p=m.p;f=m.f;a=m.a;old=m.old;sp=m.sp;gap=m.gap;n=m.n;v=m.v
ROOT=n.BASE/"output"/"vp05_residual_covariance19"
SOURCE=m.ROOT/"audit.json"
SHA="19e8e57cddac4b05c5b08bd51d2decb3e6133ea151287731835c842f82387996"
R=(-1,0,1,0,0,1,1,1,0,0,0,0)
J=(0,0,1,0,0,1,1,1,0,0,0,-1)

def covariance_row(key,props,inverse):
    base=tuple(max(x,0) for x in key)
    if base!=f.scalar(228) or sum(-x for x in key if x<0)!=1:
        raise RuntimeError("Single numerator scope")
    for i in r.positive(base):
        if f.a.momentum(props[i]).has(old.MOM[4]):raise RuntimeError("Denominator depends on q")
    index=next(i for i,x in enumerate(key) if x<0)
    original=r.polynomial(f.a.momentum(props[index]),props[index].mass)
    qs=[old.dot(i,4) for i in range(3)]
    if sp.Poly(original,*qs).total_degree()>1:raise RuntimeError("Higher tensor rank")
    # The coefficients of L.q must contain no loop scalar products:
    # otherwise an additional tensor argument would be needed.
    if any(original.diff(x).free_symbols&set(old.X) for x in qs):raise RuntimeError("Nonconstant vector coefficient")
    replacements={old.dot(i,4):-old.Z*old.dot(i,3)/2 for i in range(3)}
    projected=sp.expand(original.subs(replacements,simultaneous=True))
    poly=sp.Poly(sp.expand(projected.subs(inverse,simultaneous=True)),*old.Y)
    if sp.expand(poly.as_expr().subs(dict(zip(old.Y,s.polys(props))),simultaneous=True)-projected)!=0:
        raise RuntimeError("Covariance polynomial replay")
    row={tuple(x-y for x,y in zip(base,mon)):coef for mon,coef in poly.terms() if coef}
    return row,{"integral":list(key),"numerator_line":index+1,"numerator_momentum":str(f.a.momentum(props[index])),
                "original_polynomial":str(original),"projected_polynomial":str(projected),
                "propagator_polynomial":str(poly.as_expr()),"expanded":p.encode(row),
                "assumptions":["DR","denominators independent of q","p^2=1","p.q=-z/2","rank-one Lorentz covariance"]}

def solve(keys,candidates,props,deadline,symmetry):
    base=f.scalar(228);inverse=s.inverse_polys(props)
    # Include all single-numerator columns, and both kinds of relations.
    unknown=[];equations=[];evidence=[]
    for i,x in enumerate(base):
        if x:continue
        k=list(base);k[i]=-1;k=tuple(k)
        if k not in candidates:unknown.append(k)
        expanded,cert=covariance_row(k,props,inverse)
        row={j:-x for j,x in expanded.items()};row[k]=row.get(k,0)+1
        row={j:sp.cancel(x) for j,x in row.items() if sp.cancel(x)!=0}
        if not row:continue
        reduced,remaining,proofs=s.reduce_terms(row,candidates,props,deadline)
        equations.append({**reduced,**remaining})
        evidence.append({"kind":"covariance","certificate":cert,"term_proofs":proofs,"equation":p.encode(equations[-1])})
    covariance_count=len(equations)
    for item in symmetry["equations"]:
        equations.append(p.decode(item["equation"]))
        evidence.append({"kind":"symmetry","certificate":item,"equation":item["equation"]})
    field,_,_=sp.polys.fields.field("z,d",sp.QQ)
    piv={};candidate_relations=[]
    def add(dst,src,coef):
        for j,x in src.items():
            val=dst.get(j,field.zero)+coef*x
            if val:dst[j]=val
            else:dst.pop(j,None)
    for idx,eq in enumerate(equations):
        if time.monotonic()>=deadline:raise TimeoutError("Covariance budget")
        if not set(eq)<=set(unknown)|candidates:raise RuntimeError("Unexpected column")
        row={k:field.from_expr(x) for k,x in eq.items() if x};weights={idx:field.one}
        while row:
            leads=sorted(set(row)&set(unknown))
            if not leads:
                candidate_relations.append(p.encode({j:x.as_expr() for j,x in row.items()}));break
            k=leads[0];coef=row[k]
            if k not in piv:
                piv[k]=({j:x/coef for j,x in row.items()},{j:x/coef for j,x in weights.items()});break
            add(row,piv[k][0],-coef);add(weights,piv[k][1],-coef)
    # Unexpected nonzero candidate-only relations are not silently discarded.
    if candidate_relations:raise RuntimeError("Candidate-only relations require review: "+str(candidate_relations))
    results=[]
    for key in keys:
        row={key:field.one};free={};weights={}
        while row:
            lead=min(row,key=lambda k:(k not in unknown,k));coef=row[lead]
            if lead not in piv:free[lead]=row.pop(lead);continue
            add(row,piv[lead][0],-coef);add(weights,piv[lead][1],coef)
        check={key:field.one}
        for i,x in weights.items():add(check,{k:field.from_expr(y) for k,y in equations[i].items()},-x)
        if check!=free:raise RuntimeError("Exact equation replay")
        ok=set(free)<=candidates
        results.append({"integral":list(key),"sector":228,"kind":"covariance_symmetry" if ok else "unresolved",
                        "rule":p.encode({k:x.as_expr() for k,x in free.items()}) if ok else [],
                        "partial_remainder":p.encode({k:x.as_expr() for k,x in free.items()}),
                        "multipliers":[[i,str(x.as_expr())] for i,x in sorted(weights.items())]})
    return results,{"covariance_equations":covariance_count,"equations":evidence,"rank":len(piv),"unknowns":[list(k) for k in unknown]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (m.ROOT,s.ROOT,s.m.ROOT,c.ROOT,s.retry.ROOT,s.retry.m.ROOT,c.audit.ROOT,c.audit.PROOFS):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={SOURCE:SHA,m.SOURCE:m.SHA,s.SOURCE:s.SHA,s.RETRY:s.RETRY_SHA,s.m.SOURCE:s.m.SHA,c.AUDIT:c.SHA}
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Evidence SHA")
        prior=gap.read(SOURCE);structure=gap.read(m.SOURCE)
        if prior["status"]!="VP05_RESIDUAL_MOMENTS_NOT_CLOSURE" or {tuple(x["integral"]) for x in prior["records"] if x["kind"]=="unresolved"}!={R}:raise RuntimeError("Residual scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[manifest]=n.sha(manifest)
        if prior["inputs"].get(str(manifest))!=pins[manifest]:raise RuntimeError("Manifest SHA")
        candidates=set(gap.indices(x) for x in gap.read(manifest)["candidate_masters"])
        if len(candidates)!=63 or None in candidates or f.a.CAND not in candidates:raise RuntimeError("Candidate scope")
        props=old.build_family_spec("VP05_full").propagators
        if old.digest(old.build_kernel(props))!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        f.e.b.a.memory()
        # Reproduce the earlier four massless zeros and moment/symmetry
        # evidence, not merely trust their success flags.
        zeros=[x for x in structure["records"] if x["kind"]=="massless_factor_zero"]
        if len(zeros)!=4 or any(s.massless_factor(tuple(x["integral"]),props)!=x["certificate"] for x in zeros):raise RuntimeError("Massless factor replay")
        bubble=m.bubble71(props,candidates,deadline)
        if bubble!=next(x for x in prior["records"] if tuple(x["integral"])==m.K71):raise RuntimeError("Bubble replay")
        symkeys=sorted(tuple(x["integral"]) for x in prior["records"] if x["sector"]==228)
        sym,proof=m.symmetry228(symkeys,candidates,props,deadline)
        if sym!=[x for x in prior["records"] if x["sector"]==228] or proof!=prior["symmetry_certificate"]:raise RuntimeError("Symmetry replay")
        records,cert=solve([R,J],candidates,props,deadline,proof)
        v.log("VP05_COVARIANCE_RULES",rank=cert["rank"],covariance_equations=cert["covariance_equations"],results=records)
        jobs=[]
        for job in prior["jobs"]:
            checks=s.m.apply(job["post_identity_checks"],records,candidates)
            ready=[x["target"] for x,y in zip(checks[0]["targets"],checks[1]["targets"]) if x["candidate_only"] and y["candidate_only"]]
            remaining=c.inv.residuals(checks,candidates)
            if not set(map(tuple,job["ready_targets"]))<=set(map(tuple,ready)):raise RuntimeError("Lost ready target")
            result={"sector":job["sector"],"candidate_only_before":job["candidate_only_after"],"candidate_only_after":len(ready),
                    "ready_targets":ready,"unresolved":[[list(k),x] for k,x in sorted(remaining.items())],"post_identity_checks":checks}
            jobs.append(result);v.log("VP05_COVARIANCE_JOB",**{k:x for k,x in result.items() if k!="post_identity_checks"})
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_RESIDUAL_COVARIANCE_NOT_CLOSURE","inputs":{str(k):d for k,d in pins.items()},
                 "records":records,"certificate":cert,"jobs":jobs,"earlier_rules_replayed":7,
                 "generic_rational_target_proof":False,"full_closure_proven":False}
        digest=c.save(ROOT/"audit.json",payload)
        v.log("VP05_RESIDUAL_COVARIANCE_NOT_CLOSURE",residuals=1,residual_resolved=records[0]["kind"]!="unresolved",
              candidate_only_both=sum(x["candidate_only_after"] for x in jobs),residuals_job_sum=sum(len(x["unresolved"]) for x in jobs),
              sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
