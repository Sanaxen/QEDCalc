"""Test VP05 degree-(5,5) only for the 53 degree-(4,4) infeasible rows.

The original 8 holdouts are reserved. Recheck previous 113 candidates against
new v4 training points before counting them. Finite-field hypotheses only.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_certificate_adaptive_degree import fit
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value

ROOT=Path("output/three_loop_integral_family_audit")
def check_model(model,samples,p,row):
    numerator=powers(model["numerator_degree"])
    denominator=powers(model["denominator_degree"])
    for s in samples:
        z,d=s["point"][1:]
        n=sum(x*y for x,y in zip(model["numerator"],value(numerator,z,d,p)))%p
        q=sum(x*y for x,y in zip(model["denominator"],value(denominator,z,d,p)))%p
        if not q or n!=(s["coefficients_by_compressed_row"][row]*q)%p:
            return False
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--samples",type=Path,default=ROOT/"vp05_same_prime_certificate_samples_grid_v4.json")
    ap.add_argument("--v3-samples",type=Path,default=ROOT/"vp05_same_prime_certificate_samples_grid_v3.json")
    ap.add_argument("--adaptive",type=Path,default=ROOT/"vp05_certificate_adaptive_degree_grid_v3.json")
    ap.add_argument("--degree4",type=Path,default=ROOT/"vp05_certificate_degree4_trial.json")
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_certificate_degree5_trial_grid_v4.json")
    a=ap.parse_args()
    raw=a.samples.read_bytes(); source=json.loads(raw.decode("utf-8-sig"))
    v3raw=a.v3_samples.read_bytes();v3=json.loads(v3raw.decode("utf-8-sig"))
    adaptive=json.loads(a.adaptive.read_text(encoding="utf-8-sig"))
    degree4=json.loads(a.degree4.read_text(encoding="utf-8-sig"))
    if source.get("type")!="same_prime_modular_certificate_samples" or source.get("rows")!=166:
        ap.error("Invalid v4 archive")
    if source.get("parent_archive_sha256")!=hashlib.sha256(v3raw).hexdigest():
        ap.error("v4 parent archive digest mismatch")
    if source.get("source_sha256")!=v3.get("source_sha256") or source["prime"]!=v3["prime"]:
        ap.error("v3/v4 compressed equations or prime mismatch")
    if adaptive["summary"]["source_sha256"]!=hashlib.sha256(v3raw).hexdigest() or degree4["summary"]["source_sha256"]!=hashlib.sha256(v3raw).hexdigest():
        ap.error("Prior fits not linked to v3 sample archive")
    prev={tuple(s["point"]):s for s in v3["samples"]}
    current={tuple(s["point"]):s for s in source["samples"]}
    if len(prev)!=len(v3["samples"]) or len(current)!=len(source["samples"]):
        ap.error("Duplicate evaluation point")
    if any(current.get(k)!=v for k,v in prev.items()):ap.error("v4 changed v3 sample content or role")
    train=[s for s in source["samples"] if s["role"]=="training"]
    hold=[s for s in source["samples"] if s["role"]=="holdout"]
    if len(train)<50 or len(hold)!=8:ap.error("Expected at least 50 training and exactly 8 holdouts")
    oldtrain={tuple(s["point"]) for s in v3["samples"] if s["role"]=="training"}
    added=[s for s in train if tuple(s["point"]) not in oldtrain]
    p=source["prime"]
    candidates={}
    for e in adaptive["results"]:
        if e["status"]=="holdout_pass":candidates[e["row"]]=e["model"]
    for e in degree4["rows"]:
        if e["status"]=="holdout_pass":
            if e["row"] in candidates:ap.error("Overlapping previous resolved rows")
            candidates[e["row"]]=e
    if len(candidates)!=113:ap.error("Unexpected prior passing candidate count")
    retained={}; invalid=[]
    for row,model in candidates.items():
        if check_model(model,added,p,row):retained[row]=model
        else:invalid.append(row)
    remaining=sorted(set(range(166))-set(candidates))
    if len(remaining)!=53:ap.error("Expected exactly 53 degree4-unresolved rows")
    outcomes=Counter();results=[]
    for row in remaining:
        m=fit(train,hold,p,row,5,5)
        outcomes[m["status"]]+=1
        results.append({"row":row,**m})
    new_pass=[x["row"] for x in results if x["status"]=="holdout_pass"]
    summary={"prime":p,"training":len(train),"new_training":len(added),"holdouts":len(hold),
        "tested_degree_pair":[5,5],"targeted_rows":len(remaining),
        "outcome_counts":dict(outcomes),"new_pass":len(new_pass),
        "old_candidates_retained_on_extra_training":len(retained),
        "old_candidates_failed_extra_training":len(invalid),
        "combined_validated_pass":len(retained)+len(new_pass),
        "samples_sha256":hashlib.sha256(raw).hexdigest(),
        "proof":False,"fermat_executed":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"summary":summary,"rows":results,
       "invalidated_earlier_rows":sorted(invalid),
       "retained_earlier_rows":sorted(retained)},indent=2)+"\n",encoding="utf-8")
    print("VP05_DEGREE5_TRIAL "+json.dumps({**summary,"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
