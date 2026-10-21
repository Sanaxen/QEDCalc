"""Assemble all 166 VP05 modular rational coefficient models and replay them.

Does not lift F_p coefficients to Q; provenance and complete sample replay only.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_certificate_degree5_trial import check_model

ROOT=Path("output/three_loop_integral_family_audit")
def get(path):
    raw=path.read_bytes()
    return json.loads(raw.decode("utf-8-sig")),hashlib.sha256(raw).hexdigest()

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--samples",type=Path,default=ROOT/"vp05_same_prime_certificate_samples_grid_v4.json")
    a.add_argument("--v3-samples",type=Path,default=ROOT/"vp05_same_prime_certificate_samples_grid_v3.json")
    a.add_argument("--adaptive",type=Path,default=ROOT/"vp05_certificate_adaptive_degree_grid_v3.json")
    a.add_argument("--degree4",type=Path,default=ROOT/"vp05_certificate_degree4_trial.json")
    a.add_argument("--degree5",type=Path,default=ROOT/"vp05_certificate_degree5_trial_grid_v4.json")
    a.add_argument("--degree6",type=Path,default=ROOT/"vp05_certificate_degree6_residual_trial.json")
    a.add_argument("--output",type=Path,default=ROOT/"vp05_modular_certificate_assembled.json")
    args=a.parse_args()
    samples,sha=get(args.samples);v3,v3sha=get(args.v3_samples)
    ad,adsha=get(args.adaptive);d4,d4sha=get(args.degree4)
    d5,d5sha=get(args.degree5);d6,d6sha=get(args.degree6)
    if samples.get("type")!="same_prime_modular_certificate_samples" or samples.get("rows")!=166:
        a.error("Invalid grid-v4 sample archive")
    if samples.get("parent_archive_sha256")!=v3sha:
        a.error("Invalid grid-v4 parent SHA256")
    if not (ad["summary"]["source_sha256"]==v3sha==d4["summary"]["source_sha256"]):
        a.error("Grid-v3 provenance conflict")
    if not (d5["summary"]["samples_sha256"]==sha==d6["summary"]["source_sha256"]):
        a.error("Grid-v4 provenance conflict")
    if samples["source_sha256"]!=v3["source_sha256"] or samples["prime"]!=v3["prime"]:
        a.error("Equation hash or prime mismatch")
    original={tuple(s["point"]):s for s in v3["samples"]}
    current={tuple(s["point"]):s for s in samples["samples"]}
    if len(original)!=len(v3["samples"]) or len(current)!=len(samples["samples"]) or any(current.get(k)!=s for k,s in original.items()):
        a.error("Changed original sample or duplicate point")
    if len([s for s in samples["samples"] if s["role"]=="training"])!=63 or len([s for s in samples["samples"] if s["role"]=="holdout"])!=8:
        a.error("Unexpected training/holdout partition")
    p=samples["prime"];models={};sources={}
    def add(row,model,origin):
        if not isinstance(row,int) or not 0<=row<166 or row in models:
            a.error("Duplicate or invalid model row "+str(row))
        if not model or not all(k in model for k in ("numerator_degree","denominator_degree","numerator","denominator")):
            a.error("Missing model fields "+str(row))
        models[row]=model;sources[row]=origin
    for e in ad["results"]:
        if e["status"]=="holdout_pass":add(e["row"],e["model"],"adaptive")
    for e in d4["rows"]:
        if e["status"]=="holdout_pass":add(e["row"],e,"degree4")
    for e in d5["rows"]:
        if e["status"]=="holdout_pass":add(e["row"],e,"degree5")
    for e in d6["rows"]:
        if e["degree6_status"]=="holdout_pass":add(e["row"],e["degree6_model"],"degree6")
    if set(models)!=set(range(166)):
        a.error("Incomplete model row coverage")
    if Counter(sources.values())!=Counter({"adaptive":94,"degree4":19,"degree5":45,"degree6":8}):
        a.error("Unexpected model breakdown")
    failed=[]
    for row,model in sorted(models.items()):
        if not check_model(model,samples["samples"],p,row):failed.append(row)
    if failed:a.error("Complete replay failed for rows: "+str(failed[:15]))
    records=[{"row":row,"origin":sources[row],"model":models[row]} for row in sorted(models)]
    summary={"prime":p,"rows":166,"train_replayed":63,"holdouts_replayed":8,
       "complete_sample_replay_passed":True,
       "origin_histogram":dict(Counter(sources.values())),
       "equations_sha256":samples["source_sha256"],
       "samples_sha256":sha,
       "artifact_sha256":{"adaptive":adsha,"degree4":d4sha,"degree5":d5sha,"degree6":d6sha},
       "rational_coefficient_lift":False,"symbolic_proof":False,"fermat_executed":False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({"summary":summary,"coefficients":records},indent=2)+"\n",encoding="utf-8")
    print("VP05_MODULAR_CERTIFICATE_ASSEMBLY "+json.dumps({**summary,"output":str(args.output)}),flush=True)
if __name__=="__main__":main()
