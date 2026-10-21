"""Analyze common factors in five ambiguous VP05 degree-six rational kernels.

Replays 80 modular certificate evaluations because original second-prime trial
did not persist raw samples. Restricts polynomial gcd work to five residual
rows; uses SymPy polynomial arithmetic over the second finite field.
No characteristic-zero proof and no Fermat/Kira.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_second_prime_ambiguity_audit import rref
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_dual_certificate_preflight import dual_certificate
from examples.three_loop_sector203_target_scope_preflight import TARGET,DEFAULT
from examples.three_loop_sector203_target_rowspace_audit import residue

ROOT=Path("output/three_loop_integral_family_audit")
EXPECTED={21,32,44,110,113}

def poly(coeff,mons,z,d,p):
    return sp.Poly(sum(int(c)*z**i*d**j for c,(i,j) in zip(coeff,mons)),z,d,modulus=p)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--trial",type=Path,default=ROOT/"vp05_independent_prime_certificate_grid9.json")
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_grid9_kernel_factor_audit.json")
    a=ap.parse_args()
    original=a.trial.read_bytes();trial=json.loads(original.decode("utf-8-sig"))
    eqraw=a.equations.read_bytes();equations=json.loads(eqraw.decode("utf-8-sig"))
    summ=trial["summary"];p=summ["prime"]
    if (summ.get("columns"),summ["training"],summ["holdouts"],summ["rejected"])!=(9,70,10,0):
        ap.error("Expected grid9: 70 training + 10 holdouts, zero rejected")
    if hashlib.sha256(eqraw).hexdigest()!=summ["equations_sha256"] or len(equations["rows"])!=166:
        ap.error("Compressed equation provenance conflict")
    failures=[x for x in trial["fits"] if x["result"]["status"]!="holdout_pass"]
    if len(failures)!=5 or {x["row"] for x in failures}!=EXPECTED:
        ap.error("Unexpected residual row set")
    samples=[]
    for i in range(80):
        z=(47+53*(i%9))%p;d=(83+79*(i//9))%p
        e=mod_rows(equations["rows"],p,z,d)
        target={k:residue(v,p,z,d) for k,v in TARGET.items()}
        c=dual_certificate(e,target,p)
        if c["rank"]!=166 or not c["replay_verified"]:
            raise RuntimeError("Certificate replay failure at "+str(i))
        samples.append({"z":z,"d":d,"coeff":[c["certificate"].get(row,0) for row in sorted(EXPECTED)]})
        if (i+1)%20==0:print("VP05_GRID9_FACTOR_PROGRESS "+json.dumps({"replayed":i+1}),flush=True)
    rows=sorted(EXPECTED);mons=powers(6);m=len(mons);zsym,dsym=sp.symbols("z d")
    output=[];tally=Counter()
    for failure in sorted(failures,key=lambda x:x["row"]):
        row=failure["row"];ind=rows.index(row)
        mat=[]
        for s in samples[:70]:
            v=value(mons,s["z"],s["d"],p);y=s["coeff"][ind]
            mat.append(v+[(-y*x)%p for x in v])
        rank,basis=rref(mat,p)
        if rank!=failure["result"]["rank"] or len(basis)!=failure["result"]["nullity"]:
            raise RuntimeError("Mismatch with saved fit rank/nullity: "+str(row))
        members=[]
        for b in basis:
            pn=poly(b[:m],mons,zsym,dsym,p)
            pd=poly(b[m:],mons,zsym,dsym,p)
            if pd.is_zero:
                members.append({"zero_denominator":True,"common_factor_total_degree":None})
                continue
            g=pn.gcd(pd)
            # Degree of the gcd is a property of a particular basis vector,
            # not necessarily the underlying rational function.
            gd=g.total_degree() if not g.is_zero else None
            members.append({"zero_denominator":False,"common_factor_total_degree":gd,
                            "reduced_numerator_degree":pn.exquo(g).total_degree(),
                            "reduced_denominator_degree":pd.exquo(g).total_degree()})
        checks=[]
        for s in samples[70:]:
            v=value(mons,s["z"],s["d"],p);observed=s["coeff"][ind]
            denom=[sum(c*x for c,x in zip(b[m:],v))%p for b in basis]
            num=[sum(c*x for c,x in zip(b[:m],v))%p for b in basis]
            all_agree=any(denom) and all((n-observed*q)%p==0 for n,q in zip(num,denom))
            checks.append(all_agree)
        all_pass=all(checks)
        tally["all_holdouts_function_fixed" if all_pass else "holdouts_not_fixed"]+=1
        output.append({"row":row,"kernel_rank":rank,"kernel_nullity":len(basis),
           "basis_polynomial_gcd_diagnostics":members,
           "all_kernel_vectors_match_holdout_count":sum(checks),
           "function_fixed_at_all_holdouts":all_pass})
    summary={"prime":p,"training":70,"holdouts":10,"rows":5,
        "kernel_nullity_histogram":dict(Counter(str(x["kernel_nullity"]) for x in output)),
        "outcomes":dict(tally),"trial_sha256":hashlib.sha256(original).hexdigest(),
        "equations_sha256":hashlib.sha256(eqraw).hexdigest(),
        "note":"GCDs of individual kernel basis vectors cannot alone establish a common rational function. Full-field sampled evidence, not exact proof.",
        "proof":False,"fermat_executed":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"summary":summary,"rows":output},indent=2)+"\n",encoding="utf-8")
    print("VP05_GRID9_FACTOR_AUDIT "+json.dumps({**summary,"row_ids":rows,"output":str(a.output)}),flush=True)
if __name__=="__main__":main()
