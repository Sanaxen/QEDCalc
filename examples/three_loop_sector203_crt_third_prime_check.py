"""Independent third-prime verification of tentative VP05 CRT rational functions.

Evaluates reconstructed P(z,d)/Q(z,d) at fresh modular points and compares
every coefficient with freshly replayed compressed-IBP dual certificates.
No symbolic proof, Fermat, or Kira.
"""
from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
import sympy as sp
from examples.three_loop_sector203_certificate_interpolation_trial import powers,value
from examples.three_loop_sector203_fermat_gaussian_pilot import mod_rows
from examples.three_loop_sector203_dual_certificate_preflight import dual_certificate
from examples.three_loop_sector203_target_scope_preflight import TARGET,DEFAULT
from examples.three_loop_sector203_target_rowspace_audit import residue

ROOT=Path("output/three_loop_integral_family_audit")

def rat_mod(pair,p):
    if pair is None:return None
    n,d=pair
    if d%p==0:return None
    return (n%p)*pow(d,-1,p)%p

def evaluate(entry,z,d,p):
    ndeg,ddeg=entry["degree_pair"]
    vv_n=value(powers(ndeg),z,d,p)
    vv_d=value(powers(ddeg),z,d,p)
    numerator=0;denominator=0
    for term,v in zip(entry["coefficients"]["numerator"],vv_n):
        t=rat_mod(term["rational_candidate"],p)
        if t is None:return None
        numerator=(numerator+t*v)%p
    for term,v in zip(entry["coefficients"]["denominator"],vv_d):
        t=rat_mod(term["rational_candidate"],p)
        if t is None:return None
        denominator=(denominator+t*v)%p
    return numerator*pow(denominator,-1,p)%p if denominator else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--crt",type=Path,default=ROOT/"vp05_two_prime_crt_candidate_audit.json")
    ap.add_argument("--equations",type=Path,default=DEFAULT)
    ap.add_argument("--prime",type=int,default=1001107)
    ap.add_argument("--points",type=int,default=3)
    ap.add_argument("--output",type=Path,default=ROOT/"vp05_crt_third_prime_check.json")
    a=ap.parse_args()
    if not sp.isprime(a.prime) or a.prime in (1000037,1001003):ap.error("Select a fresh prime")
    if not 1<=a.points<=8:ap.error("Bounded to 1..8 test points")
    crt_raw=a.crt.read_bytes();report=json.loads(crt_raw.decode("utf-8-sig"))
    eq_raw=a.equations.read_bytes();eq=json.loads(eq_raw.decode("utf-8-sig"))
    rows=report["rows"]
    if len(rows)!=166 or {x["row"] for x in rows}!=set(range(166)) or not all(x["all_coefficients_reconstructed"] for x in rows):
        ap.error("Incomplete CRT coefficient candidates")
    if eq.get("type")!="symbolic_exact_linear_combinations" or len(eq.get("rows",[]))!=166:
        ap.error("Unexpected compressed equations")
    candidates=sorted(rows,key=lambda x:x["row"])
    checks=[];invalid=Counter();matches=0
    for i in range(a.points):
        z=(301+97*i+11*i*i)%a.prime
        d=(503+131*i+17*i*i)%a.prime
        matrix=mod_rows(eq["rows"],a.prime,z,d)
        target={k:residue(v,a.prime,z,d) for k,v in TARGET.items()}
        certificate=dual_certificate(matrix,target,a.prime)
        if certificate["rank"]!=166 or not certificate["replay_verified"]:
            raise RuntimeError("Third-prime IBP replay failure at sample "+str(i))
        disagree=[];undefined=[]
        for entry in candidates:
            row=entry["row"];pred=evaluate(entry,z,d,a.prime)
            if pred is None:undefined.append(row);invalid[row]+=1
            elif pred!=certificate["certificate"].get(row,0):disagree.append(row);invalid[row]+=1
            else:matches+=1
        checks.append({"point":[a.prime,z,d],"matches":166-len(disagree)-len(undefined),
                       "disagreements":disagree,"undefined":undefined})
        print("VP05_CRT_THIRD_PRIME_POINT "+json.dumps({"point":[a.prime,z,d],
             "matches":checks[-1]["matches"],"disagreement_count":len(disagree),
             "undefined_count":len(undefined)}),flush=True)
    summary={"prime":a.prime,"points":a.points,"rows":166,
        "comparisons":166*a.points,"matching_comparisons":matches,
        "rows_failing_any_point":len(invalid),
        "all_pass":not invalid,
        "failing_row_ids":sorted(invalid),
        "crt_sha256":hashlib.sha256(crt_raw).hexdigest(),
        "equations_sha256":hashlib.sha256(eq_raw).hexdigest(),
        "symbolic_proof":False,"fermat_executed":False}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"summary":summary,"checks":checks},indent=2)+"\n",encoding="utf-8")
    print("VP05_CRT_THIRD_PRIME_SUMMARY "+json.dumps({**summary,"output":str(a.output)}),flush=True)

if __name__=="__main__":main()
