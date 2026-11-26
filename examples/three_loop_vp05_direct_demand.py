"""Read-only reduction of the twelve observed direct parent demands.
Record modular substitution traces, not exact original-source certificates.
"""
import collections
import gc
import json
import os
import time
from examples import three_loop_vp05_parent_demand as q

t=q.t
b=t.b
n=t.n
v=t.v
gap=t.gap
ROOT=n.BASE/"output"/"vp05_direct_demand02"
SOURCE=q.ROOT/"demand_1795660139834708900.json"
SHA="3b54c0111b53042b612ef6ca92ff31013e94e5b11844d8e5e35b5b03a0d0f503"
CAP=2000000

def validate(source,manifest,kernel,deadline):
    if n.sha(source)!=SHA:raise RuntimeError("Demand artifact SHA mismatch")
    obj=gap.read(source)
    if obj["status"]!="VP05_PARENT_DEMAND_NOT_CLOSURE" or obj["kernel_sha256"]!=b.c.PIN or obj["direct_rows"]!=2070 or obj["envelope_complete"] is not False:
        raise RuntimeError("Demand artifact scope")
    direct={}
    count=q.scan_direct(manifest,kernel,direct,deadline)
    saved={tuple(k):val for k,val in obj["direct"]}
    # JSON converts tuple provenance to list; compare serialized values.
    if count!=2070 or len(obj["direct"])!=12 or len(saved)!=12 or json.dumps([[list(k),val] for k,val in sorted(direct.items())],sort_keys=True)!=json.dumps(obj["direct"],sort_keys=True):
        raise RuntimeError("Direct regeneration mismatch")
    if collections.Counter(gap.sector(k) for k in saved)!={196:7,200:5}:raise RuntimeError("Sector scope")
    if any(t.degree(k)>2 or sum(max(a-1,0) for a in k)>1 for k in saved):raise RuntimeError("Degree scope")
    return obj,saved

def reduce_target(ex,stores,p,deadline=float("inf")):
    cur={b.c.key(ex):1};free={};trace=[];ops=0
    while cur:
        if time.monotonic()>=deadline:raise TimeoutError("Direct reduction budget")
        if len(cur)+len(free)>t.MAX_FILL or ops>CAP:raise RuntimeError("Direct reduction cap")
        lead=max(cur)
        match=next(((s,st) for s,st in enumerate(stores) if lead in st.piv),None)
        if match is None:
            free[lead]=cur.pop(lead);continue
        shell,store=match
        factor=cur[lead]
        items=list(store.items(lead))
        if not items or dict(items).get(lead)!=1 or max(k for k,_ in items)!=lead:raise RuntimeError("Nontriangular pivot")
        if ops+len(items)>CAP:raise RuntimeError("Direct operation cap")
        trace.append({"shell":shell,"lead":list(b.c.decode(lead)),"factor":factor})
        for k,val in items:
            a=(cur.get(k,0)-factor*val)%p
            if a:cur[k]=a
            else:cur.pop(k,None)
        ops+=len(items)
        if len(trace)%64==0:b.a.memory()
    return {"target":list(ex),"remainder":[[list(b.c.decode(k)),val] for k,val in sorted(free.items())],"operations":ops,"trace":trace}

def replay(result,stores,p,deadline=float("inf")):
    # Replay the stored relation against the normalized modular pivots.
    # This is NOT a replay against the original symbolic IBP rows.
    cur={b.c.key(result["target"]):1}
    for step in result["trace"]:
        if time.monotonic()>=deadline:raise TimeoutError("Replay budget")
        lead=b.c.key(step["lead"]);factor=step["factor"]
        if cur.get(lead)!=factor or not 0<factor<p:raise RuntimeError("Trace factor")
        for k,val in stores[step["shell"]].items(lead):
            a=(cur.get(k,0)-factor*val)%p
            if a:cur[k]=a
            else:cur.pop(k,None)
    expected={b.c.key(k):val for k,val in result["remainder"]}
    if cur!=expected:raise RuntimeError("Trace replay mismatch")

def main():
    deadline=time.monotonic()+3600
    ROOT.mkdir(exist_ok=True)
    lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    try:
        for root in (q.ROOT,b.ROOT,b.a.ROOT,b.c.ROOT,n.ROOT,v.ROOT,t.x.ROOT):
            if (root/"running.lock").exists():raise RuntimeError("Other engine lock")
        stage=gap.inspect()
        if stage["status"]!="VP05_STAGE2_BOUNDARY_GAPS_REMAIN" or stage["canonical_candidate_count"]!=63:raise RuntimeError("Stage scope")
        path=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
        digest=n.sha(path);manifest=gap.read(path)
        kernel=b.c.old.build_kernel(b.c.old.build_family_spec("VP05_full").propagators)
        if b.c.old.digest(kernel)!=b.c.PIN:raise RuntimeError("Kernel differs")
        obj,direct=validate(SOURCE,manifest,kernel,deadline)
        if obj["manifest_sha256"]!=digest:raise RuntimeError("Manifest SHA mismatch")
        pins={SOURCE:SHA,path:digest}
        results=[];comparisons=[]
        v.log("VP05_DIRECT_DEMAND_REGENERATED",rows=2070,targets=len(direct),source_sha256=SHA)
        for sec in (196,200):
            pair=[]
            targets=sorted(k for k in direct if gap.sector(k)==sec)
            for point in range(2):
                p=b.c.old.POINTS[point][0];stores=[]
                for s in range(4):
                    if s<2:store=t.low_shell(sec,s,point,kernel)
                    else:
                        source=b.a.state_path(sec,s,point);h=n.sha(source)
                        cursor,store,_,_=b.read_legacy(sec,s,point,p)
                        if cursor!=b.c.expected(s) or n.sha(source)!=h:raise RuntimeError("Lower shell mismatch")
                        pins[source]=h
                    stores.append(store)
                source,h,store=t.load_s4(sec,point);pins[source]=h;stores.append(store)
                rows=[]
                for ex in targets:
                    b.a.memory()
                    result=reduce_target(ex,stores,p,deadline)
                    replay(result,stores,p,deadline)
                    result.update({"sector":sec,"point":point,"field":list(b.c.old.POINTS[point]),"source":direct[ex],"pivot_replay":True})
                    rows.append(result)
                    v.log("VP05_DIRECT_DEMAND_REDUCED",sector=sec,point=point,target=list(ex),remaining_terms=len(result["remainder"]),remainder=result["remainder"][:32],operations=result["operations"],shells=sorted({s["shell"] for s in result["trace"]}),pivot_replay=True)
                pair.append(rows);results.extend(rows)
                del store,stores
                gc.collect()
            for left,right in zip(*pair):
                if left["target"]!=right["target"]:raise RuntimeError("Target order")
                a=[k for k,_ in left["remainder"]];c=[k for k,_ in right["remainder"]]
                row={"sector":sec,"target":left["target"],"support_match":a==c,"remaining_counts":[len(a),len(c)],"max_numerator_degree":[max(map(t.degree,keys),default=0) for keys in (a,c)]}
                comparisons.append(row);v.log("VP05_DIRECT_DEMAND_COMPARE",**row)
        if any(n.sha(path)!=h for path,h in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_DIRECT_DEMAND_NOT_CLOSURE","input_sha256":{str(path):h for path,h in pins.items()},"kernel_sha256":b.c.PIN,"results":results,"comparisons":comparisons,"original_symbolic_replay":False,"recursive_demand_proven":False,"full_closure_proven":False}
        dest=ROOT/f"reduction_{time.time_ns()}.json";tmp=dest.with_suffix(".tmp")
        with tmp.open("x",encoding="utf-8") as f:
            json.dump(payload,f,separators=(",",":"));f.flush();os.fsync(f.fileno())
        os.rename(tmp,dest)
        if gap.read(dest)!=payload:raise RuntimeError("Saved artifact mismatch")
        v.log("VP05_DIRECT_DEMAND_NOT_CLOSURE",artifact=str(dest),sha256=n.sha(dest),targets=12,point_results=len(results),support_matches=sum(r["support_match"] for r in comparisons),inputs_unchanged=True,original_symbolic_replay=False,full_closure_proven=False)
    finally:lock.unlink()

if __name__=="__main__":main()
