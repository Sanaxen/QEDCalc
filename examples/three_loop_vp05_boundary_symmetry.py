"""Exact denominator-permutation and numerator polynomial scope audit.
Do not discard seeds on the basis of denominator symmetry alone.
"""
import argparse,time,itertools
from pathlib import Path
from examples import three_loop_vp05_abc_banana as banana
from examples import three_loop_vp05_boundary_incremental_ibp as inc
a=inc.a;n=a.n;gap=a.gap;old=banana.old;sp=banana.sp
ROOT=n.BASE/"output"/"vp05_boundary_symmetry47"
SOURCE=inc.ROOT/"report_1795826171376540700.json"
SHA="fda9651d15e9e05e1ffb95b929045ee1f954630fe334d84e5d561177ef9f94d7"

def permutation_of_polynomials(transformed,original):
    perm=[]
    for x in transformed:
        hits=[i for i,y in enumerate(original) if sp.expand(x-y)==0]
        if len(hits)!=1:return None
        perm.append(hits[0])
    return tuple(perm) if len(set(perm))==len(original) else None

def act(ex,perm):
    out=[0]*len(ex)
    for i,j in enumerate(perm):out[j]=ex[i]
    return tuple(out)

def orbits(keys,perms):
    unseen=set(keys);result=[]
    while unseen:
        k=min(unseen);orbit={act(k,p) for p in perms}
        if not orbit<=unseen:raise RuntimeError("Nonclosed orbit or non-group")
        unseen.difference_update(orbit);result.append((k,len(orbit)))
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=2:ap.error("Time cap")
    start=time.monotonic();deadline=start+args.hours*3600
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Incremental report SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_BOUNDARY_INCREMENTAL_IBP_NOT_CLOSURE" or len(data["jobs"])!=4 or sum(j["rows"] for j in data["jobs"])!=11520:raise RuntimeError("Incremental scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    for job in data["jobs"]:
        for item in job["batches"]:
            path=inc.ROOT/item["path"]
            if path.parent!=inc.ROOT:raise RuntimeError("Batch path")
            pins[path]=item["sha256"]
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    props=old.build_family_spec("VP05_full").propagators
    if old.digest(old.build_kernel(props))!=banana.f.e.b.c.PIN:raise RuntimeError("Kernel")
    center,original,lines,maps=banana.geometry(props)
    polynomials=banana.s.polys(props)
    centered=[banana.transform(x,center) for x in polynomials]
    inverse=banana.s.inverse_polys(props)
    pp,q=old.MOM[3:]
    records=[];perms={202:[],203:[]}
    for perm in banana.PERMS:
        if time.monotonic()>=deadline:raise TimeoutError("Symmetry budget")
        i,j,k,l=perm;mp=(lines[i],lines[k],lines[l],pp,q)
        transformed=[banana.transform(banana.transform(x,mp),original) for x in centered]
        # Check the complete affine propagator polynomial map and its inverse
        # representation, not just the four active denominators.
        expressions=[]
        for x in transformed:
            y=sp.expand(x.subs(inverse,simultaneous=True))
            poly=sp.Poly(y,*old.Y)
            if poly.total_degree()>1:raise RuntimeError("Non-affine propagator map")
            replay=sp.Poly(sp.expand(y.subs(dict(zip(old.Y,polynomials)),simultaneous=True)-x),*old.X)
            if any(sp.cancel(c)!=0 for _,c in replay.terms()):raise RuntimeError("Affine map replay")
            expressions.append(str(y))
        perm12=permutation_of_polynomials(transformed,polynomials)
        active={}
        for sec in (202,203):
            support={i for i in range(12) if sec&(1<<i)}
            hits=[{j for j,y in enumerate(polynomials) if sp.expand(transformed[i]-y)==0} for i in sorted(support)]
            active[str(sec)]=all(len(h)==1 for h in hits) and set().union(*hits)==support
            if active[str(sec)] and perm12 is not None:perms[sec].append(perm12)
        records.append({"banana_permutation":list(perm),"affine_map":expressions,"full_permutation":list(perm12) if perm12 is not None else None,"active_support_preserved":active})
    jobs=[]
    for sec,s,d in inc.JOBS:
        group=sorted(set(perms[sec]))
        identity=tuple(range(12))
        if identity not in group or any(tuple(q[p[i]] for i in range(12)) not in group for p in group for q in group):raise RuntimeError("Permutation subgroup")
        keys=list(inc.envelope.envelope(sec,8,s,d))
        reps=orbits(keys,group)
        item={"sector":sec,"s":s,"d":d,"envelope_seeds":len(keys),"active_symmetries":sum(r["active_support_preserved"][str(sec)] for r in records),"full_propagator_permutations":len(group),"orbit_count":len(reps),"orbit_sizes":{str(i):sum(v==i for _,v in reps) for i in sorted({v for _,v in reps})},"representatives":[[list(k),v] for k,v in reps]}
        jobs.append(item);a.v.log("VP05_BOUNDARY_SYMMETRY_SCOPE",**{k:v for k,v in item.items() if k!="representatives"})
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    payload={"status":"VP05_BOUNDARY_SYMMETRY_SCOPE_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},"maps":records,"jobs":jobs,"ibp_operator_equivalence_verified":False,"full_closure_proven":False}
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],maps=len(records),jobs=len(jobs),report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
if __name__=="__main__":main()
