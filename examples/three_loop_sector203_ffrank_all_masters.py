"""Read-only finite-field audit with all 10 Kira masters and validated sector-rank remapping."""
import argparse
import json
from pathlib import Path
from collections import defaultdict

from examples.three_loop_sector203_weight_audit import ROOT, RUN, CANDIDATE, load_codec, parse_file_integrals, system_ids
from examples.three_loop_sector203_ffrank_audit import equations, insert

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--project",type=Path,default=ROOT/"output"/RUN)
    a.add_argument("--codec-file",type=Path,required=True)
    a.add_argument("--z",type=int,default=17)
    a.add_argument("--d",type=int,default=7)
    a.add_argument("--max-fill",type=int,default=25000)
    args=a.parse_args()
    prime=1000003
    project=args.project.resolve()
    m=load_codec(args.codec_file.resolve())
    bits,ordering=m.from_kiradb(str(project/"results/kira.db"))
    if ordering!=5: a.error("Unexpected Kira ordering")
    codec=m.WeightCodec(12,bits,ordering,topsectors=[203])
    files=sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    if len(files)!=14: a.error("Expected 14 saved SYSTEM files")
    records=set()
    for file in files:
        ids,heads,_=system_ids(file)
        records.update(ids)
    observed=defaultdict(set)
    for weight,sector in records:
        powers=codec.decode(weight)
        if codec.encode(powers)!=weight: a.error("codec roundtrip failed")
        observed[sector].add(m.sec_of(powers))
    if any(len(v)!=1 for v in observed.values()): a.error("nonunique observed sector mapping")
    remap={k:next(iter(v)) for k,v in observed.items()}
    if len(set(remap.values()))!=len(remap): a.error("observed sector mapping is not injective")
    if remap.get(203)!=203: a.error("sector203 rank not preserved")
    shift=sum(bits)
    def key(integral):
        sector=m.sec_of(integral)
        if sector not in remap: raise ValueError(f"missing observed rank mapping for sector {sector}")
        standard=codec.encode(integral)
        standard_rank=codec.rank[sector]
        if standard>>shift!=standard_rank: raise ValueError("unexpected rank bits")
        # Reassign the rank field to the engine's observed sector-rank slot.
        observed_rank=codec.rank[remap[sector]]
        mapped=(observed_rank<<shift) | (standard&((1<<shift)-1))
        return (mapped,sector)
    masters=parse_file_integrals(project/"results/VP05_full/masters")
    candidates=[x for x in parse_file_integrals(CANDIDATE) if m.sec_of(x)==203]
    if len(masters)!=10 or len(candidates)!=4: a.error("wrong master or candidate list size")
    rows=[]
    for file in files: rows.extend(equations(file,prime,args.z,args.d))
    if len(rows)!=3317: a.error("SYSTEM equations changed")
    pivots={}
    for i,row in enumerate(rows,1):
        insert(row,pivots,prime,args.max_fill)
        if i%500==0: print(f"RANK_PROGRESS equations={i}/3317 pivots={len(pivots)}",flush=True)
    augmented=dict(pivots)
    master_status=[]
    for integral in masters:
        k=key(integral)
        added=insert({k:1},augmented,prime,args.max_fill)
        master_status.append({"integral":list(integral),"sector":k[1],"weight":k[0],
          "appears_in_selected_system":k in records,"rank_increase":added})
    candidate_status=[]
    for integral in candidates:
        k=key(integral)
        probe=dict(augmented)
        added=insert({k:1},probe,prime,args.max_fill)
        candidate_status.append({"integral":list(integral),"rank_increase_after_all_10_masters":added,
          "in_saved_equation_plus_all_masters_span":not added})
    print(json.dumps({"scope":"single-point rank of saved target1 selected SYSTEM equations only",
      "prime":prime,"z":args.z,"d":args.d,"equations":len(rows),
      "selected_equation_rank":len(pivots),
      "observed_sector_remap":{str(k):v for k,v in sorted(remap.items())},
      "master_status":master_status,"candidate_status":candidate_status,
      "warning":"No symbolic proof, no missing IBP equations inferred; other targets and r7s6d2 untested."},
      indent=2))

if __name__=="__main__": main()
