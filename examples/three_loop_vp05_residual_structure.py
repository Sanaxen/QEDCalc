"""Structural residual audit: centered massless factors and affine numerators.

No new IBP search. Only exact transformations with checked denominators,
Jacobian and polynomial inversion are accepted. Partial maps are diagnostic.
"""
import argparse
import os
import time
from examples import three_loop_vp05_common_residual as m
from examples import three_loop_vp05_sec77_exact_retry as retry

c=m.c;r=m.r;p=m.p;f=m.f;a=m.a;old=m.old;sp=m.sp;gap=m.gap;n=m.n;v=m.v
ROOT=n.BASE/"output"/"vp05_residual_structure17"
SOURCE=m.ROOT/"audit.json"
SHA="4c61d580deb6474e929f639b41266e88afe26802831c630fe9c8006712635ecb"
RETRY=retry.ROOT/"report_1795757206443529000.json"
RETRY_SHA="b4c4388e350f16b8c081578c1230cbef2f44ca26a038dad457dd975afde0417f"

def polys(props):
    return [r.polynomial(f.a.momentum(prop),prop.mass) for prop in props]

def inverse_polys(props):
    pp=polys(props)
    mat=sp.Matrix([[x.coeff(y) for y in old.X] for x in pp])
    constants=sp.Matrix([x.subs(dict.fromkeys(old.X,0)) for x in pp])
    sol=mat.inv()*(sp.Matrix(old.Y)-constants)
    sub=dict(zip(old.X,sol))
    if any(sp.expand(x.subs(sub,simultaneous=True)-y)!=0 for x,y in zip(pp,old.Y)):
        raise RuntimeError("Propagator inversion mismatch")
    return sub

def massless_factor(key,props):
    lines=r.positive(key)
    if len(lines)!=3:return None
    mom=sp.Matrix([f.a.momentum(props[i]) for i in lines])
    A=mom.jacobian(old.MOM[:3])
    if A.det()==0:return None
    shift=(mom-A*sp.Matrix(old.MOM[:3])).applyfunc(sp.expand)
    if any(x.free_symbols-set(old.MOM[3:]) for x in shift):raise RuntimeError("Non-affine denominator")
    mass=[props[i].mass for i in lines]
    if not all(x in ("0","m2") for x in mass):raise RuntimeError("Mass scope")
    if "0" not in mass:return None
    mapping=(A.inv()*(sp.Matrix(old.MOM[:3])-shift)).applyfunc(sp.expand)
    sub=dict(zip(old.MOM[:3],mapping))
    if any(sp.expand(x.subs(sub,simultaneous=True)-y)!=0 for x,y in zip(mom,old.MOM[:3])):
        raise RuntimeError("Centered denominator check")
    numerator=sp.prod(r.polynomial(sp.expand(f.a.momentum(prop).subs(sub,simultaneous=True)),prop.mass)**(-ex)
                      for prop,ex in zip(props,key) if ex<0)
    poly=sp.Poly(sp.expand(numerator),*old.X)
    return {"positive_lines":[i+1 for i in lines],"masses":mass,"powers":[key[i] for i in lines],
            "determinant":str(A.det()),"old_loop_in_centered":[str(x) for x in mapping],
            "massless_centered_loops":[i for i,x in enumerate(mass) if x=="0"],
            "numerator_polynomial":str(poly.as_expr()),"polynomial_terms":len(poly.terms()),
            "reason":"Each tensor monomial has an independent scaleless massless tadpole in DR"}

def affine_expansion(key,base_map,props,inverse):
    src=tuple(base_map["source"]);dst=tuple(base_map["destination"])
    if tuple(max(x,0) for x in key)!=src:raise RuntimeError("Positive powers differ")
    mapping=[sp.sympify(x,locals=dict(zip(map(str,old.MOM),old.MOM))) for x in base_map["source_loop_in_destination"]]
    sub=dict(zip(old.MOM[:3],mapping))
    if abs(sp.Matrix(mapping).jacobian(old.MOM[:3]).det())!=1:raise RuntimeError("Jacobian")
    for i,j,sign in zip(base_map["source_lines"],base_map["destination_lines"],base_map["signs"]):
        if props[i-1].mass!=props[j-1].mass or src[i-1]!=dst[j-1] or sp.expand(f.a.momentum(props[i-1]).subs(sub,simultaneous=True)-sign*f.a.momentum(props[j-1]))!=0:
            raise RuntimeError("Denominator map mismatch")
    numerator=sp.prod(r.polynomial(sp.expand(f.a.momentum(prop).subs(sub,simultaneous=True)),prop.mass)**(-ex)
                      for prop,ex in zip(props,key) if ex<0)
    poly=sp.Poly(sp.expand(numerator.subs(inverse,simultaneous=True)),*old.Y)
    if sp.expand(poly.as_expr().subs(dict(zip(old.Y,polys(props))),simultaneous=True)-numerator)!=0:
        raise RuntimeError("Numerator inverse replay")
    result={}
    for mon,coef in poly.terms():
        if coef:result[tuple(x-y for x,y in zip(dst,mon))]=coef
    return result,str(poly.as_expr())

def reduce_terms(row,candidates,props,deadline):
    out={};unresolved={};proofs=[];reducers={}
    try:
        for key,coef in sorted(row.items()):
            if time.monotonic()>=deadline:raise TimeoutError("Structure budget")
            if key in candidates:dest=key;value=sp.S.One;proof={"kind":"candidate"}
            else:
                zero=massless_factor(key,props)
                rank=r.rank_certificate(key,props)
                if zero or rank["scaleless_free_loop"]:
                    proofs.append({"integral":list(key),"kind":"zero","certificate":zero or rank});continue
                lines=r.positive(key);sec=gap.sector(key);s,d=a.degrees(key)
                if len(lines)==3 and all(props[i].mass=="m2" for i in lines) and s<=f.MAX_DEGREE and d<=f.MAX_DOTS and abs(sp.Matrix([f.a.momentum(props[i]) for i in lines]).jacobian(old.MOM[:3]).det())==1:
                    if sec not in reducers:reducers[sec]=f.Reducer(props,sec,deadline)
                    rr=reducers[sec];a.begin_seed(rr);value=rr.reduce(key);dest=f.a.CAND
                    proof={"kind":"factorized","map":rr.map,"coefficient":str(value)}
                else:
                    match=None
                    for candidate in sorted(candidates):
                        match=r.affine_match(key,candidate,props,deadline)
                        if match:break
                    if not match:
                        unresolved[key]=coef;continue
                    dest=tuple(match["destination"]);value=sp.S.One;proof={"kind":"affine","map":match}
            out[dest]=out.get(dest,0)+coef*value
            proofs.append({"integral":list(key),**proof})
        out={k:sp.cancel(x) for k,x in out.items() if sp.cancel(x)!=0}
        return out,unresolved,proofs
    finally:
        for rr in reducers.values():rr.close()

def investigate(key,candidates,props,inverse,deadline):
    lines=r.positive(key)
    item={"integral":list(key),"sector":gap.sector(key),"kind":"unresolved","rule":[],
          "denominators":[{"line":i+1,"momentum":str(f.a.momentum(props[i])),"mass":props[i].mass,"power":key[i]} for i in lines]}
    zero=massless_factor(key,props)
    if zero:
        item.update(kind="massless_factor_zero",certificate=zero);return item
    base=tuple(max(x,0) for x in key)
    options=[]
    # Include identity map to the same positive-power candidate if present.
    for candidate in sorted(candidates):
        if any(x<0 for x in candidate):continue
        mapping=r.affine_match(base,candidate,props,deadline)
        if not mapping:continue
        row,poly=affine_expansion(key,mapping,props,inverse)
        reduced,remaining,proofs=reduce_terms(row,candidates,props,deadline)
        option={"map":mapping,"numerator_polynomial":poly,"expanded":p.encode(row),
                "candidate_part":p.encode(reduced),"unresolved":p.encode(remaining),"term_proofs":proofs}
        options.append(option)
        if not remaining:
            item.update(kind="affine_polynomial",rule=p.encode(reduced),certificate=option)
            return item
    item["partial_maps"]=options
    return item

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (m.ROOT,c.ROOT,retry.ROOT,retry.m.ROOT,c.audit.ROOT,c.audit.PROOFS):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={SOURCE:SHA,RETRY:RETRY_SHA,m.SOURCE:m.SHA,c.AUDIT:c.SHA}
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Evidence SHA")
        prior=gap.read(SOURCE);common=gap.read(m.SOURCE);rr=gap.read(RETRY)
        if prior["status"]!="VP05_COMMON_RESIDUAL_NOT_CLOSURE" or len(rr["results"])!=13 or rr["unresolved"]:raise RuntimeError("Evidence scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[manifest]=n.sha(manifest)
        if common["inputs"].get(str(manifest))!=pins[manifest]:raise RuntimeError("Manifest SHA")
        candidates=set(gap.indices(x) for x in gap.read(manifest)["candidate_masters"])
        if len(candidates)!=63 or None in candidates or f.a.CAND not in candidates:raise RuntimeError("Candidate scope")
        spec=old.build_family_spec("VP05_full");props=spec.propagators
        if old.digest(old.build_kernel(props))!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        inv=inverse_polys(props)
        keys={tuple(x["integral"]) for x in prior["records"] if x["kind"]=="unresolved"}
        if len(keys)!=7:raise RuntimeError("Residual scope")
        records=[]
        for key in sorted(keys):
            f.e.b.a.memory()
            item=investigate(key,candidates,props,inv,deadline)
            records.append(item)
            v.log("VP05_STRUCTURE_RESIDUAL",**item)
        jobs=[]
        for job in prior["jobs"]:
            checks=m.apply(job["post_identity_checks"],records,candidates)
            ready=[x["target"] for x,y in zip(checks[0]["targets"],checks[1]["targets"]) if x["candidate_only"] and y["candidate_only"]]
            remaining=c.inv.residuals(checks,candidates)
            if not set(map(tuple,job["ready_targets"]))<=set(map(tuple,ready)):raise RuntimeError("Lost ready target")
            result={"sector":job["sector"],"candidate_only_before":job["candidate_only_after"],"candidate_only_after":len(ready),
                    "ready_targets":ready,"unresolved":[[list(k),x] for k,x in sorted(remaining.items())],"post_identity_checks":checks}
            jobs.append(result);v.log("VP05_STRUCTURE_JOB",**{k:x for k,x in result.items() if k!="post_identity_checks"})
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_RESIDUAL_STRUCTURE_NOT_CLOSURE","inputs":{str(k):d for k,d in pins.items()},
                 "records":records,"jobs":jobs,"generic_rational_target_proof":False,"full_closure_proven":False}
        digest=c.save(ROOT/"audit.json",payload)
        v.log("VP05_RESIDUAL_STRUCTURE_NOT_CLOSURE",residuals=7,identities=sum(x["kind"]!="unresolved" for x in records),
              candidate_only_both=sum(x["candidate_only_after"] for x in jobs),residuals_job_sum=sum(len(x["unresolved"]) for x in jobs),
              sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
