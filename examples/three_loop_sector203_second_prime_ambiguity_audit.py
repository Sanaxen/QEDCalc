"""Audit ambiguity of the eight VP05 degree-(6,6) second-prime fits.

Compute homogeneous nullspace and ask whether all possible numerator/
denominator pairs imply the same value on reserved holdouts, using the
cross-product rank test (no arbitrary basis-vector selection).
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value

ROOT=Path("output/three_loop_integral_family_audit")

def rref(matrix,p):
    a=[list(map(lambda v:v%p,row)) for row in matrix]
    n=len(a[0]); piv=[];r=0
    for c in range(n):
        j=next((j for j in range(r,len(a)) if a[j][c]),None)
        if j is None:continue
        a[r],a[j]=a[j],a[r]
        inv=pow(a[r][c],-1,p);a[r]=[x*inv%p for x in a[r]]
        for k in range(len(a)):
            if k!=r and a[k][c]:
                v=a[k][c];a[k]=[(x-v*y)%p for x,y in zip(a[k],a[r])]
        piv.append(c);r+=1
        if r==len(a):break
    free=[c for c in range(n) if c not in piv]
    basis=[]
    for j in free:
        v=[0]*n;v[j]=1
        for i,c in enumerate(piv):v[c]=-a[i][j]%p
        basis.append(v)
    return r,basis

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--independent",type=Path,default=ROOT/"vp05_independent_prime_certificate.json")
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_second_prime_ambiguity_audit.json")
    args=ap.parse_args()
    obj=json.loads(args.independent.read_text(encoding="utf-8-sig"))
    summ=obj["summary"];p=summ["prime"]
    fails=[x for x in obj["fits"] if x["result"]["status"]!="holdout_pass"]
    if len(fails)!=8 or any(x["original_degree"]!=[6,6] for x in fails):
        ap.error("Expected eight degree-(6,6) residual fits")
    # Original independent-prime script stores model fits, but NOT the sampled
    # certificate vectors. Recompute only if a separate sample archive exists.
    # This audit can still safely expose the known exact nullity from results
    # and identify what must be retained to determine rational-function identity.
    details=[{"row":x["row"],"kernel_rank":x["result"].get("rank"),
              "kernel_nullity":x["result"].get("nullity"),
              "holdout_function_equivalence":"not_testable_without_saved_second_prime_samples"}
             for x in fails]
    histogram={}
    for x in details:
        k=str(x["kernel_nullity"]);histogram[k]=histogram.get(k,0)+1
    report={"summary":{"prime":p,"residual_rows":len(details),
         "kernel_nullity_histogram":histogram,"source_sha256":hashlib.sha256(args.independent.read_bytes()).hexdigest(),
         "saved_second_prime_sample_vectors":False,
         "next_action":"Save new-prime raw modular certificate evaluations before testing holdout rational equivalence.",
         "proof":False,"fermat_executed":False},"rows":details}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("VP05_SECOND_PRIME_AMBIGUITY "+json.dumps({**report["summary"],"row_ids":[x["row"] for x in details],"output":str(args.output)}),flush=True)
if __name__=="__main__":main()
