"""Read-only target-oriented reuse probe before expanding to s5/s6.

Independent shell pivots are valid modular relations but their union is not
necessarily an echelon basis. Deterministic substitution is NOT cumulative
Gaussian elimination or a proof that a nonzero remainder is irreducible.
"""
import gc
import hashlib
import json
import time
from collections import Counter
from examples import three_loop_vp05_native_batch as x
from examples import three_loop_vp05_stage2_step93_gap_audit as gap

b=x.b
n=x.n
v=x.v
SECTORS=(69,196,200)
RANKS={69:43732,196:46280,200:46280}
TERMS={(69,0):15365823,(69,1):15368744,(196,0):37355607,
       (196,1):37361354,(200,0):18828945,(200,1):18830204}
MISSING={"r8s6d2":(202,203,204,205,206,207,228,229,230,231,234,237,238,239),
         "r8s5d3":(202,203,206,207,234,238,239)}
MAX_OPS=2000000
MAX_FILL=20000

def degree(ex):
    return sum(-a for a in ex if a<0)

def load_s4(sec,point):
    if sec==69:
        path=b.ROOT/f"sec{sec}_s4_p{point}.bin";m=b.meta(sec,4,point)
    elif sec==196 and point==0:
        path=v.ROOT/"sec196_s4_p0.bin";m=v.META
    else:
        path=x.ROOT/f"sec{sec}_s4_p{point}.bin"
        source=x.source_for(sec,point)
        m=x.meta(sec,point,n.sha(source) if source else "empty")
    digest=n.sha(path)
    cursor,store,_,_=b.load(path,m,b.c.old.POINTS[point][0])
    if (cursor,len(store.piv),store.terms)!=(74250,RANKS[sec],TERMS[sec,point]) or n.sha(path)!=digest:
        raise RuntimeError("s4 observed state mismatch")
    return path,digest,store

def low_shell(sec,s,point,kernel):
    p,z,d=b.c.old.POINTS[point]
    ev={ij:[(b.c.old.evaluate(c,p,z),tuple(b.c.old.evaluate(y,p,z) for y in cs)) for c,cs in entries] for ij,entries in kernel.items()}
    store=b.Packed()
    for i,(ex,j,k) in enumerate(b.c.rows(sec,s)):
        if i%64==0:b.a.memory()
        lead,row=b.reduce(b.c.old.row(ex,ev[j,k],j,k,d),store,p,b.CAP)
        if lead is not None:store.add(i,lead,row.items())
    rank=127 if s==0 else 959 if sec==69 else 987
    if len(store.piv)!=rank:raise RuntimeError("Low shell rank mismatch")
    return store

def substitute(target,stores,p,deadline=float("inf"),cap=MAX_OPS):
    """Reduce by any available triangular pivot, then retain free terms."""
    cur={target:1};free={};ops=0;used=Counter()
    while cur:
        if len(cur)+len(free)>MAX_FILL or ops>cap:
            return None,dict(used),ops,"cap"
        if time.monotonic()>=deadline:raise TimeoutError("Target probe time budget")
        lead=max(cur)
        found=next(((s,st) for s,st in enumerate(stores) if lead in st.piv),None)
        if found is None:
            free[lead]=cur.pop(lead);continue
        s,st=found;factor=cur[lead];used[s]+=1
        for k,val in st.items(lead):
            value=(cur.get(k,0)-factor*val)%p
            if value:cur[k]=value
            else:cur.pop(k,None)
            ops+=1
        if sum(used.values())%64==0:b.a.memory()
    return free,dict(used),ops,"zero" if not free else "nonzero"

def inventory(manifest,sec):
    targets={}
    for kind in ("candidate_masters","closure_targets"):
        for item in manifest[kind]:
            ex=gap.indices(item)
            if ex is None:raise RuntimeError("Invalid manifest integral")
            if gap.sector(ex)==sec:targets.setdefault(ex,set()).add(kind)
    # Explicit ten scalar/dot targets from the former r5s6d2 Kira pilot.
    pos=[i for i in range(12) if sec&(1<<i)]
    scalar=tuple(int(i in pos) for i in range(12))
    targets.setdefault(scalar,set()).add("scalar_dot_diagnostic")
    for i in pos:
        for j in [None]+[k for k in pos if k>=i]:
            ex=list(scalar);ex[i]+=1
            if j is not None:ex[j]+=1
            targets.setdefault(tuple(ex),set()).add("scalar_dot_diagnostic")
    return targets

def summarize(ex,labels,stores,p,deadline):
    target=b.c.key(ex)
    free,used,ops,state=substitute(target,stores,p,deadline)
    result={"target":list(ex),"labels":sorted(labels),"degree":degree(ex),
            "direct_pivot_shells":[s for s,st in enumerate(stores) if target in st.piv],
            "state":state,"operations":ops,"used_shells":used}
    if free is not None:
        support=sorted(free)
        result.update({"remaining_terms":len(free),
          "remaining_degree_histogram":dict(sorted(Counter(degree(b.c.decode(k)) for k in free).items())),
          "remaining_sector_histogram":dict(sorted(Counter(gap.sector(b.c.decode(k)) for k in free).items())),
          "support_sha256":hashlib.sha256(repr(support).encode()).hexdigest(),
          "coefficient_sha256":hashlib.sha256(repr(sorted(free.items())).encode()).hexdigest(),
          "frontier_degree_4_to_7":[list(b.c.decode(k)) for k in support if 4<=degree(b.c.decode(k))<=7][:32],
          "frontier_count":sum(4<=degree(b.c.decode(k))<=7 for k in support)})
    return result

def main():
    deadline=time.monotonic()+3600
    for root in (b.ROOT,b.a.ROOT,b.c.ROOT,n.ROOT,v.ROOT,x.ROOT):
        if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
    stage=gap.inspect()
    if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:
        raise RuntimeError("Standard scope changed")
    path=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
    manifest=gap.read(path);pins={path:n.sha(path)}
    if not isinstance(manifest.get("closure_targets"),list) or not manifest["closure_targets"]:
        raise RuntimeError("Missing closure target list")
    kernel=b.c.old.build_kernel(b.c.old.build_family_spec("VP05_full").propagators)
    if b.c.old.digest(kernel)!=b.c.PIN:raise RuntimeError("Kernel differs")
    for sec in SECTORS:
        targets=inventory(manifest,sec)
        parents={seed:[s for s in missing if (s&sec)==sec] for seed,missing in MISSING.items()}
        v.log("VP05_TARGET_SCOPE",sector=sec,targets=len(targets),candidate_targets=sum("candidate_masters" in k for k in targets.values()),closure_targets=sum("closure_targets" in k for k in targets.values()),missing_parent_sectors_bitwise_only=parents)
        pair=[]
        for point in range(2):
            p=b.c.old.POINTS[point][0];stores=[]
            for s in range(4):
                if s<2:store=low_shell(sec,s,point,kernel)
                else:
                    source=b.a.state_path(sec,s,point);digest=n.sha(source)
                    cursor,store,_,_=b.read_legacy(sec,s,point,p)
                    if cursor!=b.c.expected(s) or n.sha(source)!=digest:raise RuntimeError("Lower shell changed")
                    pins[source]=digest
                stores.append(store)
            source,digest,store=load_s4(sec,point);pins[source]=digest;stores.append(store)
            v.log("VP05_TARGET_PIVOT_INVENTORY",sector=sec,point=point,ranks=[len(st.piv) for st in stores],terms=[st.terms for st in stores])
            results=[]
            for ex,labels in sorted(targets.items()):
                b.a.memory()
                result=summarize(ex,labels,stores,p,deadline)
                v.log("VP05_TARGET_REMAINDER",sector=sec,point=point,**result)
                results.append(result)
            pair.append(results)
            del stores,store
            gc.collect()
        for left,right in zip(*pair):
            if left["target"]!=right["target"]:raise RuntimeError("Target order")
            v.log("VP05_TARGET_POINT_COMPARE",sector=sec,target=left["target"],labels=left["labels"],
                  states=[left["state"],right["state"]],
                  support_match=(left.get("support_sha256")==right.get("support_sha256")) if "support_sha256" in left and "support_sha256" in right else None,
                  frontier_counts=[left.get("frontier_count"),right.get("frontier_count")])
    if any(n.sha(path)!=digest for path,digest in pins.items()):raise RuntimeError("Protected input changed")
    v.log("VP05_TARGET_REUSE_PROBE_NOT_CLOSURE",inputs_unchanged=True,full_closure_proven=False,
          cumulative_rowspace_proven=False,parents_equivalent=False,s5_s6_executed=False)

if __name__=="__main__":main()
