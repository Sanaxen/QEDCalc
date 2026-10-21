"""Diagnose exact homogeneous kernel nullities for VP05 degree-(4,4) trial.

Distinguishes nullity=0 (no nonzero degree-bounded fit) from nullity>1
(multiple polynomial representations). No Fermat/Kira or symbolic proof.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value,null_vector

ROOT=Path("output/three_loop_integral_family_audit")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--samples",type=Path,default=ROOT/"vp05_same_prime_certificate_samples_grid_v3.json")
    ap.add_argument("--trial",type=Path,default=ROOT/"vp05_certificate_degree4_trial.json")
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_degree4_kernel_diagnostic.json")
    a=ap.parse_args()
    raw=a.samples.read_bytes()
    source=json.loads(raw.decode("utf-8-sig"))
    trial=json.loads(a.trial.read_text(encoding="utf-8-sig"))
    summary=trial["summary"]
    if source.get("type")!="same_prime_modular_certificate_samples" or source.get("rows")!=166:
        ap.error("Unexpected sample archive")
    if hashlib.sha256(raw).hexdigest()!=summary["source_sha256"]:
        ap.error("Trial/sample SHA256 mismatch")
    p=source["prime"]
    train=[s for s in source["samples"] if s["role"]=="training"]
    hold=[s for s in source["samples"] if s["role"]=="holdout"]
    if len(train)!=39 or len(hold)!=8 or summary["training"]!=39 or summary["holdouts"]!=8:
        ap.error("Unexpected training/holdout partition")
    records=trial["rows"]
    if len(records)!=summary["targeted_rows"] or len({r["row"] for r in records})!=len(records):
        ap.error("Invalid trial rows")
    mon=powers(4)
    evals=[value(mon,s["point"][1],s["point"][2],p) for s in train]
    hist=Counter()
    detailed=[]
    for entry in records:
        if not 0<=entry["row"]<166:ap.error("Invalid row index")
        row=entry["row"]
        mat=[v+[(-s["coefficients_by_compressed_row"][row]*x)%p for x in v]
             for v,s in zip(evals,train)]
        _,rank,nullity=null_vector(mat,p)
        expected="no_nonzero_fit" if nullity==0 else "projectively_unique" if nullity==1 else "representation_nonunique"
        # Catch incompatibility with the original trial while repairing its legacy label.
        if (nullity==1)!=(entry["status"] in ("holdout_pass","holdout_fail","singular_training")):
            ap.error("Kernel nullity/trial status mismatch on row "+str(row))
        hist[expected]+=1
        detailed.append({"row":row,"kernel_rank":rank,"kernel_nullity":nullity,
                         "classification":expected,"original_status":entry["status"]})
    summary_out={"prime":p,"training":len(train),"holdouts_unchanged":len(hold),
       "degree_pair":[4,4],"targeted_rows":len(records),"counts":dict(hist),
       "kernel_nullity_histogram":dict(sorted(Counter(x["kernel_nullity"] for x in detailed).items())),
       "samples_sha256":hashlib.sha256(raw).hexdigest(),
       "symbolic_proof":False,"fermat_executed":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"summary":summary_out,"rows":detailed},indent=2)+"\n",encoding="utf-8")
    print("VP05_DEGREE4_KERNEL_DIAGNOSTIC "+json.dumps({**summary_out,"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
