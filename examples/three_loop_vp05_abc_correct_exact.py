"""Exact sparse QQ(z,d) reduction on corrected modular dependency union.
Resume at completed source rows; verify expanded original-source multipliers.
No physical custom-ID assignment or closure claim.
"""
import argparse,json,time,os
from pathlib import Path
from examples import three_loop_vp05_abc_cost_probe as prev
a=prev.a;n=a.n;gap=a.gap;old=a.old;sp=a.sp
ROOT=n.BASE/"output"/"vp05_abc_correct_exact38"
SOURCE=prev.ROOT/"report_1795818340202992800.json"
SHA="24044bbd102763376d4513860e225681381d585ac2ab400b7a1771cea256e98e"

def add(row,other,factor):
    for k,v in other.items():
        x=row.get(k,0)+factor*v
        if x:row[k]=x
        else:row.pop(k,None)

def reduce(row,pivots,free,deadline,cap):
    cur=dict(row);trace={}
    while True:
        nonfree=[k for k in cur if k not in free]
        if not nonfree:break
        lead=max(nonfree)
        if lead not in pivots:break
        if time.monotonic()>=deadline:raise TimeoutError("Time budget")
        base,owner=pivots[lead];factor=cur[lead]
        trace[owner]=factor
        add(cur,base,-factor)
        if len(cur)>cap:raise RuntimeError("Fill cap")
    return cur,trace

def replay(trace,rows):
    out={}
    for i,c in trace.items():add(out,rows[i],c)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);ap.add_argument("--max-fill",type=int,default=2000);args=ap.parse_args()
    if not 0<args.hours<=12 or not 1<=args.max_fill<=20000:ap.error("Safety caps")
    start=time.monotonic();deadline=start+args.hours*3600
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Cost report SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_ABC_COST_PROBE_NOT_PROOF" or len(data["trials"])!=3:raise RuntimeError("Cost scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    trials=data["trials"];free={tuple(k) for k in data["retained_keys"]}
    targets=[tuple(t["key"]) for t in trials[0]["targets"]]
    if any(not t["retained_only"] for r in trials for t in r["targets"]):raise RuntimeError("Unresolved sample")
    ids=sorted({i for r in trials for t in r["targets"] for i in t["source_ids"]})
    field,z,d=sp.polys.fields.field("z,d",sp.QQ)
    def coef(c):return field.from_expr(sp.sympify(c.replace("^","**"),locals={"z":old.Z,"d":old.D}))
    rows={};idx=0
    for path in sorted((a.exact.P/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if path not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(path):
            if idx in ids:
                row={}
                for t in terms:add(row,{tuple(map(int,t[2:4])):coef(t[1])},field.one)
                rows[idx]=row
            idx+=1
    if idx!=2678 or set(rows)!=set(ids):raise RuntimeError("Source scope")
    ROOT.mkdir(exist_ok=True);cp=ROOT/"checkpoint.json";lock=ROOT/"running.lock"
    def enc(row):return [[list(k) if isinstance(k,tuple) else k,str(v.as_expr())] for k,v in sorted(row.items())]
    def dec(items,trace=False):return {(int(k) if trace else tuple(k)):coef(v) for k,v in items}
    def save(payload):
        tmp=ROOT/"checkpoint.tmp"
        tmp.write_text(json.dumps(payload),encoding="utf-8")
        if json.loads(tmp.read_text(encoding="utf-8"))!=payload:raise RuntimeError("Checkpoint reread")
        os.replace(tmp,cp)
    with lock.open("x") as f:f.write(str(os.getpid()))
    try:
        pivots={};recipes={};processed=0
        if cp.exists():
            saved=gap.read(cp)
            if saved["source_sha"]!=SHA or saved["ids"]!=ids:raise RuntimeError("Checkpoint scope")
            processed=saved["processed"]
            if not 0<=processed<=len(ids):raise RuntimeError("Checkpoint progress")
            for item in saved["pivots"]:
                lead=tuple(item["lead"]);owner=item["owner"];row=dec(item["row"])
                if owner not in ids[:processed] or row.get(lead)!=field.one or lead!=max(k for k in row if k not in free):raise RuntimeError("Checkpoint pivot")
                pivots[lead]=(row,owner)
                recipes[owner]=(coef(item["scale"]),dec(item["trace"],True))
            # Independently replay each local DAG edge against original row.
            byowner={owner:row for row,owner in pivots.values()}
            for owner,(scale,trace) in recipes.items():
                rr=dict(rows[owner])
                for j,c in trace.items():
                    if j>=owner:raise RuntimeError("Checkpoint dependency order")
                    add(rr,byowner[j],-c)
                if {k:v*scale for k,v in rr.items()}!=byowner[owner]:raise RuntimeError("Checkpoint local replay")
        def checkpoint():
            save({"source_sha":SHA,"ids":ids,"processed":processed,"pivots":[{"lead":list(k),"owner":i,"row":enc(r),"scale":str(recipes[i][0].as_expr()),"trace":enc(recipes[i][1])} for k,(r,i) in sorted(pivots.items())]})
        stop=None
        try:
            for i in ids[processed:]:
                if time.monotonic()>=deadline:raise TimeoutError("Time budget")
                old.memory_guard()
                cur,trace=reduce(rows[i],pivots,free,deadline,args.max_fill)
                nonfree=[k for k in cur if k not in free]
                if nonfree:
                    lead=max(nonfree);scale=field.one/cur[lead]
                    normalized={k:v*scale for k,v in cur.items()}
                    pivots[lead]=(normalized,i);recipes[i]=(scale,trace)
                processed+=1
                if processed%5==0 or processed==len(ids):
                    checkpoint()
                    a.v.log("VP05_ABC_EXACT_PROGRESS",processed=processed,total=len(ids),pivots=len(pivots),elapsed_s=time.monotonic()-start)
        except (TimeoutError,MemoryError,RuntimeError) as exc:
            stop=str(exc);checkpoint()
        results=[]
        if processed==len(ids):
            try:
                for k in targets:
                    cur,trace=reduce({k:field.one},pivots,free,deadline,args.max_fill)
                    # Expand backwards in source-row order, avoiding repeated recursive expansion.
                    source={}
                    while trace:
                        if time.monotonic()>=deadline:raise TimeoutError("Trace budget")
                        i=max(trace);c=trace.pop(i);scale,deps=recipes[i]
                        add(source,{i:scale},c)
                        add(trace,deps,-c*scale)
                    expected={k:field.one};add(expected,cur,-field.one)
                    if replay(source,rows)!=expected:raise RuntimeError("Original source replay mismatch")
                    samples=[]
                    for trial in trials:
                        p,zv,dv=trial["point"]
                        observed={j:q for j,v in cur.items() if (q:=a.exact.modular(v.as_expr(),old.Z,old.D,(p,zv,dv)))}
                        target=next(t for t in trial["targets"] if tuple(t["key"])==k)
                        samples.append(observed=={tuple(j):v for j,v in target["remainder"]})
                    if not all(samples):raise RuntimeError("Sample replay mismatch")
                    result={"key":list(k),"retained_only":set(cur)<=free,"remainder":enc(cur),"source_multipliers":enc(source),"original_encoded_source_replay":True,"sample_replay":samples}
                    results.append(result)
                    a.v.log("VP05_ABC_EXACT_TARGET",key=list(k),retained_only=result["retained_only"],remainder=result["remainder"],source_support=len(source),sample_replay=samples)
            except (TimeoutError,MemoryError,RuntimeError) as exc:stop=str(exc)
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
        status="VP05_ABC_CORRECT_ENCODED_EXACT_REPLAY" if len(results)==2 and all(t["retained_only"] for t in results) else "VP05_ABC_CORRECT_EXACT_INCOMPLETE"
        payload={"status":status,"inputs":{str(k):v for k,v in pins.items()},"processed":processed,"total":len(ids),"results":results,"stop_reason":stop,"physical_custom_mapping_verified":False,"full_closure_proven":False}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
        a.v.log(status,processed=processed,total=len(ids),targets_verified=len(results),stop_reason=stop,report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()
if __name__=="__main__":main()
