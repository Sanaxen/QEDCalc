"""Read-only quotient rank modulo saved equations AND five lower-sector masters.

Uses an empirical Kira sector-rank mapping verified against saved SYSTEM weights.
No Kira execution or changes to inputs; not a proof of symbolic IBP closure.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,RUN,CANDIDATE,load_codec,parse_file_integrals,system_ids
from examples.three_loop_sector203_ffrank_audit import equations,insert

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project",type=Path,default=ROOT/"output"/RUN)
    ap.add_argument("--codec-file",type=Path,required=True)
    ap.add_argument("--max-fill",type=int,default=25000)
    args=ap.parse_args()
    project=args.project.resolve()
    mod=load_codec(args.codec_file.resolve())
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    if ordering!=5: ap.error("unexpected ordering")
    codec=mod.WeightCodec(12,bits,ordering,topsectors=[203])
    files=sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    if len(files)!=14: ap.error("expected 14 saved SYSTEM files")
    recorded=set()
    for f in files: recorded.update(system_ids(f)[0])
    mappings=defaultdict(set)
    for weight,sec in recorded:
        x=codec.decode(weight)
        if codec.encode(x)!=weight: ap.error("weight roundtrip failure")
        mappings[sec].add(mod.sec_of(x))
    if any(len(v)!=1 for v in mappings.values()): ap.error("non-uniform sector map")
    observed={sec:next(iter(vals)) for sec,vals in mappings.items()}
    if len(set(observed.values()))!=len(observed) or observed.get(203)!=203:
        ap.error("invalid empirical sector ranking")
    shift=sum(bits)
    def key(x):
        sec=mod.sec_of(x)
        if sec not in observed: raise ValueError(f"unknown sector rank for {sec}")
        default=codec.encode(x)
        if default>>shift!=codec.rank[sec]: raise ValueError("weight format mismatch")
        weight=(codec.rank[observed[sec]]<<shift)|(default&((1<<shift)-1))
        return (weight,sec)
    masters=parse_file_integrals(project/"results/VP05_full/masters")
    lower=[x for x in masters if mod.sec_of(x)!=203]
    upper=[x for x in masters if mod.sec_of(x)==203]
    candidates=[x for x in parse_file_integrals(CANDIDATE) if mod.sec_of(x)==203]
    if (len(lower),len(upper),len(candidates))!=(5,5,4): ap.error("unexpected master/candidate counts")
    results=[]
    for z,d in ((17,7),(29,11),(37,13)):
        p=1000003
        base={}
        n=0
        for f in files:
            for row in equations(f,p,z,d):
                n+=1
                insert(row,base,p,args.max_fill)
        if n!=3317 or len(base)!=3317: ap.error("equation count/rank changed")
        lower_span=base.copy()
        lower_inc=[insert({key(x):1},lower_span,p,args.max_fill) for x in lower]
        cand_span=lower_span.copy()
        cand_inc=[insert({key(x):1},cand_span,p,args.max_fill) for x in candidates]
        after_cand=cand_span.copy()
        upper_inc=[insert({key(x):1},after_cand,p,args.max_fill) for x in upper]
        upper_span=lower_span.copy()
        upper_base_inc=[insert({key(x):1},upper_span,p,args.max_fill) for x in upper]
        cand_after_upper=[not insert({key(x):1},upper_span.copy(),p,args.max_fill) for x in candidates]
        entry={"z":z,"d":d,"selected_equation_rank":len(base),
          "lower_master_rank_increments":lower_inc,
          "candidate_rank_over_equations_and_lower_masters":sum(cand_inc),
          "candidate_increments":cand_inc,
          "sector203_master_rank_over_equations_and_lower_masters":sum(upper_base_inc),
          "upper_master_increments_after_candidates":upper_inc,
          "extra_upper_master_directions_after_candidates":sum(upper_inc),
          "candidates_in_full_10_master_span":cand_after_upper,
          "combined_upper_and_candidate_rank":len(after_cand)-len(lower_span)}
        results.append(entry)
        print("RANK_POINT "+json.dumps(entry),flush=True)
    print(json.dumps({"scope":"saved selected r5s6d0 equations modulo 5 lower-sector masters",
      "prime":1000003,"sector203_masters":5,"candidate_count":4,"points":results,
      "limitation":"empirical sector rank map; finite-field selected-equation quotient, not symbolic or r7s6d2 closure"},indent=2))
if __name__=="__main__": main()
