"""Incremental physical IBPs at four boundary envelopes.
Persist exact source batches; rank diagnostics on cumulative saved+new rows.
No claim that sampled seed subsets cover Kira's complete boundary.
"""
import argparse,time,os
from pathlib import Path
from examples import three_loop_vp05_boundary_rank as rank
from examples import three_loop_vp05_abc_physical as physical
from examples import three_loop_vp05_boundary202203 as envelope
a=rank.a;n=a.n;gap=a.gap;old=a.old
ROOT=n.BASE/"output"/"vp05_boundary_incremental46"
SOURCE=rank.ROOT/"report_1795825664998317100.json"
SHA="0897ef813fe557207243a998dcf2a65d41eb8e0deaf85bbc3c9c73110c97e8c7"
JOBS=((202,6,2),(202,5,3),(203,6,2),(203,5,3))
BATCH=24

def degrees(k):
    return sum(max(-x,0) for x in k),sum(max(x-1,0) for x in k)

def schedule(sec,s,d,candidates,rules):
    # Prioritize candidate seeds, then boundary shell and nearby known rules.
    allkeys=list(envelope.envelope(sec,8,s,d))
    def order(k):
        ns,nd=degrees(k)
        shell=ns==s if s==6 else nd==d
        return (k not in candidates,not shell,k not in rules,ns+nd,k)
    return sorted(allkeys,key=order)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=12);ap.add_argument("--batches",type=int,default=8);args=ap.parse_args()
    if not 0<args.hours<=12 or not 1<=args.batches<=64:ap.error("Safety cap")
    start=time.monotonic();deadline=start+args.hours*3600
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Rank report SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_BOUNDARY_SAVED_RANK_NOT_CLOSURE" or not data["substitution_rank_consistent"] or not data["saved_SYSTEM_independence_certified_by_row_bound"]:raise RuntimeError("Rank scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
    candidates={gap.indices(x) for x in gap.read(manifest)["candidate_masters"]}
    if len(candidates)!=63 or manifest not in pins:raise RuntimeError("Candidate scope")
    exact=gap.read(rank.SOURCE);recovery=gap.read(rank.prev.prev.SOURCE)
    rules={tuple(k):{tuple(j):v for j,v in r} for k,r in recovery["candidate_rules"]}
    for item in exact["results"]:
        path=Path(item["path"])
        if pins.get(path)!=item["sha256"]:raise RuntimeError("Unpinned certificate")
        cert=gap.read(path);k=tuple(item["exponents"])
        if k in rules or cert["key"]!=item["key"]:raise RuntimeError("Rule scope")
        rules[k]={tuple(j):v for j,v in cert["candidate_remainder"]}
    if len(rules)!=421 or set(rules)&candidates or any(not set(r)<=candidates for r in rules.values()):raise RuntimeError("Rule count/scope")
    mapping=gap.read(rank.prev.prev.prev.prev.prev.SOURCE)["custom_mapping"]
    custom={tuple(k):tuple(e) for k,e,w in mapping}
    project=a.exact.P
    perm=rank.read_permutation((project/"sectormappings/auxiliary.yaml").read_text(encoding="utf-8-sig"),"VP05_full",12)
    mod=a.exact.load_codec(a.exact.ROOT/"output/tools/pyred_weight.py")
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    codec=rank.PhysicalWeightCodec(mod,np=12,bits=bits,iord=ordering,topsectors=[203],permutation=perm)
    cache={};raw=[]
    for path in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if path not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(path):
            row=[]
            for t in terms:
                k=tuple(map(int,t[2:4]))
                if k not in cache:cache[k]=custom[k] if k in custom else codec.decode_key(k,custom_keys=custom)
                row.append((cache[k],t[1]))
            raw.append(row)
    if len(raw)!=2678 or len(set(cache.values()))!=len(cache):raise RuntimeError("SYSTEM scope")
    kernel=physical.old.build_kernel(physical.old.build_family_spec("VP05_full").propagators)
    if physical.old.digest(kernel)!=physical.f.e.b.c.PIN or len(kernel)!=15:raise RuntimeError("Kernel")
    points=rank.prev.prev.ff.POINTS
    evaluators=[]
    for p,z,d in points:
        values={}
        def ev(c,values=values,p=p,z=z,d=d):
            if c not in values:values[c]=rank.coefficient(c,z,d,p)
            return values[c]
        def convert(terms,ev=ev,p=p):
            row={}
            for k,c in terms:
                x=(row.get(k,0)+ev(c))%p
                if x:row[k]=x
                else:row.pop(k,None)
            return row
        rr={k:convert(r.items()) for k,r in rules.items()}
        base=[rank.substitute(convert(r),rr,p) for r in raw]
        check=rank.ranks(base,candidates,p,deadline,guard=old.memory_guard)
        if (check["rank_E"],check["rank_N"])!=(2257,2257):raise RuntimeError("Base rank mismatch")
        evaluators.append((p,rr,base))
    ROOT.mkdir(exist_ok=True);lock=ROOT/"running.lock"
    with lock.open("x") as f:f.write(str(os.getpid()))
    try:
        summaries=[]
        for sec,s,d in JOBS:
            name=f"sec{sec}_s{s}d{d}"
            seq=schedule(sec,s,d,candidates,rules)
            # Each completed source batch is immutable and regenerated on resume
            # to verify exact provenance, before computing the cumulative rank.
            rows=[];completed=0;records=[]
            for b in range(args.batches):
                if time.monotonic()>=deadline:break
                seeds=seq[b*BATCH:(b+1)*BATCH]
                if not seeds:break
                dest=ROOT/f"{name}_batch{b:03d}.json"
                batch=[]
                for k in seeds:
                    old.memory_guard()
                    if time.monotonic()>=deadline:raise TimeoutError("Generation budget")
                    for ij,entries in sorted(kernel.items()):
                        row=physical.q.exact_row(k,entries,*ij)
                        batch.append({"seed":list(k),"derivative":list(ij),"row":physical.p.encode(row)})
                payload={"source_sha256":SHA,"kernel_sha256":physical.f.e.b.c.PIN,"sector":sec,"s":s,"d":d,"batch":b,"rows":batch}
                if dest.exists():
                    if gap.read(dest)!=payload:raise RuntimeError("Saved batch mismatch")
                else:a.scope.c.save(dest,payload)
                if gap.read(dest)!=payload:raise RuntimeError("Batch reread")
                rows.extend(batch);completed+=len(seeds);records.append({"path":dest.name,"sha256":n.sha(dest)})
                a.v.log("VP05_BOUNDARY_IBP_BATCH",sector=sec,s=s,d=d,batch=b,seeds=completed,rows=len(rows),elapsed_s=time.monotonic()-start)
            checks=[]
            if rows:
                for point,(p,rr,base) in zip(points,evaluators):
                    fresh=[]
                    for rec in rows:
                        if time.monotonic()>=deadline:raise TimeoutError("Evaluation budget")
                        # Evaluate independently generated SymPy expressions
                        # using the existing rational finite-field evaluator.
                        sym=physical.p.decode(rec["row"])
                        rawrow=physical.p.field_row(sym,point)
                        fresh.append(rank.substitute(rawrow,rr,p))
                    result=rank.ranks(base+fresh,candidates,p,deadline,guard=old.memory_guard)
                    checks.append({"point":list(point),**result,"new_rows":len(fresh),"new_terms_after":sum(map(len,fresh))})
                    a.v.log("VP05_BOUNDARY_IBP_RANK",sector=sec,s=s,d=d,**checks[-1])
            summaries.append({"sector":sec,"s":s,"d":d,"seeds":completed,"envelope_seeds":len(seq),"rows":len(rows),"batches":records,"checks":checks,"full_envelope_generated":completed==len(seq)})
        if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
        payload={"status":"VP05_BOUNDARY_INCREMENTAL_IBP_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},"jobs":summaries,"rules":421,"full_closure_proven":False}
        dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
        a.v.log(payload["status"],jobs=len(summaries),seeds=sum(j["seeds"] for j in summaries),rows=sum(j["rows"] for j in summaries),report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
    finally:lock.unlink()
if __name__=="__main__":main()
