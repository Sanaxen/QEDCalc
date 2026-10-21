"""VP05 rational interpolation identifiability diagnosis (finite field only).

Compare polynomial evaluation ranks with homogeneous rational-kernel nullities
for all 166 compressed certificate components. No Fermat/Kira, no proof.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from collections import Counter
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value,null_vector

DEFAULT=Path("output/three_loop_integral_family_audit/vp05_same_prime_certificate_samples_grid_v3.json")
OUT=Path("output/three_loop_integral_family_audit/vp05_identifiability_diagnostic.json")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--samples",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=OUT)
    ap.add_argument("--degree",type=int,default=3)
    args=ap.parse_args()
    if not 0<=args.degree<=6:ap.error("degree must be 0..6")
    raw=args.samples.read_bytes()
    data=json.loads(raw.decode("utf-8-sig"))
    if data.get("type")!="same_prime_modular_certificate_samples" or data.get("rows")!=166:
        ap.error("Unexpected sample archive")
    p=data["prime"]
    training=[s for s in data["samples"] if s["role"]=="training"]
    if not training:ap.error("No training points")
    mons=powers(args.degree)
    evaluation=[value(mons,s["point"][1],s["point"][2],p) for s in training]
    _,poly_rank,poly_nullity=null_vector(evaluation,p)
    dimensions=Counter();entries=[]
    for row in range(166):
        a=[v+[(-s["coefficients_by_compressed_row"][row]*x)%p for x in v]
           for v,s in zip(evaluation,training)]
        _,rank,nullity=null_vector(a,p)
        dimensions[nullity]+=1
        entries.append({"row":row,"rank":rank,"kernel_nullity":nullity})
    report={"prime":p,"degree":args.degree,"training":len(training),
            "monomials":len(mons),"polynomial_rank":poly_rank,
            "polynomial_nullity":poly_nullity,
            "rational_kernel_nullity_histogram":dict(sorted(dimensions.items())),
            "rows_with_no_nonzero_rational_solution":dimensions[0],
            "rows_with_unique_rational_representation":dimensions[1],
            "rows_with_nonunique_rational_representation":sum(n for k,n in dimensions.items() if k>1),
            "rows":entries,"samples_sha256":hashlib.sha256(raw).hexdigest(),
            "explanation":"Kernel nullity 0 means no nonzero degree-bounded rational representation exists at the sampled points; nullity 1 is projectively unique; nullity >1 is genuinely nonunique. Full polynomial evaluation rank does not establish a full rational model.",
            "fermat_executed":False,"proof":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_IDENTIFIABILITY_SUMMARY "+json.dumps({k:v for k,v in report.items() if k!="rows"} | {"output":str(args.output)}),flush=True)

if __name__=="__main__":main()
