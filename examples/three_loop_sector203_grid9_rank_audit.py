"""Audit second-prime 9-column degree-six geometry and residual kernels.

Uses saved second-prime fit ranks and deterministic sample coordinates.
No modular IBP replay and no Fermat/Kira.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value,null_vector

ROOT=Path("output/three_loop_integral_family_audit")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--trial",type=Path,default=ROOT/"vp05_independent_prime_certificate_grid9.json")
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_independent_prime_grid9_rank_audit.json")
    args=ap.parse_args()
    raw=args.trial.read_bytes();trial=json.loads(raw.decode("utf-8-sig"))
    s=trial["summary"];p=s["prime"]
    if s.get("columns")!=9 or s.get("training")!=70 or s.get("holdouts")!=10 or s.get("rejected")!=0:
        ap.error("Expected 9-column, 70-training, 10-holdout zero-rejection trial")
    fits=trial["fits"]
    if len(fits)!=166 or {x["row"] for x in fits}!=set(range(166)):
        ap.error("Invalid coefficient fit coverage")
    mons=powers(6)
    coords=[((47+53*(i%9))%p,(83+79*(i//9))%p) for i in range(70)]
    poly=[value(mons,z,d,p) for z,d in coords]
    _,poly_rank,poly_nullity=null_vector(poly,p)
    residuals=[];counts=Counter()
    for fit in fits:
        r=fit["result"]
        if r["status"]=="holdout_pass":continue
        degree=fit["original_degree"]
        nullity=r.get("nullity")
        if nullity is None:ap.error("Residual kernel dimension missing")
        if nullity==0:kind="no_nonzero_fit"
        elif nullity==1:kind="unique_fit_other_failure"
        else:kind="nonunique_representation"
        counts[kind]+=1
        residuals.append({"row":fit["row"],"degree_pair":degree,
          "rank":r.get("rank"),"nullity":nullity,"classification":kind})
    report={"summary":{"prime":p,"columns":9,"training":70,"holdouts":10,
      "degree6_polynomial_monomials":len(mons),
      "degree6_polynomial_rank":poly_rank,
      "degree6_polynomial_nullity":poly_nullity,
      "degree6_polynomial_full_rank":poly_rank==len(mons),
      "passed":sum(x["result"]["status"]=="holdout_pass" for x in fits),
      "residual":len(residuals),"residual_categories":dict(counts),
      "source_sha256":hashlib.sha256(raw).hexdigest(),
      "proof":False,"fermat_executed":False},
      "residual_rows":residuals}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_GRID9_RANK_AUDIT "+json.dumps({**report["summary"],"row_ids":[x["row"] for x in residuals],"nullities":{str(x["row"]):x["nullity"] for x in residuals},"output":str(args.output)}),flush=True)
if __name__=="__main__":main()
