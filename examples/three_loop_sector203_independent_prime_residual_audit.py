"""Audit VP05 independent-prime residuals by original degree and kernel nullity.

Read saved 166 coefficient fits; recompute homogeneous matrix ranks only for
unresolved rows. No Fermat/Kira, no extra modular sampling.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value,null_vector
from examples.three_loop_sector203_target_scope_preflight import DEFAULT
ROOT=Path("output/three_loop_integral_family_audit")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--independent",type=Path,default=ROOT/"vp05_independent_prime_certificate.json")
    ap.add_argument("--assembled",type=Path,default=ROOT/"vp05_modular_certificate_assembled.json")
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_independent_prime_residual_audit.json")
    a=ap.parse_args()
    result=json.loads(a.independent.read_text(encoding="utf-8-sig"))
    models=json.loads(a.assembled.read_text(encoding="utf-8-sig"))
    summ=result["summary"]
    if summ["original_models_sha256"]!=hashlib.sha256(a.assembled.read_bytes()).hexdigest():
        ap.error("Assembled source hash mismatch")
    if summ["equations_sha256"]!=hashlib.sha256(a.equations.read_bytes()).hexdigest():
        ap.error("Equations hash mismatch")
    if len(result["fits"])!=166 or {x["row"] for x in result["fits"]}!=set(range(166)):
        ap.error("Incomplete independent fits")
    if len(models["coefficients"])!=166:ap.error("Incomplete assembled models")
    original={x["row"]:x for x in models["coefficients"]}
    hist=Counter();degree_hist=Counter();details=[]
    for fit in result["fits"]:
        row=fit["row"]; status=fit["result"]["status"]
        degree=tuple(fit["original_degree"])
        if degree!=(original[row]["model"]["numerator_degree"],original[row]["model"]["denominator_degree"]):
            ap.error("Model degree mismatch on row "+str(row))
        if status=="holdout_pass":continue
        nullity=fit["result"].get("nullity")
        # The standard fitter returns nullity for nonunique outcomes.
        if nullity is None:ap.error("Missing fit nullity for unresolved row")
        category="no_nonzero_fit" if nullity==0 else "nonunique_representation" if nullity>1 else "unexpected_unique_fit_failure"
        hist[category]+=1;degree_hist[str(degree)]+=1
        details.append({"row":row,"degree_pair":list(degree),"origin":fit["origin"],
                        "kernel_nullity":nullity,"kernel_rank":fit["result"].get("rank"),
                        "classification":category})
    report={"summary":{"independent_prime":summ["prime"],"original_prime":summ["original_prime"],
        "passed":summ["independent_prime_pass"],"unresolved":len(details),
        "residual_categories":dict(hist),"residual_degree_pairs":dict(degree_hist),
        "source_sha256":hashlib.sha256(a.independent.read_bytes()).hexdigest(),
        "proof":False,"fermat_executed":False},"rows":details}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_INDEPENDENT_RESIDUAL_AUDIT "+json.dumps({**report["summary"],"row_ids":[x["row"] for x in details],"output":str(a.output)}),flush=True)
if __name__=="__main__":main()
