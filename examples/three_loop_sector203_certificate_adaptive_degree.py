"""Adaptive (numerator degree, denominator degree) VP05 certificate search.

Finite-field hypotheses only. Fits 19 training points, verifies 8 untouched
holdouts. Rejects ambiguous kernels and invalid denominators. No Fermat/Kira.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value,null_vector

DEFAULT=Path("output/three_loop_integral_family_audit/vp05_same_prime_certificate_samples_grid_v2.json")
OUT=Path("output/three_loop_integral_family_audit/vp05_certificate_adaptive_degree.json")


def fit(train,hold,p,row,nd,dd):
    nm=powers(nd);dm=powers(dd)
    if len(nm)+len(dm)-1>len(train):
        return {"status":"insufficient_training"}
    matrix=[]
    for s in train:
        z,d=s["point"][1:]
        y=s["coefficients_by_compressed_row"][row]%p
        matrix.append(value(nm,z,d,p)+[(-y*x)%p for x in value(dm,z,d,p)])
    v,rank,nullity=null_vector(matrix,p)
    if v is None:return {"status":"nonunique","nullity":nullity,"rank":rank}
    numerator=v[:len(nm)];denominator=v[len(nm):]
    for s in train:
        z,d=s["point"][1:]
        den=sum(a*b for a,b in zip(denominator,value(dm,z,d,p)))%p
        num=sum(a*b for a,b in zip(numerator,value(nm,z,d,p)))%p
        if den==0 or num!=s["coefficients_by_compressed_row"][row]*den%p:
            return {"status":"singular_training","rank":rank}
    matches=0
    for s in hold:
        z,d=s["point"][1:]
        den=sum(a*b for a,b in zip(denominator,value(dm,z,d,p)))%p
        num=sum(a*b for a,b in zip(numerator,value(nm,z,d,p)))%p
        if not den or num!=s["coefficients_by_compressed_row"][row]*den%p:break
        matches+=1
    return {"status":"holdout_pass" if matches==len(hold) else "holdout_fail",
            "holdouts_passed":matches,"rank":rank,"numerator_degree":nd,
            "denominator_degree":dd,"numerator":numerator,"denominator":denominator}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--samples",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=OUT)
    ap.add_argument("--max-degree",type=int,default=3)
    a=ap.parse_args()
    if not 0<=a.max_degree<=5:ap.error("max-degree must be 0..5")
    raw=a.samples.read_bytes()
    data=json.loads(raw.decode("utf-8-sig"))
    if data.get("type")!="same_prime_modular_certificate_samples" or data.get("rows")!=166:
        ap.error("Invalid same-prime sample archive")
    p=data["prime"]
    train=[s for s in data["samples"] if s["role"]=="training"]
    hold=[s for s in data["samples"] if s["role"]=="holdout"]
    if len(train)<1 or len(hold)<1:ap.error("Both training and holdout samples are required")
    if len({tuple(s["point"]) for s in data["samples"]})!=len(data["samples"]):
        ap.error("Repeated sampling point")
    for s in data["samples"]:
        if s["point"][0]!=p or not s.get("replay_verified") or len(s["coefficients_by_compressed_row"])!=166:
            ap.error("Invalid or unverified sample")
    candidates=sorted(((n,d) for n in range(a.max_degree+1) for d in range(a.max_degree+1)),
                      key=lambda q:(len(powers(q[0]))+len(powers(q[1]))-1,q[0]+q[1],q[0],q[1]))
    results=[]
    for row in range(166):
        attempted=0;nonunique=0;holdout_failed=0
        best=None
        for nd,dd in candidates:
            if len(powers(nd))+len(powers(dd))-1>len(train):continue
            attempted+=1
            model=fit(train,hold,p,row,nd,dd)
            if model["status"]=="holdout_pass":
                best=model;break
            if model["status"]=="nonunique":nonunique+=1
            if model["status"]=="holdout_fail":holdout_failed+=1
        results.append({"row":row,"status":"holdout_pass" if best else "unresolved",
                        "models_tried":attempted,"nonunique":nonunique,
                        "holdout_failures":holdout_failed,
                        "model":best})
    successes=sum(x["status"]=="holdout_pass" for x in results)
    histogram={}
    for entry in results:
        if entry["model"]:
            m=entry["model"];key=f'{m["numerator_degree"]},{m["denominator_degree"]}'
            histogram[key]=histogram.get(key,0)+1
    summary={"prime":p,"training":len(train),"holdouts":len(hold),
             "max_degree":a.max_degree,"resolved_finite_field":successes,
             "unresolved":166-successes,"degree_pair_histogram":histogram,
             "source_sha256":hashlib.sha256(raw).hexdigest(),
             "equations_sha256":data.get("source_sha256"),
             "symbolic_proof":False,"fermat_executed":False,
             "interpretation":"Held-out finite-field fits are hypotheses, not exact identities."}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"summary":summary,"results":results},indent=2)+"\n",encoding="utf-8")
    print("VP05_ADAPTIVE_DEGREE_SUMMARY "+json.dumps({**summary,"output":str(a.output)}),flush=True)


if __name__=="__main__":main()
