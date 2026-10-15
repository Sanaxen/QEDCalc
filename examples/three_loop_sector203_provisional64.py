"""Create provisional 64-candidate file and audit sector203 rank 5. Original 63 untouched."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,RUN,CANDIDATE,load_codec,parse_file_integrals
from examples.three_loop_sector203_ffrank_audit import equations,insert

ADDED=(1,1,-1,1,0,0,1,1,0,0,0,0)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--codec-file",type=Path,required=True)
    p.add_argument("--project",type=Path,default=ROOT/"output"/RUN)
    p.add_argument("--output",type=Path,default=ROOT/"output/three_loop_integral_family_audit/vp05_full_masters_r8s3d0_union_r8s5d2_provisional64_masters.txt")
    p.add_argument("--max-fill",type=int,default=25000)
    args=p.parse_args()
    existing=parse_file_integrals(CANDIDATE)
    if len(existing)!=63 or len(set(existing))!=63: p.error("refined source must contain 63 unique candidates")
    if ADDED in existing: p.error("provisional integral already present in 63-source; refusing duplicate")
    sector=lambda x:sum(1<<i for i,v in enumerate(x) if v>0)
    candidates=[x for x in existing if sector(x)==203]
    if len(candidates)!=4 or sector(ADDED)!=203: p.error("unexpected sector203 candidate count")
    project=args.project.resolve()
    m=load_codec(args.codec_file.resolve())
    bits,ordering=m.from_kiradb(str(project/"results/kira.db"))
    if ordering!=5: p.error("unexpected ordering")
    codec=m.WeightCodec(12,bits,ordering,topsectors=[203])
    masters=parse_file_integrals(project/"results/VP05_full/masters")
    upper=[x for x in masters if sector(x)==203]
    if len(upper)!=5: p.error("expected 5 upper masters")
    files=sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    if len(files)!=14: p.error("expected 14 saved SYSTEM files")
    results=[]
    for z,d in ((17,7),(29,11),(37,13)):
        prime=1000003
        base={};count=0
        for file in files:
            for eq in equations(file,prime,z,d):
                count+=1;insert(eq,base,prime,args.max_fill)
        if count!=3317 or len(base)!=3317: p.error("unexpected equation count/rank")
        # For independence modulo lower sectors, their master coordinates
        # can be eliminated by a rank-preserving projection: instead of
        # using guessed lower-sector weights, reuse the full verified sector
        # remapping and the lower-master quotient audit before promotion.
        from collections import defaultdict
        from examples.three_loop_sector203_weight_audit import system_ids
        recorded=set()
        for file in files:recorded.update(system_ids(file)[0])
        observed=defaultdict(set)
        for w,s in recorded:
            x=codec.decode(w)
            if codec.encode(x)!=w:p.error("codec roundtrip")
            observed[s].add(sector(x))
        if any(len(v)!=1 for v in observed.values()):p.error("bad sector map")
        mapping={k:next(iter(v)) for k,v in observed.items()}
        if len(set(mapping.values()))!=len(mapping) or mapping.get(203)!=203:p.error("bad rank map")
        shift=sum(bits)
        def key(x):
            sec=sector(x)
            if sec not in mapping:raise ValueError(f"unknown sector {sec}")
            w=codec.encode(x)
            if w>>shift!=codec.rank[sec]:raise ValueError("bad rank bits")
            return ((codec.rank[mapping[sec]]<<shift)|(w&((1<<shift)-1)),sec)
        lower=[x for x in masters if sector(x)!=203]
        if len(lower)!=5:p.error("expected five lower masters")
        lower_span=base.copy()
        if not all(insert({key(x):1},lower_span,prime,args.max_fill) for x in lower):
            p.error("lower master rank not five")
        trial=lower_span.copy()
        increments=[insert({key(x):1},trial,prime,args.max_fill) for x in (*candidates,ADDED)]
        master_probe=trial.copy()
        remaining=[insert({key(x):1},master_probe,prime,args.max_fill) for x in upper]
        item={"z":z,"d":d,"candidate_rank":sum(increments),"candidate_increments":increments,
              "additional_upper_master_directions":sum(remaining),"upper_master_increments":remaining}
        results.append(item)
        print("RANK_POINT "+json.dumps(item),flush=True)
        if increments!=[True]*5 or any(remaining):
            p.error("provisional five-candidate completeness not supported; output not written")
    # Explicitly create a NEW file, fail closed if it already exists.
    out=args.output.resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    lines=["VP05_full["+",".join(map(str,x))+"]" for x in [*existing,ADDED]]
    with out.open("x",encoding="utf-8",newline="\n") as f:
        f.write("\n".join(lines)+"\n")
    print(json.dumps({"status":"PASS_PROVISIONAL_ONLY","source_63":str(CANDIDATE),
      "created_64":str(out),"candidate_count":64,"additional_integral":lines[-1],
      "rank_checks":results,
      "warning":"Only saved r5s6d0 selected equations at sampled fields; not r7s6d2 or symbolic closure"},indent=2))
if __name__=="__main__":main()
