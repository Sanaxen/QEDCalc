"""Sector202 exact S4 averaging and rank-one covariance in centered banana coordinates.

All four massive denominator lines are verified against the physical family.
Polynomial identities and DR tensor pinches are analytic; a nonzero remainder
is NOT an independence proof. No new IBP rows, Kira, or candidate revision.
"""
import argparse
import itertools
import os
import time
from pathlib import Path
from examples import three_loop_vp05_abc_residual_audit as prior
from examples import three_loop_vp05_residual_structure as s

gap=prior.gap;n=prior.n;v=prior.v;p=prior.p;f=prior.f;old=prior.old;sp=prior.sp
ROOT=n.BASE/"output"/"vp05_abc_banana26"
SOURCE=prior.ROOT/"report_1795772999855223100.json"
SHA="42a4c7c15d0976e585e3ec3ac5615f5841db166a607c1d0b561d7ffa40ff9eb0"
BASE=gap.TARGETS[2]
LINES=(1,3,6,7) # original 1-based lines 2,4,7,8
PERMS=tuple(itertools.permutations(range(4)))

def sq(x):
    return s.r.polynomial(sp.expand(x),"0")

def product(x,y):
    return sp.expand((sq(x+y)-sq(x)-sq(y))/2)

def transform(poly,mapping):
    replacement={x:product(mapping[i],mapping[j]) for x,(i,j) in zip(old.X,old.PAIRS)}
    return sp.expand(poly.subs(replacement,simultaneous=True))

def geometry(props):
    k,l,r,pp,q=old.MOM
    # New independent coordinates are represented by k,l,r = u,w,t.
    u,w,t=k,l,r
    vv=q-u-w-t
    lines=(u,vv,w,t)
    to_center=(w+t,pp+u,-w,pp,q)
    to_original=(l-pp,-r,k+r,pp,q)
    det=sp.Matrix(to_center[:3]).jacobian(old.MOM[:3]).det()
    if abs(det)!=1:raise RuntimeError("Center Jacobian")
    if tuple(sp.expand(x.subs(dict(zip(old.MOM,to_original)),simultaneous=True)) for x in to_center)!=old.MOM:
        raise RuntimeError("Inverse coordinate map")
    if tuple(sp.expand(x.subs(dict(zip(old.MOM,to_center)),simultaneous=True)) for x in to_original)!=old.MOM:
        raise RuntimeError("Reverse coordinate map")
    mom=[f.a.momentum(prop) for prop in props]
    for i,expected in zip(LINES,(-vv,u,-w,t)):
        if props[i].mass!="m2" or BASE[i]!=1 or sp.expand(mom[i].subs(dict(zip(old.MOM,to_center)),simultaneous=True)-expected)!=0:
            raise RuntimeError("Physical denominator map")
    if {i for i,x in enumerate(BASE) if x>0}!=set(LINES) or sp.expand(sum(lines)-q)!=0:raise RuntimeError("Banana scope")
    maps=[]
    for perm in PERMS:
        mapped=tuple(lines[i] for i in perm)
        mp=(mapped[0],mapped[2],mapped[3],pp,q)
        jac=sp.Matrix(mp[:3]).jacobian(old.MOM[:3]).det()
        if abs(jac)!=1 or tuple(sp.expand(x.subs(dict(zip(old.MOM,mp)),simultaneous=True)) for x in lines)!=mapped:
            raise RuntimeError("Permutation Jacobian or conservation")
        maps.append({"permutation":list(perm),"mapping":[str(x) for x in mp],"determinant":str(jac)})
    return to_center,to_original,lines,maps

def average(poly,lines):
    pp,q=old.MOM[3:]
    result=sp.expand(sum(transform(poly,(lines[i],lines[k],lines[l],pp,q)) for i,j,k,l in PERMS)/24)
    # Explicit invariance under generators of S4 (adjacent transpositions).
    for perm in ((1,0,2,3),(0,2,1,3),(0,1,3,2)):
        i,j,k,l=perm
        if transform(result,(lines[i],lines[k],lines[l],pp,q))!=result:
            raise RuntimeError("Average invariance")
    return result

def covariance(poly):
    # Denominator depends on q only. Rank-one p contractions can be
    # projected along q; scalar coefficient may depend on loop products
    # and q contractions but must not contain any p contraction.
    xs=[old.dot(i,3) for i in range(3)]
    if sp.Poly(poly,*xs).total_degree()>1:raise RuntimeError("Higher p tensor rank")
    projected=sp.expand(poly.subs({x:-old.dot(i,4)/2 for i,x in enumerate(xs)},simultaneous=True))
    if projected.free_symbols&set(xs):raise RuntimeError("p projection")
    return projected

def expand_integral(poly,to_original,props,inverse):
    raw=transform(poly,to_original)
    pp=s.polys(props)
    num=sp.Poly(sp.expand(raw.subs(inverse,simultaneous=True)),*old.Y)
    if sp.expand(num.as_expr().subs(dict(zip(old.Y,pp)),simultaneous=True)-raw)!=0:
        raise RuntimeError("Original propagator polynomial replay")
    return {tuple(x-y for x,y in zip(BASE,mon)):sp.cancel(coef) for mon,coef in num.terms() if coef},num.as_expr()

def reduce_pinches(row,props,deadline):
    top={k:x for k,x in row.items() if gap.sector(k)==202}
    lower={k:x for k,x in row.items() if gap.sector(k)!=202}
    if any(gap.sector(k)&202!=gap.sector(k) for k in lower):raise RuntimeError("Non-subsector")
    reduced,remaining,proofs=s.reduce_terms(lower,{f.a.CAND},props,deadline)
    return top,reduced,remaining,proofs

def add(row,other,scale):
    for k,x in other.items():
        value=sp.cancel(row.get(k,0)+scale*x)
        if value:row[k]=value
        else:row.pop(k,None)

def calculate(props,target,deadline):
    center,original,lines,maps=geometry(props)
    inverse=s.inverse_polys(props)
    pp=s.polys(props)
    results=[];combined={};combined_poly=sp.S.Zero
    for name,key in zip("ABC",gap.TARGETS):
        raw=sp.prod(pp[i]**(-x) for i,x in enumerate(key) if x<0)
        if tuple(max(0,x) for x in key)!=BASE:raise RuntimeError("Target denominator")
        centered=transform(raw,center)
        projected=covariance(centered)
        averaged=average(projected,lines)
        row,poly=expand_integral(averaged,original,props,inverse)
        add(combined,row,target[key]);combined_poly+=target[key]*averaged
        top,lower,remaining,proofs=reduce_pinches(row,props,deadline)
        item={"name":name,"integral":list(key),"centered_numerator":str(centered),
              "covariant_numerator":str(projected),"averaged_numerator":str(averaged),
              "propagator_polynomial":str(poly),"expanded":p.encode(row),"top":p.encode(top),
              "pinch_reduced":p.encode(lower),"pinch_unresolved":p.encode(remaining),"pinch_proofs":proofs}
        results.append(item)
        v.log("VP05_BANANA_TARGET",name=name,top_terms=len(top),pinch_terms=len(lower),unresolved_pinches=len(remaining),top=p.encode(top),pinch_reduced=p.encode(lower))
    check,_=expand_integral(sp.expand(combined_poly),original,props,inverse)
    if combined!=check:raise RuntimeError("Combined polynomial replay")
    top,lower,remaining,proofs=reduce_pinches(combined,props,deadline)
    relation=dict(top);add(relation,lower,1);add(relation,remaining,1)
    return {"geometry":{"center_map":[str(x) for x in center],"inverse_map":[str(x) for x in original],"lines":[str(x) for x in lines],"permutations":maps},
            "targets":results,"combined":{"averaged_numerator":str(sp.expand(combined_poly)),"expanded":p.encode(combined),
            "top":p.encode(top),"pinch_reduced":p.encode(lower),"pinch_unresolved":p.encode(remaining),
            "pinch_proofs":proofs,"remainder":p.encode(relation),"analytic_zero":not relation}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    start=time.monotonic();deadline=start+args.hours*3600
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as out:out.write(str(os.getpid()))
    try:
        if n.sha(SOURCE)!=SHA:raise RuntimeError("Residual audit SHA")
        data=gap.read(SOURCE)
        if data["status"]!="VP05_ABC_RESIDUAL_AUDIT_NOT_PROOF" or {tuple(x["integral"]) for x in data["structures"]}!=set(gap.TARGETS):raise RuntimeError("Residual audit scope")
        pins={Path(k):d for k,d in data["inputs"].items()};pins[SOURCE]=SHA
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input SHA")
        target=p.decode(data["target"])
        if set(target)!=set(gap.TARGETS):raise RuntimeError("Target scope")
        props=old.build_family_spec("VP05_full").propagators
        if old.digest(old.build_kernel(props))!=f.e.b.c.PIN:raise RuntimeError("Kernel")
        result=calculate(props,target,deadline)
        # Rebuild the analytic certificate before accepting the result.
        if calculate(props,target,deadline)!=result:raise RuntimeError("Analytic replay differs")
        if any(n.sha(k)!=d for k,d in pins.items()):raise RuntimeError("Protected input changed")
        status="VP05_ABC_BANANA_ANALYTIC_PROVEN_NOT_CLOSURE" if result["combined"]["analytic_zero"] else "VP05_ABC_BANANA_RESIDUAL_NOT_PROOF"
        payload={"status":status,"inputs":{str(k):d for k,d in pins.items()},"kernel_sha256":f.e.b.c.PIN,
                 "result":result,"analytic_replay_verified":True,"full_closure_proven":False,
                 "new_ibp_rows":0,"registry_changed":False}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=prior.physical.scope.c.save(dest,payload)
        v.log(status,permutations=24,top_terms=len(result["combined"]["top"]),pinch_terms=len(result["combined"]["pinch_reduced"]),
              unresolved_pinches=len(result["combined"]["pinch_unresolved"]),remainder=result["combined"]["remainder"],
              analytic_replay_verified=True,sha256=digest,report=dest.name,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
