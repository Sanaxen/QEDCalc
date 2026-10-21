"""Compare all nullspace basis rational functions by polynomial cross-products.

Five VP05 second-prime grid9 residual rows, four basis vectors per row.
Unlike held-out point checks, P_i Q_j - P_j Q_i == 0 in F_p[z,d]
establishes equality of the corresponding rational functions (when
denominators are nonzero polynomials). Not a Q(z,d) characteristic-zero proof.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from itertools import combinations
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_second_prime_ambiguity_audit import rref
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_dual_certificate_preflight import dual_certificate
from examples.three_loop_sector203_target_scope_preflight import TARGET,DEFAULT
from examples.three_loop_sector203_target_rowspace_audit import residue

ROOT=Path("output/three_loop_integral_family_audit")
ROWS=[21,32,44,110,113]

def poly(coeff,mons,z,d,p):
    return sp.Poly(sum(int(c)*z**i*d**j for c,(i,j) in zip(coeff,mons)),z,d,modulus=p)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--trial",type=Path,default=ROOT/"vp05_independent_prime_certificate_grid9.json")
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_grid9_kernel_cross_product.json")
    args=ap.parse_args()
    trial_bytes=args.trial.read_bytes()
    trial=json.loads(trial_bytes.decode("utf-8-sig"))
    eqbytes=args.equations.read_bytes()
    eq=json.loads(eqbytes.decode("utf-8-sig"))
    s=trial["summary"];p=s["prime"]
    if (s.get("columns"),s["training"],s["holdouts"],s["rejected"])!=(9,70,10,0):
        ap.error("Expected 9-column second-prime 70/10 trial")
    if hashlib.sha256(eqbytes).hexdigest()!=s["equations_sha256"] or len(eq["rows"])!=166:
        ap.error("Equations SHA256 or row count mismatch")
    failures={x["row"]:x for x in trial["fits"] if x["result"]["status"]!="holdout_pass"}
    if set(failures)!=set(ROWS) or any(x["original_degree"]!=[6,6] for x in failures.values()):
        ap.error("Unexpected residual rows or degrees")
    data=[]
    for i in range(70):
        z=(47+53*(i%9))%p;d=(83+79*(i//9))%p
        evaluated=mod_rows(eq["rows"],p,z,d)
        target={k:residue(v,p,z,d) for k,v in TARGET.items()}
        result=dual_certificate(evaluated,target,p)
        if result["rank"]!=166 or not result["replay_verified"]:
            raise RuntimeError("Modular certificate replay failed at training point "+str(i))
        data.append((z,d,[result["certificate"].get(row,0) for row in ROWS]))
        if (i+1)%20==0 or i==69:
            print("VP05_CROSS_PRODUCT_PROGRESS "+json.dumps({"training_replayed":i+1}),flush=True)
    mons=powers(6);m=len(mons);zsym,dsym=sp.symbols("z d")
    rows=[];hist=Counter()
    for j,row in enumerate(ROWS):
        matrix=[]
        for z,d,coeffs in data:
            v=value(mons,z,d,p);y=coeffs[j]%p
            matrix.append(v+[(-y*x)%p for x in v])
        rank,basis=rref(matrix,p)
        if rank!=failures[row]["result"]["rank"] or len(basis)!=4:
            raise RuntimeError("Rank/nullity mismatch at row "+str(row))
        parts=[(poly(v[:m],mons,zsym,dsym,p),poly(v[m:],mons,zsym,dsym,p)) for v in basis]
        if any(q.is_zero for _,q in parts):
            raise RuntimeError("Nullspace basis has zero denominator polynomial; separate treatment required")
        comparisons=[]
        for u,v in combinations(range(len(parts)),2):
            n1,q1=parts[u];n2,q2=parts[v]
            cross=n1*q2-n2*q1
            identical=cross.is_zero
            hist["identical" if identical else "distinct"]+=1
            comparisons.append({"basis_indices":[u,v],"identical_rational_function":identical,
                "cross_product_degree":None if identical else cross.total_degree(),
                "cross_product_terms":len(cross.terms())})
        rows.append({"row":row,"kernel_rank":rank,"kernel_nullity":len(basis),
            "pair_comparisons":comparisons,
            "all_basis_functions_identical":all(x["identical_rational_function"] for x in comparisons)})
    out={"summary":{"prime":p,"training_replayed":70,"holdouts_not_used":10,
        "rows":len(rows),"pair_comparisons":sum(len(x["pair_comparisons"]) for x in rows),
        "cross_product_outcomes":dict(hist),"all_rows_identical":all(x["all_basis_functions_identical"] for x in rows),
        "trial_sha256":hashlib.sha256(trial_bytes).hexdigest(),
        "equations_sha256":hashlib.sha256(eqbytes).hexdigest(),
        "modular_polynomial_identity_only":True,"symbolic_proof":False,
        "fermat_executed":False},"rows":rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("VP05_GRID9_CROSS_PRODUCT "+json.dumps({**out["summary"],"per_row":[{"row":r["row"],"all_identical":r["all_basis_functions_identical"]} for r in rows],"output":str(args.output)}),flush=True)
if __name__=="__main__":main()
