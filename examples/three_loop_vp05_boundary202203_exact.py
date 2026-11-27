"""Shared exact DAG for saved 202/203 targets; immutable per-target replay.
Cooperative budget; completed certificates survive interruption.
"""
import argparse,time,os
from pathlib import Path
from examples import three_loop_vp05_boundary202203 as prev
from examples import three_loop_vp05_abc_correct_exact as ex
from examples.kira_physical_weight_codec import PhysicalWeightCodec,read_permutation,sector
a=prev.a;n=a.n;gap=a.gap;old=a.old;sp=a.sp
ROOT=n.BASE/"output"/"vp05_boundary_exact44"
SOURCE=prev.ROOT/"report_1795821109270661300.json"
SHA="fa3635df5c2e6dfc07c8d39ea78b74292779918ae4c6a8a9d3243319f706157b"

def expand(trace,recipes,field,deadline):
    trace=dict(trace);out={}
    while trace:
        if time.monotonic()>=deadline:raise TimeoutError("Trace deadline")
        i=max(trace);c=trace.pop(i);scale,deps=recipes[i]
        ex.add(out,{i:scale},c)
        ex.add(trace,deps,-c*scale)
    return out

def collapse(row,decode,rules,field):
    out={}
    for k,c in row.items():
        j=decode(k);ex.add(out,rules.get(j,{j:field.one}),c)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);args=ap.parse_args()
    if not 0<args.hours<=12:ap.error("Time cap")
    start=time.monotonic();deadline=start+args.hours*3600
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Boundary report SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_BOUNDARY_202203_SAVED_REDUCTION_NOT_CLOSURE":raise RuntimeError("Boundary scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    recovery=gap.read(prev.SOURCE)
    manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
    candidates={gap.indices(x) for x in gap.read(manifest)["candidate_masters"]}
    field,z,d=sp.polys.fields.field("z,d",sp.QQ)
    def coef(c):return field.from_expr(sp.sympify(str(c).replace("^","**"),locals={"z":old.Z,"d":old.D}))
    def enc(row):return [[list(k) if isinstance(k,tuple) else k,str(v.as_expr())] for k,v in sorted(row.items())]
    def dec(items,trace=False):return {(int(k) if trace else tuple(k)):coef(v) for k,v in items}
    rules={tuple(k):dec(r) for k,r in recovery["candidate_rules"]}
    if any(not set(r)<=candidates for r in rules.values()):raise RuntimeError("Rule scope")
    mapping=gap.read(prev.prev.prev.prev.SOURCE)["custom_mapping"]
    custom={tuple(k):tuple(e) for k,e,w in mapping}
    project=a.exact.P
    perm=read_permutation((project/"sectormappings/auxiliary.yaml").read_text(encoding="utf-8-sig"),"VP05_full",12)
    mod=a.exact.load_codec(a.exact.ROOT/"output/tools/pyred_weight.py")
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    codec=PhysicalWeightCodec(mod,np=12,bits=bits,iord=ordering,topsectors=[203],permutation=perm)
    def decode(k):return custom[k] if k in custom else codec.decode_key(k,custom_keys=custom)
    ready={tuple(k) for k in data["ready_keys"]}
    if len(ready)!=418 or len(data["trials"])!=3:raise RuntimeError("Ready scope")
    samples=[{tuple(t["key"]):t for t in trial["targets"]} for trial in data["trials"]]
    if any(not all(s[k]["retained_only"] for k in ready) for s in samples):raise RuntimeError("Sample scope")
    ids=sorted({i for s in samples for k in ready for i in s[k]["source_ids"]})
    rows={};seen=set();idx=0;idset=set(ids)
    for path in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if path not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(path):
            row={}
            for t in terms:
                k=tuple(map(int,t[2:4]));seen.add(k)
                if idx in idset:ex.add(row,{k:coef(t[1])},field.one)
            if idx in idset:rows[idx]=row
            idx+=1
    if idx!=2678 or set(rows)!=idset:raise RuntimeError("SYSTEM scope")
    free=set(custom)
    for k in seen-set(custom):
        if decode(k) in candidates:free.add(k)
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    try:
        results=[];pending=[];deferred=[];stop=None
        def verify(k,cert):
            if cert["source_sha256"]!=SHA or tuple(cert["key"])!=k:raise RuntimeError("Certificate scope")
            rem=dec(cert["encoded_remainder"]);trace=dec(cert["source_multipliers"],True)
            if not set(trace)<=idset or not set(rem)<=free:raise RuntimeError("Certificate support")
            expected={k:field.one};ex.add(expected,rem,-field.one)
            if ex.replay(trace,rows)!=expected:raise RuntimeError("Original replay mismatch")
            result=collapse(rem,decode,rules,field)
            if not set(result)<=candidates or enc(result)!=cert["candidate_remainder"]:raise RuntimeError("Candidate replay mismatch")
            for trial,s in zip(data["trials"],samples):
                p,zv,dv=trial["point"]
                observed={j:q for j,v in rem.items() if (q:=a.exact.modular(v.as_expr(),old.Z,old.D,(p,zv,dv)))}
                if observed!={tuple(j):v for j,v in s[k]["remainder"]}:raise RuntimeError("Sample mismatch")
            return {"key":list(k),"exponents":list(decode(k)),"source_support":len(trace),"path":str(ROOT/f"target_{k[0]}_{k[1]}.json"),"sha256":n.sha(ROOT/f"target_{k[0]}_{k[1]}.json")}
        for k in sorted(ready,key=lambda k:(samples[0][k]["source_support"],k)):
            path=ROOT/f"target_{k[0]}_{k[1]}.json"
            if time.monotonic()>=deadline:stop="Time budget";break
            if path.exists():results.append(verify(k,gap.read(path)))
            else:pending.append(k)
        if pending and not stop:
            pivots={};recipes={}
            try:
                # One shared source union, exact pivot construction once.
                for count,i in enumerate(ids,1):
                    if time.monotonic()>=deadline:raise TimeoutError("Pivot budget")
                    old.memory_guard()
                    cur,trace=ex.reduce(rows[i],pivots,free,deadline,2000)
                    nonfree=[k for k in cur if k not in free]
                    if nonfree:
                        lead=max(nonfree);scale=field.one/cur[lead]
                        pivots[lead]=({k:v*scale for k,v in cur.items()},i);recipes[i]=(scale,trace)
                    if count%100==0 or count==len(ids):
                        a.v.log("VP05_BOUNDARY_EXACT_PIVOTS",processed=count,total=len(ids),pivots=len(pivots),elapsed_s=time.monotonic()-start)
                for k in pending:
                    if time.monotonic()>=deadline:raise TimeoutError("Target budget")
                    old.memory_guard()
                    rem,trace=ex.reduce({k:field.one},pivots,free,deadline,2000)
                    if not set(rem)<=free:
                        deferred.append({"key":list(k),"reason":"Exact nonretained remainder"});continue
                    result=collapse(rem,decode,rules,field)
                    if not set(result)<=candidates:
                        deferred.append({"key":list(k),"reason":"Retained noncandidate after rules","outside":[list(j) for j in sorted(set(result)-candidates)]});continue
                    source=expand(trace,recipes,field,deadline)
                    expected={k:field.one};ex.add(expected,rem,-field.one)
                    if ex.replay(source,rows)!=expected:raise RuntimeError("Original replay mismatch")
                    for trial,s in zip(data["trials"],samples):
                        p,zv,dv=trial["point"]
                        observed={j:q for j,v in rem.items() if (q:=a.exact.modular(v.as_expr(),old.Z,old.D,(p,zv,dv)))}
                        if observed!={tuple(j):v for j,v in s[k]["remainder"]}:raise RuntimeError("Sample mismatch")
                    cert={"source_sha256":SHA,"key":list(k),"encoded_remainder":enc(rem),"candidate_remainder":enc(result),"source_multipliers":enc(source),"full_closure_proven":False}
                    path=ROOT/f"target_{k[0]}_{k[1]}.json"
                    a.scope.c.save(path,cert);results.append(verify(k,gap.read(path)))
                    if len(results)%10==0 or len(results)==len(ready):
                        a.v.log("VP05_BOUNDARY_EXACT_TARGETS",verified=len(results),total=len(ready),elapsed_s=time.monotonic()-start)
            except (TimeoutError,MemoryError) as exc:stop=str(exc)
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_BOUNDARY_202203_EXACT_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},
                 "results":results,"deferred":deferred,"stop_reason":stop,"ready":len(ready),"full_closure_proven":False}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
        a.v.log(payload["status"],verified=len(results),ready=len(ready),source_union=len(ids),deferred=len(deferred),stop_reason=stop,report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()
if __name__=="__main__":main()
