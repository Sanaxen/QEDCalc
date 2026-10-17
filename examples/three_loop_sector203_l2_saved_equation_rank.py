"""Read-only finite-field quotient test using completed truncate_sp l2 SYSTEM equations.

Requires external pyred_weight.py codec already used in earlier audits.
Does not execute Kira or alter the completed project.
"""
from __future__ import annotations
import argparse,json
from collections import defaultdict
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,load_codec,parse_file_integrals,system_ids
from examples.three_loop_sector203_ffrank_audit import equations,insert

DEFAULT=ROOT/"output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project",type=Path,default=DEFAULT)
    ap.add_argument("--codec-file",type=Path,default=ROOT/"output/tools/pyred_weight.py")
    ap.add_argument("--max-fill",type=int,default=25000)
    ap.add_argument("--points",type=int,choices=(1,2,3),default=1)
    args=ap.parse_args()
    project=args.project.resolve()
    mod=load_codec(args.codec_file.resolve())
    bits,ordering=mod.from_kiradb(str(project/"results/kira.db"))
    if ordering!=5:ap.error(f"unexpected Kira integral ordering {ordering}")
    codec=mod.WeightCodec(12,bits,ordering,topsectors=[203])
    files=sorted((project/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
    if len(files)!=14:ap.error(f"expected 14 SYSTEM files, got {len(files)}")
    recorded=set()
    counts={}
    for f in files:
        ids,_,n=system_ids(f)
        recorded.update(ids)
        counts[f.name]=n
    mappings=defaultdict(set)
    # Kira reserves tiny numeric IDs for selected masters. They are not
    # encoded integral weights and MUST NOT be sent to WeightCodec.decode.
    # The selected masters file order is not a documented guarantee of the
    # temporary ID assignment, so mark those columns opaque in this audit.
    opaque={(weight,sec) for weight,sec in recorded if weight < 1024}
    for weight,sec in recorded - opaque:
        indices=codec.decode(weight)
        if codec.encode(indices)!=weight:ap.error(f"weight roundtrip failed: {weight}")
        mappings[sec].add(mod.sec_of(indices))
    if any(len(v)!=1 for v in mappings.values()):ap.error("nonuniform observed sector mapping")
    observed={k:next(iter(v)) for k,v in mappings.items()}
    if len(set(observed.values()))!=len(observed.values()) or observed.get(203)!=203:ap.error("non-bijective sector mapping")
    shift=sum(bits)
    def key(indices):
        sec=mod.sec_of(indices)
        if sec not in observed:ap.error(f"unobserved sector mapping {sec}")
        original=codec.encode(indices)
        if original>>shift!=codec.rank[sec]:ap.error("unexpected weight format")
        value=(codec.rank[observed[sec]]<<shift)|(original & ((1<<shift)-1))
        return (value,sec)
    targets=parse_file_integrals(project/"mandatory_provisional64_sector203.txt")
    masters=parse_file_integrals(project/"results/VP05_full/masters")
    if len(targets)!=5 or len(masters)!=5:ap.error("unexpected five mandatory or master entries")
    present=recorded
    target_presence=[key(t) in present for t in targets]
    master_presence=[key(t) in present for t in masters]
    output={"project":str(project),"opaque_small_id_columns":sorted([list(x) for x in opaque]),"equation_counts_by_file":counts,
       "total_saved_equations":sum(counts.values()),"all_targets_in_saved_terms":target_presence,
       "masters_in_saved_terms":master_presence,
       "observed_sector_mapping":observed,"points":[]}
    if opaque:
        output["warning_opaque_ids"]="Small numeric IDs represent aliased master columns; adding full-weight master vectors without resolving aliases cannot prove or disprove candidate membership."
    if not all(target_presence):
        output["warning"]="Some mandatory integrals do not appear in serialized SYSTEM equations. Cannot conclude their reducibility without further evidence."
    p=1000003
    for z,d in [(17,7),(29,11),(37,13)][:args.points]:
        span={}
        rows=0
        for f in files:
            for row in equations(f,p,z,d):
                rows+=1
                insert(row,span,p,args.max_fill)
        master_span=span.copy()
        independent_masters=[insert({key(x):1},master_span,p,args.max_fill) for x in masters]
        statuses=[]
        for t in targets:
            probe=master_span.copy()
            inc=insert({key(t):1},probe,p,args.max_fill)
            statuses.append({"integral":"VP05_full["+",".join(map(str,t))+"]",
              "in_saved_terms":key(t) in present,
              "in_equations_plus_selected_masters_span":not inc,
              "rank_increase":inc})
        output["points"].append({"z":z,"d":d,"equations":rows,"equation_rank":len(span),
          "reported_master_rank_increments":independent_masters,
          "mandatory":statuses})
        print("POINT "+json.dumps(output["points"][-1],ensure_ascii=False),flush=True)
    output["limitation"]="Opaque small IDs are not identified with corresponding full master weights; span tests are ONLY conditional, and a positive rank increase may be an alias mismatch, not independence. Finite-field saved-system audit only."
    print(json.dumps(output,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
