"""VP05 residual certificate diagnosis and bounded degree-(6,6) trial.

Classify degree-(5,5) kernel nullity correctly (zero versus >1).
Only for zero-kernel rows, try degree-(6,6) using the existing 63
training samples and eight reserved holdouts. Modular hypotheses only.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value,null_vector
from examples.three_loop_sector203_certificate_adaptive_degree import fit

ROOT=Path("output/three_loop_integral_family_audit")

def kernel_info(train,p,row,degree):
    mons=powers(degree)
    matrix=[]
    for s in train:
        z,d=s["point"][1:]
        v=value(mons,z,d,p)
        y=s["coefficients_by_compressed_row"][row]%p
        matrix.append(v+[(-y*x)%p for x in v])
    _,rank,nullity=null_vector(matrix,p)
    return {"rank":rank,"nullity":nullity}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--samples",type=Path,default=ROOT/"vp05_same_prime_certificate_samples_grid_v4.json")
    ap.add_argument("--degree5",type=Path,default=ROOT/"vp05_certificate_degree5_trial_grid_v4.json")
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_certificate_degree6_residual_trial.json")
    a=ap.parse_args()
    raw=a.samples.read_bytes()
    source=json.loads(raw.decode("utf-8-sig"))
    old=json.loads(a.degree5.read_text(encoding="utf-8-sig"))
    digest=hashlib.sha256(raw).hexdigest()
    if source.get("type")!="same_prime_modular_certificate_samples" or source.get("rows")!=166:
        ap.error("Invalid grid-v4 certificate sample archive")
    if old["summary"]["samples_sha256"]!=digest or old["summary"]["combined_validated_pass"]!=158:
        ap.error("Degree5 archive digest or preceding fit count mismatch")
    p=source["prime"]
    train=[x for x in source["samples"] if x["role"]=="training"]
    hold=[x for x in source["samples"] if x["role"]=="holdout"]
    if len(train)!=63 or len(hold)!=8 or len({tuple(x["point"]) for x in source["samples"]})!=71:
        ap.error("Expected 63 distinct training samples and 8 holdouts")
    if not all(s["point"][0]==p and s.get("replay_verified") and len(s["coefficients_by_compressed_row"])==166 for s in source["samples"]):
        ap.error("Sample replay metadata invalid")
    remaining=[x for x in old["rows"] if x["status"]!="holdout_pass"]
    if len(remaining)!=8 or len({x["row"] for x in remaining})!=8:
        ap.error("Expected exactly 8 remaining distinct coefficient rows")
    histogram5=Counter(); histogram6=Counter(); results=[]
    for entry in remaining:
        row=entry["row"]
        info5=kernel_info(train,p,row,5)
        histogram5[info5["nullity"]]+=1
        record={"row":row,"degree5_kernel":info5}
        if info5["nullity"]==0:
            info6=kernel_info(train,p,row,6)
            histogram6[info6["nullity"]]+=1
            model=fit(train,hold,p,row,6,6) if info6["nullity"]==1 else None
            record.update({"degree6_kernel":info6,
                 "degree6_status":model["status"] if model else ("no_nonzero_fit" if info6["nullity"]==0 else "nonunique"),
                 "degree6_model":model})
        else:
            record["degree6_status"]="not_tried_degree5_nonzero_kernel"
        results.append(record)
    added=sum(x["degree6_status"]=="holdout_pass" for x in results)
    summary={"prime":p,"training":len(train),"untouched_holdouts":len(hold),
        "residual_rows":len(remaining),"degree5_nullity_histogram":dict(sorted(histogram5.items())),
        "degree6_nullity_histogram":dict(sorted(histogram6.items())),
        "degree6_new_pass":added,"combined_provisional_pass":158+added,
        "source_sha256":digest,"proof":False,"fermat_executed":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"summary":summary,"rows":results},indent=2)+"\n",encoding="utf-8")
    print("VP05_DEGREE6_RESIDUAL_SUMMARY "+json.dumps({**summary,"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
