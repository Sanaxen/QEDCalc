"""Diagnose why the VP05 rational interpolation kernel is non-unique.

Two independent tests: polynomial evaluation rank and rational homogeneous
kernel nullity. Distinguishes sampling-geometry deficiency from rational
representation ambiguity. No Fermat/Kira and no symbolic proof.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value,null_vector
from examples.three_loop_sector203_certificate_interpolation_trial import DEFAULT

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--samples",type=Path,default=DEFAULT)
    ap.add_argument("--degree",type=int,default=3)
    ap.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_interpolation_rank_diagnostic.json"))
    a=ap.parse_args()
    if not 0<=a.degree<=6:ap.error("degree must be 0..6")
    data=json.loads(a.samples.read_text(encoding="utf-8-sig"))
    if data.get("type")!="same_prime_modular_certificate_samples" or data.get("rows")!=166:
        ap.error("Invalid samples")
    p=data["prime"];train=[s for s in data["samples"] if s["role"]=="training"]
    hold=[s for s in data["samples"] if s["role"]=="holdout"]
    mons=powers(a.degree)
    evals=[value(mons,s["point"][1],s["point"][2],p) for s in train]
    _,evaluation_rank,evaluation_nullity=null_vector(evals,p)
    ranks={}
    first=[]
    for col in range(166):
        matrix=[v+[(-s["coefficients_by_compressed_row"][col]*x)%p for x in v] for v,s in zip(evals,train)]
        _,rank,nullity=null_vector(matrix,p)
        ranks[str(nullity)]=ranks.get(str(nullity),0)+1
        if col<12:first.append({"row":col,"rank":rank,"nullity":nullity})
    result={"point_count":len(train),"holdouts":len(hold),"prime":p,"degree":a.degree,
            "monomial_count":len(mons),"evaluation_matrix_rank":evaluation_rank,
            "evaluation_matrix_nullity":evaluation_nullity,
            "rational_kernel_nullity_histogram":ranks,"first_12":first,
            "training_grid_deficient":evaluation_rank<len(mons),
            "rational_unique_model":ranks.get("1",0),
            "recommendation":"If evaluation rank deficient: choose genuine two-dimensional points. If full rank but rational kernel nonunique: use lower degrees or additional training points; do not identify coefficient functions from a single null vector.",
            "fermat_executed":False,"proof":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("VP05_INTERPOLATION_RANK_DIAG "+json.dumps({k:v for k,v in result.items() if k!="first_12"} | {"output":str(a.output)}),flush=True)
if __name__=="__main__":main()
