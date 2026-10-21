"""Preflight the 166 exact-combination symbolic IBP equations over finite fields.

Reports rank, target membership, full original-equation replay, and sparse
elimination work. Numerical evidence only, not an exact Q(z,d) certificate.
Does not invoke Kira/Fermat.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows, modular_echelon
from examples.three_loop_sector203_target_rowspace_audit import eliminate, residue

DEFAULT=Path("output/three_loop_integral_family_audit/vp05_target_symbolic_compressed.equations.json")
POINTS=((1000037,21,15),(1001003,19,53),(1001107,36,64),(1002101,47,83))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--max-operations",type=int,default=15000)
    a=ap.parse_args()
    source=json.loads(a.equations.read_text(encoding="utf-8-sig"))
    if source.get("type")!="symbolic_exact_linear_combinations" or source.get("target_identity_proven") is not False:
        ap.error("Unexpected compressed witness format")
    rows=source["rows"]
    keys={(10,203):"z",(6,203):"-2",(5,201):"2"}
    columns={tuple(t["key"]) for row in rows for t in row["terms"]}
    if len(rows)!=166 or set(keys)-columns:
        ap.error("Expected 166 compressed equations containing all target keys")
    print("TARGET_COMPRESSED_PREFLIGHT_INPUT "+json.dumps({
        "rows":len(rows),"columns":len(columns),"terms":sum(len(x["terms"]) for x in rows),
        "source":str(a.equations),"proof":False}),flush=True)
    samples=[]
    for p,z,d in POINTS:
        matrix=mod_rows(rows,p,z,d)
        schedule,pivots=modular_echelon(matrix,p)
        operations=sum(len(ops) for ops,_ in schedule)
        target={(k):residue(v,p,z,d) for k,v in keys.items()}
        outcome=eliminate(matrix,target,p)
        result={"point":[p,z,d],"rank":len(pivots),"operations":operations,
            "target_in_rowspace":outcome["target_in_rowspace"],
            "target_remainder_size":outcome["target_remainder_size"],
            "target_elimination_steps":outcome["target_elimination_steps"],
            "certificate_support_count":outcome["certificate_support_count"],
            "certificate_original_equation_replay_verified":outcome["certificate_original_equation_replay_verified"],
            "under_operation_cap":operations<=a.max_operations,"proof":False}
        samples.append(result)
        print("TARGET_COMPRESSED_PREFLIGHT_POINT "+json.dumps(result),flush=True)
    print("TARGET_COMPRESSED_PREFLIGHT_SUMMARY "+json.dumps({
        "points":len(samples),"all_rank_166":all(x["rank"]==166 for x in samples),
        "all_target_in_rowspace":all(x["target_in_rowspace"] for x in samples),
        "all_replayed":all(x["certificate_original_equation_replay_verified"] for x in samples),
        "max_operations":max(x["operations"] for x in samples),
        "all_under_operation_cap":all(x["under_operation_cap"] for x in samples),
        "proof":False}),flush=True)


if __name__=="__main__":
    main()
