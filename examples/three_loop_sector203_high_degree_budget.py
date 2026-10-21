"""Budget higher-degree VP05 rational certificate interpolation per coefficient.

Diagnoses whether 39 training samples can identify bivariate numerator and
denominator degree bounds 3..6. Read-only finite-field rank diagnostics.
No Fermat/Kira, no exact Q(z,d) proof.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value,null_vector

ROOT=Path("output/three_loop_integral_family_audit")
DEFAULT=ROOT/"vp05_same_prime_certificate_samples_grid_v3.json"
OUT=ROOT/"vp05_high_degree_budget.json"


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--samples",type=Path,default=DEFAULT)
    parser.add_argument("--output",type=Path,default=OUT)
    parser.add_argument("--max-degree",type=int,default=6)
    args=parser.parse_args()
    if not 4<=args.max_degree<=8:parser.error("max-degree must be 4..8")
    raw=args.samples.read_bytes()
    source=json.loads(raw.decode("utf-8-sig"))
    if source.get("type")!="same_prime_modular_certificate_samples" or source.get("rows")!=166:
        parser.error("Expected 166-component grid-v3 samples")
    p=source["prime"]
    training=[s for s in source["samples"] if s["role"]=="training"]
    holdouts=[s for s in source["samples"] if s["role"]=="holdout"]
    if len(training)!=39 or len(holdouts)!=8:
        parser.error("Expected 39 training and 8 reserved holdouts")
    if len({tuple(s["point"]) for s in source["samples"]})!=len(source["samples"]):
        parser.error("Duplicate sample point")
    for s in source["samples"]:
        if s["point"][0]!=p or not s.get("replay_verified") or len(s["coefficients_by_compressed_row"])!=166:
            parser.error("Unverified or invalid sample")
    models=[]
    for n in range(3,args.max_degree+1):
        for d in range(3,args.max_degree+1):
            numerator=powers(n);denominator=powers(d)
            parameters=len(numerator)+len(denominator)-1
            # Data-independent polynomial evaluation ranks; not equivalent
            # to coefficient-dependent homogeneous rational rank.
            eval_n=[value(numerator,s["point"][1],s["point"][2],p) for s in training]
            eval_d=[value(denominator,s["point"][1],s["point"][2],p) for s in training]
            _,rank_n,_=null_vector(eval_n,p)
            _,rank_d,_=null_vector(eval_d,p)
            models.append({"numerator_degree":n,"denominator_degree":d,
                "free_projective_parameters":parameters,
                "training":len(training),"extra_training_lower_bound":max(0,parameters-len(training)),
                "numerator_evaluation_rank":rank_n,
                "denominator_evaluation_rank":rank_d,
                "numerator_evaluation_full_rank":rank_n==len(numerator),
                "denominator_evaluation_full_rank":rank_d==len(denominator),
                "identified_from_current_samples":False,
                "note":"Projective parameter count is a generic lower bound, not a sufficient identification criterion."})
    summary={"prime":p,"training":len(training),"reserved_holdouts":len(holdouts),
       "sample_sha256":hashlib.sha256(raw).hexdigest(),
       "equations_sha256":source.get("source_sha256"),
       "models":models,"proof":False,"fermat_executed":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print("VP05_HIGH_DEGREE_BUDGET_SUMMARY "+json.dumps({
       "training":len(training),"holdouts":len(holdouts),"model_count":len(models),
       "output":str(args.output),"proof":False}),flush=True)
    for x in models:
        if x["numerator_degree"]==x["denominator_degree"]:
            print("VP05_HIGH_DEGREE_BUDGET_MODEL "+json.dumps(x),flush=True)

if __name__=="__main__":main()
