"""Stage 2-8b: direct parent IBP demand, not recursive closure.

Enumerate actual candidate and closure targets in unresolved parent sectors.
Generate exact symbolic IBP coefficients at those seeds only; record terms
entering the three hard subsectors, with source provenance. In addition,
inspect all proper subsector parents one line above each hard sector within
the unresolved parent masks, enumerating their bounded boundary seeds that
can directly pinch into that sector. No Kira or elimination.
"""
import argparse
import collections
import hashlib
import json
import os
import time
from examples import three_loop_vp05_target_reuse_probe as t

b=t.b
n=t.n
v=t.v
gap=t.gap
old=b.c.old
ROOT=n.BASE/"output"/"vp05_parent_demand01"
MAX_ROWS=2000000
MAX_TARGETS=200000

def sector(ex):
    return gap.sector(ex)

def scope(ex,r,s,d):
    return sum(max(a,0) for a in ex)<=r and t.degree(ex)<=s and sum(max(a-1,0) for a in ex)<=d

def boundary_seeds(parent,r,s,d):
    pos=[i for i in range(12) if parent&(1<<i)]
    neg=[i for i in range(12) if not parent&(1<<i)]
    for dots in range(min(d,r-len(pos))+1):
        for ds in old.compositions(dots,len(pos)):
            for degree in range(s+1):
                for ns in old.compositions(degree,len(neg)):
                    ex=[0]*12
                    for i,a in zip(pos,ds):ex[i]=1+a
                    for i,a in zip(neg,ns):ex[i]=-a
                    yield tuple(ex)

def exact_row(ex,entries,i,j):
    # row() is linear in d,z; expand to remove symbolic cancellations.
    raw=old.row(ex,entries,i,j,old.D)
    out={}
    for key,val in raw.items():
        val=old.sp.expand(val)
        if val!=0:out[key]=val
    return out

def evaluated_row(ex,entries,i,j,dim,p):
    return {k:v%p for k,v in old.row(ex,entries,i,j,dim).items() if v%p}

def one_line_parents(sec,parent):
    if sec&parent!=sec:return ()
    return tuple(sec|(1<<i) for i in range(12) if parent&(1<<i) and not sec&(1<<i))

def record(demand,key,source):
    if key not in demand:
        if len(demand)>=MAX_TARGETS:raise RuntimeError("Demand target cap")
        demand[key]={"count":0,"first_source":source}
    demand[key]["count"]+=1

def scan_direct(manifest,kernel,demand,deadline):
    rows=0
    for label in ("candidate_masters","closure_targets"):
        for item in manifest[label]:
            ex=gap.indices(item)
            if ex is None:raise RuntimeError("Bad manifest integral")
            for seed,parents in t.MISSING.items():
                if sector(ex) not in parents:continue
                r,s,d=(8,6,2) if seed=="r8s6d2" else (8,5,3)
                if not scope(ex,r,s,d):continue
                for (i,j),entries in kernel.items():
                    if time.monotonic()>=deadline:raise TimeoutError("Budget")
                    rows+=1
                    for key in exact_row(ex,entries,i,j):
                        if sector(key) in t.SECTORS:
                            record(demand,key,{"kind":"manifest_direct","seed":seed,"label":label,"ex":ex,"derivative":[i,j]})
    return rows

def scan_envelope(kernel,demand,deadline):
    # A single IBP can lower the positive-line count by at most one.
    # Deduplicate intermediate parent envelopes, preserving which boundary
    # jobs include each mask. These are potential direct dependencies, NOT
    # necessarily selected by Kira's recursive selection.
    jobs=collections.defaultdict(set)
    for seed,parents in t.MISSING.items():
        for parent in parents:
            for sec in t.SECTORS:
                for intermediate in one_line_parents(sec,parent):
                    jobs[seed,intermediate].add(parent)
    points=old.POINTS
    ev=[{ij:[(old.evaluate(c,p,z),tuple(old.evaluate(x,p,z) for x in cs)) for c,cs in entries] for ij,entries in kernel.items()} for p,z,d in points]
    rows=0
    for (seed,intermediate),parents in sorted(jobs.items()):
        r,s,d=(8,6,2) if seed=="r8s6d2" else (8,5,3)
        count=0;before=len(demand)
        for ex in boundary_seeds(intermediate,r,s,d):
            # Only terms pinching a line of power 1 can reach exact hard sector.
            # Use exact affine coefficient checks on potential pinch terms,
            # including cancellation among derivative contributions.
            for (i,j),entries in kernel.items():
                rows+=1;count+=1
                if rows%256==0:
                    b.a.memory()
                    if rows>MAX_ROWS or time.monotonic()>=deadline:raise TimeoutError("Envelope budget")
                # Pinch comes from a[h] unchanged/raised and a[k] decreased.
                # For h != k, a[h] must be positive or negative; if negative
                # it may also become zero but cannot add a positive line.
                raw={}
                for h,(c0,cs) in enumerate(entries):
                    if not ex[h]:continue
                    for k,c in enumerate(cs):
                        if h==k or ex[k]!=1 or not c:continue
                        key=list(ex);key[h]+=1;key[k]-=1;key=tuple(key)
                        if sector(key) in t.SECTORS:
                            raw[key]=raw.get(key,0)-ex[h]*c
                for key,val in raw.items():
                    if old.sp.expand(val)==0:continue
                    record(demand,key,{"kind":"potential_envelope","seed":seed,"intermediate":intermediate,"parents":sorted(parents),"ex":ex,"derivative":[i,j]})
        v.log("VP05_PARENT_ENVELOPE",seed=seed,intermediate=intermediate,parents=sorted(parents),rows=count,new_targets=len(demand)-before,total_targets=len(demand))
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hours",type=float,default=2)
    args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Invalid hours")
    deadline=time.monotonic()+args.hours*3600
    ROOT.mkdir(exist_ok=True)
    lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    try:
        for root in (b.ROOT,b.a.ROOT,b.c.ROOT,n.ROOT,v.ROOT,t.x.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        path=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        digest=n.sha(path);manifest=gap.read(path)
        kernel=old.build_kernel(old.build_family_spec("VP05_full").propagators)
        if old.digest(kernel)!=b.c.PIN:raise RuntimeError("Kernel differs")
        direct={};potential={}
        count=scan_direct(manifest,kernel,direct,deadline)
        v.log("VP05_PARENT_DIRECT",rows=count,targets=len(direct))
        complete=True
        try:rows=scan_envelope(kernel,potential,deadline)
        except TimeoutError as exc:
            complete=False;rows=None
            v.log("VP05_PARENT_ENVELOPE_STOP",reason=str(exc),partial_targets=len(potential))
        if n.sha(path)!=digest:raise RuntimeError("Manifest changed")
        result={"status":"VP05_PARENT_DEMAND_NOT_CLOSURE","manifest_sha256":digest,"kernel_sha256":b.c.PIN,"envelope_complete":complete,
          "direct_rows":count,"envelope_rows":rows,"direct":[[list(k),v] for k,v in sorted(direct.items())],
          "potential":[[list(k),v] for k,v in sorted(potential.items())],"recursive_demand_proven":False,"full_closure_proven":False}
        # Write unique result, never replace previous evidence.
        stamp=str(time.time_ns())
        dest=ROOT/f"demand_{stamp}.json";tmp=dest.with_suffix(".tmp")
        with tmp.open("x",encoding="utf-8") as f:
            json.dump(result,f,separators=(",",":"));f.flush();os.fsync(f.fileno())
        os.rename(tmp,dest)
        for sec in t.SECTORS:
            for label,data in (("direct",direct),("potential",potential)):
                keys=[k for k in data if sector(k)==sec]
                v.log("VP05_PARENT_DEMAND_SUMMARY",sector=sec,kind=label,targets=len(keys),
                      numerator_degree=dict(sorted(collections.Counter(t.degree(k) for k in keys).items())),
                      dot_degree=dict(sorted(collections.Counter(sum(max(a-1,0) for a in k) for k in keys).items())))
        v.log("VP05_PARENT_DEMAND_NOT_CLOSURE",artifact=str(dest),sha256=n.sha(dest),envelope_complete=complete,recursive_demand_proven=False,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
