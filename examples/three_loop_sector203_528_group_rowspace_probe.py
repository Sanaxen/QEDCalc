"""Finite-field rank/replay probe for each VP05 compressed-row source group.

This is a necessary diagnostic, NOT rational-function proof. Witness original_rows
are witness-list positions, distinct from raw SYSTEM source row_index.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_target_reverse_certificate import DEFAULT
from examples.three_loop_sector203_exact_528_provenance_audit import WITNESS
from examples.three_loop_sector203_target_scope_preflight import POINTS
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows,order

def solve(rows,target,p):
    basis={};used=0
    for ri,row in enumerate(rows):
        vec=dict(row);provenance={ri:1}
        while vec:
            k=min(vec,key=order)
            if k not in basis:break
            owner,ownerprov=basis[k]
            factor=vec[k]
            for col,val in owner.items():
                new=(vec.get(col,0)-factor*val)%p
                if new:vec[col]=new
                else:vec.pop(col,None)
            for j,val in ownerprov.items():
                new=(provenance.get(j,0)-factor*val)%p
                if new:provenance[j]=new
                else:provenance.pop(j,None)
        if vec:
            pivot=min(vec,key=order)
            inv=pow(vec[pivot],-1,p)
            basis[pivot]=({k:v*inv%p for k,v in vec.items()},
                          {j:v*inv%p for j,v in provenance.items()})
    vec=dict(target);certificate={}
    while vec:
        k=min(vec,key=order)
        if k not in basis:return False,len(basis),0,len(vec)
        owner,ownerprov=basis[k]
        factor=vec[k]
        used+=1
        for col,val in owner.items():
            n=(vec.get(col,0)-factor*val)%p
            if n:vec[col]=n
            else:vec.pop(col,None)
        for j,val in ownerprov.items():
            n=(certificate.get(j,0)+factor*val)%p
            if n:certificate[j]=n
            else:certificate.pop(j,None)
    replay={}
    for j,factor in certificate.items():
        for k,v in rows[j].items():
            n=(replay.get(k,0)+factor*v)%p
            if n:replay[k]=n
            else:replay.pop(k,None)
    if replay!=target:raise AssertionError("Modular group certificate replay mismatch")
    return True,len(basis),len(certificate),0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--witness",type=Path,default=WITNESS)
    ap.add_argument("--max-groups",type=int,default=166)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_528_group_rowspace_probe.json"))
    a=ap.parse_args()
    if not 1<=a.max_groups<=166:ap.error("--max-groups must be 1..166")
    src=json.loads(a.equations.read_text(encoding="utf-8-sig"))["rows"]
    witness=json.loads(a.witness.read_text(encoding="utf-8-sig"))["rows"]
    if len(src)!=166 or len(witness)!=528:ap.error("Unexpected compressed/witness size")
    results=[]
    for pt in POINTS:
        p,z,d=pt;cr=mod_rows(src[:a.max_groups],p,z,d);wr=mod_rows(witness,p,z,d)
        groups=[]
        for i,row in enumerate(src[:a.max_groups]):
            ids=row["original_rows"]
            if not ids or len(set(ids))!=len(ids) or any(type(k)!=int or k<0 or k>=528 for k in ids):
                raise ValueError(f"Invalid witness-list positions for compressed row {i}")
            ok,rank,support,remaining=solve([wr[j] for j in ids],cr[i],p)
            groups.append({"row":i,"group_size":len(ids),"rank":rank,
                 "in_span":ok,"certificate_support":support,"remainder_columns":remaining})
        result={"point":list(pt),"groups_tested":len(groups),"in_span":sum(x["in_span"] for x in groups),
          "not_in_span":sum(not x["in_span"] for x in groups),
          "multi_in_span":sum(x["in_span"] and x["group_size"]>1 for x in groups),
          "multi_not_in_span":sum(not x["in_span"] and x["group_size"]>1 for x in groups),
          "unresolved_rows":[x["row"] for x in groups if not x["in_span"]],
          "examples":groups[:10],"exact_proof":False}
        results.append(result)
        print("VP05_528_GROUP_ROWSPACE_POINT "+json.dumps({k:v for k,v in result.items() if k!="examples"}),flush=True)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"points":results,"symbolic_exact_replay":False,
        "original_528_row_exact_replay_verified":False},indent=2)+"\n",encoding="utf-8")
    print("VP05_528_GROUP_ROWSPACE_SUMMARY "+json.dumps({
       "all_groups_in_span_all_points":all(x["not_in_span"]==0 for x in results),
       "unresolved_union":sorted(set.union(*(set(x["unresolved_rows"]) for x in results))),
       "output":str(a.output),"original_528_row_exact_replay_verified":False}),flush=True)
if __name__=="__main__":main()
