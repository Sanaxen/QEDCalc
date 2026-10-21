"""Recompute second-prime VP05 sample values and audit 8 ambiguous rational fits.

For every held-out point test if the evaluation linear forms N and Q are
proportional on the complete training nullspace, and whether a nonzero
denominator exists. If not proportional, rational value is not fixed by
the training constraints. Never select arbitrary kernel basis vectors.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
from examples.three_loop_sector203_second_prime_ambiguity_audit import rref
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_dual_certificate_preflight import dual_certificate
from examples.three_loop_sector203_target_scope_preflight import TARGET,DEFAULT
from examples.three_loop_sector203_target_rowspace_audit import residue

ROOT=Path("output/three_loop_integral_family_audit")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--independent",type=Path,default=ROOT/"vp05_independent_prime_certificate.json")
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_second_prime_functional_ambiguity.json")
    a=ap.parse_args()
    raw=a.equations.read_bytes();eq=json.loads(raw.decode("utf-8-sig"))
    report=json.loads(a.independent.read_text(encoding="utf-8-sig"))
    s=report["summary"];p=s["prime"]
    if hashlib.sha256(raw).hexdigest()!=s["equations_sha256"] or len(eq["rows"])!=166:
        ap.error("Independent trial compressed-equation digest mismatch")
    if s["training"]!=70 or s["holdouts"]!=10 or s["rejected"]!=0:
        ap.error("Expected exactly 80 accepted points and zero rejects for deterministic replay")
    failed=[x for x in report["fits"] if x["result"]["status"]!="holdout_pass"]
    if len(failed)!=8 or any(x["original_degree"]!=[6,6] for x in failed):
        ap.error("Unexpected residual set or degrees")
    # Exact same geometry and order as the original independent prime runner.
    samples=[];targets={}
    for i in range(80):
        z=(47+53*(i%13))%p;d=(83+79*(i//13))%p
        ev=mod_rows(eq["rows"],p,z,d)
        target={k:residue(v,p,z,d) for k,v in TARGET.items()}
        cert=dual_certificate(ev,target,p)
        if cert["rank"]!=166 or not cert["replay_verified"]:
            raise RuntimeError("Independent sample replay failure at "+str(i))
        samples.append({"point":[p,z,d],
          "coefficients_by_compressed_row":[cert["certificate"].get(j,0) for j in range(166)]})
        if (i+1)%20==0:print("VP05_SECOND_PRIME_FUNCTION_PROGRESS "+json.dumps({"replayed":i+1}),flush=True)
    train=samples[:70];hold=samples[70:]
    mons=powers(6);m=len(mons);results=[];tally=Counter()
    for x in failed:
        row=x["row"];matrix=[]
        for sample in train:
            z,d=sample["point"][1:];v=value(mons,z,d,p)
            y=sample["coefficients_by_compressed_row"][row]
            matrix.append(v+[(-y*t)%p for t in v])
        rank,basis=rref(matrix,p)
        if len(basis)!=x["result"]["nullity"] or rank!=x["result"]["rank"]:
            raise RuntimeError("Nullity/rank mismatch on row "+str(row))
        checks=[]
        for sample in hold:
            z,d=sample["point"][1:];v=value(mons,z,d,p)
            den=[sum(u*w for u,w in zip(b[m:],v))%p for b in basis]
            num=[sum(u*w for u,w in zip(b[:m],v))%p for b in basis]
            y=sample["coefficients_by_compressed_row"][row]
            denominator_possible=any(den)
            all_agree=denominator_possible and all((n-y*q)%p==0 for n,q in zip(num,den))
            checks.append({"point":[p,z,d],"denominator_possible":denominator_possible,
                           "all_kernel_vectors_agree":all_agree})
        count=sum(t["all_kernel_vectors_agree"] for t in checks)
        verdict="holdout_function_fixed" if count==10 else "training_nullspace_not_function_fixed"
        tally[verdict]+=1
        results.append({"row":row,"rank":rank,"nullity":len(basis),
                        "verified_holdouts":count,"status":verdict,"holdout_checks":checks})
    output={"summary":{"prime":p,"training":70,"holdouts":10,
      "replayed":80,"rows":len(results),"outcomes":dict(tally),
      "source_sha256":hashlib.sha256(a.independent.read_bytes()).hexdigest(),
      "equations_sha256":hashlib.sha256(raw).hexdigest(),
      "proof":False,"fermat_executed":False},
      "rows":results}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("VP05_SECOND_PRIME_FUNCTIONAL_AMBIGUITY "+json.dumps({**output["summary"],"output":str(a.output)}),flush=True)
if __name__=="__main__":main()
