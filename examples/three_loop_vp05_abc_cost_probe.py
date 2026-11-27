"""Bounded sampled cost probe for corrected sector202, no symbolic proof."""
import argparse
import time
from pathlib import Path
from collections import Counter
from examples import three_loop_vp05_abc_custom_ids as prev
from examples.three_loop_sector203_ffrank_audit import coefficient
a=prev.a;n=a.n;gap=a.gap;old=a.old
ROOT=n.BASE/"output"/"vp05_abc_cost_probe37"
SOURCE=prev.ROOT/"report_1795817832486082100.json"
SHA="664d6e0724682f88e0952620b66072cb66ecc34d0e6cb9d019ab9401c4b4d842"
POINTS=((1000003,17,7),(1000033,19,11),(1000037,21,15))

def eliminate(row,pivots,p,free,deadline,cap,ops):
    cur=dict(row);trace={}
    while True:
        keys=[k for k in cur if k not in free]
        if not keys:break
        lead=max(keys)
        if lead not in pivots:break
        base,owner=pivots[lead];factor=cur[lead]
        trace[owner]=factor
        ops[0]+=len(base)
        if ops[0]>50_000_000 or time.monotonic()>deadline:raise TimeoutError("Operation/time budget")
        for k,v in base.items():
            x=(cur.get(k,0)-factor*v)%p
            if x:cur[k]=x
            else:cur.pop(k,None)
        if len(cur)>cap:raise RuntimeError("Fill cap")
    return cur,trace

def probe(rows,point,targets,free,deadline,cap):
    p,z,d=point;start=time.monotonic();pivots={};deps={};ops=[0];maxfill=0
    cache={}
    for idx,terms in enumerate(rows):
        if time.monotonic()>deadline:raise TimeoutError("Time budget")
        if idx%100==0:old.memory_guard()
        row={}
        for k,c in terms:
            if c not in cache:cache[c]=coefficient(c,z,d,p)
            x=(row.get(k,0)+cache[c])%p
            if x:row[k]=x
            else:row.pop(k,None)
        cur,trace=eliminate(row,pivots,p,free,deadline,cap,ops)
        nonfree=[k for k in cur if k not in free]
        # Free-only relations are retained separately as consistency diagnostics.
        if not nonfree:
            if cur:deps[idx]=None
            continue
        lead=max(nonfree);inv=pow(cur[lead],-1,p)
        pivots[lead]=({k:v*inv%p for k,v in cur.items()},idx)
        deps[idx]=list(trace)
        maxfill=max(maxfill,len(cur))
    results=[]
    for k in targets:
        cur,trace=eliminate({k:1},pivots,p,free,deadline,cap,ops)
        queue=list(trace);support=set()
        while queue:
            i=queue.pop()
            if i in support:continue
            support.add(i);queue.extend(deps[i])
        results.append({"key":list(k),"retained_only":set(cur)<=free,"remainder":[[list(j),v] for j,v in sorted(cur.items())],
                        "nonretained_terms":sum(j not in free for j in cur),"source_support":len(support),"source_ids":sorted(support)})
    return {"point":list(point),"pivot_count":len(pivots),"free_only_rows":sum(v is None for v in deps.values()),
            "max_pivot_fill":maxfill,"operations":ops[0],"elapsed_s":time.monotonic()-start,"targets":results}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);ap.add_argument("--max-fill",type=int,default=20000);args=ap.parse_args()
    if not 0<args.hours<=2 or not 1<=args.max_fill<=20000:ap.error("Cost probe cap")
    start=time.monotonic();deadline=start+args.hours*3600
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Custom report SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_ABC_CUSTOM_ID_INVENTORY_NOT_PROOF":raise RuntimeError("Custom scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    prior=gap.read(prev.SOURCE)
    targets=[tuple(r["new_key"]) for r in prior["targets"][:2]]
    free={tuple(k) for k in data["custom_keys"]}
    rows=[]
    for path in sorted((a.exact.P/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if path not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(path):
            rows.append([(tuple(map(int,t[2:4])),t[1]) for t in terms])
    if len(rows)!=2678:raise RuntimeError("SYSTEM count")
    trials=[];stop=None
    for point in POINTS:
        try:result=probe(rows,point,targets,free,deadline,args.max_fill)
        except (TimeoutError,RuntimeError,MemoryError) as exc:
            stop=str(exc);break
        trials.append(result)
        a.v.log("VP05_ABC_COST_POINT",**{**result,"targets":[{k:v for k,v in t.items() if k!="source_ids"} for t in result["targets"]]})
    payload={"status":"VP05_ABC_COST_PROBE_NOT_PROOF","inputs":{str(k):v for k,v in pins.items()},
             "trials":trials,"stop_reason":stop,"retained_keys":[list(k) for k in sorted(free)],
             "custom_physical_assignment_assumed":False,"full_closure_proven":False}
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],points_completed=len(trials),stop_reason=stop,
            all_targets_retained_only=len(trials)==3 and all(t["retained_only"] for r in trials for t in r["targets"]),
            report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
if __name__=="__main__":main()
