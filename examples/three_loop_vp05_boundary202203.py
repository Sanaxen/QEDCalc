"""Enumerate actual exact-sector boundary integrals and reduce saved SYSTEM columns.
No extrapolation from restricted seed to full boundary closure.
"""
import argparse,time,itertools
from pathlib import Path
from examples import three_loop_vp05_recovery_gate as prev
from examples import three_loop_vp05_abc_exact_audit as decoded
from examples import three_loop_vp05_abc_cost_probe as ff
from examples.kira_physical_weight_codec import PhysicalWeightCodec,read_permutation,sector
a=prev.a;n=a.n;gap=a.gap;old=a.old
ROOT=n.BASE/"output"/"vp05_boundary202203_43"
SOURCE=prev.ROOT/"report_1795820871336224500.json"
SHA="a6d66cfb273f39ca7643bf4f1f1010c632f84b2c2c986480872bb5ac070c69c0"

def compositions(total,n):
    if n==1:
        yield (total,);return
    for i in range(total+1):
        for tail in compositions(total-i,n-1):yield (i,)+tail

def envelope(sec,r,s,d):
    pos=[i for i in range(12) if sec&(1<<i)]
    neg=[i for i in range(12) if not sec&(1<<i)]
    for dots in range(min(d,r-len(pos))+1):
        for ps in compositions(dots,len(pos)):
            for nums in range(s+1):
                for ns in compositions(nums,len(neg)):
                    ex=[0]*12
                    for i,v in zip(pos,ps):ex[i]=1+v
                    for i,v in zip(neg,ns):ex[i]=-v
                    yield tuple(ex)

def classify(targets,candidates,rules,reverse,seen,codec):
    out={"candidate":[], "existing_rule":[], "saved_noncandidate":[], "not_in_saved_SYSTEM":[]}
    for ex in targets:
        if ex in candidates:kind="candidate";key=None
        elif ex in rules:kind="existing_rule";key=None
        else:
            try:key=reverse[ex] if ex in reverse else (codec.encode(ex),sector(ex))
            except (ValueError,AssertionError,OverflowError,IndexError,KeyError):key=None
            kind="saved_noncandidate" if key in seen else "not_in_saved_SYSTEM"
        out[kind].append({"exponents":list(ex),"key":list(key) if key is not None else None})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--hours",type=float,default=2);args=ap.parse_args()
    if not 0<args.hours<=2:ap.error("Time cap")
    start=time.monotonic();deadline=start+args.hours*3600
    if n.sha(SOURCE)!=SHA:raise RuntimeError("Recovery gate SHA")
    data=gap.read(SOURCE)
    if data["status"]!="VP05_RECOVERY_GATE_REVIEW_REQUIRED" or data["review_issues"] or data["local_evidence_total"]!=57:raise RuntimeError("Recovery scope")
    pins={Path(k):v for k,v in data["inputs"].items()};pins[SOURCE]=SHA
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected SHA")
    manifest=gap.AUDIT/f"{gap.PREFIX}_candidate_{gap.CANDIDATE_SEED}_closure_manifest.json"
    candidates={gap.indices(x) for x in gap.read(manifest)["candidate_masters"]}
    rules={tuple(k) for k,r in data["candidate_rules"]}
    mapping=gap.read(prev.prev.prev.SOURCE)["custom_mapping"]
    custom={tuple(k):tuple(ex) for k,ex,w in mapping};reverse={ex:k for k,ex in custom.items()}
    project=a.exact.P
    perm=read_permutation((project/"sectormappings/auxiliary.yaml").read_text(encoding="utf-8-sig"),"VP05_full",12)
    mod=a.exact.load_codec(a.exact.ROOT/"output/tools/pyred_weight.py")
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    codec=PhysicalWeightCodec(mod,np=12,bits=bits,iord=ordering,topsectors=[203],permutation=perm)
    rows=[];seen=set()
    for path in sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
        if path not in pins:raise RuntimeError("Unpinned SYSTEM")
        for ordinal,head,terms in a.parse_system(path):
            row=[(tuple(map(int,t[2:4])),t[1]) for t in terms]
            rows.append(row);seen.update(k for k,c in row)
    if len(rows)!=2678:raise RuntimeError("SYSTEM scope")
    free=set(custom)
    jobs=[];wanted=set()
    for sec in (202,203):
        for seed,s,d in (("r8s6d2",6,2),("r8s5d3",5,3)):
            targets=list(envelope(sec,8,s,d))
            parts=classify(targets,candidates,rules,reverse,seen,codec)
            wanted.update(tuple(t["key"]) for t in parts["saved_noncandidate"] if tuple(t["key"]) not in free)
            counts={k:len(v) for k,v in parts.items()}
            jobs.append({"sector":sec,"seed":seed,"target_count":len(targets),"counts":counts,"targets":parts})
            a.v.log("VP05_BOUNDARY_ENVELOPE",sector=sec,seed=seed,target_count=len(targets),**counts)
    # Retain custom columns and any actual candidate columns present.
    for ex in candidates:
        if ex in reverse:free.add(reverse[ex]);continue
        try:key=(codec.encode(ex),sector(ex))
        except (ValueError,AssertionError,OverflowError,IndexError,KeyError):continue
        if key in seen:free.add(key)
    trials=[]
    for point in ff.POINTS:
        result=ff.probe(rows,point,sorted(wanted),free,deadline,2000)
        trials.append(result)
        a.v.log("VP05_BOUNDARY_SAVED_POINT",point=list(point),targets=len(wanted),retained_only=sum(t["retained_only"] for t in result["targets"]),max_support=max((t["source_support"] for t in result["targets"]),default=0),elapsed_s=result["elapsed_s"])
    ready=set(wanted)
    for result in trials:ready&={tuple(t["key"]) for t in result["targets"] if t["retained_only"]}
    for job in jobs:
        job["modular_ready"]=sum(tuple(t["key"]) in ready for t in job["targets"]["saved_noncandidate"])
        a.v.log("VP05_BOUNDARY_SAVED_COVERAGE",sector=job["sector"],seed=job["seed"],modular_ready=job["modular_ready"],missing=job["counts"]["not_in_saved_SYSTEM"])
    if any(n.sha(k)!=v for k,v in pins.items()):raise RuntimeError("Protected input changed")
    payload={"status":"VP05_BOUNDARY_202203_SAVED_REDUCTION_NOT_CLOSURE","inputs":{str(k):v for k,v in pins.items()},
             "jobs":jobs,"trials":trials,"ready_keys":[list(k) for k in sorted(ready)],"full_closure_proven":False}
    ROOT.mkdir(exist_ok=True);dest=ROOT/f"report_{time.time_ns()}.json";digest=a.scope.c.save(dest,payload)
    a.v.log(payload["status"],jobs=4,unique_modular_ready=len(ready),unique_requested=len(wanted),report=dest.name,sha256=digest,elapsed_s=time.monotonic()-start,inputs_unchanged=True,full_closure_proven=False)
if __name__=="__main__":main()
