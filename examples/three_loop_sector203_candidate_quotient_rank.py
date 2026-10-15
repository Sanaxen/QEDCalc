"""Read-only quotient-rank audit of four VP05 sector203 candidates.

Ranks are computed in V / span(saved 3317 SYSTEM equations).
This avoids interpreting Kira's five sector203 masters as a proved
five-dimensional subspace: lower sectors must also be accounted for.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,RUN,CANDIDATE,load_codec,parse_file_integrals
from examples.three_loop_sector203_ffrank_audit import equations,insert
from examples.three_loop_sector203_ffrank_all_masters import main as _previous_main

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--codec-file",type=Path,required=True)
    ap.add_argument("--project",type=Path,default=ROOT/"output"/RUN)
    ap.add_argument("--max-fill",type=int,default=25000)
    args=ap.parse_args()
    project=args.project.resolve()
    mod=load_codec(args.codec_file.resolve())
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    if ordering!=5: ap.error("unexpected Kira integral ordering")
    codec=mod.WeightCodec(12,bits,ordering,topsectors=[203])
    candidates=[x for x in parse_file_integrals(CANDIDATE) if mod.sec_of(x)==203]
    masters=[x for x in parse_file_integrals(project/"results/VP05_full/masters") if mod.sec_of(x)==203]
    if len(candidates)!=4 or len(masters)!=5: ap.error("unexpected candidates/sector203 masters count")
    files=sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    if len(files)!=14: ap.error("expected 14 SYSTEM files")
    conditions=((17,7),(29,11),(37,13))
    results=[]
    for z,d in conditions:
        prime=1000003
        rows=[]
        for file in files: rows.extend(equations(file,prime,z,d))
        if len(rows)!=3317: ap.error("saved equation count changed")
        base={}
        for row in rows: insert(row,base,prime,args.max_fill)
        if len(base)!=3317: ap.error(f"Unexpected equation rank at z={z},d={d}")
        augmented=base.copy()
        candidate_increments=[]
        for x in candidates:
            k=(codec.encode(x),203)
            candidate_increments.append(insert({k:1},augmented,prime,args.max_fill))
        c_rank=sum(candidate_increments)
        master_after_candidates=augmented.copy()
        master_increments=[]
        for x in masters:
            k=(codec.encode(x),203)
            master_increments.append(insert({k:1},master_after_candidates,prime,args.max_fill))
        # Also measure candidate span after adding all five sector203 masters.
        with_masters=base.copy()
        for x in masters: insert({(codec.encode(x),203):1},with_masters,prime,args.max_fill)
        candidate_after_masters=[]
        for x in candidates:
            candidate_after_masters.append(insert({(codec.encode(x),203):1},with_masters.copy(),prime,args.max_fill))
        report={"z":z,"d":d,"equation_rank":len(base),
          "candidate_rank_mod_saved_equations":c_rank,
          "candidate_independent_in_insert_order":candidate_increments,
          "extra_sector203_master_directions_after_candidates":sum(master_increments),
          "sector203_masters_independent_after_candidates":master_increments,
          "candidate_in_span_of_equations_plus_sector203_masters": [not v for v in candidate_after_masters]}
        results.append(report)
        print("RANK_POINT "+json.dumps(report),flush=True)
    print(json.dumps({"scope":"saved selected r5s6d0 SYSTEM equations only",
      "field_prime":1000003,"candidate_count":4,"sector203_master_count":5,
      "points":results,
      "interpretation":"quotient ranks of explicit unit vectors; NOT a resolved coefficient matrix, symbolic IBP identity, or r7s6d2 closure"},indent=2))

if __name__=="__main__": main()
