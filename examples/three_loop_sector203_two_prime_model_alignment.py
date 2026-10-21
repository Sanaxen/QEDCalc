"""Assemble VP05 second-prime models and compare projective normalizations.

Only models with the SAME monomial degree bases and the SAME nonzero
pivot index can be coefficient-aligned across primes. Distinct degree
pairs are recorded as blockers, never silently padded/lifted.
CRT and characteristic-zero reconstruction are NOT performed here.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
from examples.three_loop_sector203_certificate_interpolation_trial import powers

ROOT=Path("output/three_loop_integral_family_audit")
RESIDUAL={21,32,44,110,113}

def read(path):
    raw=path.read_bytes()
    return json.loads(raw.decode("utf-8-sig")),hashlib.sha256(raw).hexdigest()

def canonical(model,p):
    nd=model["numerator_degree"];dd=model["denominator_degree"]
    n=list(model["numerator"]); d=list(model["denominator"])
    if len(n)!=len(powers(nd)) or len(d)!=len(powers(dd)):
        raise ValueError("Model vector length does not match degree bounds")
    v=[int(x)%p for x in (n+d)]
    # Favor denominator coefficient as a stable projective pivot; pick
    # deterministically from highest-index nonzero coefficient.
    candidates=[i for i in range(len(n),len(v)) if v[i]]
    if not candidates:raise ValueError("Zero denominator polynomial")
    pivot=candidates[-1];inv=pow(v[pivot],-1,p)
    out=[x*inv%p for x in v]
    return {"degree_pair":[nd,dd],"pivot":pivot,
            "numerator":out[:len(n)],"denominator":out[len(n):]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--first",type=Path,default=ROOT/"vp05_modular_certificate_assembled.json")
    ap.add_argument("--second",type=Path,default=ROOT/"vp05_independent_prime_certificate_grid9.json")
    ap.add_argument("--offgrid",type=Path,default=ROOT/"vp05_grid9_offgrid_kernel_shrink.json")
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_two_prime_model_alignment.json")
    a=ap.parse_args()
    first,hash1=read(a.first);second,hash2=read(a.second);offgrid,hash3=read(a.offgrid)
    p1=first["summary"]["prime"];p2=second["summary"]["prime"]
    if p1==p2 or (p1,p2)!=(1000037,1001003):
        ap.error("Unexpected pair of primes")
    if (first["summary"]["equations_sha256"]!=second["summary"]["equations_sha256"]
       or second["summary"]["equations_sha256"]!=offgrid["summary"]["equations_sha256"]):
        ap.error("Compressed equations provenance mismatch")
    if not first["summary"]["complete_sample_replay_passed"]:
        ap.error("First-prime assembly has no complete replay")
    if (offgrid["summary"]["trial_sha256"]!=hash2 or
        offgrid["summary"]["holdouts_untouched"]!=10 or
        offgrid["summary"]["outcome_counts"].get("holdout_pass")!=5):
        ap.error("Offgrid result provenance or holdouts mismatch")
    if len(first["coefficients"])!=166 or len(second["fits"])!=166:
        ap.error("Incomplete coefficient sets")
    f1={e["row"]:e for e in first["coefficients"]}
    f2={e["row"]:e for e in second["fits"]}
    recovered={e["row"]:e for e in offgrid["rows"]}
    if set(f1)!=set(range(166)) or set(f2)!=set(range(166)) or set(recovered)!=RESIDUAL:
        ap.error("Duplicate, missing or incorrect row IDs")
    output=[];hist=Counter()
    for row in range(166):
        base=f1[row]
        candidate=f2[row]
        if row in RESIDUAL:
            recovered_row=recovered[row]
            if recovered_row["status"]!="holdout_pass" or recovered_row["nullity"]!=1:
                ap.error("Recovered row not uniquely validated "+str(row))
            model=recovered_row["model"]
            origin="offgrid"
        else:
            if candidate["result"]["status"]!="holdout_pass":
                ap.error("Unresolved non-recovered second-prime row "+str(row))
            model=candidate["result"]
            origin="grid9"
        if tuple(candidate["original_degree"])!=(
            base["model"]["numerator_degree"],base["model"]["denominator_degree"]):
            ap.error("Degree lineage mismatch "+str(row))
        m1=canonical(base["model"],p1)
        m2=canonical(model,p2)
        comparable=m1["degree_pair"]==m2["degree_pair"] and m1["pivot"]==m2["pivot"]
        reason="common_projective_pivot" if comparable else "pivot_or_degree_mismatch"
        hist[reason]+=1
        output.append({"row":row,"first_origin":base["origin"],"second_origin":origin,
          "coefficient_alignment_possible":comparable,"alignment_status":reason,
          "first":m1,"second":m2})
    report={"summary":{"first_prime":p1,"second_prime":p2,"rows":166,
      "second_prime_grid9_pass":161,"second_prime_offgrid_pass":5,
      "alignment_status_histogram":dict(hist),
      "coefficient_alignment_is_rational_reconstruction":False,
      "cross_prime_equality_proven":False,"symbolic_proof":False,
      "fermat_executed":False,
      "source_sha256":{"first":hash1,"second":hash2,"offgrid":hash3},
      "equations_sha256":first["summary"]["equations_sha256"]},
      "coefficients":output}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_TWO_PRIME_MODEL_ALIGNMENT "+json.dumps({**report["summary"],"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
