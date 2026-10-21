"""Degree-(4,4) VP05 rational certificate trial, targeting v3-unresolved rows.

Read-only finite-field interpolation; does not run Fermat/Kira or prove Q(z,d).
Uses the original 8 holdout samples solely for validation.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from collections import Counter
from examples.three_loop_sector203_certificate_adaptive_degree import fit

ROOT=Path("output/three_loop_integral_family_audit")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--samples",type=Path,default=ROOT/"vp05_same_prime_certificate_samples_grid_v3.json")
    ap.add_argument("--adaptive",type=Path,default=ROOT/"vp05_certificate_adaptive_degree_grid_v3.json")
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_certificate_degree4_trial.json")
    a=ap.parse_args()
    raw=a.samples.read_bytes()
    source=json.loads(raw.decode("utf-8-sig"))
    prior=json.loads(a.adaptive.read_text(encoding="utf-8-sig"))
    if source.get("type")!="same_prime_modular_certificate_samples" or source.get("rows")!=166:
        ap.error("Unexpected sample archive")
    if prior["summary"]["source_sha256"]!=hashlib.sha256(raw).hexdigest():
        ap.error("Adaptive result not linked to same samples")
    if source["source_sha256"]!=prior["summary"]["equations_sha256"]:
        ap.error("Equation digest mismatch")
    if len(prior["results"])!=166 or {x["row"] for x in prior["results"]}!=set(range(166)):
        ap.error("Expected 166 distinct previous rows")
    p=source["prime"]
    train=[x for x in source["samples"] if x["role"]=="training"]
    hold=[x for x in source["samples"] if x["role"]=="holdout"]
    if len(train)!=39 or len(hold)!=8:
        ap.error("Expected 39 training and 8 untouched holdouts")
    rows=[x["row"] for x in prior["results"] if x["status"]=="unresolved"]
    hist=Counter();details=[]
    for row in rows:
        ans=fit(train,hold,p,row,4,4)
        hist[ans["status"]]+=1
        details.append({"row":row,**ans})
    summary={"prime":p,"targeted_rows":len(rows),"training":len(train),
       "holdouts":len(hold),"numerator_degree":4,"denominator_degree":4,
       "outcome_counts":dict(hist),
       "additional_holdout_pass":hist.get("holdout_pass",0),
       "combined_pass_if_previous_retained":166-len(rows)+hist.get("holdout_pass",0),
       "source_sha256":hashlib.sha256(raw).hexdigest(),
       "proof":False,"fermat_executed":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"summary":summary,"rows":details},indent=2)+"\n",encoding="utf-8")
    print("VP05_DEGREE4_TRIAL "+json.dumps({**summary,"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
