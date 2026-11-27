"""Exact bubble/tadpole numerator moments and four-line symmetry relations."""
import argparse
import itertools
import os
import time
from examples import three_loop_vp05_residual_structure as s

c=s.c;r=s.r;p=s.p;f=s.f;a=s.a;old=s.old;sp=s.sp;gap=s.gap;n=s.n;v=s.v
ROOT=n.BASE/"output"/"vp05_residual_moments18"
SOURCE=s.ROOT/"audit.json"
SHA="0b7e476d89a80abfaff8fb5931a9eaca2c099fec48adfd4f3b0b7f847d61fef8"
K71=(1,1,1,-2,0,0,1,0,0,0,0,0)
D=old.D;Z=old.Z

def bubble71(props,candidates,deadline):
    # Center independent tadpoles in k,r; bubble in l,l+q.
    mom=sp.Matrix([f.a.momentum(props[i]) for i in (0,1,6)])
    A=mom.jacobian(old.MOM[:3]);shift=(mom-A*sp.Matrix(old.MOM[:3])).applyfunc(sp.expand)
    if abs(A.det())!=1 or any(props[i].mass!="m2" for i in (0,1,2,6)):raise RuntimeError("Bubble basis")
    mapping=(A.inv()*(sp.Matrix(old.MOM[:3])-shift)).applyfunc(sp.expand)
    sub=dict(zip(old.MOM[:3],mapping))
    if any(sp.expand(f.a.momentum(props[i]).subs(sub,simultaneous=True)-want)!=0 for i,want in zip((0,1,2,6),(old.MOM[0],old.MOM[1],old.MOM[1]+old.MOM[4],old.MOM[2]))):
        raise RuntimeError("Bubble denominator check")
    N=sp.expand(f.a.momentum(props[3]).subs(sub,simultaneous=True))
    k,l,rr,pv,qv=old.MOM
    alpha=N.coeff(k);beta=N.coeff(rr)
    V=sp.expand(N-alpha*k-beta*rr)
    lam,mu,nu=(V.coeff(x) for x in (l,pv,qv))
    if sp.expand(V-lam*l-mu*pv-nu*qv)!=0:raise RuntimeError("Numerator basis")
    if props[3].mass not in ("0","m2"):raise RuntimeError("Numerator mass")
    mass=int(props[3].mass=="m2")
    t,h,j=sp.symbols("t h j")
    vsq=lam**2*t+mu**2+nu**2*Z+2*lam*mu*j+2*lam*nu*h-mu*nu*Z
    aa=alpha**2;bb=beta**2
    # J1[u^2]/J1=J1[(u^2)^2]/J1=1. Odd moments vanish;
    # <u_mu u_nu>=g_mu_nu/d for each independent tadpole.
    tad=sp.expand((vsq-mass+aa+bb)**2+4*(aa*bb+(aa+bb)*vsq)/D)
    jp=sp.Poly(tad,j)
    if jp.degree()>2:raise RuntimeError("Bubble tensor rank")
    mean=-h/2
    variance=(1-Z/4)*(t-h**2/Z)/(D-1)
    projected=sp.expand(jp.nth(0)+jp.nth(1)*mean+jp.nth(2)*(mean**2+variance))
    # q.u=(P3-P2-z)/2; u^2=P2+1, in original bubble coordinates.
    Y=old.Y
    polynomial=sp.Poly(sp.cancel(projected.subs({t:Y[1]+1,h:(Y[2]-Y[1]-Z)/2})),Y[1],Y[2])
    expanded={}
    base=f.scalar(71)
    for (i,jj),coef in polynomial.terms():
        ex=list(base);ex[1]-=i;ex[2]-=jj
        expanded[tuple(ex)]=sp.cancel(coef)
    # The two tadpoles remain represented by original positive lines1,7.
    # Pinched bubble terms reduce by verified three-line factorization.
    scalar_map=r.affine_match(base,f.scalar(78),props,deadline)
    if not scalar_map or f.scalar(78) not in candidates:raise RuntimeError("Bubble scalar candidate")
    combined={}
    for key,coef in expanded.items():
        dest=f.scalar(78) if key==base else key
        combined[dest]=combined.get(dest,0)+coef
    reduced,remaining,proofs=s.reduce_terms(combined,candidates,props,deadline)
    if remaining:raise RuntimeError("Unexpected bubble moment residual")
    return {"integral":list(K71),"sector":71,"kind":"bubble_tadpole_tensor","rule":p.encode(reduced),
            "certificate":{"centered_map":[str(x) for x in mapping],"determinant":str(A.det()),"numerator_momentum":str(N),
                           "tadpole_average":str(tad),"bubble_projection":str(projected),"propagator_polynomial":str(polynomial.as_expr()),
                           "expanded":p.encode(expanded),"scalar_map":scalar_map,"term_proofs":proofs,
                           "assumptions":["DR","m2=1","generic d and nonzero q^2=z","p^2=1,p.q=-z/2"]}}

def maps228(props,deadline):
    base=f.scalar(228);lines=r.positive(base)
    mom=[f.a.momentum(x) for x in props]
    A=sp.Matrix([mom[i] for i in lines]).jacobian(old.MOM[:3])
    rows=next(t for t in itertools.combinations(range(4),3) if A[list(t),:].det()!=0)
    inv=A[list(rows),:].inv()
    shift=[sp.expand(mom[i]-sum(A[j,k]*old.MOM[k] for k in range(3))) for j,i in enumerate(lines)]
    for perm in itertools.permutations(lines):
        if any(props[i].mass!=props[j].mass for i,j in zip(lines,perm)):continue
        for signs in itertools.product((-1,1),repeat=4):
            if time.monotonic()>=deadline:raise TimeoutError("Symmetry budget")
            mapping=(inv*sp.Matrix([signs[j]*mom[perm[j]]-shift[j] for j in rows])).applyfunc(sp.expand)
            T=mapping.jacobian(old.MOM[:3])
            if abs(T.det())!=1:continue
            sub=dict(zip(old.MOM[:3],mapping))
            if any(sp.expand(mom[i].subs(sub,simultaneous=True)-sign*mom[j])!=0 for i,j,sign in zip(lines,perm,signs)):continue
            yield {"source":list(base),"destination":list(base),"source_lines":[i+1 for i in lines],
                   "destination_lines":[i+1 for i in perm],"signs":list(signs),
                   "source_loop_in_destination":[str(x) for x in mapping],"determinant":str(T.det())}

def symmetry228(keys,candidates,props,deadline):
    base=f.scalar(228);inverse=s.inverse_polys(props);maps=list(maps228(props,deadline))
    unknown=[]
    for i,x in enumerate(base):
        if not x:
            k=list(base);k[i]=-1;k=tuple(k)
            if k not in candidates:unknown.append(k)
    # Equations from I(key)-I(transformed key)=0, including known numerator candidate.
    equations=[];evidence=[]
    numerators=[]
    for i,x in enumerate(base):
        if not x:
            k=list(base);k[i]=-1;numerators.append(tuple(k))
    for mapping in maps:
        for key in numerators:
            expanded,poly=s.affine_expansion(key,mapping,props,inverse)
            row={k:-x for k,x in expanded.items()};row[key]=row.get(key,0)+1
            row={k:sp.cancel(x) for k,x in row.items() if sp.cancel(x)!=0}
            if not row:continue
            reduced,remaining,proofs=s.reduce_terms(row,candidates,props,deadline)
            if not set(remaining)<=set(unknown):raise RuntimeError("Unexpected symmetry column")
            equations.append({**reduced,**remaining})
            evidence.append({"integral":list(key),"map":mapping,"polynomial":poly,"expanded":p.encode(expanded),
                             "equation":p.encode(equations[-1]),"term_proofs":proofs})
    # Exact row reduction with explicit original symmetry multipliers.
    field,_,_=sp.polys.fields.field("z,d",sp.QQ)
    piv={}
    for idx,eq in enumerate(equations):
        row={k:field.from_expr(x) for k,x in eq.items() if x};weights={idx:field.one}
        while True:
            leads=sorted(set(row)&set(unknown))
            if not leads:break
            k=leads[0];coef=row[k]
            if k not in piv:
                piv[k]=({j:x/coef for j,x in row.items()},{j:x/coef for j,x in weights.items()});break
            for dst,src in ((row,piv[k][0]),(weights,piv[k][1])):
                for j,x in src.items():
                    val=dst.get(j,field.zero)-coef*x
                    if val:dst[j]=val
                    else:dst.pop(j,None)
    results=[]
    for key in keys:
        row={key:field.one};weights={};free={}
        while row:
            lead=min(row,key=lambda k:(k not in unknown,k))
            coef=row[lead]
            if lead not in piv:free[lead]=row.pop(lead);continue
            for j,x in piv[lead][0].items():
                val=row.get(j,field.zero)-coef*x
                if val:row[j]=val
                else:row.pop(j,None)
            for j,x in piv[lead][1].items():weights[j]=weights.get(j,field.zero)+coef*x
        check={key:field.one}
        for idx,coef in weights.items():
            for j,x in equations[idx].items():check[j]=check.get(j,field.zero)-coef*field.from_expr(x)
        if {j:x for j,x in check.items() if x}!=free:raise RuntimeError("Symmetry certificate replay")
        ok=set(free)<=candidates
        results.append({"integral":list(key),"sector":228,"kind":"symmetry_linear" if ok else "unresolved",
                        "rule":p.encode({j:x.as_expr() for j,x in free.items()}) if ok else [],
                        "partial_remainder":p.encode({j:x.as_expr() for j,x in free.items()}),
                        "multipliers":[[i,str(x.as_expr())] for i,x in sorted(weights.items()) if x]})
    return results,{"maps":maps,"equations":evidence,"rank":len(piv),"unknowns":[list(k) for k in unknown]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        for root in (s.ROOT,s.m.ROOT,c.ROOT,s.retry.ROOT,s.retry.m.ROOT,c.audit.ROOT,c.audit.PROOFS):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        pins={SOURCE:SHA,s.RETRY:s.RETRY_SHA,s.SOURCE:s.SHA,s.m.SOURCE:s.m.SHA,c.AUDIT:c.SHA}
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Evidence SHA")
        prior=gap.read(SOURCE)
        if prior["status"]!="VP05_RESIDUAL_STRUCTURE_NOT_CLOSURE":raise RuntimeError("Prior scope")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        pins[manifest]=n.sha(manifest)
        if prior["inputs"].get(str(manifest))!=pins[manifest]:raise RuntimeError("Manifest SHA")
        candidates=set(gap.indices(x) for x in gap.read(manifest)["candidate_masters"])
        if len(candidates)!=63 or None in candidates or f.a.CAND not in candidates:raise RuntimeError("Candidate scope")
        props=old.build_family_spec("VP05_full").propagators
        if old.digest(old.build_kernel(props))!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        keys={tuple(x["integral"]) for x in prior["records"] if x["kind"]=="unresolved"}
        if len(keys)!=3 or K71 not in keys or any(gap.sector(k)!=228 for k in keys-{K71}):raise RuntimeError("Residual scope")
        f.e.b.a.memory()
        one=bubble71(props,candidates,deadline);v.log("VP05_MOMENT_BUBBLE",**one)
        two,proof=symmetry228(sorted(keys-{K71}),candidates,props,deadline)
        v.log("VP05_MOMENT_SYMMETRY",maps=len(proof["maps"]),equations=len(proof["equations"]),rank=proof["rank"],results=two)
        records=[one,*two];jobs=[]
        for job in prior["jobs"]:
            checks=s.m.apply(job["post_identity_checks"],records,candidates)
            ready=[x["target"] for x,y in zip(checks[0]["targets"],checks[1]["targets"]) if x["candidate_only"] and y["candidate_only"]]
            remaining=c.inv.residuals(checks,candidates)
            if not set(map(tuple,job["ready_targets"]))<=set(map(tuple,ready)):raise RuntimeError("Lost ready target")
            result={"sector":job["sector"],"candidate_only_before":job["candidate_only_after"],"candidate_only_after":len(ready),
                    "ready_targets":ready,"unresolved":[[list(k),x] for k,x in sorted(remaining.items())],"post_identity_checks":checks}
            jobs.append(result);v.log("VP05_MOMENT_JOB",**{k:x for k,x in result.items() if k!="post_identity_checks"})
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_RESIDUAL_MOMENTS_NOT_CLOSURE","inputs":{str(k):d for k,d in pins.items()},
                 "records":records,"symmetry_certificate":proof,"jobs":jobs,"generic_rational_target_proof":False,"full_closure_proven":False}
        digest=c.save(ROOT/"audit.json",payload)
        v.log("VP05_RESIDUAL_MOMENTS_NOT_CLOSURE",residuals=3,identities=sum(x["kind"]!="unresolved" for x in records),
              candidate_only_both=sum(x["candidate_only_after"] for x in jobs),residuals_job_sum=sum(len(x["unresolved"]) for x in jobs),
              sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
