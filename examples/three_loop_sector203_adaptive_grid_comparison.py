"""Compare VP05 adaptive grid-v2/v3 results row by row, audit model rank.

Read-only modular diagnostic, no Fermat/Kira or exact rational proof.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_certificate_adaptive_degree import fit
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value,null_vector

ROOT=Path("output/three_loop_integral_family_audit")
def load(path,samples):
    b=samples.read_bytes()
    a=json.loads(path.read_text(encoding="utf-8-sig"))
    s=json.loads(b.decode("utf-8-sig"))
    if a["summary"]["source_sha256"]!=hashlib.sha256(b).hexdigest():
        raise ValueError("Archive digest mismatch: "+str(path))
    if a["summary"]["equations_sha256"]!=s["source_sha256"]:
        raise ValueError("Equation digest mismatch")
    if len(a["results"])!=166 or {x["row"] for x in a["results"]}!=set(range(166)):
        raise ValueError("Missing or duplicate row IDs")
    return a,s

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v2",type=Path,default=ROOT/"vp05_certificate_adaptive_degree.json")
    ap.add_argument("--v3",type=Path,default=ROOT/"vp05_certificate_adaptive_degree_grid_v3.json")
    ap.add_argument("--samples-v2",type=Path,default=ROOT/"vp05_same_prime_certificate_samples_grid_v2.json")
    ap.add_argument("--samples-v3",type=Path,default=ROOT/"vp05_same_prime_certificate_samples_grid_v3.json")
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_adaptive_grid_comparison.json")
    args=ap.parse_args()
    a,s2=load(args.v2,args.samples_v2)
    b,s3=load(args.v3,args.samples_v3)
    if s2["prime"]!=s3["prime"] or s2["source_sha256"]!=s3["source_sha256"]:
        ap.error("Grid-v2 and grid-v3 are incompatible")
    original={tuple(x["point"]):x for x in s2["samples"]}
    newer={tuple(x["point"]):x for x in s3["samples"]}
    if not set(original).issubset(newer):
        ap.error("Grid-v3 omitted original samples")
    for key,item in original.items():
        if newer[key]!=item:ap.error("Existing samples/holdout roles changed")
    old={x["row"]:x for x in a["results"]}
    new={x["row"]:x for x in b["results"]}
    changes={"pass_to_unresolved":[],"unresolved_to_pass":[],"pass_to_pass":[],"unresolved_to_unresolved":[]}
    details=[]
    p=s3["prime"]
    train=[x for x in s3["samples"] if x["role"]=="training"]
    hold=[x for x in s3["samples"] if x["role"]=="holdout"]
    for row in range(166):
        prev=old[row];curr=new[row]
        prior=prev["status"]=="holdout_pass";now=curr["status"]=="holdout_pass"
        name=("pass" if prior else "unresolved")+"_to_"+("pass" if now else "unresolved")
        changes[name].append(row)
        if not now:
            # Examine (3,3) under the full training grid and distinguish
            # kernel nonuniqueness from unique-but-invalid holdouts.
            diagnostic=fit(train,hold,p,row,3,3)
            details.append({"row":row,"transition":name,
                "v2_model_degrees":[prev["model"]["numerator_degree"],prev["model"]["denominator_degree"]] if prev["model"] else None,
                "v3_nonunique_attempts":curr["nonunique"],
                "v3_holdout_failed_attempts":curr["holdout_failures"],
                "full_3_3_status":diagnostic["status"],
                "full_3_3_nullity":diagnostic.get("nullity"),
                "full_3_3_rank":diagnostic.get("rank"),
                "full_3_3_holdouts_passed":diagnostic.get("holdouts_passed")})
    summary={"v2_resolved":len(changes["pass_to_pass"])+len(changes["pass_to_unresolved"]),
      "v3_resolved":len(changes["pass_to_pass"])+len(changes["unresolved_to_pass"]),
      "transitions":{k:len(v) for k,v in changes.items()},
      "prime":p,"train_v2":sum(x["role"]=="training" for x in s2["samples"]),
      "train_v3":len(train),"untouched_holdouts":len(hold),
      "proof":False,"fermat_executed":False}
    report={"summary":summary,"row_ids":changes,"unresolved_diagnostics":details}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_GRID_COMPARE_SUMMARY "+json.dumps({**summary,"output":str(args.output)}),flush=True)
    counts={}
    for item in details:
        key=item["full_3_3_status"]
        counts[key]=counts.get(key,0)+1
    print("VP05_GRID_COMPARE_UNRESOLVED "+json.dumps({"count":len(details),"degree_3_3_statuses":counts,"proof":False}),flush=True)

if __name__=="__main__":main()
